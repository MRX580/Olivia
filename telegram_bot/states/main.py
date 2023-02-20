from aiogram.dispatcher.filters.state import State, StatesGroup
class Register(StatesGroup):
    input_name = State()
    input_question = State()

class Session(StatesGroup):
    session = State()
    session_3_cards = State()
    get_card = State()

class FortuneState(StatesGroup):
    question = State()

class WisdomState(StatesGroup):
    wisdom = State()