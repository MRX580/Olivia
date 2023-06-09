from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
CODE_MODE = os.getenv('CODE_MODE')
if CODE_MODE == 'TEST':
    memory = MemoryStorage()
elif CODE_MODE == 'PROD':
    memory = RedisStorage2(host="127.0.0.1", port=6379)
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=memory)
print("ONLINE")
