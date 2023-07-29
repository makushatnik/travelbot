from telebot.types import Message
from loader import bot, log
from database.db import db


@bot.message_handler(commands=['highprice'])
def highprice_handler(message: Message):
    print('highprice_handler func')
    chat_id = message.chat.id
    db.add_request(chat_id, 'highprice')
    bot.send_message(chat_id, "Not implemented yet. Call to admin ASAP")
