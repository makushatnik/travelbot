from telebot.types import Message
from keyboards.reply.reply import remove_keyboard
from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=["help"])
def bot_help(message: Message):
    chat_id = message.chat.id
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.send_message(chat_id, "\n".join(text), reply_markup=remove_keyboard())
