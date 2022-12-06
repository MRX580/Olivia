import asyncio
import logging
import random
import os
import io

from PIL import Image
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime

from create_bot import bot
from keyboards.main_keyboards import Kb, KbReply
from utils.database import User, Fortune, Wisdom, Decks
from utils.languages import lang, all_lang
from utils.decks import decks


logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()
database_decks = Decks()


class Register(StatesGroup):
    input_name = State()
    input_question = State()

class Session(StatesGroup):
    session = State()
    get_card = State()


class WisdomState(StatesGroup):
    wisdom = State()


async def welcome(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    if database.is_user_exists(message):
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                               reply_markup=KbReply.GET_CARD(message))
        await Session.get_card.set()
    else:
        await Register.input_name.set()
        database.create_user(message)
        await bot.send_message(message.chat.id, 'Всегда рада новому гостю. Вам тут рады. Как я могу называть Вас, '
                                                'гость?🦄', reply_markup=Kb.LANGUAGES)


async def check_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | {datetime.now()}')
    try:
        if data['check'] == 'False':
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['get_card'],
                                   reply_markup=KbReply.GET_CARD(message))
            await state.finish()
    except KeyError:
        pass


# async def check_time_fortune(message: types.Message, state: FSMContext):



async def get_name(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    database.update_name(message)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_start'](message))
    await Register.input_question.set()
    await state.update_data(check='False')
    await asyncio.sleep(30)
    await check_time(message, state)


async def get_fortune(message: types.Message, state: FSMContext,
                      DIR_IMG='static/img/decks_1',
                      DIR_TXT=lambda lang: f'static/text/{lang}/day_card',
                      DIR_REVERSE=lambda lang: f'static/text/{lang}/reverse'):
    if database.get_olivia_energy() > 0:
        if message.text in all_lang['get_card_again']:
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_again'](message), reply_markup=types.ReplyKeyboardRemove()
)
            await Register.input_question.set()
            await state.update_data(check='False')
            await asyncio.sleep(30)
            await check_time(message, state)
            return
    else:
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['no_energy'])
        return
    database.get_name(message)
    await bot.send_animation(message.chat.id, 'https://media.giphy.com/media/3oKIPolAotPmdjjVK0/giphy.gif')
    await asyncio.sleep(2)
    rand_card = random.randint(0, 77)
    lang_user = database.get_language(message)
    card = os.listdir(DIR_IMG)[rand_card][:-4]
    card_name = decks[card][lang_user]
    path_img = os.path.join(DIR_IMG, f'{card}.jpg')
    path_txt = os.path.join(DIR_TXT(lang_user), f'{card_name}.txt')
    im = Image.open(open(path_img, 'rb'))
    buffer = io.BytesIO()
    if database_decks.get_reversed(lang_user, card_name):
        path_txt = os.path.join(DIR_REVERSE(lang_user), f'{card_name}.txt')
        im = im.rotate(180)
        im.save(buffer, format='JPEG', quality=75)
    im.save(buffer, format='JPEG', quality=75)
    await bot.send_photo(message.chat.id, buffer.getbuffer(), reply_markup=KbReply.FULL_TEXT(message))
    im.close()
    await state.update_data(text=open(path_txt, 'r').read())
    msg = await bot.send_message(message.chat.id, open(path_txt, 'r').read()[:380] + '...', reply_markup=Kb.TEXT_FULL(message))
    await state.update_data(msg=msg)
    database_fortune.add_history(message, card_name, open(path_txt, 'r').read()[0:150])
    database.minus_energy()
    database_fortune.check_first_try(message)
    await state.update_data(card=card_name)
    await state.update_data(thx=False)
    await state.update_data(full_text=False)
    if random.randint(1, 10) in [1, 5]:
        database_decks.update_reverse(lang_user, decks[card]['reversed'], card_name)
    await Session.session.set()
    await state.update_data(check_time=msg['date'])
    await asyncio.sleep(20)


async def thanks(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: thx | {datetime.now()}')
    async with state.proxy() as data:
        if not data['thx']:
            data['thx'] = True
            database.plus_energy()
            if not data['full_text']:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['thanks'](message),
                                       reply_markup=KbReply.FULL_TEXT_WITHOUT_THX(message))
            else:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['thanks'](message), reply_markup=KbReply.FULL_TEXT_WITHOUT_THX(message))



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


async def send_message(message: types.Message):
    if message.from_user.id == 951679992:
        user_id = message.text.split()[1]
        text = message.text.split()[2:]
        await bot.send_message(user_id, ' '.join(text))


async def text(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    # if message.from_user.id == 610027951:
    #     response = openai.Completion.create(model="text-davinci-002", prompt=message.text, temperature=0.7, max_tokens=256)
    #     await bot.send_message(message.chat.id, response['choices'][0]['text'])


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'])
    dp.register_message_handler(about_olivia, commands=['intro'], state='*')
    dp.register_message_handler(history, commands=['memories'], state='*')
    dp.register_message_handler(add_wisdom, commands=['addwisdom'], state='*')
    dp.register_message_handler(change_language, commands=['language'], state='*')
    dp.register_message_handler(get_name, state=Register.input_name)
    dp.register_message_handler(get_question, state=Register.input_question)
    dp.register_message_handler(listen_wisdom, state=WisdomState.wisdom)
    dp.register_message_handler(send_message, commands=['send'])
    dp.register_message_handler(get_fortune, Text(equals=all_lang['get_card']), state=Session.get_card)
    dp.register_message_handler(get_fortune, Text(equals=all_lang['get_card_again']), state=Session.session)
    dp.register_message_handler(thanks, Text(equals=all_lang['thx']), state=Session.session)
    dp.register_message_handler(text)
