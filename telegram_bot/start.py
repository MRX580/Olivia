import asyncio

from handlers.user import register_handlers_client
from callbacks.user import register_handlers_callback
from aiogram import executor
from create_bot import dp
from utils.database import Database
database = Database()


async def plus_energy(dp):
    asyncio.create_task(database.get_energy())


if __name__ == "__main__":
    register_handlers_client(dp)
    register_handlers_callback(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=plus_energy)
