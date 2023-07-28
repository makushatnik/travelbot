import logging
from telebot import TeleBot, logger
from telebot.storage import StateMemoryStorage
from config_data import config

log = logger
log.setLevel(logging.DEBUG)
storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
# bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage, parse_mode=None)
