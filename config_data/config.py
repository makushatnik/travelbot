import os
from dotenv import load_dotenv, find_dotenv

if find_dotenv():
    load_dotenv()
else:
    exit("Переменные окружения не загружены т.к отсутствует файл .env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv('RAPID_API_HOST')
DATABASE_NAME = os.getenv('DATABASE_NAME')

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("lowprice", "Вывести список отелей с низкой стоимостью")
)