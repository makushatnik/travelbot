from telebot import TeleBot


def safe_str(string: str) -> str:
    res = string.replace("'", "")
    res = res.replace("\"", "")
    return res


def get_sort(command: str) -> str:
    if command == 'lowprice':
        return "PRICE_LOW_TO_HIGH"
    elif command == "highprice":
        return "PRICE_HIGH_TO_LOW"
    elif command == "bestdeal":
        return "DISTANCE"
    return ""


def get_user_state(bot: TeleBot, chat_id: int) -> str:
    with bot.retrieve_data(chat_id) as data:
        state = data["state"]
    return state.name
