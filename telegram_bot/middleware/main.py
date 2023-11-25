from aiogram import types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types.update import Update
from aiogram_calendar import DialogCalendar

from telegram_bot.utils.database import Temp, User
from telegram_bot.utils.languages import lang
from telegram_bot.create_bot import dp
from telegram_bot.states.main import Register

database = User()
database_temp = Temp()

dp.middleware.setup(LoggingMiddleware())


class BirthRequestMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        current_state = dp.current_state(user=message.from_user.id)

        is_birth = database_temp.get_birth_status(message.from_user.id)
        is_user = database.is_user_exists(message)

        if not is_birth and not 'input_location' in await current_state.get_state() and is_user:
            await message.answer(lang[database.get_language(message)]['not_confirmed_birth'])
            raise BirthRequestNotSent()


class BirthRequestNotSent(Exception):
    pass


async def birth_request_not_sent_handler(update: Update, exception):
    print(update.message.from_user.id)
    await update.message.answer(lang[database.get_language(update)]['get_date_start'],
                                reply_markup=await DialogCalendar().start_calendar())


def middleware_register(dp):
    dp.middleware.setup(BirthRequestMiddleware())
    dp.register_errors_handler(birth_request_not_sent_handler, exception=BirthRequestNotSent)
