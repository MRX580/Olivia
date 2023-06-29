import asyncio
import datetime

from handlers import user, fortunes, admin
from callbacks.user import register_handlers_callback
from aiogram import executor
from create_bot import dp, CODE_MODE, bot
from utils.database import Database, User
from migrations import Migration
database = Database()
users = User()


async def send_kpi():
    while True:
        now = datetime.datetime.now()
        if now.hour == 10 and now.minute == 0:
            user_ids = [951679992, 272433944]
            today_opened = users.get_all_users_for_today()
            all_users = users.get_all_users()
            all_history = users.get_all_history()
            all_active_users = users.get_active_users_for_today()
            all_thanks = users.get_all_thanks()
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



async def plus_energy(dp):

    asyncio.create_task(database.get_energy())
    asyncio.create_task(send_kpi())
    if CODE_MODE == 'PROD':
        asyncio.create_task(database.get_users_value())


if __name__ == "__main__":
    fortunes.register_handlers_client(dp)
    user.register_handlers_client(dp)
    admin.register_handlers_client(dp)
    register_handlers_callback(dp)
    if not Migration.is_perform_migrations():
        executor.start_polling(dp, skip_updates=True, on_startup=plus_energy)
