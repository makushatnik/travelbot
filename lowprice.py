from telebot import TeleBot


class LowPrice:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    # @bot.message_handler(commands=['lowprice'])
    # def lowprice_handler(self, message):
    #     pass
