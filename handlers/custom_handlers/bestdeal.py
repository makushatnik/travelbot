from telebot.types import Message
from loader import bot
from database.db import db
from database.orm import User


@bot.message_handler(commands=['bestdeal'])
def bestdeal_handler(message: Message):
    print('bestdeal_handler func')
    chat_id = message.chat.id
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.send_message(user_id, "Вы не зарегистрированы. Напишите /start")
        return

    bot.send_message(chat_id, "Not implemented yet. Call to admin ASAP")
