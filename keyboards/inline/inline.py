from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_show_photo_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    key_no = InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_yes)
    keyboard.add(key_no)
    return keyboard
