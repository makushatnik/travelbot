from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram_bot_calendar import DetailedTelegramCalendar


def get_help_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_help = KeyboardButton("/help")
    markup.add(btn_help)
    return markup


def get_keyboard_for_cities():
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)


def get_calendar():
    return DetailedTelegramCalendar().build()


def get_changed_calendar(data: str):
    return DetailedTelegramCalendar().process(data)


def remove_keyboard():
    return ReplyKeyboardRemove()
