import asyncio
import os
import random

from datetime import datetime, timedelta
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from keyboards.main_keyboards import Kb
from utils.database import User, Fortune
from utils.languages import lang
from create_bot import bot

database = User()
database_fortune = Fortune()

DIR_IMG = 'static/img/cards'
DIR_TXT = 'static/text'


class Fortune(StatesGroup):
    question = State()


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


async def fortune(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'fortune':
        # await call.message.answer(lang[database.get_language(call)]['fortune?'], reply_markup=Kb.fortune(call))
        if database.get_energy(call) < 50:
            await call.message.edit_text(lang[database.get_language(call)]['no_energy'], reply_markup=Kb.only_back(call))
            return
        await call.message.answer('🔮')
        await asyncio.sleep(2)
        choose = random.choice(os.listdir(DIR_IMG))[:-4]
        path_img = os.path.join(DIR_IMG, f'{choose}.jpg')
        path_txt = os.path.join(DIR_TXT, f'{choose}.txt')
        await call.message.answer_photo(open(path_img, 'rb'))
        if len(open(path_txt, 'r').read()) > 4096:
            for x in range(0, len(open(path_txt, 'r').read()), 4096):
                await call.message.answer(open(path_txt, 'r').read()[x:x + 4096])
        else:
            await call.message.answer(open(path_txt, 'r').read())
        database.minus_energy(call)
        await state.update_data(card=choose)
        await call.message.answer(lang[database.get_language(call)]['question'])
        await Fortune.question.set()
        await call.answer()
        await asyncio.sleep(600)
        if datetime.now()-timedelta(minutes=10) < database_fortune.check_session(call)+timedelta(seconds=1):
            return
        await call.message.answer(lang[database.get_language(call)]['session'], reply_markup=Kb.only_back(call))
        await Fortune.next()
    if call.data == 'fortune_back':
        await call.message.edit_text(lang[database.get_language(call)]['send_welcome'](call), reply_markup=Kb.start_button(call))
        await call.answer()


async def question(message: types.Message, state: FSMContext):
    await message.bot.send_message(message.chat.id, lang[database.get_language(message)]['question2'])
    data = await state.get_data()
    database_fortune.create_fortune(message, data['card'], message.text)
    database_fortune.check_session(message)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                           reply_markup=Kb.start_button(message))
    await Fortune.next()


def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(welcome, text=['standard', 'authors cards', 'switch language'])
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian'])
    dp.register_callback_query_handler(fortune, text=['fortune', 'fortune_back'])
    dp.register_message_handler(question, state=Fortune.question)
