import asyncio
import os
import random
import logging

from datetime import datetime
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from PIL import Image

from keyboards.main_keyboards import Kb
from utils.database import User, Fortune, Wisdom, Decks
from utils.languages import lang
from utils.decks import decks
from create_bot import bot, dp
from handlers.user import Register

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()
database_decks = Decks()

DIR_IMG = f'static/img/decks_1'
DIR_TXT = lambda lang: f'static/text/{lang}/day_card'
DIR_TXT_REVERSE = lambda lang: f'static/text/{lang}/reverse'
DIR_TXT_LOVE = lambda lang: f'static/text/{lang}/relationship'
DIR_TXT_LOVE_REVERSE = lambda lang: f'static/text/{lang}/reverse_relationship'


class FortuneState(StatesGroup):
    question = State()



async def welcome(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'switch language':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка | {datetime.now()}')
        await call.message.edit_text('Выбери язык\n'
                                     'Choose language', reply_markup=Kb.SWITCH_LANGUAGE)
    elif call.data == 'day_card':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Стандартные карты | {datetime.now()}')
        await call.message.edit_text(lang[database.get_language(call)]['fortune?'](call),
                                     reply_markup=Kb.fortune_menu(call))
    await call.answer()


async def switch_language(call: types.CallbackQuery):
    if call.data == 'switch english':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на английский | {datetime.now()}')
        database.switch_language('en', call)
        await call.message.answer('The language has been successfully changed')
        await call.message.answer(lang[database.get_language(call)]['send_welcome'](call),
                                  reply_markup=Kb.start_button(call))
    if call.data == 'switch russian':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Смена языка на русский | {datetime.now()}')
        database.switch_language('ru', call)
        await call.message.answer('Язык был успешно изменен')
        await call.message.answer(lang[database.get_language(call)]['send_welcome'](call),
                                  reply_markup=Kb.start_button(call))
    await call.answer()


async def get_fortune(call: types.CallbackQuery, state: FSMContext, DIR_IMG, DIR_TXT, DIR_REVERSE):
    database.get_name(call)
    await call.message.answer_animation('https://media.giphy.com/media/3oKIPolAotPmdjjVK0/giphy.gif')
    await asyncio.sleep(2)
    rand_card = random.randint(0, 77)
    lang_user = database.get_language(call)
    card = os.listdir(DIR_IMG)[rand_card][:-4]
    card_name = decks[card][lang_user]
    path_img = os.path.join(DIR_IMG, f'{card}.jpg')
    path_txt = os.path.join(DIR_TXT(lang_user), f'{card_name}.txt')
    im = Image.open(open(path_img, 'rb'))
    if database_decks.get_reversed(lang_user, card_name):
        path_txt = os.path.join(DIR_REVERSE(lang_user), f'{card_name}.txt')
        im = im.rotate(180)
        im.save(path_img)
    await call.message.answer_photo(open(path_img, 'rb'))
    im.close()
    await state.update_data(text=open(path_txt, 'r').read())
    await call.message.answer(open(path_txt, 'r').read()[0:380] + '...', reply_markup=Kb.FULL_TEXT)
    database_fortune.add_history(call, card_name, open(path_txt, 'r').read()[0:150])
    database.minus_energy()
    dp.register_callback_query_handler(full_text_history, text=database.get_data_history())
    dp.register_callback_query_handler(back_text_history, text=database.get_data_history_back())
    database_fortune.check_first_try(call)
    await state.update_data(card=card_name)
    await state.update_data(thx=False)
    await state.update_data(full_text=False)
    if random.randint(1, 10) in [1, 5]:
        database_decks.update_reverse(lang_user, decks[card]['reversed'], card_name)


async def fortune(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'fortune-1d':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Гадание раз в день | {datetime.now()}')
        if database.get_olivia_energy() > 0:
            await state.update_data(type_fortune='day_card')
            await get_fortune(call, state, DIR_IMG, DIR_TXT, DIR_TXT_REVERSE)
        else:
            await call.message.answer(f'Мне надо отдохнуть, я погадаю для вас чуть позже..')
    if call.data == 'relationship':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Гадание в отношениях | {datetime.now()}')
        await state.update_data(type_fortune='relationship')
        await get_fortune(call, state, DIR_IMG, DIR_TXT_LOVE, DIR_TXT_LOVE_REVERSE)
    if call.data == 'fortune_back':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: Назад(фортуна) | {datetime.now()}')
        await call.message.edit_text(lang[database.get_language(call)]['send_welcome'](call),
                                     reply_markup=Kb.start_button(call))
        await call.answer()
    if call.data == 'fortune_again':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: fortune_again | {datetime.now()}')
        if database.get_olivia_energy() > 0:
            await call.message.answer(f'Какой ещё вопрос не даёт вам покоя, {database.get_name(call)}?')
            await Register.input_question.set()
            await state.update_data(check='False')
            await asyncio.sleep(30)
            await check_time(call, state)
        else:
            await call.message.answer(f'Мне надо отдохнуть, я погадаю для вас чуть позже..')
    if call.data == 'thx':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: thx | {datetime.now()}')
        async with state.proxy() as data:
            if not data['thx']:
                if not data['full_text']:
                    await call.message.edit_reply_markup(Kb.FULL_TEXT_WITHOUT_THX)
                else:
                    await call.message.edit_reply_markup(Kb.BACK_TEXT_WITHOUT_THX)
            data['thx'] = True
            database.plus_energy()
            await call.message.answer(f'Рада была помочь, {database.get_name(call)}')


async def check_time(call: types.CallbackQuery, state: FSMContext):
    logging.info(
        f'[{call.from_user.id} | {call.from_user.first_name}] Callback: check_time | {datetime.now()}')
    data = await state.get_data()
    if data['check'] == 'False':
        await call.message.answer('Сконцентрируйте сознание на своем вопросе и вытяните карту...',
                               reply_markup=Kb.get_card())
        await state.finish()


async def full_text(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'full_text':
        logging.info(
            f'[{call.from_user.id} | {call.from_user.first_name}] Callback: full_text | {datetime.now()}')
        data = await state.get_data()
        keyboard = Kb.BACK_TEXT
        if data['thx']:
            keyboard = Kb.BACK_TEXT_WITHOUT_THX
        if len(data['text']) > 4096:
            await call.message.edit_text(data['text'][:4096])
            await call.message.answer(data['text'][4096:8192], reply_markup=keyboard)
            if len(data['text']) > 8192:
                await call.message.answer(data['text'][8192:12288], reply_markup=keyboard)
        else:
            await call.message.edit_text(data['text'], reply_markup=keyboard)
        await state.update_data(full_text=True)


async def full_text_history(call: types.CallbackQuery, state: FSMContext):
    if call.data in database.get_last_5_history(call):
        async with state.proxy() as data:
            data = open(f'{DIR_TXT(database.get_language(call))}/{data[f"history_{call.data}"]}.txt', 'r').read()
            if len(data) > 4096:
                for x in range(0, len(data), 4096):
                    await call.message.edit_text(data[x:x + 4096], reply_markup=Kb.history_back(call.data))
            else:
                await call.message.edit_text(data, reply_markup=Kb.history_back(call.data))


async def back_text_history(call: types.CallbackQuery, state: FSMContext):
    if call.data in database.get_last_5_history_back(call):
        async with state.proxy() as data:
            await call.message.edit_text(f'{call.data[:-5]} | {data[f"history_{call.data[:-5]}"]}\n' +
                                         open(
                                             f'{DIR_TXT(database.get_language(call))}/{data[f"history_{call.data[:-5]}"]}.txt',
                                             'r').read()[:150],
                                         reply_markup=Kb.history_full(call.data[:-5]))


async def question(message: types.Message, state: FSMContext):
    logging.info(f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    await message.bot.send_message(message.chat.id, lang[database.get_language(message)]['question2'])
    data = await state.get_data()
    database_fortune.create_fortune(message, data['card'], message.text, data['type_fortune'])
    database_fortune.check_session(message)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                           reply_markup=Kb.start_button(message))
    await FortuneState.next()



def register_handlers_callback(dp: Dispatcher):
    dp.register_callback_query_handler(welcome, text=['day_card', 'authors ru', 'switch language', 'history'])
    dp.register_callback_query_handler(switch_language, text=['switch english', 'switch russian'])
    dp.register_callback_query_handler(fortune, text=['fortune', 'fortune_back', 'fortune-1d', 'relationship',
                                                      'fortune_again', 'thx'])
    dp.register_callback_query_handler(full_text, text=['full_text'])
    dp.register_callback_query_handler(full_text_history, text=database.get_data_history())
    dp.register_callback_query_handler(back_text_history, text=database.get_data_history_back())
    dp.register_message_handler(question, state=FortuneState.question)
