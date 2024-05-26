from aiogram.dispatcher.filters.state import State, StatesGroup


class Register(StatesGroup):
    input_name = State()
    input_question = State()
    input_date = State()
    input_location = State()
    input_language = State()


class Session(StatesGroup):
    session = State()
    session_3_cards = State()
    get_card = State()


class FortuneState(StatesGroup):
    question = State()


class WisdomState(StatesGroup):
    wisdom = State()


class ChannelNewsLetter(StatesGroup):
    wait_for_data = State()
    confirm_newletter_data = State()
