import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
# from amplitude import Amplitude, BaseEvent

from create_bot import bot, dp
from keyboards.main_keyboards import Kb, KbReply
from utils.database import User, Fortune, Wisdom
from utils.languages import lang, all_lang
from callbacks.user import full_text_history, back_text_history
from states.main import Session, WisdomState, Register


logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()

# amplitude = Amplitude("bbdc22a8304dbf12f2aaff6cd40fbdd3")
#


# def callback_fun(e, code, message):
#     """A callback function"""
#     print(e)
#     print(code, message)
# amplitude.configuration.callback = callback_fun

# async def typing(message: types.Message):
#     msg = await bot.send_message(message.chat.id, 'Typing.')
#     for i in range(2):
#         if i != 0:
#             await bot.edit_message_text(message_id=msg['message_id'], text='Typing.', chat_id=message.chat.id)
#         await asyncio.sleep(0.5)
#         for j in range(1, 3):
#             await bot.edit_message_text(message_id=msg['message_id'], text=msg['text'] + '.' * j, chat_id=message.chat.id)
#             await asyncio.sleep(0.5)
#     await msg.delete()


async def welcome(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    # amplitude.track(BaseEvent(event_type='Welcome', user_id=f'{message.from_user.id}', user_properties={'source': 'test'}))

    if database.is_user_exists(message):
        # await typing(message)
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                               reply_markup=KbReply.MAIN_MENU(message))
        await Session.session.set()
    else:
        await Register.input_name.set()
        database.create_user(message)
        await bot.send_message(message.chat.id, 'Всегда рада новому гостю. Вам тут рады. Как я могу называть Вас, '
                                                'гость?🦄', reply_markup=Kb.LANGUAGES)


async def divination(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    text = lang[database.get_language(message)]['divination_text']
    if message.text.lower() in all_lang['another_alignment']:
        text = lang[database.get_language(message)]['another_alignment_text']

    await bot.send_message(message.chat.id, text,
                           reply_markup=KbReply.GET_CARD(message))
    await Session.get_card.set()


async def close_session(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        if data['thx']:
            if data['close_session']+timedelta(hours=1) < datetime.now():
                logging.info(
                    f'[{message.from_user.id} | {message.from_user.first_name}] Callback: close_session(thx) | {datetime.now()}')
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['end_session'](message),
                                       reply_markup=KbReply.AFTER_END_SESSION(message))
                await state.reset_state()
        else:
            if data['close_session']+timedelta(minutes=5) < datetime.now():
                logging.info(
                    f'[{message.from_user.id} | {message.from_user.first_name}] Callback: close_session | {datetime.now()}')
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
    await asyncio.sleep(45)
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
            await asyncio.sleep(300)
            await close_session(message, state)


async def past_present_future(message: types.Message):
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['start_3_cards']
                           , reply_markup=KbReply.MENU_3_CARDS(message))


async def get_question(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    await state.update_data(check='True')
    database.add_question(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['what_say'],
                           reply_markup=KbReply.GET_CARD(message))
    await state.finish()
    async with state.proxy() as data:
        data['question'] = message.text
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
            msg_d = []
            for count, i in enumerate(database_fortune.get_history(message)):
                if count == 5:
                    break
                time = i[4][:-7].replace('-', '/') # 2022-11-18 13:04:38.097140
                msg = await bot.send_message(message.chat.id, '%s\n%s\n\n<b>%s</b>\n<i>%s</i>' % (time, i[5], i[2], i[3].replace('\t', '')), parse_mode='HTML')
                await bot.edit_message_reply_markup(message_id=msg['message_id'], chat_id=message.chat.id,
                                                    reply_markup=Kb.HISTORY_FULL(msg["message_id"]))
                data[f'{msg["message_id"]}'] = {'time': time, 'card_name': i[2], 'full_text': i[3]}
                msg_d.append(msg["message_id"])
            dp.register_callback_query_handler(full_text_history, text=msg_d)
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
    await asyncio.sleep(45)
    await check_time(message, state)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'])
    dp.register_message_handler(about_olivia, commands=['intro'], state='*')
    dp.register_message_handler(history, commands=['memories'], state='*')
    dp.register_message_handler(add_wisdom, commands=['addwisdom'], state='*')
    dp.register_message_handler(change_language, commands=['language'], state='*')
    dp.register_message_handler(get_name, state=Register.input_name)
    dp.register_message_handler(get_question, state=Register.input_question)
    dp.register_message_handler(listen_wisdom, state=WisdomState.wisdom)
    dp.register_message_handler(divination, Text(equals=[*all_lang['divination'], *all_lang['another_alignment']]), state=Session.get_card)
    dp.register_message_handler(past_present_future, Text(equals=all_lang['past_present_future']), state=Session.get_card)
    dp.register_message_handler(thanks, Text(equals=all_lang['thx']), state=Session.session)
    dp.register_message_handler(after_session, Text(equals=all_lang['after_session']))
