import asyncio
import datetime

import aiogram.utils.exceptions

from handlers import user, fortunes, admin, channels
from callbacks.user import register_handlers_callback
from handlers.admin import ADMINS_ID, get_kpi
from aiogram import executor
from create_bot import dp, CODE_MODE, bot
from utils.database import Database, User, Temp
from utils.languages import lang
from migrations import Migration
from middleware.main import middleware_register
from aiogram_calendar import DialogCalendar

database = Database()
database_user = User()
database_temp = Temp()


async def send_kpi():
    while True:
        now = datetime.datetime.now()
        if now.hour == 10 and now.minute == 0:
            user_ids = ADMINS_ID

            for user_id in user_ids:
                await bot.send_message(user_id, await get_kpi())
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)


async def get_date_from_users():
    users = database_user.get_all_users()
    for i in users:
        is_birth = await database_temp.get_birth_status(i[1])
        if is_birth is None:
            try:
                await bot.send_message(i[1], lang[i[5]]['get_date_start'],
                                       reply_markup=await DialogCalendar(language=i[5]).start_calendar(year=1995))
                database_temp.check_entry(i[1], False)
            except (aiogram.utils.exceptions.BotBlocked, aiogram.utils.exceptions.UserDeactivated):
                pass


# async def send_letter_to_users():
#     users = database_user.get_all_users()
#     keyboard = Kb
#     for user in users:
#         try:
#             await bot.send_message(user[1], lang[user[5]]['first_april'], reply_markup=keyboard.FIRST_APRIL(user[5]))
#         except (aiogram.utils.exceptions.BotBlocked, aiogram.utils.exceptions.UserDeactivated):
#             pass


async def runnable(dp):
    asyncio.create_task(database.get_energy())
    asyncio.create_task(send_kpi())
    # asyncio.create_task(send_letter_to_users())
    if CODE_MODE == 'PROD':
        asyncio.create_task(database.get_users_value())
    # await get_date_from_users()


if __name__ == "__main__":
    fortunes.register_handlers_client(dp)
    user.register_handlers_client(dp)
    admin.register_handlers_client(dp)
    channels.register_handlers_client(dp)
    register_handlers_callback(dp)
    middleware_register(dp)
    if not Migration.is_perform_migrations():
        print("ONLINE")
        executor.start_polling(dp, skip_updates=True, on_startup=runnable)
