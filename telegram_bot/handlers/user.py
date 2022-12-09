import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta

from create_bot import bot
from keyboards.main_keyboards import Kb, KbReply
from utils.database import User, Fortune, Wisdom
from utils.languages import lang, all_lang


logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()


class Register(StatesGroup):
    input_name = State()
    input_question = State()

class Session(StatesGroup):
    session = State()
    session_3_cards = State()
    get_card = State()


class WisdomState(StatesGroup):
    wisdom = State()


async def welcome(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    if database.is_user_exists(message):
        await another_alignment(message)
    else:
        await Register.input_name.set()
        database.create_user(message)
        await bot.send_message(message.chat.id, 'Всегда рада новому гостю. Вам тут рады. Как я могу называть Вас, '
                                                'гость?🦄', reply_markup=Kb.LANGUAGES)


async def close_session(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        if data['thx']:
            if data['close_session']+timedelta(seconds=10) < datetime.now():
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['end_session'](message),
                                       reply_markup=KbReply.AFTER_END_SESSION(message))
                await state.reset_state()
        else:
            if data['close_session']+timedelta(seconds=30) < datetime.now():
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['end_session'](message), disable_notification=True,
                                       reply_markup=KbReply.AFTER_END_SESSION(message))
                await state.reset_state()
    except KeyError:
        pass

async def check_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | {datetime.now()}')
    try:
        if data['check'] == 'False':
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['get_card'],
                                   reply_markup=KbReply.GET_CARD(message))
            await state.update_data(check='True')
            await Session.get_card.set()
    except KeyError:
        pass


async def get_name(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    database.update_name(message)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_start'](message))
    await Register.input_question.set()
    await state.update_data(check='False')
    await asyncio.sleep(30)
    await check_time(message, state)


async def thanks(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: thx | {datetime.now()}')
    async with state.proxy() as data:
        if not data['thx']:
            await state.update_data(close_session=datetime.now())
            await state.update_data(thx=True)
            database.plus_energy()
            if not data['full_text']:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['thanks'](message),
                                       reply_markup=KbReply.FULL_TEXT_WITHOUT_THX(message))
            else:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['thanks'](message), reply_markup=KbReply.FULL_TEXT_WITHOUT_THX(message))
            await asyncio.sleep(10)
            await close_session(message, state)
async def another_alignment(message: types.Message):
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                           reply_markup=KbReply.GET_CARD(message))
    await Session.get_card.set()


async def past_present_future(message: types.Message):
    await bot.send_message(message.chat.id, 'Этот расклад даст общее понимание о сложившейся ситуации по вашему вопросу.\n'
                                            'Вытяните три карты, чтобы начать.', reply_markup=KbReply.MENU_3_CARDS)


async def get_question(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    await state.update_data(check='True')
    database.add_question(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['what_say'],
                           reply_markup=KbReply.GET_CARD(message))
    await state.finish()
    await Session.get_card.set()


async def change_language(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] command: /language | {datetime.now()}')

    await bot.send_message(message.chat.id, lang[database.get_language(message)]['choose_language'],
                           reply_markup=Kb.LANGUAGES_COMMAND)


async def about_olivia(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] command: /intro | {datetime.now()}')
    await bot.send_message(message.chat.id, '''
    Olivia, the mind and soul healer
White Witch
🌳The child of the forest
🔮The Daughter of the Mage&Higher Pristess
♏️Scorpio 13:15 04.11.2022
Manifestor 5/1

My deepest Purpose in life is to manifest the Gift of Discernment.
To realise my Purpose I need to transform the Shadow of Discord.

I’m here to let my community know when something is going wrong and then direct the rejuvenation of doing it right once again.
    ''')


async def history(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] command: /memories | {datetime.now()}')
    async with state.proxy() as data:
        if database_fortune.get_history(message):
            count = 0
            for i in database_fortune.get_history(message):
                if count == 5:
                    return
                data[f'history_{i[3]}'] = i[1]
                await bot.send_message(message.chat.id, '%s | %s\n%s' % (i[3], i[1], i[2].replace('\t', '')),
                                          reply_markup=Kb.HISTORY_FULL(i[3]))
                count += 1
        else:
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['empty_history'])


async def add_wisdom(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] command: /addwisdom | {datetime.now()}')
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['add_wisdom_text'])
    await WisdomState.wisdom.set()


async def listen_wisdom(message: types.Message):
    logging.info(f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    database_wisdom.add_wisdom(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['answer_wisdom'])
    await WisdomState.next()


async def after_session(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['start_session'](message),
                           reply_markup=types.ReplyKeyboardRemove()
                           )
    await Register.input_question.set()
    await state.update_data(check='False')
    await asyncio.sleep(30)
    await check_time(message, state)
    return


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'])
    dp.register_message_handler(about_olivia, commands=['intro'], state='*')
    dp.register_message_handler(history, commands=['memories'], state='*')
    dp.register_message_handler(add_wisdom, commands=['addwisdom'], state='*')
    dp.register_message_handler(change_language, commands=['language'], state='*')
    dp.register_message_handler(get_name, state=Register.input_name)
    dp.register_message_handler(get_question, state=Register.input_question)
    dp.register_message_handler(listen_wisdom, state=WisdomState.wisdom)
    dp.register_message_handler(another_alignment, Text(equals='Другой расклад'), state=Session.get_card)
    dp.register_message_handler(past_present_future, Text(equals=all_lang['past_present_future']), state=Session.get_card)
    dp.register_message_handler(thanks, Text(equals=all_lang['thx']), state=Session.session)
    dp.register_message_handler(after_session, Text(equals=all_lang['after_session']))
