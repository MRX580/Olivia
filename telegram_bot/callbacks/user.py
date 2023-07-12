import logging

from datetime import datetime

import aiogram.utils.exceptions
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from telegram_bot.create_bot import dp, bot
from keyboards.inline_keyboard import Kb
from utils.database import User, Fortune, Decks
from utils.languages import lang
from states.main import Session


logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_decks = Decks()

DIR_TXT = lambda lang: f'static/text/{lang}/day_card'
DIR_TXT_GENERAL = 'static/text/general/day_card'


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
        text = data['text_data']
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
        full_text_message = data[call.data]['full_text']
        if full_text_message:
            if len(full_text_message) > 4096:
                for x in range(0, len(full_text_message), 4096):
                    await call.message.edit_text(full_text_message[x:x + 4096], reply_markup=Kb.HISTORY_BACK(call.data))
                    break
            else:
                if not full_text_message:
                    await call.message.edit_text('Не удалось загрузить интерпретацию', reply_markup=Kb.HISTORY_BACK(call.data))
                await call.message.edit_text(full_text_message, reply_markup=Kb.HISTORY_BACK(call.data))
        else:
            await call.message.edit_text('Не удалось загрузить интерпретацию', reply_markup=Kb.HISTORY_BACK(call.data))
        dp.register_callback_query_handler(back_text_history, text=call.data+'_back', state='*')


async def back_text_history(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        call_data = call.data[:-5]
        data_m = data[f"{call_data}"]
        text = data_m['short_text']
        await call.message.edit_text(f'{data_m["time"]}\n{data_m["user_q"]}\n\n<b>{data_m["card_name"]}</b>\n<i>{text}</i>',
                                     reply_markup=Kb.HISTORY_FULL(call_data), parse_mode='HTML')


async def add_reaction(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    message_id = state_data['message_id']
    if call.data == 'like reaction':
            logging.info(
                f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Понравилась интерпретация | {datetime.now()}')
            database_fortune.change_reaction('Like', message_id)
    elif call.data == 'dislike reaction':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Не понравилась интерпретация | {datetime.now()}')
        database_fortune.change_reaction('Dislike', message_id)
        

async def back_to_fortune(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    language_message = state_data['delete_msg']
    user_message = state_data['user_message']
    await bot.delete_message(chat_id=call.message.chat.id, message_id=language_message['message_id'])
    await bot.delete_message(chat_id=call.message.chat.id, message_id=user_message['message_id'])


def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian', 'switch english_command',
                                                              'switch russian_command'], state='*')
    dp.register_callback_query_handler(full_text, text=['full_text'], state=[Session.session, Session.session_3_cards])
    dp.register_callback_query_handler(back_to_fortune, text=['back_to_fortune'], state='*')
    dp.register_callback_query_handler(add_reaction, text=['like reaction', 'dislike reaction'],
                                       state=[Session.session, Session.session_3_cards])
