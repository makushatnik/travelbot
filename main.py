import telebot
from datetime import datetime

LOG_FILE = 'log.txt'
TOKEN = '5474253233:AAEJAgtOWZbm4OjF_UMqc9NoFkcYM6otcu8'
DATETIME_FORMAT = '%d/%m/%y %H:%M'
HISTORY_FILE = 'history.txt'
# ERRORS
INCORRECT_COMMAND = 'Incorrect command'


def log(text: str) -> None:
    with open(LOG_FILE, 'a') as fw:
        fw.write('%s\n' % text)


def hello() -> str:
    """ Just pings Telegram bot. """
    return "Привет"


def highprice() -> str:
    return 'OK'


def lowprice() -> str:
    return 'OK'


def bestdeal() -> str:
    return 'OK'


def get_history(username: str) -> str:
    """ Get History by Username """
    results = []
    with open(HISTORY_FILE) as fr:
        for line in fr:
            if username in line:
                results.append(line)
    return ''.join(results)


def add_command(username: str, command: str) -> None:
    """ Add Command to a History file """
    with open(HISTORY_FILE, 'a') as fw:
        fw.write('%s: %s' % (username, command))


def history(username: str) -> str:
    """ Main function """
    return 'OK'


def main():
    bot = telebot.TeleBot(TOKEN, parse_mode=None)
    log('Bot started at: %s' % datetime.now().strftime(DATETIME_FORMAT))

    @bot.message_handler(commands=["hello-world"])
    def get_hello_message(message):
        log('Received message: \'%s\' at %s' % (message.text, datetime.now().strftime(DATETIME_FORMAT)))
        bot.send_message(message.from_user.id, hello())

    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
