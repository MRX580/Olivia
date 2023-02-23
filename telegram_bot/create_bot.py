from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

redis = RedisStorage2(host="127.0.0.1", port=6379)
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=redis)
print("ONLINE")
