import logging
from logging.handlers import TimedRotatingFileHandler
from telegram_bot.create_bot import bot
import asyncio


class TelegramLogsHandler(logging.Handler):
    def __init__(self, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.bot.send_message(chat_id=self.chat_id, text=log_entry))


def logging_to_file_telegram(log_type, *args):
    log_file = 'bot.log'
    logger = logging.getLogger(__name__)

    # Словарь уровней логирования
    log_levels = {'warn': logging.WARNING, 'info': logging.INFO, 'error': logging.ERROR}

    # Добавляем обработчики, если их еще нет
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        telegram_handler = TelegramLogsHandler(-4180190396)  # Используйте свой chat_id
        logger.addHandler(telegram_handler)

    # Проверка на допустимость типа лога
    if log_type not in log_levels:
        raise ValueError("Недопустимый тип лога: должен быть 'warn', 'info' или 'error'.")

    # Логирование сообщений
    for message in args:
        logger.log(log_levels[log_type], message)



