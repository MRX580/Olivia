import asyncio
import json
import os
from pathlib import Path

import aiohttp
import requests

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from aiogram.types import LabeledPrice, InputFile, ContentType, ParseMode
from amplitude import Amplitude, BaseEvent

from telegram_bot.create_bot import bot, CODE_MODE
from telegram_bot.keyboards.inline_keyboard import Kb
from telegram_bot.keyboards.reply_keyboard import KbReply
from telegram_bot.utils.database import User, Fortune, Wisdom, Temp
from telegram_bot.utils.languages import lang, all_lang
from telegram_bot.utils.logging_system import logging_to_file_telegram
from telegram_bot.states.main import Session, WisdomState, Register

database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()
database_temp = Temp()

current_dir = Path(__file__).resolve().parent

load_dotenv(find_dotenv())
amplitude = Amplitude("bbdc22a8304dbf12f2aaff6cd40fbdd3")


def callback_fun(e, code, message):
    print(e)
    print(code, message)


amplitude.configuration.callback = callback_fun

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_IMG_DONATE = os.path.join(BASE_DIR, '..', 'static', 'img', 'static', 'donate_picture.jpg')


def convert_str_in_datetime(time_str: str) -> datetime:
    time_str = time_str.replace('"', '')
    date_part, time_part = time_str[:-7].split(' ')
    y, m, d = map(int, date_part.split('-'))
    h, mi, s = map(int, time_part.split(':'))
    return datetime(year=y, month=m, day=d, hour=h, minute=mi, second=s)


async def welcome(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text}')
    await state.finish()

    user_language = database.get_language(message)
    if not database.get_name(message) and user_language:
        await bot.send_message(
            message.from_user.id,
            lang[user_language]['your_name_question'],
            reply_markup=types.ReplyKeyboardRemove()
        )
        await Register.input_name.set()
        return
    elif not user_language:
        await Register.input_language.set()
        if not database.is_user_exists(message):
            database.create_user(message)
        msg = await bot.send_message(
            message.chat.id,
            'Welcome, wonderer.\nВсегда рада новому гостю.\n\nНа каком языке предпочитаете общаться?\nWhich language '
            'would you prefer?',
            reply_markup=Kb.LANGUAGES
        )
        await state.update_data(welcome_message_id=msg.message_id)
    else:
        await bot.send_message(
            message.chat.id,
            lang[database.get_language(message)]['send_welcome'](message),
            reply_markup=KbReply.MAIN_MENU(message)
        )
        await Session.session.set()


async def divination(message: types.Message):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text}')
    text = lang[database.get_language(message)]['divination_text']
    if message.text.lower() in all_lang['another_alignment']:
        text = lang[database.get_language(message)]['another_alignment_text']

    await bot.send_message(message.chat.id, text,
                           reply_markup=KbReply.GET_CARD(message))
    await Session.get_card.set()


async def close_session_with_delay(message: types.Message, state: FSMContext, delay: int = 0):
    if delay:
        await asyncio.sleep(delay)
    data = await state.get_data()
    try:
        close_time = convert_str_in_datetime(data['close_session'])
        threshold = timedelta(hours=1) if not data.get('thx') else timedelta(minutes=5)
        if close_time + threshold < datetime.now():
            logging_to_file_telegram('info',
                                     f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Сессия закрыта {"с" if data.get("thx") else "без"} "Спасибо"')
            await bot.send_message(
                message.chat.id,
                lang[database.get_language(message)]['end_session'](message),
                reply_markup=KbReply.AFTER_END_SESSION(message),
                disable_notification=data.get('thx', False)
            )

            msg = await bot.send_photo(message.chat.id, photo=open(DIR_IMG_DONATE, 'rb'), reply_markup=Kb.DONATE(message))
            await state.reset_state()
            await state.update_data(delete_msg_id=msg['message_id'])
    except KeyError:
        pass


async def check_time(message: types.Message, state: FSMContext):
    await asyncio.sleep(90)
    data = await state.get_data()
    if data.get('check') == 'False':
        logging_to_file_telegram('info',
                                 f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | Пользователь не задал вопрос')
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['get_card'],
                               reply_markup=KbReply.GET_CARD(message))
        rand_card = data.get('rand_card', [None, None])[::-1] if data.get('rand_card') else None
        prompt = data.get('prompt', {'messages': [{'role': 'system', 'content': None}]})
        await state.finish()
        await state.update_data(rand_card=rand_card, prompt=prompt, check='True', question=None)
        await Session.get_card.set()
    else:
        logging_to_file_telegram('info',
                                 f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | Пользователь задал вопрос')


async def get_name(message: types.Message):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Придумал себе имя "{message.text}" при регистрации')
    database.update_name(message)
    lang_user = database.get_language(message)
    welcome_text = (
        f'Вам тут рады, {message.text}, добро пожаловать.\n\nНачнем наше первое гадание?\nЗадайте свой вопрос 👇'
        if lang_user == 'ru'
        else f'Warm welcome, {message.text}, honored to meet you.\n\nLet’s start our first reading?\nAsk your question 👇'
    )
    await bot.send_message(message.chat.id, welcome_text)
    await Register.input_question.set()


async def thanks(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Нажато "Спасибо"')
    data = await state.get_data()
    if not data.get('thx'):
        if CODE_MODE == 'PROD':
            amplitude.track(BaseEvent(event_type='Thanks', user_id=str(message.from_user.id)))
        await state.update_data(close_session=json.dumps(datetime.now(), default=str), thx=True)
        database.add_thanks(data['message_id'])
        database.plus_energy()
        reply = KbReply.FULL_TEXT_WITHOUT_THX(message) if data.get('full_text') else KbReply.FULL_TEXT_WITHOUT_THX(
            message)
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['thanks'](message),
                               reply_markup=reply)
        await close_session_with_delay(message, state, 3)


async def get_question(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] При получении вопроса написал:\n{message.text}')
    if CODE_MODE == 'PROD':
        amplitude.track(BaseEvent(event_type='UserQuestion', user_id=f'{message.from_user.id}',
                                  event_properties={'question': message.text}))
    await state.update_data(check='True')
    database.add_question(message, message.text)
    data = await state.get_data('rand_card')
    try:
        rand_card = data['rand_card']
        rand_card[0], rand_card[1] = rand_card[1], rand_card[0]
        prompt = data['prompt']
    except KeyError:
        rand_card = None
        prompt = {'messages': [{'role': 'system', 'content': None}]}
    await state.finish()
    await state.update_data(rand_card=rand_card, prompt=prompt, question=message.text)
    await Session.get_card.set()
    from telegram_bot.handlers.fortunes import get_card, update_energy_and_schedule_session_close
    if CODE_MODE == 'PROD':
        amplitude.track(BaseEvent(event_type='OneCard', user_id=f'{message.from_user.id}'))
    await get_card(message, state)
    await update_energy_and_schedule_session_close(state, message)


async def change_language(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] command: /language')

    msg = await bot.send_message(message.chat.id, lang[database.get_language(message)]['choose_language'],
                                 reply_markup=Kb.LANGUAGES_COMMAND(message))
    await state.update_data(delete_msg_id=msg['message_id'], user_message_id=message['message_id'])


async def about_olivia(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] command: /intro')
    msg = await bot.send_message(message.chat.id, lang[database.get_language(message)]['about_olivia'],
                                 reply_markup=Kb.BACK_TO_FORTUNE(message))
    await state.update_data(delete_msg_id=msg['message_id'], user_message_id=message['message_id'])


async def feedback(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] command: /addwisdom ')
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['add_feedback_text'])
    await state.update_data(last_state=await state.get_state())
    await WisdomState.wisdom.set()


async def join(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] command: /join')
    msg = await bot.send_message(message.chat.id, lang[database.get_language(message)][
        'join'] + '<a href="https://t.me/+Y32Jaq8sMCFhZTVi">Olivia_Familia</a>', parse_mode='HTML',
                                 reply_markup=Kb.BACK_TO_FORTUNE(message))
    await state.update_data(delete_msg_id=msg['message_id'], user_message_id=message['message_id'])


async def listen_wisdom(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Callback: listen_wisdom | Написал {message.text}')
    database_wisdom.add_wisdom(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['answer_feedback'](message))
    data = await state.get_data()  # Сделать проверку на сессию
    await state.finish()
    try:
        if data['last_state'] == 'Session:session':
            await Session.session.set()
            await state.update_data(thx=data['thx'], full_text=data['full_text'])
            return
        elif data['last_state'] == 'Session:session_3_cards':
            await Session.session_3_cards.set()
            if data['past'] and data['present'] and data['future']:
                await Session.session.set()
            await state.update_data(thx=data['thx'], full_text=data['full_text'])
            await state.update_data(past=data['past'], present=data['present'], future=data['future'])
            return
    except KeyError:
        pass
    await WisdomState.next()


async def after_session(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['start_session'](message),
                           reply_markup=types.ReplyKeyboardRemove()
                           )
    await Register.input_question.set()
    await state.update_data(check='False')
    await check_time(message, state)


async def payment(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['payment_choice'],
                           reply_markup=Kb.PAYMENT)
    await state.update_data(delete_msg_id=message['message_id'])


def get_city_info(city):
    api_key = 'dfcf0c52ee3e443eb6b799640b21b754'
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    params = {
        'q': city,
        'key': api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200 and data.get('results'):
        # Вам могут быть интересны различные данные, например, координаты города
        city_info = data['results'][0]
        return city_info
    else:
        return None


async def get_location(message: types.Message, state: FSMContext):
    try:
        city = get_city_info(message.text)['components']['city']
    except KeyError:
        await message.answer(lang[database.get_language(message)]['city_not_recognized'])
        return

    data = await state.get_data()
    date = data['user_date']
    if city is not None:
        try:
            database.update_natal_data(message, date)
            database.update_natal_city(message, city)
            database_temp.check_entry(message.from_user.id)
            logging_to_file_telegram('info',
                                     f'[{message.from_user.id} | {message.from_user.first_name}] Заполнил натальные данные:\n{date}, {city} ')
        except Exception as e:
            print(e)
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['city_end_message'])
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_start'](message))
        await Register.input_question.set()
        await state.update_data(check='False')
        await check_time(message, state)


async def donate_payment(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Стандарт"))
    keyboard.add(types.KeyboardButton(text="Безлимитный месяц"))
    keyboard.add(types.KeyboardButton(text="Пожизненно"))

    msg = await message.answer(
        "Пожалуйста, выберите тип подписки:\n\n"
        "🔹 *Стандарт* — 10 гаданий в день вместо 3 на протяжении месяца.\n\n"
        "🔹 *Безлимитный месяц* — неограниченное количество гаданий в течение одного месяца.\n\n"
        "🔹 *Пожизненная подписка* — бесконечные гадания на всю жизнь!",
        reply_markup=keyboard
    )

    msg_back = await message.answer("Вернуться к гаданиям?", reply_markup=Kb.BACK_TO_FORTUNE(message))
    await state.update_data(delete_msg_id=[msg['message_id'], msg_back['message_id'], message['message_id']])


async def standard_subscription(message: types.Message, state: FSMContext):
    prices = [LabeledPrice(label='Стандарт', amount=100)]
    await bot.send_invoice(
        message.chat.id,
        title='Покупка "Стандарт" подписки',
        description='С этой подпиской вы получаете 10 гаданий каждый день!',
        payload='unique_payload',
        provider_token='PROVIDER_TOKEN',
        currency='XTR',
        prices=prices,
        start_parameter='purchase',
        photo_url='https://t3.ftcdn.net/jpg/01/09/07/98/360_F_109079871_OigjZSPKSyTu7ap2nD3no18RjkLIH4eV.jpg'
    )


async def month_unlimited_subscription(message: types.Message, state: FSMContext):
    prices = [LabeledPrice(label='Unlimited month', amount=400)]
    await bot.send_invoice(
        message.chat.id,
        title='Покупка "Безлимитный месяц" подписки',
        description='С этой подпиской вы получаете безграничные гадания на протяжении месяца!',
        payload='unique_payload',
        provider_token='PROVIDER_TOKEN',
        currency='XTR',
        prices=prices,
        start_parameter='purchase',
        photo_url='https://t3.ftcdn.net/jpg/01/09/07/98/360_F_109079871_OigjZSPKSyTu7ap2nD3no18RjkLIH4eV.jpg'
    )


async def choice_payment(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Криптовалютой"))
    keyboard.add(types.KeyboardButton(text="Telegram Stars"))

    if message.text == "Стандарт":
        description = "Подписка \"Стандарт\" даёт вам в течении месяца открывать до 10 карт в день!"
        subscription = "standard"
    elif message.text == "Безлимитный месяц":
        description = "Подписка \"Безлимитный месяц\" даёт вам бессконечно открывать карты в течении месяца"
        subscription = "month_unlimited"
    elif message.text == "Пожизненно":
        description = "Подписка \"Пожизненно\" даёт вам пожизненый доступ к бессконечному количеству гаданий"
        subscription = "lifetime"
    else:
        await message.reply("Unknown subscription")
        return

    await state.update_data(subscription=subscription)
    msg = await bot.send_message(message.chat.id,
                                 f'Вы выбрали подписку "{message.text}"\n{description}\n\nВыберите удобный способ оплаты',
                                 reply_markup=keyboard)
    temp_state = await state.get_data('delete_msg_id')
    await bot.delete_message(message.chat.id, temp_state['delete_msg_id'][1])  # back_message from last action
    temp_state['delete_msg_id'].pop(1)
    msg_back = await message.answer("Вернуться к гаданиям?", reply_markup=Kb.BACK_TO_FORTUNE(message))
    temp_state['delete_msg_id'].append(msg['message_id'])
    temp_state['delete_msg_id'].append(msg_back['message_id'])
    await state.update_data(delete_msg_id=temp_state['delete_msg_id'], user_message_id=message['message_id'])


async def handle_subscription_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subscription = data['subscription']
    if subscription == "standard":
        payload = "standard_subscription"
        price = 1
        label = "Стандарт"
        description = "Подписка \"Стандарт\" даёт вам в течении месяца открывать до 10 карт в день!"
    elif subscription == "month_unlimited":
        payload = "month_unlimited_subscription"
        price = 1
        label = "Безлимитный месяц"
        description = "Подписка \"Безлимитный месяц\" даёт вам бессконечно открывать карты в течении месяца"
    elif subscription == "lifetime":
        payload = "lifetime_subscription"
        price = 1
        label = "Пожизненно"
        description = "Подписка \"Пожизненно\" даёт вам пожизненый доступ к бессконечному количеству гаданий"
    else:
        await message.reply("Unknown subscription")
        return

    # Send invoice
    msg_invoice = await bot.send_invoice(
        chat_id=message.from_user.id,
        title=label,
        description=description,
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=label, amount=price)],
        photo_url='https://i.imgur.com/dI7HPmJ.jpeg',
        start_parameter=payload
    )

    temp_state = await state.get_data('delete_msg_id')
    await bot.delete_message(message.chat.id, temp_state['delete_msg_id'][3])  # back_message from last action
    temp_state['delete_msg_id'].pop(3)
    temp_state['delete_msg_id'].append(msg_invoice['message_id'])
    temp_state['delete_msg_id'].append(temp_state['user_message_id'])
    msg_back = await message.answer("Вернуться к гаданиям?", reply_markup=Kb.BACK_TO_FORTUNE(message))
    temp_state['delete_msg_id'].append(msg_back['message_id'])
    await state.update_data(delete_msg_id=temp_state['delete_msg_id'], user_message_id=message['message_id'])


async def precheckout_callback(update: types.PreCheckoutQuery):
    query = update

    if (query.invoice_payload == 'standard_subscription' or query.invoice_payload == 'month_unlimited_subscription'
            or query.invoice_payload == 'lifetime_subscription'):
        await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
    else:
        await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                            error_message="Что-то пошло не так, свяжитесь с @MRXlllll для решение "
                                                          "проблемы")


async def successful_payment(message: types.Message, state: FSMContext) -> None:
    item_id = message.successful_payment.invoice_payload

    # Логика выдачи подписки
    if item_id == "standard_subscription":
        await message.answer(
            "Поздравляем! Вам выдана подписка \"Стандарт\" на месяц. Вы можете открывать до 10 карт в день в течении месяца!\nЧто ж, давайте теперь я вам погадаю"
        )
        database.set_subscription_expiration(message)
        database.change_user_subscription(message, 'standard')
    elif item_id == "month_unlimited_subscription":
        await message.answer(
            "Поздравляем! Вам выдана подписка \"Безлимитный месяц\". Вы можете открывать карты неограниченно в течение месяца!\nЧто ж, давайте теперь я вам погадаю"
        )
        database.change_user_subscription(message, 'month_unlimited')
        database.set_subscription_expiration(message)
    elif item_id == "lifetime_subscription":
        await message.answer(
            "Поздравляем! Вам выдана подписка \"Пожизненно\". Вы можете открывать карты неограниченно!\nЧто ж, давайте теперь я вам погадаю"
        )
        database.change_user_subscription(message, 'lifetime')

    await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_start'](message))
    await Register.input_question.set()
    await state.update_data(check='False')
    await check_time(message, state)


async def crypto(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    subscription = data['subscription']
    user_id = message.from_user.id

    charge = await create_charge(subscription, user_id, 0)

    if "error" not in charge:
        charge_url = charge["data"]["hosted_url"]
        msg = await message.reply(f"Ссылка на оплату: [Оплатить здесь]({charge_url})", parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = await message.reply(f"Ошибка создания платежа: {charge['error']}",
                                  reply_markup=types.ReplyKeyboardRemove())

    temp_state = await state.get_data('delete_msg_id')
    await bot.delete_message(message.chat.id, temp_state['delete_msg_id'][3])  # back_message from last action
    temp_state['delete_msg_id'].pop(3)
    temp_state['delete_msg_id'].append(msg['message_id'])
    temp_state['delete_msg_id'].append(temp_state['user_message_id'])
    msg_back = await message.answer("Вернуться к гаданиям?", reply_markup=Kb.BACK_TO_FORTUNE(message))
    temp_state['delete_msg_id'].append(msg_back['message_id'])
    await state.update_data(delete_msg_id=temp_state['delete_msg_id'], user_message_id=message['message_id'])


async def create_charge(item, user_id, amount: float):
    url = "https://api.commerce.coinbase.com/charges/"
    headers = {
        "Content-Type": "application/json",
        "X-CC-Api-Key": os.getenv("COINBASE_TOKEN"),
    }
    payload = {
        "name": f"{item}",
        "description": f"Оплата от пользователя {user_id}",
        "pricing_type": "fixed_price",
        "local_price": {
            "amount": f"{amount}",
            "currency": "USD"
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 201:
                charge_data = await response.json()
                return charge_data
            else:
                error = await response.text()
                return {"error": error}


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'], state='*')
    dp.register_message_handler(about_olivia, commands=['intro'], state='*')
    dp.register_message_handler(join, commands=['join'], state='*')
    dp.register_message_handler(payment, commands=['payment'], state='*')
    dp.register_message_handler(change_language, commands=['language'], state='*')
    dp.register_message_handler(donate_payment, commands=['donate'], state='*')
    dp.register_message_handler(crypto, commands=['crypto'], state='*')
    dp.register_message_handler(get_name, state=Register.input_name)
    dp.register_message_handler(get_question, state=Register.input_question)
    dp.register_message_handler(listen_wisdom, state=WisdomState.wisdom)
    dp.register_message_handler(divination, Text(equals=[*all_lang['divination'], *all_lang['another_alignment']]),
                                state=Session.get_card)
    dp.register_message_handler(thanks, Text(equals=all_lang['thx']), state=Session.session)
    dp.register_message_handler(after_session, Text(equals=all_lang['after_session']))
    dp.register_message_handler(after_session, Text(equals=all_lang['after_session']))
    dp.register_message_handler(after_session, Text(equals=all_lang['after_session']))
    dp.register_message_handler(get_location, state=Register.input_location)
    dp.register_message_handler(choice_payment,
                                text=["Стандарт", "Безлимитный месяц", "Пожизненно"], state='*')
    dp.register_message_handler(crypto, text="Криптовалютой", state='*')
    dp.register_message_handler(handle_subscription_choice, text="Telegram Stars", state='*')
    dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
    dp.register_pre_checkout_query_handler(precheckout_callback)