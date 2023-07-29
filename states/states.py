from telebot.handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    get_city = State()
    select_city = State()
    price_range = State()
    distance_range = State()
    start_date = State()
    end_date = State()
    hotel_count = State()
    # photo_needed = State()
    photo_count = State()
    send_request = State()
