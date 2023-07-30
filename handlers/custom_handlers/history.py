from telebot.types import Message
from loader import bot
from database.db import db
from database.orm import User


@bot.message_handler(commands=['history'])
def history_handler(message: Message):
    print('history_handler func')
    chat_id = message.chat.id
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.send_message(user_id, "Вы не зарегистрированы. Напишите /start")
        return

    bot.send_message(chat_id, "Not implemented yet. Call to admin ASAP")
