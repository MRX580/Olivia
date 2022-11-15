import asyncio
import os
import random
import logging

from datetime import datetime, timedelta
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from keyboards.main_keyboards import Kb
from utils.database import User, Fortune, Wisdom
from utils.languages import lang
from create_bot import bot

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()

DIR_IMG = 'static/img/cards'
DIR_TXT = 'static/text'


class FortuneState(StatesGroup):
    question = State()


class WisdomState(StatesGroup):
    wisdom = State()


async def welcome(call: types.CallbackQuery):
    if call.data == 'switch language':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка | {datetime.now()}')
        await call.message.edit_text('Выбери язык\n'
                                     'Choose language', reply_markup=Kb.SWITCH_LANGUAGE)
    elif call.data == 'authors cards':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Авторские карты | {datetime.now()}')
        await call.message.answer(lang[database.get_language(call)]['author_cards'])
    elif call.data == 'standard':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Стандартные карты | {datetime.now()}')
        await call.message.edit_text(lang[database.get_language(call)]['fortune?'](call), reply_markup=Kb.fortune_menu(call))
    await call.answer()


async def switch_language(call: types.CallbackQuery):
    if call.data == 'switch english':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский | {datetime.now()}')
        database.switch_language('en', call)
        await call.message.answer('The language has been successfully changed')
        await call.message.answer(lang[database.get_language(call)]['send_welcome'](call), reply_markup=Kb.start_button(call))
    if call.data == 'switch russian':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский | {datetime.now()}')
        database.switch_language('ru', call)
        await call.message.answer('Язык был успешно изменен')
        await call.message.answer(lang[database.get_language(call)]['send_welcome'](call), reply_markup=Kb.start_button(call))
    await call.answer()


async def fortune(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'fortune':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Стандартное гадание | {datetime.now()}')
        if database.get_energy(call) < 50:
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Нехватает энергии для гадания | {datetime.now()}')
            await call.message.edit_text(lang[database.get_language(call)]['no_energy'], reply_markup=Kb.only_back(call))
            return
        await call.message.answer('🔮')
        await asyncio.sleep(2)
        choose = random.choice(os.listdir(DIR_IMG))[:-4]
        path_img = os.path.join(DIR_IMG, f'{choose}.jpg')
        path_txt = os.path.join(DIR_TXT, f'{choose}.txt')
        await call.message.answer_photo(open(path_img, 'rb'))
        await state.update_data(text=open(path_txt, 'r').read())
        await call.message.answer(open(path_txt, 'r').read()[0:380] + '...', reply_markup=Kb.FULL_TEXT)
        database.minus_energy(call)
        database_fortune.check_first_try(call)
        await state.update_data(card=choose)
        await call.message.answer(lang[database.get_language(call)]['question'])
        await FortuneState.question.set()
        await call.answer()
        await asyncio.sleep(600)
        try:
            if datetime.now()-timedelta(minutes=10) < database_fortune.check_session(call)+timedelta(seconds=1):
                return
            await call.message.answer(lang[database.get_language(call)]['session'], reply_markup=Kb.only_back(call))
            await FortuneState.next()
        except IndexError:
            return
    if call.data == 'fortune-1d':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Гадание раз в день | {datetime.now()}')
        if database.get_day(call) <= datetime.now():
            database.update_day(call)
        else:
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Нельзя гадать сегодня | {datetime.now()}')
            await call.message.answer(lang[database.get_language(call)]['1-d_fail'], reply_markup=Kb.only_back(call))
            return
        await call.message.answer('🔮')
        await asyncio.sleep(2)
        choose = random.choice(os.listdir(DIR_IMG))[:-4]
        path_img = os.path.join(DIR_IMG, f'{choose}.jpg')
        path_txt = os.path.join(DIR_TXT, f'{choose}.txt')
        await call.message.answer_photo(open(path_img, 'rb'))
        await state.update_data(text=open(path_txt, 'r').read())
        await call.message.answer(open(path_txt, 'r').read()[0:380] + '...', reply_markup=Kb.FULL_TEXT)
        database_fortune.check_first_try(call)
        await state.update_data(card=choose)
        await call.message.answer(lang[database.get_language(call)]['question'])
        await FortuneState.question.set()
        await call.answer()
        await asyncio.sleep(600)
        try:
            if datetime.now()-timedelta(minutes=10) < database_fortune.check_session(call)+timedelta(seconds=1):
                return
            await call.message.answer(lang[database.get_language(call)]['session'], reply_markup=Kb.only_back(call))
            await FortuneState.next()
        except IndexError:
            return
    if call.data == 'fortune-7d':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Гадание раз в неделю | {datetime.now()}')
        if database.get_week(call) <= datetime.now():
            database.update_week(call)
        else:
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Нельзя гадать на этой неделе | {datetime.now()}')
            await call.message.answer(lang[database.get_language(call)]['7-d_fail'], reply_markup=Kb.only_back(call))
            return
        await call.message.answer('🔮')
        await asyncio.sleep(2)
        choose = random.choice(os.listdir(DIR_IMG))[:-4]
        path_img = os.path.join(DIR_IMG, f'{choose}.jpg')
        path_txt = os.path.join(DIR_TXT, f'{choose}.txt')
        await call.message.answer_photo(open(path_img, 'rb'))
        await state.update_data(text=open(path_txt, 'r').read())
        await call.message.answer(open(path_txt, 'r').read()[0:380] + '...', reply_markup=Kb.FULL_TEXT)
        database_fortune.check_first_try(call)
        await state.update_data(card=choose)
        await call.message.answer(lang[database.get_language(call)]['question'])
        await FortuneState.question.set()
        await call.answer()
        await asyncio.sleep(600)
        try:
            if datetime.now()-timedelta(minutes=10) < database_fortune.check_session(call)+timedelta(seconds=1):
                return
            await call.message.answer(lang[database.get_language(call)]['session'], reply_markup=Kb.only_back(call))
            await FortuneState.next()
        except IndexError:
            return
    if call.data == 'fortune-30d':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Гадание раз в месяц | {datetime.now()}')
        if database.get_month(call) <= datetime.now():
            database.update_month(call)
        else:
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Нельзя гадать в этом месяце | {datetime.now()}')
            await call.message.answer(lang[database.get_language(call)]['30-d_fail'], reply_markup=Kb.only_back(call))
            return
        await call.message.answer('🔮')
        await asyncio.sleep(2)
        choose = random.choice(os.listdir(DIR_IMG))[:-4]
        path_img = os.path.join(DIR_IMG, f'{choose}.jpg')
        path_txt = os.path.join(DIR_TXT, f'{choose}.txt')
        await call.message.answer_photo(open(path_img, 'rb'))
        await state.update_data(text=open(path_txt, 'r').read())
        await call.message.answer(open(path_txt, 'r').read()[0:380] + '...', reply_markup=Kb.FULL_TEXT)
        database_fortune.check_first_try(call)
        await state.update_data(card=choose)
        await call.message.answer(lang[database.get_language(call)]['question'])
        await FortuneState.question.set()
        await call.answer()
        await asyncio.sleep(600)
        try:
            if datetime.now()-timedelta(minutes=10) < database_fortune.check_session(call)+timedelta(seconds=1):
                return
            await call.message.answer(lang[database.get_language(call)]['session'], reply_markup=Kb.only_back(call))
            await FortuneState.next()
        except IndexError:
            return
    if call.data == 'fortune_back':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Назад(фортуна) | {datetime.now()}')
        await call.message.edit_text(lang[database.get_language(call)]['send_welcome'](call), reply_markup=Kb.start_button(call))
        await call.answer()


async def full_text(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'full_text':
        data = await state.get_data()
        if len(data['text']) > 4096:
            for x in range(0, len(data['text']), 4096):
                await call.message.edit_text(data['text'][x:x + 4096])
        else:
            await call.message.edit_text(data['text'])


async def question(message: types.Message, state: FSMContext):
    logging.info(f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    await message.bot.send_message(message.chat.id, lang[database.get_language(message)]['question2'])
    data = await state.get_data()
    database_fortune.create_fortune(message, data['card'], message.text)
    database_fortune.check_session(message)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                           reply_markup=Kb.start_button(message))
    await FortuneState.next()


async def add_wisdom(call: types.CallbackQuery):
    if call.data == 'add_wisdom':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Добавить мудрости | {datetime.now()}')
        await call.message.answer(lang[database.get_language(call)]['add_wisdom_text'])
        await WisdomState.wisdom.set()


async def listen_wisdom(message: types.Message):
    logging.info(f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    database_wisdom.add_wisdom(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['answer_wisdom'])
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                                 reply_markup=Kb.start_button(message))
    await WisdomState.next()


def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(welcome, text=['standard', 'authors cards', 'switch language'])
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian'])
    dp.register_callback_query_handler(fortune, text=['fortune', 'fortune_back', 'fortune-1d', 'fortune-7d',
                                                      'fortune-30d'])
    dp.register_callback_query_handler(add_wisdom, text=['add_wisdom'])
    dp.register_callback_query_handler(full_text, text=['full_text'], state=FortuneState.question)
    dp.register_message_handler(question, state=FortuneState.question)
    dp.register_message_handler(listen_wisdom, state=WisdomState.wisdom)
