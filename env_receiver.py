import os
from dotenv import load_dotenv


class EnvReceiver:
    def __init__(self):
        load_dotenv('.env')
        self.token = os.getenv('BOT_TOKEN')
        self.rapid_api_host = os.getenv('RAPID_API_HOST')
        self.rapid_api_key = os.getenv('RAPID_API_KEY')
        self.database_name = os.getenv('DATABASE_NAME')
