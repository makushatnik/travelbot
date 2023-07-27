from telebot.types import Message

from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id, "Эхо без состояния или фильтра.\n" f"Сообщение: {message.text}"
    )
