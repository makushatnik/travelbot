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
from utils.utils import get_sort, get_user_state

api_requests = ApiRequests(log)


def make_request(message: Message):
    # print('Sending the Request!')
    chat_id = message.chat.id
    with bot.retrieve_data(chat_id) as data:
        req_data = data
        # print('DATA =', data)
    api_requests.get_hotels(bot, chat_id, req_data)

    bot.delete_state(chat_id)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def common_handler(message: Message):
    # print('common_handler func')
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        bot.send_message(user_id, "Вы не зарегистрированы. Напишите /start")
        return

    chat_id = message.chat.id
    command = message.text[1:]
    bot.send_message(chat_id, "Название города?")
    bot.set_state(message.from_user.id, UserStates.get_city, chat_id)
    with bot.retrieve_data(chat_id) as data:
        data['command'] = command
        data['sort'] = get_sort(command)
        data['state'] = UserStates.get_city
        data['language'] = user.language
    user = None
    bot.register_next_step_handler(message, process_city)


@bot.message_handler(state=UserStates.get_city)
def process_city(message: Message) -> None:
    # print('process_city func')
    chat_id = message.chat.id
    city = message.text
    if city and '/' not in city:
        with bot.retrieve_data(chat_id) as data:
            language = data['language']
        api_requests.get_cities(bot, chat_id, city, language)
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
    with bot.retrieve_data(chat_id) as data:
        command = data["command"]
        if region_id:
            data["region_id"] = region_id

    if command == 'bestdeal':
        render_min_price(message)
    else:
        # We send it just to delete latter keyboard
        bot.send_message(chat_id, "Ok", reply_markup=remove_keyboard())
        render_start_date(chat_id)


def render_min_price(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите минимальную цену", reply_markup=remove_keyboard())
    bot.set_state(chat_id, UserStates.min_price)
    with bot.retrieve_data(chat_id) as data:
        data["state"] = UserStates.min_price
    bot.register_next_step_handler(message, process_min_price)


@bot.message_handler(state=UserStates.min_price, is_digit=True)
def process_min_price(message: Message) -> None:
    chat_id = message.chat.id
    min_price = round(float(message.text), 2)
    if min_price <= 0 or min_price > MAX_PRICE:
        bot.send_message(chat_id, "Incorrect min price!")
        return

    bot.send_message(chat_id, "Введите максимальную цену")
    bot.set_state(chat_id, UserStates.max_price)
    with bot.retrieve_data(chat_id) as data:
        data['min_price'] = min_price
        data['state'] = UserStates.max_price
    bot.register_next_step_handler(message, process_max_price)


@bot.message_handler(state=UserStates.max_price, is_digit=True)
def process_max_price(message: Message) -> None:
    chat_id = message.chat.id
    max_price = round(float(message.text), 2)
    if max_price <= 0 or max_price > MAX_PRICE:
        bot.send_message(chat_id, "Incorrect max price!")
        return

    with bot.retrieve_data(chat_id) as data:
        min_price = data['min_price']
    if max_price < min_price:
        bot.send_message(chat_id, "Максимальная цена не может быть меньше минимальной.")
        bot.set_state(chat_id, UserStates.select_city)
        render_min_price(message)
        return

    bot.send_message(chat_id, "Введите максимальное расстояние от центра")
    bot.set_state(chat_id, UserStates.max_distance)
    with bot.retrieve_data(chat_id) as data:
        data['max_price'] = max_price
        data['state'] = UserStates.max_distance
    bot.register_next_step_handler(message, process_max_distance)


@bot.message_handler(state=UserStates.max_distance, is_digit=True)
def process_max_distance(message: Message) -> None:
    chat_id = message.chat.id
    max_distance = round(float(message.text), 2)
    if max_distance <= 0 or max_distance > MAX_DISTANCE:
        bot.send_message(chat_id, "Incorrect max distance!")
        return

    with bot.retrieve_data(chat_id) as data:
        data['max_distance'] = max_distance

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
    state = get_user_state(bot, chat_id)
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
    state = get_user_state(bot, chat_id)
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
