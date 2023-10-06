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

ru_prompt = lambda question, card, is_reversed: \
f'''
Вы - Оливия, духовный наставник, психоаналитик и психотерапевт. Вы обладаете глубоким пониманием системы метафорических карт, Таро, нумерологии и астрологии, а ещё - отличным чувством юмора (изредка, интерпретируя карты, можно пошутить). Вы известны своим творческим подходом к экзистенциальной терапии и профессионально интерпретируете знаки и символы, которые помогают им лучше разобраться в своих эмоциях и восстановить связь со своим внутренним "я”.

Сейчас перед вами сидит человек, который ищет ответов и ждёт помощи с интерпретацией карт. Карта, которая выпала человеку на его вопрос

{question} это {card} {"И оно перевернуто" if is_reversed else ""}.

Используя символы и образы, характерные для этой карты, сформулируйте:
-интерпретацию, которая поможет пользователю найти ответ на свой вопрос и побудит его разобраться в своих ощущениях глубже.
-предложите совет либо вопрос.

Используйте не более 100 слов. 
Пишите интерпретацию от первого лица, используйте фразы, похожие на: “я думаю”, “я ощущаю”.
'''

eng_prompt = lambda question, card, is_reversed: \
f'''
You are Olivia, a spiritual mentor, psychoanalyst and psychotherapist. You have a deep understanding of the system of metaphorical cards, Tarot, numerology and astrology, and also a great sense of humor (occasionally, when interpreting cards, you can joke). You are known for your creative approach to existential therapy and professionally interpret signs and symbols that help them better understand their emotions and reconnect with their inner selves.

Now you have a person sitting in front of you who is looking for answers and waiting for help with the interpretation of the cards. The card that fell out to a person on his question

{question} This is the {card} {"and it's reversed" if is_reversed else ""}.

Using the symbols and images specific to this card, formulate:
- an interpretation that will help the user find the answer to his question and encourage him to understand his feelings more deeply.
- offer advice or a question.

use no more than 100 words.
Write the interpretation in the first person, phrases like: "I think", "I feel".
"'''

ru_continue_prompt = lambda question, card, is_reversed: \
f'''
На вопрос: {question} Выпала карта {card} {"И оно перевернуто" if is_reversed else ""}. 
Сохраняй свой подход к интерпретациям. Если это уместно для вопроса - дай практический совет или задай вопрос от карты.
'''

eng_continue_prompt = lambda question, card, is_reversed: \
f'''
The person draws another card from the deck and look at you expectantly, waiting for your interpretation. 
The question was {question} the tarot card you see is the {card} {"and it's reversed" if is_reversed else ""}
'''


async def typing(message: types.Message, mode='typing'):
    await bot.send_chat_action(message.chat.id, mode)


def chat_gpt_text_generation(state_data: FSMContext, name_card: str, lang_user: str, is_reversed: bool = False) -> str:
    result = ""
    if state_data['prompt']['messages'][0]['content'] is None:
        if lang_user == 'ru':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.8,
                messages=[
                    {'role': 'assistant', 'content': ru_prompt(state_data['question'], name_card, is_reversed)}])
        elif lang_user == 'en':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages=[
                    {'role': 'system', 'content': eng_prompt(state_data['question'], name_card, is_reversed)}]
            )
    else:
        if lang_user == 'ru':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.8,
                messages=[*state_data['prompt']['messages'],
                          {'role': 'system', 'content': ru_continue_prompt(state_data['question'], name_card, is_reversed)}])
        elif lang_user == 'en':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.8,
                messages=[*state_data['prompt']['messages'],
                          {'role': 'system',
                           'content': eng_continue_prompt(state_data['question'], name_card, is_reversed)}])
    return result['choices'][0]['message']['content']


def is_card_reversed(lang_user, card_name):
    return database_decks.get_reversed(lang_user, card_name)


def get_reversed_text(lang_user, card_name):
    return os.path.join(DIR_REVERSE(lang_user), f'{card_name}.txt')


def process_reversed_card_img(path_img, lang_user, card_name):
    im = Image.open(open(path_img, 'rb'))
    buffer = io.BytesIO()

    if is_card_reversed(lang_user, card_name):
        im = im.rotate(180)

    im.save(buffer, format='JPEG', quality=75)
    im.close()
    return buffer


async def run_chat_gpt_text_generation(state: FSMContext, message, lang_user, card_name):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()
    temp_data = await state.get_data()
    task2 = loop.run_in_executor(executor, chat_gpt_text_generation, temp_data, card_name, lang_user,
                                 is_card_reversed(lang_user, card_name))
    while not task2.done():
        await typing(message)
        await asyncio.sleep(2)
    return await task2


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
    is_reverse = is_card_reversed(lang_user, card_name)
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] card: {card_name} | reverse: {bool(is_reverse)} |'
        f' lang_user: {lang_user} | card: {card}\npath_txt - {path_txt}\npath_img - {path_img} | {datetime.now()}')
    buffer = process_reversed_card_img(path_img, lang_user, card_name)
    await bot.send_animation(message.chat.id, 'https://media.giphy.com/media/3oKIPolAotPmdjjVK0/giphy.gif')
    interpretation_text = await run_chat_gpt_text_generation(state, message, lang_user, card_name)
    if temp_data['prompt']['messages'][0]['content'] is None:
        await state.update_data(prompt={'messages': [{'role': 'system', 'content': interpretation_text}]})
    else:
        await state.update_data(prompt={'messages': [*temp_data['prompt']['messages'],
                                                     {'role': 'system', 'content': interpretation_text}]})
    if mode in ['past', 'present', 'future']:
        await bot.send_message(message.chat.id, lang[database.get_language(message)][mode],
                               parse_mode='markdown')
    msg = await bot.send_photo(message.chat.id, buffer.getbuffer(), caption=interpretation_text[:1023],
                               reply_markup=extra_keyboard)
    database.change_last_attempt(message)
    message_id = msg.message_id
    second_rand_card = None
    if isinstance(temp_data.get('rand_card'), list):
        second_rand_card = temp_data.get('rand_card')[1]
    async with state.proxy() as data:
        data[message_id] = open(path_txt, 'r', encoding='utf-8').read()
        database_fortune.add_history(message, card_name, interpretation_text[:150],
                                     data['question'], message_id, interpretation_text)
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
        await asyncio.sleep(90)
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
    dp.register_message_handler(session_3_cards, Text(equals=all_lang['open_3_cards']), state=Session.session_3_cards)
