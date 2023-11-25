from datetime import datetime, timedelta

import aiogram.utils.exceptions
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from telegram_bot.create_bot import dp, bot
from telegram_bot.keyboards.inline_keyboard import Kb
from telegram_bot.keyboards.utils import h_m_keyboard
from telegram_bot.utils.database import User, Fortune, Decks, Web3
from telegram_bot.utils.languages import lang
from telegram_bot.states.main import Register
from telegram_bot.utils.logging_system import logging_to_file
from telegram_bot.utils.auto_creating_adress import BitcoinAddress, RippleAddress, EthereumAddress
from telegram_bot.states.main import Session

from aiogram_calendar import DialogCalendar, dialog_cal_callback
from aiogram_timepicker import carousel

database = User()
database_fortune = Fortune()
database_decks = Decks()
web3 = Web3()

DIR_TXT = lambda lang: f'static/text/{lang}/day_card'
DIR_TXT_GENERAL = 'static/text/general/day_card'


async def switch_language(call: types.CallbackQuery):
    try:
        if call.data == 'switch english':
            logging_to_file('info', f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский')
            database.switch_language('en', call)
            await call.message.edit_text(lang[database.get_language(call)]['start'],
                                         reply_markup=Kb.LANGUAGES)
        elif call.data == 'switch russian':
            logging_to_file('info', f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский')
            database.switch_language('ru', call)
            await call.message.edit_text(lang[database.get_language(call)]['start'],
                                         reply_markup=Kb.LANGUAGES)
        elif call.data == 'switch english_command':
            logging_to_file('info', f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский command')
            database.switch_language('en', call)
            await call.message.edit_text(lang[database.get_language(call)]['choose_language'],
                                         reply_markup=Kb.LANGUAGES_COMMAND(call))
        elif call.data == 'switch russian_command':
            logging_to_file('info', f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский command')
            database.switch_language('ru', call)
            await call.message.edit_text(lang[database.get_language(call)]['choose_language'],
                                         reply_markup=Kb.LANGUAGES_COMMAND(call))
    except aiogram.utils.exceptions.MessageNotModified:
        pass
    await call.answer()


async def full_text(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'full_text':
        logging_to_file('info', f'[{call.from_user.id} | {call.from_user.first_name}] Callback: full_text')
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
        logging_to_file('info', f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Понравилась интерпретация')
        database_fortune.change_reaction('Like', message_id)
    elif call.data == 'dislike reaction':
        logging_to_file('info', f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Не понравилась интерпретация')
        database_fortune.change_reaction('Dislike', message_id)
        

async def back_to_fortune(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    language_message = state_data['delete_msg_id']
    user_message = state_data['user_message_id']
    await bot.delete_message(chat_id=call.message.chat.id, message_id=language_message)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=user_message)


async def create_crypto_address(call: types.CallbackQuery, state: FSMContext, crypto_manager, currency):
    crypto_address = crypto_manager.create_address(call.from_user.id)
    if web3.is_user_addresses_exists(blockchain=currency.lower(), user_id=call.from_user.id):
        crypto_address = web3.get_blockchain_address(blockchain=currency.lower(), user_id=call.from_user.id)
    else:
        web3.create_unique_address(blockchain=currency.lower(), address=crypto_address, user_id=call.from_user.id)
    msg = await call.message.edit_text(lang[database.get_language(call)]['switch_payment_to_address'](currency, crypto_address),
                                 reply_markup=Kb.BACK_TO_FORTUNE(call), parse_mode="MarkdownV2")
    await state.update_data(user_message_id=msg['message_id'])


async def create_bitcoin_address(call: types.CallbackQuery, state: FSMContext):
    bitcoin_manager = BitcoinAddress()
    await create_crypto_address(call, state, bitcoin_manager, 'Bitcoin')


async def create_ethereum_address(call: types.CallbackQuery, state: FSMContext):
    ethereum_manager = EthereumAddress()
    await create_crypto_address(call, state, ethereum_manager, 'Ethereum')


async def create_ripple_address(call: types.CallbackQuery, state: FSMContext):
    ripple_manager = RippleAddress()
    await create_crypto_address(call, state, ripple_manager, 'Ripple')


async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await DialogCalendar(language=database.get_language(callback_query)).process_selection(callback_query, callback_data) # date.strftime("%d/%m/%Y")
    if selected:
        await callback_query.message.answer(
            lang[database.get_language(callback_query)]['get_date_process'],
            reply_markup=h_m_keyboard()
        )
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)

        await state.update_data(user_dateYMD=date.strftime("%Y-%m-%d"), user_dateHM="12:0")


async def process_full_my_timepicker(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    hour = data.get('hour', 12)
    minute = data.get('minute', 0)

    actions = {'plus_h': 1, 'minus_h': -1, 'plus_m': 3, 'minus_m': -3}
    action = actions.get(callback_query.data)

    if action:
        if 'h' in callback_query.data:
            hour += action
            hour = 1 if hour > 24 else 24 if hour < 1 else hour
        else:
            minute += action
            minute = (minute + 60) % 60 if minute < 0 else minute % 60

    await callback_query.message.edit_reply_markup(h_m_keyboard(hour, minute))
    await state.update_data(hour=hour, minute=minute, user_dateHM=f"{hour}:{minute}")


async def result_full_my_timepicker(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    result_dataYMD = data['user_dateYMD']
    result_dataHM = data['user_dateHM']
    date_obj = datetime.strptime(result_dataYMD, "%Y-%m-%d")
    time_obj = datetime.strptime(result_dataHM, "%H:%M")

    full_date = datetime.combine(date_obj, time_obj.time())

    await state.update_data(user_date=full_date)
    await callback_query.message.answer(
        lang[database.get_language(callback_query)]['get_location_start'](full_date),
    )
    await callback_query.message.delete()
    state = dp.current_state()
    await state.set_state('input_location')
    await Register.input_location.set()



def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian', 'switch english_command',
                                                              'switch russian_command'], state='*')
    dp.register_callback_query_handler(full_text, text=['full_text'], state=[Session.session, Session.session_3_cards])
    dp.register_callback_query_handler(back_to_fortune, text=['back_to_fortune'], state='*')
    dp.register_callback_query_handler(create_bitcoin_address, text=['bitcoin_address'], state='*')
    dp.register_callback_query_handler(create_ethereum_address, text=['ethereum_address'], state='*')
    dp.register_callback_query_handler(create_ripple_address, text=['ripple_address'], state='*')
    dp.register_callback_query_handler(add_reaction, text=['like reaction', 'dislike reaction'],
                                       state=[Session.session, Session.session_3_cards])
    dp.register_callback_query_handler(process_dialog_calendar, dialog_cal_callback.filter(), state='*')
    dp.register_callback_query_handler(process_full_my_timepicker, text=['plus_h', 'plus_m', 'minus_h', 'minus_m'], state='*')
    dp.register_callback_query_handler(result_full_my_timepicker, text=['select_h_m'], state='*')
