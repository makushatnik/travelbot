from telebot.types import Message
from loader import bot, log
from database.db import db


@bot.message_handler(commands=['history'])
def history_handler(message: Message):
    print('history_handler func')
    chat_id = message.chat.id
    db.add_request(chat_id, 'history')
    bot.send_message(chat_id, "Not implemented yet. Call to admin ASAP")
