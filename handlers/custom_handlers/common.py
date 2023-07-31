from telebot.types import Message, CallbackQuery
from loader import bot, log
from datetime import datetime, date, timedelta
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from states.states import UserStates
from keyboards.inline.inline import get_show_photo_keyboard
from keyboards.reply.reply import get_calendar, get_changed_calendar, remove_keyboard
from utils.constants import *
from api.api_hotels import ApiRequests
from database.orm import User, get_region_id_by_city_name

api_requests = ApiRequests(log)


def get_user_state(chat_id: int) -> str:
    with bot.retrieve_data(chat_id) as data:
        state = data["state"]
    return state.name


def make_request(message: Message):
    # print('Sending the Request!')
    chat_id = message.chat.id
    # with bot.retrieve_data(chat_id) as data:
    #     print('DATA =', data)
    api_requests.get_hotels(bot, chat_id)

    bot.delete_state(chat_id)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def common_handler(message: Message):
    print('common_handler func')
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.send_message(user_id, "Вы не зарегистрированы. Напишите /start")
        return

    chat_id = message.chat.id
    command = message.text[1:]
    if command == 'bestdeal':
        bot.send_message(chat_id, "Not implemented yet.")
        return

    bot.send_message(chat_id, "Название города?")
    bot.set_state(message.from_user.id, UserStates.get_city, chat_id)
    with bot.retrieve_data(chat_id) as data:
        data['command'] = command
        data['sort'] = get_sort(command)
        data['state'] = UserStates.get_city
    bot.register_next_step_handler(message, process_city)


@bot.message_handler(state=UserStates.get_city)
def process_city(message: Message) -> None:
    # print('process_city func')
    chat_id = message.chat.id
    city = message.text
    if city and '/' not in city:
        api_requests.get_cities(bot, chat_id, city)
        bot.set_state(chat_id, UserStates.select_city)
        with bot.retrieve_data(chat_id) as data:
            data["city"] = city
            data["state"] = UserStates.select_city
        bot.register_next_step_handler(message, process_select_city)
    else:
        bot.register_next_step_handler(message, process_city)
        bot.send_message(chat_id, "Некорректное название города. Попробуйте снова:")


@bot.message_handler(state=UserStates.select_city)
def process_select_city(message: Message) -> None:
    # print('process_select_city func')
    chat_id = message.chat.id
    city_name = message.text
    region_id = get_region_id_by_city_name(city_name)
    if region_id:
        with bot.retrieve_data(chat_id) as data:
            data["region_id"] = region_id

    # We send it just to delete latter keyboard
    bot.send_message(chat_id, "Ok", reply_markup=remove_keyboard())
    render_start_date(chat_id)


def render_start_date(chat_id: int):
    """
    Intermediate function before process_select_city and process_start_date
    """
    # print('render_start_date func')
    calendar, step = get_calendar(date.today())
    bot.send_message(chat_id, f"Введите дату въезда {LSTEP[step]}", reply_markup=calendar)
    bot.set_state(chat_id, UserStates.start_date)
    with bot.retrieve_data(chat_id) as data:
        data["state"] = UserStates.start_date


@bot.message_handler(state=UserStates.start_date)
def process_start_date(message: Message) -> None:
    # print('process_start_date func')
    chat_id = message.chat.id

    min_date = date.today()
    min_date += timedelta(days=1)
    calendar, step = get_calendar(min_date)
    bot.send_message(chat_id, f"Введите дату выезда {LSTEP[step]}", reply_markup=calendar)
    bot.set_state(chat_id, UserStates.end_date)
    with bot.retrieve_data(chat_id) as data:
        data["state"] = UserStates.end_date


@bot.message_handler(state=UserStates.end_date)
def process_end_date(message: Message) -> None:
    # print('process_end_date func')
    chat_id = message.chat.id
    bot.send_message(chat_id, "Количество отелей?", reply_markup=remove_keyboard())
    bot.set_state(chat_id, UserStates.hotel_count)
    with bot.retrieve_data(chat_id) as data:
        data["state"] = UserStates.hotel_count
    bot.register_next_step_handler(message, process_hotel_count)


@bot.message_handler(state=UserStates.hotel_count)
def process_hotel_count(message: Message) -> None:
    # print('process_hotel_count func')
    chat_id = message.chat.id
    try:
        count = int(message.text)
        if count < 1 or count > MAX_HOTEL_COUNT:
            bot.send_message(chat_id, f"Некорректное число отелей. Введите число от 1 до {MAX_HOTEL_COUNT}.")
            bot.register_next_step_handler(message, process_hotel_count)
        else:
            with bot.retrieve_data(chat_id) as data:
                data["hotel_count"] = count
            bot.send_message(chat_id, 'Показывать фото?', reply_markup=get_show_photo_keyboard())
    except ValueError as ex:
        log.error(ex)
        bot.send_message(chat_id, "Цифрами, пожалуйста")
        bot.register_next_step_handler(message, process_hotel_count)


def process_photo_needed(message: Message, answer: str) -> None:
    # print('process_photo_needed func')
    chat_id = message.chat.id
    if answer == 'yes':
        bot.send_message(chat_id, 'Какое количество фото?')
        bot.set_state(chat_id, UserStates.photo_count)
        with bot.retrieve_data(chat_id) as data:
            data["photo_needed"] = 1
            data["state"] = UserStates.photo_count
        bot.register_next_step_handler(message, process_photo_count)
    elif answer == 'no':
        bot.set_state(chat_id, UserStates.send_request)
        with bot.retrieve_data(chat_id) as data:
            data["photo_needed"] = 0
            data["state"] = UserStates.send_request
        make_request(message)


@bot.message_handler(state=UserStates.photo_count)
def process_photo_count(message: Message) -> None:
    # print('process_photo_count func')
    chat_id = message.chat.id
    try:
        count = int(message.text)
        if count < 1 or count > MAX_PHOTO_COUNT:
            bot.send_message(chat_id, f"Некорректное число фото. Введите число от 1 до {MAX_PHOTO_COUNT}")
            bot.register_next_step_handler(message, process_photo_count)
        else:
            with bot.retrieve_data(chat_id) as data:
                data["photo_count"] = count
                data["state"] = UserStates.send_request
            bot.set_state(chat_id, UserStates.send_request)
            make_request(message)
    except ValueError as ex:
        log.error(ex)
        bot.send_message(chat_id, "Цифрами, пожалуйста")
        bot.register_next_step_handler(message, process_photo_count)


@bot.message_handler(state="*", content_types=['text'])
def message_reply(message: Message):
    # print('message_reply func')
    user_id = message.from_user.id
    cur_state = bot.get_state(user_id)
    if message.text[0] == '/':
        bot.delete_state(message.chat.id)
        command = message.text[1:]
        if command in ['lowprice', 'highprice', 'bestdeal']:
            common_handler(message)
        else:
            bot.send_message(user_id, 'Incorrect command')
            log.error('Incorrect command')
    if cur_state == UserStates.get_city.name:
        bot.register_next_step_handler(message, process_city)
    elif cur_state == UserStates.hotel_count.name:
        bot.register_next_step_handler(message, process_hotel_count)
    elif cur_state == UserStates.photo_count.name:
        bot.register_next_step_handler(message, process_photo_count)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def callback_calendar(call):
    # print('calendar func')
    chat_id = call.message.chat.id
    state = get_user_state(chat_id)
    min_date = date.today()
    if state == UserStates.end_date.name:
        min_date += timedelta(days=1)
    result, key, step = get_changed_calendar(min_date, call.data)
    if not result and key:
        select_text = "Выберите дату " + "въезда" if state == UserStates.end_date else "выезда"
        bot.edit_message_text(f"{select_text} {LSTEP[step]}",
                              chat_id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        if state == UserStates.start_date.name:
            save_start_date(call.message, result)
        elif state == UserStates.end_date.name:
            save_end_date(call.message, result)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # print('callback_worker func')
    chat_id = call.message.chat.id
    state = get_user_state(chat_id)
    if state == UserStates.select_city.name:
        bot.register_next_step_handler(call.message, process_select_city)
    elif state == UserStates.hotel_count.name:
        process_photo_needed(call.message, call.data)


def save_start_date(message: Message, result: date):
    chat_id = message.chat.id
    bot.edit_message_text(f"Вы выбрали дату въезда: {result}",
                          chat_id,
                          message.message_id)

    start_date_str = result.strftime(DATE_FORMAT)
    with bot.retrieve_data(chat_id) as data:
        data["start_date"] = start_date_str
    bot.set_state(chat_id, UserStates.start_date)
    process_start_date(message)


def save_end_date(message: Message, result: date):
    chat_id = message.chat.id
    bot.edit_message_text(f"Вы выбрали дату выезда: {result}",
                          chat_id,
                          message.message_id)

    with bot.retrieve_data(chat_id) as data:
        start_date = datetime.strptime(data["start_date"], DATE_FORMAT).date()
    if start_date and result <= start_date:
        bot.send_message(chat_id, 'Дата въезда не может быть позже даты выезда!')
        with bot.retrieve_data(chat_id) as data:
            data["state"] = UserStates.select_city
        render_start_date(chat_id)
        return

    end_date_str = result.strftime(DATE_FORMAT)
    with bot.retrieve_data(chat_id) as data:
        data["end_date"] = end_date_str
    process_end_date(message)


def get_sort(command: str) -> str:
    if command == 'lowprice':
        return "PRICE_LOW_TO_HIGH"
    elif command == "highprice":
        return "PRICE_HIGH_TO_LOW"
    return ""
