import logging

from create_bot import bot, dp, CODE_MODE
from aiogram import types, Dispatcher

ADMINS = [951679992, 272433944, 178594884, 610027951]


def is_admin(user_id):
    return user_id in ADMINS


def admin_check_filter(message):
    user_id = message.from_user.id
    return is_admin(user_id)


async def get_log(message: types.Message):
    await bot.send_message(message.chat.id, 'Отправляю логи...')
    await bot.send_document(message.chat.id, open('bot.log', 'rb'))


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_log, admin_check_filter, commands=['log'], state='*')