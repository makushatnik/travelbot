from telebot.types import Message
from loader import bot
from database.orm import User
from states.states import UserStates
from keyboards.inline.inline import get_language_keyboard
from utils.utils import get_user_state
from telebot.callback_data import CallbackData

ru_lang = CallbackData('ru_RU', prefix="search")


@bot.message_handler(commands=['language'])
def language_handler(message: Message):
    print('language_handler func')
    chat_id = message.chat.id
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.send_message(user_id, "Вы не зарегистрированы. Напишите /start")
        return

    bot.set_state(chat_id, UserStates.select_language)
    with bot.retrieve_data(chat_id) as data:
        data["user_id"] = user_id
        data["state"] = UserStates.select_language
    # bot.register_next_step_handler(message, process_select_language)
    bot.send_message(chat_id, "Select language", reply_markup=get_language_keyboard())


def process_select_language(message: Message,  answer: str):
    print('process_select_language func')
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = answer
    if language not in ['ru_RU', 'en_EN']:
        bot.send_message(chat_id, 'Incorrect language')
        bot.delete_state(chat_id)
        return

    user = User.get_or_none(User.user_id == user_id)
    if user:
        user.language = language
        user.save()
        bot.send_message(chat_id, 'Language saved!')
        bot.delete_state(chat_id)


@bot.callback_query_handler(func=None, config=ru_lang.filter())
def callback_language_worker(call):
    print('language callback_worker func')
    chat_id = call.message.chat.id
    state = get_user_state(bot, chat_id)
    if state == UserStates.select_language.name:
        process_select_language(call.message, call.data)
