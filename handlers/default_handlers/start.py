from telebot.types import Message
from keyboards.reply.reply import get_help_keyboard
from loader import bot
from database.orm import User


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    chat_id = message.chat.id
    from_user = message.from_user
    if User.get_or_none(User.user_id == from_user.id) is None:
        User.create(
            user_id=from_user.id,
            username=from_user.username,
            first_name=from_user.first_name,
            last_name=from_user.last_name,
        )
    bot.send_message(chat_id, 'Привет! Я бот для выбора отелей.\nЧтобы узнать мои команды напиши "/help"',
                     reply_markup=get_help_keyboard())
