import asyncio
import logging
import random
import os
import io
import json
import openai

from PIL import Image
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from create_bot import bot, CODE_MODE
from keyboards.inline_keyboard import Kb
from keyboards.reply_keyboard import KbReply
from utils.database import User, Fortune, Decks
from utils.languages import lang, all_lang
from utils.decks import decks
from handlers.user import Session, Register, check_time, close_session
from amplitude import BaseEvent
from .user import amplitude

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_decks = Decks()

DIR_IMG = 'static/img/decks_1'
DIR_TXT = lambda lang: f'static/text/{lang}/day_card'
DIR_REVERSE = lambda lang: f'static/text/{lang}/reverse'


async def typing(message: types.Message, mode='typing'):
    await bot.send_chat_action(message.chat.id, mode)



def chat_gpt_text_generation(question: str, name_card: str, lang_user: str, is_reversed: bool = False) -> str:
    result = ""
    if lang_user == 'ru':
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "Представь что ты гадалка"},
                {'role': 'system', 'content': f'''Ты - гадалка. К тебе пришел клиент с вопросом: {question} 
                Выпала карта {"перевернутое" if is_reversed else ""} {name_card}. Сформулируй интерпретацию к карте, 
                которая содержит ответ на этот вопрос. Тон интерпретации - дружелюбный и наставнический. Не более 222 
                слов. Упомяни: - общее значение карты, свое отношение к ней, наиболее вероятный ответ на вопрос клиента, 
                небольшую рекомендацию. Разбей текст на два абзаца. Используй слова “я думаю”, “я ощущаю” или похожие. 
                Начни с собственной реакции на выпавшую карту, например “О, это {name_card}! 
                {"И оно перевернуто" if is_reversed else ""}”'''},]
        )
    elif lang_user == 'en':
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {"role": "system", "content": "Imagine you are a fortune teller"},
                {'role': 'system', 'content': f'''
                You are a fortune teller. A client has come to you with a question: {question}.
                The {name_card} card has been drawn {"reversed" if is_reversed else "upright"}. Allow me to interpret the card, 
                providing an answer to the question in a friendly and mentoring tone. In no more than 222 words, I will discuss the 
                general meaning of the card, my personal perspective on it, the most probable answer to the client's question, 
                and offer a small recommendation. Let's divide the text into two paragraphs. Feel free to include phrases such as "I 
                think," "I sense," or similar expressions. Let's begin with my initial reaction to the drawn card, for example, "Oh, 
                it's {name_card}! {"And it's reversed" if is_reversed else ""}."'''}, ]
        )
    return result['choices'][0]['message']['content']



async def get_card(message: types.Message, state: FSMContext, extra_keyboard=False, mode=''):
    if not extra_keyboard:
        extra_keyboard = KbReply.FULL_TEXT(message)
    temp_data = await state.get_data()
    rand_card = random.randint(0, 77)
    while rand_card in temp_data.get('rand_card') if temp_data.get('rand_card') else []:
        rand_card = random.randint(0, 77)
    lang_user = database.get_language(message)
    card = os.listdir(DIR_IMG)[rand_card][:-4]
    card_name = decks[card][lang_user]
    path_img = os.path.join(DIR_IMG, f'{card}.jpg')
    path_txt = os.path.join(DIR_TXT(lang_user), f'{card_name}.txt')
    is_reverse = database_decks.get_reversed(lang_user, card_name)
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] card: {card_name} | reverse: {bool(is_reverse)} |'
        f' lang_user: {lang_user} | card: {card}\npath_txt - {path_txt}\npath_img - {path_img} | {datetime.now()}')
    im = Image.open(open(path_img, 'rb'))
    buffer = io.BytesIO()
    if is_reverse:
        path_txt = os.path.join(DIR_REVERSE(lang_user), f'{card_name}.txt')
        im = im.rotate(180)
    im.save(buffer, format='JPEG', quality=75)
    await bot.send_animation(message.chat.id, 'https://media.giphy.com/media/3oKIPolAotPmdjjVK0/giphy.gif')
    await bot.send_photo(message.chat.id, buffer.getbuffer(), reply_markup=extra_keyboard)
    im.close()
    interpretation_text = open(path_txt, 'r', encoding='utf-8').read()
    if mode == 'chatgpt':
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()
        task2 = loop.run_in_executor(executor, chat_gpt_text_generation, temp_data['question'], card_name, lang_user,
                                       is_reverse)
        while not task2.done():
            await typing(message)
            await asyncio.sleep(2)
        interpretation_text = await task2
    if mode in ['past', 'present', 'future']:
        await bot.send_message(message.chat.id, lang[database.get_language(message)][mode],
                               parse_mode='markdown')
    msg = await bot.send_message(message.chat.id, interpretation_text[:380] + '...',
                                 reply_markup=Kb.TEXT_FULL(message))
    database.change_last_attempt(message)
    message_id = msg.message_id
    second_rand_card = None
    if isinstance(temp_data.get('rand_card'), list):
        second_rand_card = temp_data.get('rand_card')[1]
    async with state.proxy() as data:
        data[message_id] = open(path_txt, 'r', encoding='utf-8').read()
        database_fortune.add_history(message, card_name, interpretation_text[:150],
                                     data['question'], message_id)
    await state.update_data(card=card_name, thx=False, full_text=False, rand_card=[rand_card, second_rand_card],
                            text_data=interpretation_text, message_id=message_id)
    database_fortune.check_first_try(message)
    if random.randint(1, 10) in [1, 2, 3, 4, 5]:
        database_decks.update_reverse(lang_user, decks[card]['reversed'], card_name)


async def get_fortune_three_cards(message: types.Message, state: FSMContext):
    if CODE_MODE == 'PROD':
        amplitude.track(BaseEvent(event_type='PSF', user_id=f'{message.from_user.id}'))
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: get_3_cards | {datetime.now()}')
    await bot.send_photo(message.chat.id, open('static/img/static/past_present_future.jpg', 'rb'))
    await state.update_data(past=False, present=False, future=False)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['open_cards'],
                           reply_markup=KbReply.PPF_MENU(message, await state.get_data()))
    await Session.session_3_cards.set()


async def get_fortune_one_cards(message: types.Message, state: FSMContext):
    if CODE_MODE == 'PROD':
        amplitude.track(BaseEvent(event_type='OneCard', user_id=f'{message.from_user.id}'))
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: one_card | {datetime.now()}')
    await get_card(message, state)
    database.minus_energy()
    await Session.session.set()
    await state.update_data(close_session=json.dumps(datetime.now(), default=str))
    await asyncio.sleep(3600)
    await close_session(message, state)


async def get_fortune_chatgpt(message: types.Message, state: FSMContext):
    # if CODE_MODE == 'PROD':
    #     amplitude.track(BaseEvent(event_type='OneCard', user_id=f'{message.from_user.id}'))
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: chatgpt | {datetime.now()}')
    await get_card(message, state, mode='chatgpt')
    database.minus_energy()
    await Session.session.set()
    await state.update_data(close_session=json.dumps(datetime.now(), default=str))
    await asyncio.sleep(3600)
    await close_session(message, state)


async def get_fortune(message: types.Message, state: FSMContext):
    if database.get_olivia_energy() > 0:
        if message.text in all_lang['get_card_again']:
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_again'](message),
                                   reply_markup=types.ReplyKeyboardRemove())
        else:
            await bot.send_message(message.chat.id, lang[database.get_language(message)]['question_start'](message),
                                   reply_markup=types.ReplyKeyboardRemove())
        await Register.input_question.set()
        await state.update_data(check='False')
        await asyncio.sleep(45)
        await check_time(message, state)
        return
    else:
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['no_energy'])
        return


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
        await state.update_data(close_session=json.dumps(datetime.now(), default=str))
        await asyncio.sleep(3600)
        await close_session(message, state)
        return
    await get_card(message, state, KbReply.PPF_MENU(message, await state.get_data()), choose)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_fortune, Text(equals=all_lang['get_card_again'] + all_lang['divination']),
                                state=Session.session)
    dp.register_message_handler(get_fortune_one_cards, Text(equals=all_lang['get_card']), state=Session.get_card)
    dp.register_message_handler(get_fortune_three_cards, Text(equals=all_lang['get_3_cards']), state=Session.get_card)
    dp.register_message_handler(get_fortune_chatgpt, Text(equals=all_lang['get_chatgpt']), state=Session.get_card)
    dp.register_message_handler(session_3_cards, Text(equals=all_lang['open_3_cards']), state=Session.session_3_cards)
