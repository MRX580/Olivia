import logging

from datetime import datetime

import aiogram.utils.exceptions
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from create_bot import dp
from keyboards.main_keyboards import Kb
from utils.database import User, Fortune, Decks
from utils.languages import lang
from states.main import Session


logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_decks = Decks()

DIR_TXT = lambda lang: f'static/text/{lang}/day_card'



async def switch_language(call: types.CallbackQuery):
    try:
        if call.data == 'switch english':
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский | {datetime.now()}')
            database.switch_language('en', call)
            await call.message.edit_text(lang[database.get_language(call)]['start'],
                                         reply_markup=Kb.LANGUAGES)
        elif call.data == 'switch russian':
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский | {datetime.now()}')
            database.switch_language('ru', call)
            await call.message.edit_text(lang[database.get_language(call)]['start'],
                                         reply_markup=Kb.LANGUAGES)
        elif call.data == 'switch english_command':
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский command | {datetime.now()}')
            database.switch_language('en', call)
            await call.message.edit_text(lang[database.get_language(call)]['choose_language'],
                                         reply_markup=Kb.LANGUAGES_COMMAND)
        elif call.data == 'switch russian_command':
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский command | {datetime.now()}')
            database.switch_language('ru', call)
            await call.message.edit_text(lang[database.get_language(call)]['choose_language'],
                                         reply_markup=Kb.LANGUAGES_COMMAND)
    except aiogram.utils.exceptions.MessageNotModified:
        pass
    await call.answer()


async def full_text(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'full_text':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: full_text | {datetime.now()}')
        data = await state.get_data()
        text = data[call.message.message_id]
        if len(text) > 4096:
            await call.message.edit_text(text[:4096])
            await call.message.answer(text[4096:8192])
            if len(text) > 8192:
                await call.message.answer(text[8192:12288])
        else:
            await call.message.edit_text(text)
        await state.update_data(full_text=True)


async def full_text_history(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data = open(f'{DIR_TXT(database.get_language(call))}/{data[f"{call.data}"]["card_name"]}.txt', 'r').read()
        if len(data) > 4096:
            for x in range(0, len(data), 4096):
                print(call.data)
                await call.message.edit_text(data[x:x + 4096], reply_markup=Kb.HISTORY_BACK(call.data))
        else:
            print(call.data)
            await call.message.edit_text(data, reply_markup=Kb.HISTORY_BACK(call.data))
        dp.register_callback_query_handler(back_text_history, text=call.data+'_back')

async def back_text_history(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        call_data = call.data[:-5]
        text = open(f'{DIR_TXT(database.get_language(call))}/{data[f"{call_data}"]["card_name"]}.txt','r').read()[:150]
        await call.message.edit_text(f'{data[f"{call_data}"]["time"]}\nquestion...\n\n<b>{data[f"{call_data}"]["card_name"]}</b>\n<i>{text}</i>',
                                     reply_markup=Kb.HISTORY_FULL(call_data), parse_mode='HTML')


def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian', 'switch english_command',
                                                              'switch russian_command'], state='*')
    dp.register_callback_query_handler(full_text, text=['full_text'], state=Session.session)
