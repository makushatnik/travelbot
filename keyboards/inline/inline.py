from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_show_photo_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    key_no = InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_yes)
    keyboard.add(key_no)
    return keyboard


def get_language_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    key_ru = InlineKeyboardButton(text='Русский', callback_data='ru_RU')
    key_en = InlineKeyboardButton(text='English', callback_data='en_EN')
    keyboard.add(key_ru)
    keyboard.add(key_en)
    return keyboard
