from telebot.types import Message
from loader import bot, log
from database.db import db


@bot.message_handler(commands=['bestdeal'])
def bestdeal_handler(message: Message):
    print('bestdeal_handler func')
    chat_id = message.chat.id
    db.add_request(chat_id, 'bestdeal')
    bot.send_message(chat_id, "Not implemented yet. Call to admin ASAP")
