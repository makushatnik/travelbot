from telebot import TeleBot
from telebot.handler_backends import State, StatesGroup


class LowpriceStates(StatesGroup):
    get_city = State()
    select_city = State()
    start_date = State()
    end_date = State()
    hotel_count = State()
    photo_needed = State()
    photo_count = State()
    send_request = State()


class LowPrice:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    # @bot.message_handler(commands=['lowprice'])
    # def lowprice_handler(self, message):
    #     pass
