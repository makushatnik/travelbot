from telebot.types import Message
from loader import bot, log
from datetime import datetime, date
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from states.states import LowpriceStates
from keyboards.inline.inline import get_show_photo_keyboard
from keyboards.reply.reply import get_calendar, get_changed_calendar, remove_keyboard
from utils.constants import *
from api.api_hotels import ApiRequests
from database.db import db

api_requests = ApiRequests(log)


def make_request(message: Message):
    # print('Sending the Request!')
    chat_id = message.chat.id
    # with bot.retrieve_data(chat_id) as data:
    #     print('DATA =', data)
    api_requests.get_hotels(bot, chat_id, db)

    db.delete_requests(chat_id)
    bot.delete_state(chat_id)


@bot.message_handler(commands=['lowprice'])
def lowprice_handler(message: Message):
    # print('lowprice_handler func')
    chat_id = message.chat.id
    db.add_request(chat_id, 'lowprice')
    bot.send_message(chat_id, "Название города?")
    bot.set_state(message.from_user.id, LowpriceStates.get_city, chat_id)
    bot.register_next_step_handler(message, process_city)


@bot.message_handler(state=LowpriceStates.get_city)
def process_city(message: Message) -> None:
    # print('process_city func')
    chat_id = message.chat.id
    city = message.text
    message.write_access_allowed = False
    if city and '/' not in city:
        with bot.retrieve_data(chat_id) as data:
            data["city"] = city
        db.add_city_to_request(chat_id, city)
        api_requests.get_cities(bot, chat_id, db, city)
        bot.set_state(chat_id, LowpriceStates.select_city)
        bot.register_next_step_handler(message, process_select_city)
    else:
        bot.register_next_step_handler(message, process_city)
        bot.send_message(chat_id, "Некорректное название города. Попробуйте снова:")


@bot.message_handler(state=LowpriceStates.select_city)
def process_select_city(message: Message) -> None:
    # print('process_city func')
    chat_id = message.chat.id
    city_name = message.text
    message.write_access_allowed = False
    with bot.retrieve_data(chat_id) as data:
        data["city_name"] = city_name
    db.add_region_id_to_request_by_city_name(chat_id, city_name)

    # We send it just to delete latter keyboard
    bot.send_message(chat_id, "Ok", reply_markup=remove_keyboard())
    render_start_date(chat_id)


def render_start_date(chat_id: int):
    """
    Intermediate function before process_select_city and process_start_date
    """
    calendar, step = get_calendar()
    bot.send_message(chat_id, f"Введите дату въезда {LSTEP[step]}", reply_markup=calendar)
    bot.set_state(chat_id, LowpriceStates.start_date)


@bot.message_handler(state=LowpriceStates.start_date)
def process_start_date(message: Message) -> None:
    # print('process_start_date func')
    chat_id = message.chat.id

    calendar, step = get_calendar()
    bot.send_message(chat_id, f"Введите дату выезда {LSTEP[step]}", reply_markup=calendar)
    bot.set_state(chat_id, LowpriceStates.end_date)


@bot.message_handler(state=LowpriceStates.end_date)
def process_end_date(message: Message) -> None:
    # print('process_end_date func')
    chat_id = message.chat.id
    bot.send_message(chat_id, "Количество отелей?", reply_markup=remove_keyboard())
    bot.set_state(chat_id, LowpriceStates.hotel_count)
    bot.register_next_step_handler(message, process_hotel_count)


@bot.message_handler(state=LowpriceStates.hotel_count)
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
            db.add_hotel_count_to_request(chat_id, count)
            bot.send_message(chat_id, 'Показывать фото?', reply_markup=get_show_photo_keyboard())
    except ValueError as ex:
        log.error(ex)
        bot.send_message(chat_id, "Цифрами, пожалуйста")
        bot.register_next_step_handler(message, process_hotel_count)


def process_photo_needed(message: Message, answer: str) -> None:
    # print('process_photo_needed func')
    chat_id = message.chat.id
    if answer == 'yes':
        db.set_photo_needed_to_request(chat_id, answer)
        bot.send_message(chat_id, 'Какое количество фото?')
        bot.set_state(chat_id, LowpriceStates.photo_count)
        bot.register_next_step_handler(message, process_photo_count)
    elif answer == 'no':
        bot.set_state(chat_id, LowpriceStates.send_request)
        make_request(message)


@bot.message_handler(state=LowpriceStates.photo_count)
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
            db.add_photo_count_to_request(chat_id, count)
            bot.set_state(chat_id, LowpriceStates.send_request)
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
        lowprice_handler(message)
    if cur_state == LowpriceStates.get_city.name:
        bot.register_next_step_handler(message, process_city)
    elif cur_state == LowpriceStates.hotel_count.name:
        bot.register_next_step_handler(message, process_hotel_count)
    elif cur_state == LowpriceStates.photo_count.name:
        bot.register_next_step_handler(message, process_photo_count)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def callback_calendar(c):
    # print('calendar func')
    chat_id = c.message.chat.id
    result, key, step = get_changed_calendar(c.data)
    user_step = db.get_step(chat_id)[0][0]
    if not result and key:
        select_text = "Выберите дату " + "въезда" if user_step == 3 else "выезда"
        bot.edit_message_text(f"{select_text} {LSTEP[step]}",
                              chat_id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        if user_step == 3:
            save_start_date(c.message, result)
        elif user_step == 4:
            save_end_date(c.message, result)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # print('callback_worker func')
    chat_id = call.message.chat.id
    step = db.get_step(chat_id)[0][0]
    if step == 2:
        bot.register_next_step_handler(call.message, process_select_city)
    elif step == 6:
        process_photo_needed(call.message, call.data)


def save_start_date(message: Message, result: date):
    chat_id = message.chat.id
    bot.edit_message_text(f"Вы выбрали дату въезда: {result}",
                          chat_id,
                          message.message_id)

    start_date_str = result.strftime(DATE_FORMAT)
    db.add_start_date_to_request(chat_id, start_date_str)
    with bot.retrieve_data(chat_id) as data:
        data["start_date"] = start_date_str
    bot.set_state(chat_id, LowpriceStates.start_date)
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
        db.set_current_step(chat_id, 3)
        render_start_date(chat_id)
        return

    end_date_str = result.strftime(DATE_FORMAT)
    with bot.retrieve_data(chat_id) as data:
        data["end_date"] = end_date_str
    db.add_end_date_to_request(chat_id, end_date_str)
    bot.set_state(chat_id, LowpriceStates.end_date)
    process_end_date(message)
