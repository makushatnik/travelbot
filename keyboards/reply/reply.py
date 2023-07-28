from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date


def get_help_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_help = KeyboardButton("/help")
    markup.add(btn_help)
    return markup


def get_keyboard_for_cities():
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)


def get_calendar(min_date: date):
    return DetailedTelegramCalendar(locale='ru',
                                    current_date=min_date, min_date=min_date).build()


def get_changed_calendar(min_date: date, data: str):
    return DetailedTelegramCalendar(locale='ru', min_date=min_date).process(data)


def remove_keyboard():
    return ReplyKeyboardRemove()
