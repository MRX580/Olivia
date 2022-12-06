import logging

from datetime import datetime
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from keyboards.main_keyboards import Kb
from utils.database import User, Fortune, Decks
from utils.languages import lang
from handlers.user import Session

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_decks = Decks()

DIR_TXT = lambda lang: f'static/text/{lang}/day_card'


class FortuneState(StatesGroup):
    question = State()


async def switch_language(call: types.CallbackQuery):
    if call.data == 'switch english':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский | {datetime.now()}')
        database.switch_language('en', call)
        await call.message.edit_text(lang[database.get_language(call)]['start'],
                                     reply_markup=Kb.LANGUAGES)
    if call.data == 'switch russian':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский | {datetime.now()}')
        database.switch_language('ru', call)
        await call.message.edit_text(lang[database.get_language(call)]['start'],
                                     reply_markup=Kb.LANGUAGES)
    if call.data == 'switch english_command':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский command | {datetime.now()}')
        database.switch_language('en', call)
        await call.message.edit_text(lang[database.get_language(call)]['choose_language'],
                                     reply_markup=Kb.LANGUAGES_COMMAND)
    if call.data == 'switch russian_command':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский command | {datetime.now()}')
        database.switch_language('ru', call)
        await call.message.edit_text(lang[database.get_language(call)]['choose_language'],
                                     reply_markup=Kb.LANGUAGES_COMMAND)
    await call.answer()


async def full_text(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'full_text':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: full_text | {datetime.now()}')
        data = await state.get_data()
        if len(data['text']) > 4096:
            await call.message.edit_text(data['text'][:4096])
            await call.message.answer(data['text'][4096:8192])
            if len(data['text']) > 8192:
                await call.message.answer(data['text'][8192:12288])
        else:
            await call.message.edit_text(data['text'])
        await state.update_data(full_text=True)


async def full_text_history(call: types.CallbackQuery, state: FSMContext):
    if call.data in database.get_last_5_history(call):
        async with state.proxy() as data:
            data = open(f'{DIR_TXT(database.get_language(call))}/{data[f"history_{call.data}"]}.txt', 'r').read()
            if len(data) > 4096:
                for x in range(0, len(data), 4096):
                    await call.message.edit_text(data[x:x + 4096], reply_markup=Kb.HISTORY_BACK(call.data))
            else:
                await call.message.edit_text(data, reply_markup=Kb.HISTORY_BACK(call.data))


async def back_text_history(call: types.CallbackQuery, state: FSMContext):
    if call.data in database.get_last_5_history_back(call):
        async with state.proxy() as data:
            await call.message.edit_text(f'{call.data[:-5]} | {data[f"history_{call.data[:-5]}"]}\n' +
                                         open(
                                             f'{DIR_TXT(database.get_language(call))}/{data[f"history_{call.data[:-5]}"]}.txt',
                                             'r').read()[:150],
                                         reply_markup=Kb.HISTORY_FULL(call.data[:-5]))


def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian', 'switch english_command',
                                                              'switch russian_command'], state='*')
    dp.register_callback_query_handler(full_text, text=['full_text'], state=Session.session)
    dp.register_callback_query_handler(full_text_history, text=database.get_data_history())
    dp.register_callback_query_handler(back_text_history, text=database.get_data_history_back())
