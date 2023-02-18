import asyncio
import logging
import random
import os
import io

from PIL import Image
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime

from create_bot import bot
from keyboards.main_keyboards import Kb, KbReply
from utils.database import User, Fortune, Decks
from utils.languages import lang, all_lang
from utils.decks import decks
from handlers.user import Session, Register, check_time, close_session

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_decks = Decks()

DIR_IMG = 'static/img/decks_1'
DIR_TXT = lambda lang: f'static/text/{lang}/day_card'
DIR_REVERSE = lambda lang: f'static/text/{lang}/reverse'


async def get_card(message: types.Message, state: FSMContext, extra_keyboard=False, mode=''):
    if not extra_keyboard:
        extra_keyboard = KbReply.FULL_TEXT(message)
    await bot.send_animation(message.chat.id, 'https://media.giphy.com/media/3oKIPolAotPmdjjVK0/giphy.gif')
    await asyncio.sleep(2)
    rand_card = random.randint(0, 77)
    lang_user = database.get_language(message)
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] | card: {DIR_IMG} | rand_card: {rand_card} | {datetime.now()}')
    card = os.listdir(DIR_IMG)[rand_card][:-4]
    card_name = decks[card][lang_user]
    path_img = os.path.join(DIR_IMG, f'{card}.jpg')
    path_txt = os.path.join(DIR_TXT(lang_user), f'{card_name}.txt')
    is_reverse = database_decks.get_reversed(lang_user, card_name)
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] card: {card_name} | reverse: {bool(is_reverse)}\n'
        f'path_txt - {path_txt}\npath_img - {path_img} | {datetime.now()}')
    im = Image.open(open(path_img, 'rb'))
    buffer = io.BytesIO()
    if is_reverse:
        path_txt = os.path.join(DIR_REVERSE(lang_user), f'{card_name}.txt')
        im = im.rotate(180)
        im.save(buffer, format='JPEG', quality=75)
    im.save(buffer, format='JPEG', quality=75)
    await bot.send_photo(message.chat.id, buffer.getbuffer(), reply_markup=extra_keyboard)
    im.close()
    if mode == 'past':
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['past'],
                               parse_mode='markdown')
    elif mode == 'present':
        await bot.send_message(message.chat.id,
                               lang[database.get_language(message)]['present'],
                               parse_mode='markdown')
    elif mode == 'future':
        await bot.send_message(message.chat.id,
                               lang[database.get_language(message)]['future'],
                               parse_mode='markdown')
    msg = await bot.send_message(message.chat.id, open(path_txt, 'r').read()[:380] + '...',
                                 reply_markup=Kb.TEXT_FULL(message))
    async with state.proxy() as data:
        data[msg.message_id] = open(path_txt, 'r').read()
    await state.update_data(card=card_name, thx=False, full_text=False)
    database_fortune.add_history(message, card_name, open(path_txt, 'r').read()[0:150])
    database_fortune.check_first_try(message)
    if random.randint(1, 10) in [1, 5]:
        database_decks.update_reverse(lang_user, decks[card]['reversed'], card_name)


async def get_fortune(message: types.Message, state: FSMContext):
    if database.get_olivia_energy() > 0:
        if message.text in all_lang['get_card_again'] + all_lang['divination']:
            if message.text in all_lang['get_card_again']:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_again'](message), reply_markup=types.ReplyKeyboardRemove())
            else:
                await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_start'](message), reply_markup=types.ReplyKeyboardRemove())
            await Register.input_question.set()
            await state.update_data(check='False')
            await asyncio.sleep(45)
            await check_time(message, state)
            return
    else:
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['no_energy'])
        return
    if message.text in all_lang['get_card_again'] + all_lang['get_card']:
        logging.info(
            f'[{message.from_user.id} | {message.from_user.first_name}] Callback: one_card | {datetime.now()}')
        await get_card(message, state)
        database.minus_energy()
        await Session.session.set()
        await state.update_data(close_session=datetime.now())
        await asyncio.sleep(3600)
        await close_session(message, state)
    elif message.text in all_lang['get_3_cards']:
        logging.info(
            f'[{message.from_user.id} | {message.from_user.first_name}] Callback: get_3_cards | {datetime.now()}')
        await bot.send_photo(message.chat.id, open('static/img/static/past_present_future.jpg', 'rb'))
        await state.update_data(past=False, present=False, future=False)
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['open_cards'],
                               reply_markup=KbReply.PPF_MENU(message, await state.get_data()))
        await Session.session_3_cards.set()



async def session_3_cards(message: types.Message, state: FSMContext):
    user_lang = lang[database.get_language(message)]
    async with state.proxy() as data:
        PPF = {user_lang['open_past']: 'past',
               user_lang['open_present']: 'present',
               user_lang['open_future']: 'future'}
        choose = PPF.get(message.text)
        data['past'] = True if message.text == user_lang['open_past'] or data['past'] else False
        data['present'] = True if message.text == user_lang['open_present'] or data['present'] else False
        data['future'] = True if message.text == user_lang['open_future'] or data['future'] else False
    if data['past'] and data['present'] and data['future']:
        await get_card(message, state, mode=choose)
        database.minus_energy()
        await Session.session.set()
        await state.update_data(close_session=datetime.now())
        await asyncio.sleep(3600)
        await close_session(message, state)
        return
    await get_card(message, state, KbReply.PPF_MENU(message, await state.get_data()), choose)

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_fortune, Text(equals=all_lang['get_card_again'] + all_lang['divination']), state=Session.session)
    dp.register_message_handler(get_fortune, Text(equals=all_lang['get_card']), state=Session.get_card)
    dp.register_message_handler(get_fortune, Text(equals=all_lang['get_3_cards']), state=Session.get_card)
    dp.register_message_handler(session_3_cards, Text(equals=all_lang['open_3_cards']), state=Session.session_3_cards)