from aiogram import types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types.update import Update
from aiogram_calendar import DialogCalendar

from telegram_bot.utils.database import Temp, User
from telegram_bot.utils.languages import lang
from telegram_bot.create_bot import dp

database = User()
database_temp = Temp()

dp.middleware.setup(LoggingMiddleware())


class BirthRequestMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        current_state = dp.current_state(user=message.from_user.id)
        state = await current_state.get_state()
        if state is None:
            state = ''

        is_user = database.is_user_exists(message)
        if not 'input_location' in state and is_user:
            is_birth = await database_temp.get_birth_status(message.from_user.id)
            if not is_birth:
                # await message.answer(lang[database.get_language(message)]['not_confirmed_birth'])
                raise BirthRequestNotSent()


class BirthRequestNotSent(Exception):
    pass


async def birth_request_not_sent_handler(update: Update, exception):
    language = database.get_language(update)
    await update.message.answer(lang[database.get_language(update)]['get_date_start'],
                                reply_markup=await DialogCalendar(language).start_calendar(year=1995))


def middleware_register(dp):
    dp.middleware.setup(BirthRequestMiddleware())
    dp.register_errors_handler(birth_request_not_sent_handler, exception=BirthRequestNotSent)
