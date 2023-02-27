import asyncio

from handlers import user, fortunes
from callbacks.user import register_handlers_callback
from aiogram import executor
from create_bot import dp, CODE_MODE
from utils.database import Database
database = Database()


async def plus_energy(dp):
    asyncio.create_task(database.get_energy())
    if CODE_MODE == 'PROD':
        asyncio.create_task(database.get_users_value())


if __name__ == "__main__":
    fortunes.register_handlers_client(dp)
    user.register_handlers_client(dp)
    register_handlers_callback(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=plus_energy)
