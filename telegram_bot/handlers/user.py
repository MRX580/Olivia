import asyncio
import json
from pathlib import Path

import requests

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from aiogram.types import LabeledPrice, InputFile, ContentType
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


def convert_str_in_datetime(time_str: str) -> datetime:
    time_str = time_str.replace('"', '')
    time = list(map(int, time_str[:-7].split(' ')[0].split('-'))) + list(
        map(int, time_str[:-7].split(' ')[1].split(':')))
    time_result = datetime(month=time[1], year=time[0], day=time[2], hour=time[3], minute=time[4], second=time[5])
    return time_result


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


async def close_session_with_delay(message: types.Message, state: FSMContext, time: int = 0):
    if time:
        await asyncio.sleep(time)
    data = await state.get_data()
    try:
        time = convert_str_in_datetime(data['close_session'])
        if not data['thx']:
            if time + timedelta(hours=1) < datetime.now():
                logging_to_file_telegram('info',
                                         f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Сессия закрыта без "Спасибо"')
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['end_session'](message),
                                       reply_markup=KbReply.AFTER_END_SESSION(message))
                await state.reset_state()
        else:
            if time + timedelta(minutes=5) < datetime.now():
                logging_to_file_telegram('info',
                                         f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Сессия закрыта с "Спасибо"')
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['end_session'](message),
                                       disable_notification=True,
                                       reply_markup=KbReply.AFTER_END_SESSION(message))
                await state.reset_state()
    except KeyError:
        pass


async def check_time(message: types.Message, state: FSMContext):
    await asyncio.sleep(90)
    data = await state.get_data()
    try:
        if data['check'] == 'False': # Заменить на время
            logging_to_file_telegram('info',
                                     f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | Пользователь не задал вопрос')
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['get_card'],
                                   reply_markup=KbReply.GET_CARD(message))
            data = await state.get_data('rand_card')
            try:
                rand_card = data['rand_card']
                rand_card[0], rand_card[1] = rand_card[1], rand_card[0]
                prompt = data['prompt']
            except KeyError:
                rand_card = None
                prompt = {'messages': [{'role': 'system', 'content': None}]}
            await state.finish()
            await state.update_data(rand_card=rand_card, prompt=prompt, check='True', question=None)
            await Session.get_card.set()
    except KeyError:
        logging_to_file_telegram('info',
                                 f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | Пользователь задал вопрос')
        pass


async def get_name(message: types.Message):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Придумал себе имя "{message.text}" при регистрации')
    database.update_name(message)
    lang_user = database.get_language(message)
    if lang_user == 'ru':
        await bot.send_message(
            message.chat.id,
            f'Вам тут рады, {message.text}, добро пожаловать.\n\nНачнем наше первое гадание?\nЗадайте свой вопрос 👇'
        )
    elif lang_user == 'en':
        await bot.send_message(
            message.chat.id,
            f'Warm welcome, {message.text}, honored to meet you.\n\nLet’s start our first reading?\nAsk your question 👇'
        )

    await Register.input_question.set()


async def thanks(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Нажато "Спасибо"')
    async with state.proxy() as data:
        if not data['thx']:
            if CODE_MODE == 'PROD':
                amplitude.track(
                    BaseEvent(event_type='Thanks', user_id=f'{message.from_user.id}'))
            await state.update_data(close_session=json.dumps(datetime.now(), default=str))
            await state.update_data(thx=True)
            database.add_thanks(data['message_id'])
            database.plus_energy()
            if not data['full_text']:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['thanks'](message),
                                       reply_markup=KbReply.FULL_TEXT_WITHOUT_THX(message))
            else:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['thanks'](message),
                                       reply_markup=KbReply.FULL_TEXT_WITHOUT_THX(message))
            await close_session_with_delay(message, state, 300)


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


async def donate(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Подписка Standard"))
    keyboard.add(types.KeyboardButton(text="Подписка month unlimited"))
    keyboard.add(types.KeyboardButton(text="Подписка Lifetime"))

    # Отправляем сообщение с клавиатурой
    await message.answer(
        "Выберите свою подписку:",
        reply_markup=keyboard
    )


async def standard_subscription(message: types.Message, state: FSMContext):
    prices = [LabeledPrice(label='Standard', amount=100)]
    await bot.send_invoice(
        message.chat.id,
        title='Покупка standard подписки',
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
        title='Покупка unlimited month подписки',
        description='С этой подпиской вы получаете безграничные гадания на протяжении месяца!',
        payload='unique_payload',
        provider_token='PROVIDER_TOKEN',
        currency='XTR',
        prices=prices,
        start_parameter='purchase',
        photo_url='https://t3.ftcdn.net/jpg/01/09/07/98/360_F_109079871_OigjZSPKSyTu7ap2nD3no18RjkLIH4eV.jpg'
    )


async def handle_subscription_choice(message: types.Message):
    if message.text == "Подписка Standard":
        payload = "standard_subscription"
        price = 100
        label = "Подписка Standard"
        description = "Подписка Standard даёт вам в течении месяца открывать до 10 карт в день!"
    elif message.text == "Подписка month unlimited":
        payload = "standard_subscription"
        price = 400
        label = "Подписка month unlimited"
        description = "Подписка month unlimited даёт вам бессконечно открывать карты в течении месяца"
    elif message.text == "Подписка Lifetime":
        payload = "lifetime_subscription"
        price = 4000
        label = "Подписка Lifetime"
        description = "Подписка Lifetime даёт вам пожизненый доступ к бессконечному количеству гаданий"
    else:
        await message.reply("Unknown subscription")
        return

    # Send invoice
    await bot.send_invoice(
        chat_id=message.from_user.id,
        title=label,
        description=description,
        payload=payload,
        provider_token="gklsnlhjrs@$jgae32523",
        currency="XTR",
        prices=[LabeledPrice(label=label, amount=price)],
        photo_url='https://i.imgur.com/dI7HPmJ.jpeg',
        start_parameter=payload
    )


async def successful_payment(message: types.Message) -> None:
    item_id = message.successful_payment.invoice_payload

    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )

    if item_id == "standard_subscription":
        await message.answer(
            "Поздравляем! Вам выдана подписка Standard на месяц. Вы можете открывать до 10 карт в день!")
        database.change_user_subscription(message, 'standard')
    elif item_id == "month_unlimited_subscription":
        await message.answer(
            "Поздравляем! Вам выдана подписка month unlimited. Вы можете открывать карты неограниченно в течение месяца!")
        database.change_user_subscription(message, 'month_unlimited')
        database.set_subscription_expiration(message)
    elif item_id == "lifetime_subscription":
        await message.answer(
            "Поздравляем! Вам выдана пожизненная подписка Lifetime. Вы можете открывать карты неограниченно!")
        database.change_user_subscription(message, 'lifetime')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'], state='*')
    dp.register_message_handler(about_olivia, commands=['intro'], state='*')
    dp.register_message_handler(join, commands=['join'], state='*')
    dp.register_message_handler(payment, commands=['payment'], state='*')
    dp.register_message_handler(change_language, commands=['language'], state='*')
    dp.register_message_handler(donate, commands=['donate'], state='*')
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
    dp.register_message_handler(handle_subscription_choice,
                                text=["Подписка Standard", "Подписка month unlimited", "Подписка Lifetime"], state='*')
    dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)