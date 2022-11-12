import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime

from create_bot import bot
from keyboards.main_keyboards import Kb
from utils.database import User
from utils.languages import lang


logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()


class Register(StatesGroup):
    input_name = State()


async def welcome(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    if database.is_user_exists(message):
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                               reply_markup=Kb.start_button(message))
    else:
        await Register.input_name.set()
        await bot.send_message(message.chat.id, 'Всегда рада новому гостю. Вам тут рады. Как я могу называть Вас, '
                                                'гость?🦄')


async def get_name(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    database.create_user(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                           reply_markup=Kb.start_button(message))
    await Register.next()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'])
    dp.register_message_handler(get_name, state=Register.input_name)
