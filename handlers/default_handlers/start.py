from telebot.types import Message
from keyboards.reply.reply import get_help_keyboard
from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    # bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Привет! Я бот для выбора отелей.\nЧтобы узнать мои команды напиши "/help"',
                     reply_markup=get_help_keyboard())
