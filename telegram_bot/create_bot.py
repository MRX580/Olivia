from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from dotenv import load_dotenv, find_dotenv
import os
import openai

# Загрузка переменных окружения из .env файла
load_dotenv(find_dotenv())

# Получение переменных окружения
CODE_MODE = os.getenv('CODE_MODE')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройка подключения к Redis
memory = RedisStorage2(host=REDIS_HOST, port=REDIS_PORT)

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=memory)

# Настройка ключа API для OpenAI
openai.api_key = os.getenv('OPENAI_TOKEN')
