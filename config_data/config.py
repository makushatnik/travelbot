import os
from dotenv import load_dotenv, find_dotenv

if find_dotenv():
    load_dotenv()
else:
    exit("Переменные окружения не загружены т.к отсутствует файл .env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("lowprice", "Вывести список отелей с самой низкой стоимостью"),
    ("highprice", "Вывести список отелей с самой высокой стоимостью"),
    ("bestdeal", "Вывести наиболее подходящие по цене и расположению от центра"),
    ("history", "Вывести историю поиска")
)
