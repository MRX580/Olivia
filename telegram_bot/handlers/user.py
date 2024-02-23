import asyncio
import json
import requests

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
from amplitude import Amplitude, BaseEvent
from aiogram_calendar import DialogCalendar

from telegram_bot.create_bot import bot, dp, CODE_MODE
from telegram_bot.keyboards.inline_keyboard import Kb
from telegram_bot.keyboards.reply_keyboard import KbReply
from telegram_bot.utils.database import User, Fortune, Wisdom, Temp
from telegram_bot.utils.languages import lang, all_lang
from telegram_bot.utils.logging_system import logging_to_file_telegram
from telegram_bot.callbacks.user import full_text_history
from telegram_bot.states.main import Session, WisdomState, Register

database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()
database_temp = Temp()

amplitude = Amplitude("bbdc22a8304dbf12f2aaff6cd40fbdd3")


def callback_fun(e, code, message):
    """A callback function"""
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
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text}')
    await state.finish()
    if database.is_user_exists(message):
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                               reply_markup=KbReply.MAIN_MENU(message))
        await Session.session.set()
    else:
        await Register.input_name.set()
        database.create_user(message)
        await bot.send_message(message.chat.id, 'Всегда рада новому гостю. Вам тут рады. Как я могу называть Вас, '
                                                'гость?🦄', reply_markup=Kb.LANGUAGES)


async def divination(message: types.Message):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text}')
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
                logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Сессия закрыта без "Спасибо"')
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['end_session'](message),
                                       reply_markup=KbReply.AFTER_END_SESSION(message))
                await state.reset_state()
        else:
            if time + timedelta(minutes=5) < datetime.now():
                logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Сессия закрыта с "Спасибо"')
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['end_session'](message),
                                       disable_notification=True,
                                       reply_markup=KbReply.AFTER_END_SESSION(message))
                await state.reset_state()
    except KeyError:
        pass


async def check_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        if data['check'] == 'False':
            logging_to_file_telegram('info',
                                     f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | Карта открыта без вопроса')
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
                                 f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | Карта открыта с вопросом')
        pass


async def get_name(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Придумал себе имя "{message.text}" при регистрации')
    database.update_name(message)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_start'](message))
    await Register.input_question.set()
    await state.update_data(check='False')
    await asyncio.sleep(90)
    await check_time(message, state)
    # await bot.send_message(message.chat.id, lang[database.get_language(message)]['get_date_start'],
    #                        reply_markup=await DialogCalendar(language=database.get_language(message)).start_calendar(year=1995))
    # database_temp.check_entry(message.chat.id, False)


async def thanks(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Нажато "Спасибо"')
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
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] При получении вопроса написал:\n{message.text}')
    if CODE_MODE == 'PROD':
        amplitude.track(BaseEvent(event_type='UserQuestion', user_id=f'{message.from_user.id}',
                                  event_properties={'question': message.text}))
    await state.update_data(check='True')
    database.add_question(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['what_say'],
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
    await state.update_data(rand_card=rand_card, prompt=prompt)
    async with state.proxy() as data:
        data['question'] = message.text
    await Session.get_card.set()


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


async def history(message: types.Message, state: FSMContext):
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] command: /memories')
    async with state.proxy() as data:
        if database_fortune.get_history(message):
            msg_d = []
            for count, i in enumerate(database_fortune.get_history(message)):
                if count == 5:
                    break
                time = list(map(int, i[3][:-7].split(' ')[0].split('-'))) + list(
                    map(int, i[3][:-7].split(' ')[1].split(':')))
                tt = datetime(month=time[1], year=time[0], day=time[2], hour=time[3], minute=time[4],
                              second=time[5])  # 2022-11-18 13:04:38.097140
                time_result = '%s/%s/%s %s:%s' % (tt.day, tt.month, tt.year, tt.hour, tt.minute)
                msg = await bot.send_message(message.chat.id, '%s\n%s\n\n<b>%s</b>\n<i>%s</i>' % (
                time_result, i[4], i[1], i[2].replace('\t', '')), parse_mode='HTML')
                await bot.edit_message_reply_markup(message_id=msg['message_id'], chat_id=message.chat.id,
                                                    reply_markup=Kb.HISTORY_FULL(msg["message_id"]))
                data[f'{msg["message_id"]}'] = {'time': time_result, 'card_name': i[1], 'full_text': i[8], 'short_text': i[2],
                                                'user_q': i[4]}
                msg_d.append(msg["message_id"])
            dp.register_callback_query_handler(full_text_history, text=msg_d, state='*')
        else:
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['empty_history'])


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
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Callback: listen_wisdom | Написал {message.text}')
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
    await asyncio.sleep(90)
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
        await asyncio.sleep(90)
        await check_time(message, state)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'], state='*')
    dp.register_message_handler(about_olivia, commands=['intro'], state='*')
    dp.register_message_handler(join, commands=['join'], state='*')
    dp.register_message_handler(payment, commands=['payment'], state='*')
    dp.register_message_handler(change_language, commands=['language'], state='*')
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
