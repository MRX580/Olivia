from create_bot import bot
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
from keyboards.main_keyboards import Kb
from utils.database import User
from utils.languages import lang


database = User()


async def welcome(message: types.Message):
    database.is_user_exists(message)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message), reply_markup=Kb.start_button(message))


def register_handlers_client(dp: Dispatcher):
    # dp.register_message_handler(mark_as_learned, Text(equals=all_language['send1']))
    dp.register_message_handler(welcome, commands=['start', 'help'])
    # dp.register_message_handler(choose_lang, state=welcome.choose_lang)