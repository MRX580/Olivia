import os
import random

import openai

from telegram_bot.create_bot import bot
from aiogram import types, Dispatcher
from telegram_bot.utils.database import User
from telegram_bot.utils.decks import decks
from .fortunes import is_card_reversed, DIR_IMG, process_reversed_card_img
from .text_variables import text_data

# CHANNELS_RU = ['@oliviaitarot', '@sarcastictaro']
# CHANNELS_EN = ['@olivi_ai', '@sarcasmtarot']

users = User()


def chat_gpt_text_generation(name_card: str, lang_user: str, is_reversed: bool = False) -> str:
    result = ''
    if lang_user == 'ru':
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            temperature=0.8,
            messages=[
                {'role': 'assistant', 'content': text_data.ru_prompt(name_card, lang_user, 'Какая будет моя карта дня?')}])
    elif lang_user == 'en':
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            temperature=0.8,
            messages=[
                {'role': 'assistant', 'content': text_data.eng_prompt(name_card, lang_user, 'What will my card of the day be?')}])
    return result['choices'][0]['message']['content']


async def newsletter(message: types.Message): ...
    # for channel in CHANNELS_RU:
    #     rand_card = random.randint(0, 77)
    #     card = os.listdir(DIR_IMG)[rand_card][:-4]
    #     card_name = decks[card]['ru']
    #     path_img = os.path.join(DIR_IMG, f'{card}.jpg')
    #     is_reverse = is_card_reversed('ru', card_name)
    #     interpretation_text = chat_gpt_text_generation(card_name, 'ru', is_reverse)
    #     buffer = process_reversed_card_img(path_img, 'ru', card_name)
    #     await bot.send_photo(channel, buffer.getbuffer(), caption=interpretation_text[:1023])
    # for channel in CHANNELS_EN:
    #     rand_card = random.randint(0, 77)
    #     card = os.listdir(DIR_IMG)[rand_card][:-4]
    #     card_name = decks[card]['en']
    #     path_img = os.path.join(DIR_IMG, f'{card}.jpg')
    #     is_reverse = is_card_reversed('en', card_name)
    #     interpretation_text = chat_gpt_text_generation(card_name, 'en', is_reverse)
    #     buffer = process_reversed_card_img(path_img, 'en', card_name)
    #     await bot.send_photo(channel, buffer.getbuffer(), caption=interpretation_text[:1023])


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(newsletter, commands=['send_message'], state='*')
