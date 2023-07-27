from telebot.handler_backends import State, StatesGroup


class LowpriceStates(StatesGroup):
    get_city = State()
    select_city = State()
    start_date = State()
    end_date = State()
    hotel_count = State()
    # photo_needed = State()
    photo_count = State()
    send_request = State()
