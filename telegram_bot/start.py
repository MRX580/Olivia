import asyncio
import datetime
from handlers import user, fortunes, admin, channels
from callbacks.user import register_handlers_callback
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
            user_ids = [951679992, 272433944]
            today_opened = database_user.get_all_users_for_today()
            all_users = database_user.get_len_all_users()
            all_history = database_user.get_all_history()
            all_active_users = database_user.get_active_users_for_today()
            all_thanks = database_user.get_all_thanks()
            for id in user_ids:
                await bot.send_message(id,
                                       f"""
Активных пользователей сегодня: {all_active_users}
Количество открытых карт сегодня: {today_opened}

Всего пользователей в базе: {all_users}
Всего открытых карт: {all_history}
Количество “Спасибо”: {all_thanks}
                                               """)
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)


async def get_date_from_users():
    users = database_user.get_all_users()
    for i in users:
        is_birth = database_temp.get_birth_status(i[1])
        if is_birth is None:
            await bot.send_message(i[1], lang[i[5]]['get_date_start'],
                                   reply_markup=await DialogCalendar(language=i[5]).start_calendar(year=1995))
            database_temp.check_entry(i[1], False)


async def plus_energy(dp):
    asyncio.create_task(database.get_energy())
    asyncio.create_task(send_kpi())
    asyncio.create_task(get_date_from_users())
    if CODE_MODE == 'PROD':
        asyncio.create_task(database.get_users_value())


if __name__ == "__main__":
    fortunes.register_handlers_client(dp)
    user.register_handlers_client(dp)
    admin.register_handlers_client(dp)
    channels.register_handlers_client(dp)
    register_handlers_callback(dp)
    middleware_register(dp)
    if not Migration.is_perform_migrations():
        print("ONLINE")
        executor.start_polling(dp, skip_updates=True, on_startup=plus_energy)
