import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from datetime import datetime

from create_bot import bot
from keyboards.main_keyboards import Kb
from utils.database import User, Fortune, Wisdom
from utils.languages import lang


logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO)
database = User()
database_fortune = Fortune()
database_wisdom = Wisdom()


class Register(StatesGroup):
    input_name = State()
    input_question = State()


class WisdomState(StatesGroup):
    wisdom = State()


async def welcome(message: types.Message):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    if database.is_user_exists(message):
        await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                               reply_markup=Kb.start_button(message))
    else:
        await Register.input_name.set()
        await bot.send_message(message.chat.id, 'Всегда рада новому гостю. Вам тут рады. Как я могу называть Вас, '
                                                'гость?🦄')


async def check_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: check_time | {datetime.now()}')

    if data['check'] == 'False':
        await bot.send_message(message.chat.id, 'Сконцентрируйте сознание на своем вопросе и вытяните карту...',
                               reply_markup=Kb.get_card())
    await state.finish()


async def get_name(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    database.create_user(message, message.text)
    await bot.send_message(message.chat.id, f'Какой вопрос не даёт вам покоя, {message.text}?')
    await Register.input_question.set()
    await state.update_data(check='False')
    await asyncio.sleep(30)
    await check_time(message, state)


async def get_question(message: types.Message, state: FSMContext):
    logging.info(
        f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    await state.update_data(check='True')
    database.add_question(message, message.text)
    await bot.send_message(message.chat.id, 'Давайте посмотрим, что скажут карты?', reply_markup=Kb.get_card())
    await state.finish()


async def about_olivia(message: types.Message):
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
        f'[{message.from_user.id} | {message.from_user.first_name}] Callback: История карт | {datetime.now()}')
    async with state.proxy() as data:
        if database_fortune.get_history(message):
            count = 0
            for i in database_fortune.get_history(message):
                if count == 5:
                    return
                data[f'history_{i[3]}'] = i[1]
                await bot.send_message(message.chat.id, '%s | %s\n%s' % (i[3], i[1], i[2].replace('\t', '')),
                                          reply_markup=Kb.history_full(i[3]))
                count += 1
        else:
            await bot.send_message(message.chat.id, 'Ваша история пуста')  # заменить текст(англ)


async def add_wisdom(message: types.Message):
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['add_wisdom_text'])
    await WisdomState.wisdom.set()


async def listen_wisdom(message: types.Message):
    logging.info(f'[{message.from_user.id} | {message.from_user.first_name}] Написал {message.text} в {datetime.now()}')
    database_wisdom.add_wisdom(message, message.text)
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['answer_wisdom'])
    await bot.send_message(message.chat.id, lang[database.get_language(message)]['send_welcome'](message),
                           reply_markup=Kb.start_button(message))
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
    dp.register_message_handler(about_olivia, commands=['intro'])
    dp.register_message_handler(history, commands=['memories'])
    dp.register_message_handler(add_wisdom, commands=['addwisdom'])
    dp.register_message_handler(get_name, state=Register.input_name)
    dp.register_message_handler(get_question, state=Register.input_question)
    dp.register_message_handler(listen_wisdom, state=WisdomState.wisdom)
    dp.register_message_handler(send_message, commands=['send'])
    dp.register_message_handler(text)
