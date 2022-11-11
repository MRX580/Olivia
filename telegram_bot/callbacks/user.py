import time

from aiogram import types, Dispatcher
from utils.database import User
from keyboards.main_keyboards import Kb
from utils.languages import lang
import os, random, asyncio
database = User()

DIR = 'static/img/cards'


async def welcome(call: types.CallbackQuery):
    if call.data == 'switch language':
        await call.message.edit_text('Выбери язык\n'
                                     'Choose language', reply_markup=Kb.SWITCH_LANGUAGE)
    elif call.data == 'authors cards':
        await call.message.answer(lang[database.get_language(call)]['author_cards'])
    elif call.data == 'standard':
        await call.message.edit_text(lang[database.get_language(call)]['fortune?'](call), reply_markup=Kb.fortune(call))
    await call.answer()


async def switch_language(call: types.CallbackQuery):
    if call.data == 'switch english':
        database.switch_language('en', call)
        await call.message.answer('The language has been successfully changed')
        await call.message.answer(lang[database.get_language(call)]['send_welcome'](call), reply_markup=Kb.start_button(call))
    if call.data == 'switch russian':
        database.switch_language('ru', call)
        await call.message.answer('Язык был успешно изменен')
        await call.message.answer(lang[database.get_language(call)]['send_welcome'](call), reply_markup=Kb.start_button(call))
    await call.answer()


async def fortune(call: types.CallbackQuery):
    if call.data == 'fortune':
        # await call.message.answer(lang[database.get_language(call)]['fortune?'], reply_markup=Kb.fortune(call))
        if database.get_energy(call) < 50:
            await call.message.edit_text(lang[database.get_language(call)]['no_energy'], reply_markup=Kb.only_back(call))
            return
        await call.message.answer('🔮')
        await asyncio.sleep(2)
        await call.message.answer_photo(open(os.path.join(DIR, random.choice(os.listdir(DIR))), 'rb'))
        database.minus_energy(call)
        await call.message.answer(lang[database.get_language(call)]['repeat'](call), reply_markup=Kb.fortune(call))
    if call.data == 'fortune_back':
        await call.message.edit_text(lang[database.get_language(call)]['send_welcome'](call), reply_markup=Kb.start_button(call))
    await call.answer()


def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(welcome, text=['standard', 'authors cards', 'switch language'])
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian'])
    dp.register_callback_query_handler(fortune, text=['fortune', 'fortune_back'])