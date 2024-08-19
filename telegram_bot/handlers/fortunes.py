import asyncio
import random
import os
import io
import json
import openai

from PIL import Image
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from telegram_bot.create_bot import bot, CODE_MODE
from telegram_bot.keyboards.reply_keyboard import KbReply
from telegram_bot.utils.database import User, Fortune, Decks
from telegram_bot.utils.languages import lang, all_lang
from telegram_bot.utils.logging_system import logging_to_file_telegram
from telegram_bot.utils.decks import decks
from telegram_bot.handlers.user import Session, Register, check_time, close_session_with_delay
from amplitude import BaseEvent
from .user import amplitude
from .text_variables import text_data

database = User()
database_fortune = Fortune()
database_decks = Decks()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_IMG = os.path.join(BASE_DIR, '..', 'static', 'img', 'decks_1')
DIR_TXT = lambda lang: f'static/text/{lang}/day_card'
DIR_REVERSE = lambda lang: f'static/text/{lang}/reverse'


async def typing(message: types.Message, mode='typing'):
    await bot.send_chat_action(message.from_user.id, mode)


def chat_gpt_text_generation(state_data: FSMContext, name_card: str, lang_user: str, is_reversed: bool = False) -> str:
    result = ""
    try:
        letter_prompt = state_data['is_letter_prompt']
    except KeyError:
        letter_prompt = False
    if state_data['prompt']['messages'][0]['content'] is None:
        if letter_prompt:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.8,
                messages=[
                    {'role': 'assistant',
                     'content': text_data.letter_prompt()}])
            state_data['is_letter_prompt'] = False
        elif lang_user == 'ru':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.8,
                messages=[
                    {'role': 'assistant',
                     'content': text_data.ru_prompt(name_card, is_reversed, state_data['question'])}])
        elif lang_user == 'en':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages=[
                    {'role': 'system', 'content': text_data.eng_prompt(name_card, is_reversed, state_data['question'])}]
            )
    else:
        if lang_user == 'ru':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.8,
                messages=[*state_data['prompt']['messages'],
                          {'role': 'system',
                           'content': text_data.ru_continue_prompt(name_card, is_reversed, state_data['question'])}])
        elif lang_user == 'en':
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                temperature=0.8,
                messages=[*state_data['prompt']['messages'],
                          {'role': 'system',
                           'content': text_data.eng_continue_prompt(name_card, is_reversed, state_data['question'])}])

    return result['choices'][0]['message']['content']


def is_card_reversed(lang_user, card_name):
    return database_decks.get_reversed(lang_user, card_name)


def get_reversed_text(lang_user, card_name):
    return os.path.join(DIR_REVERSE(lang_user), f'{card_name}.txt')


def process_reversed_card_img(message: types.Message or types.CallbackQuery, path_img, card_name):
    lang_user = database.get_language(message)
    im = Image.open(open(path_img, 'rb'))
    buffer = io.BytesIO()

    if is_card_reversed(lang_user, card_name):
        im = im.rotate(180)

    im.save(buffer, format='JPEG', quality=75)
    im.close()
    return buffer


async def update_energy_and_schedule_session_close(state: FSMContext, message):
    database.minus_energy()
    await Session.session.set()
    await state.update_data(close_session=json.dumps(datetime.now(), default=str))
    await close_session_with_delay(message, state, 3600)


async def run_chat_gpt_text_generation(state: FSMContext, message, card_name):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()
    temp_data = await state.get_data()
    await state.update_data(is_run=True)

    lang_user = database.get_language(message)
    is_reversed = is_card_reversed(lang_user, card_name)

    task2 = loop.run_in_executor(executor, chat_gpt_text_generation, temp_data, card_name, lang_user, is_reversed)

    while not task2.done():
        await typing(message)
        await asyncio.sleep(2)

    await state.update_data(is_run=False)
    return await task2


async def get_card(message: types.Message or types.CallbackQuery, state: FSMContext, extra_keyboard=False, mode=''):
    temp_data = await state.get_data()

    if temp_data.get('is_run'):
        print('Подождите карта генерируется')
        return

    if database_decks.is_more_than_30_cards_flipped():
        logging_to_file_telegram('info', 'Карты были перевернуты в исходное положение')
        database_decks.reset_all_cards()

    rand_card = select_random_card(temp_data)
    lang_user = database.get_language(message)
    card_files = os.listdir(DIR_IMG)
    card = card_files[rand_card][:-4]
    card_name = decks[card][lang_user]
    path_img = os.path.join(DIR_IMG, f'{card}.jpg')
    is_reversed = is_card_reversed(lang_user, card_name)

    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] card: {card_name} | reverse: {bool(is_reversed)} | lang_user: {lang_user} | card: {card}\npath_img - {path_img}')

    buffer = process_reversed_card_img(message, path_img, card_name)
    interpretation_text = await generate_chatgpt_text_and_send_animation(state, message, card_name)
    await asyncio.sleep(1)

    temp_data = await state.get_data()
    await send_initial_messages(message, state, interpretation_text, mode)

    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] {interpretation_text}')

    msg = await send_card_image_and_caption(message, buffer, interpretation_text, extra_keyboard)
    await asyncio.sleep(1)
    await bot.delete_message(message.from_user.id, temp_data.get('animation_message'))
    second_rand_card = await get_second_card_if_exists(temp_data)

    await update_state_data_and_database(msg, message, state, card_name, interpretation_text, rand_card,
                                         second_rand_card)
    await handle_random_card_update(message, card, card_name)


async def get_second_card_if_exists(temp_data):
    if isinstance(temp_data.get('rand_card'), list):
        return temp_data.get('rand_card')[1]
    return None


def select_random_card(temp_data):
    rand_card = random.randint(0, 77)
    while rand_card in temp_data.get('rand_card') if temp_data.get('rand_card') else []:
        rand_card = random.randint(0, 77)
    return rand_card


async def generate_chatgpt_text_and_send_animation(state, message, card_name):
    await send_initial_animation(message, state)
    return await run_chat_gpt_text_generation(state, message, card_name)


async def update_prompt_messages(state: FSMContext, interpretation_text):
    temp_data = await state.get_data()
    messages = temp_data['prompt']['messages']

    new_message = {'role': 'system', 'content': interpretation_text}
    if messages[0]['content'] is None:
        messages = [new_message]
    else:
        messages.append(new_message)

    await state.update_data(prompt={'messages': messages})


def escape_markdown_v2(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])


async def send_card_image_and_caption(message, buffer, interpretation_text, extra_keyboard):
    if not extra_keyboard:
        extra_keyboard = KbReply.FULL_TEXT(message)

    database.change_last_attempt(message)

    # Экранируем весь текст, включая ссылку
    caption_text = escape_markdown_v2(
        interpretation_text[:997]) + "\n\n[Погадать у Оливии?](https://t\\.me\\/Oliviathebot)"

    # Отправляем фото с подписью и клавиатурой
    return await bot.send_photo(
        message.from_user.id,
        buffer.getbuffer(),
        caption=caption_text,
        parse_mode="MarkdownV2",
        reply_markup=extra_keyboard
    )


async def send_initial_messages(message, state, interpretation_text, mode):
    await update_prompt_messages(state, interpretation_text)

    if mode in ['past', 'present', 'future']:
        await send_mode_message(message, mode)


async def send_mode_message(message, mode):
    await bot.send_message(message.from_user.id, lang[database.get_language(message)][mode], parse_mode='markdown')


async def send_initial_animation(message, state: FSMContext):
    animation_message = await bot.send_animation(
        message.from_user.id,
        'https://media.giphy.com/media/3oKIPolAotPmdjjVK0/giphy.gif',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.update_data(animation_message=animation_message.message_id)


async def update_state_data_and_database(msg, message: types.Message or types.CallbackQuery, state: FSMContext,
                                         card_name, interpretation_text, rand_card, second_rand_card):
    message_id = msg.message_id
    async with state.proxy() as data:
        data[message_id] = interpretation_text
        database_fortune.add_history(message, card_name, interpretation_text[:150], data['question'], message_id,
                                     interpretation_text)

    await state.update_data(card=card_name, thx=False, full_text=False, rand_card=[rand_card, second_rand_card],
                            text_data=interpretation_text, message_id=message_id)
    database_fortune.check_first_try(message)


async def handle_random_card_update(message, card, card_name):
    if random.randint(1, 10) <= 5:
        lang_user = database.get_language(message)
        reversed_card = decks[card]['reversed']
        database_decks.update_reverse(lang_user, reversed_card, card_name)


async def get_fortune_three_cards(message: types.Message, state: FSMContext):
    if CODE_MODE == 'PROD':
        amplitude.track(BaseEvent(event_type='PSF', user_id=f'{message.from_user.id}'))
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Callback: get_3_cards')
    await bot.send_photo(message.from_user.id, open('static/img/static/past_present_future.jpg', 'rb'))
    await state.update_data(past=False, present=False, future=False)
    await bot.send_message(message.from_user.id, lang[database.get_language(message)]['open_cards'],
                           reply_markup=KbReply.PPF_MENU(message, await state.get_data()))
    await Session.session_3_cards.set()


async def get_fortune_one_cards(message: types.Message, state: FSMContext):
    if CODE_MODE == 'PROD':
        amplitude.track(BaseEvent(event_type='OneCard', user_id=f'{message.from_user.id}'))
    logging_to_file_telegram('info',
                             f'[{message.from_user.id} | {message.from_user.first_name}] Callback: Посмотреть карту')
    await get_card(message, state)
    await update_energy_and_schedule_session_close(state, message)


async def get_fortune_chatgpt(message: types.Message, state: FSMContext):
    # if CODE_MODE == 'PROD':
    #     amplitude.track(BaseEvent(event_type='OneCard', user_id=f'{message.from_user.id}'))
    logging_to_file_telegram('info', f'[{message.from_user.id} | {message.from_user.first_name}] Callback: chatgpt')
    await get_card(message, state, mode='chatgpt')
    await update_energy_and_schedule_session_close(state, message)


async def get_fortune(message: types.Message, state: FSMContext):
    if database.get_olivia_energy() > 0:
        if message.text in all_lang['get_card_again']:
            await bot.send_message(message.from_user.id,
                                   lang[database.get_language(message)]['question_again'](message),
                                   reply_markup=types.ReplyKeyboardRemove())
        else:
            await bot.send_message(message.from_user.id,
                                   lang[database.get_language(message)]['question_start'](message),
                                   reply_markup=types.ReplyKeyboardRemove())
        await Register.input_question.set()
        await state.update_data(check='False')
        await check_time(message, state)
        return
    else:
        await bot.send_message(message.from_user.id, lang[database.get_language(message)]['no_energy'])
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
        await update_energy_and_schedule_session_close(state, message)
        return
    await get_card(message, state, KbReply.PPF_MENU(message, await state.get_data()), choose)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_fortune, Text(equals=all_lang['get_card_again'] + all_lang['divination']),
                                state=Session.session)
    dp.register_message_handler(get_fortune_one_cards, Text(equals=all_lang['get_card']), state=Session.get_card)
    dp.register_message_handler(get_fortune_three_cards, Text(equals=all_lang['get_3_cards']), state=Session.get_card)
    dp.register_message_handler(session_3_cards, Text(equals=all_lang['open_3_cards']), state=Session.session_3_cards)
