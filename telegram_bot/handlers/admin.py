from telegram_bot.create_bot import bot
from aiogram import types, Dispatcher
from telegram_bot.utils.database import User

ADMINS = [951679992, 272433944, 178594884, 610027951]

users = User()


def is_admin(user_id):
    return user_id in ADMINS


def admin_check_filter(message):
    user_id = message.from_user.id
    return is_admin(user_id)


async def get_log(message: types.Message):
    await bot.send_message(message.chat.id, 'Отправляю логи...')
    await bot.send_document(message.chat.id, open('bot.log', 'rb'))


async def get_kpi(message: types.Message):
    today_opened = users.get_all_users_for_today()
    all_users = users.get_len_all_users()
    all_history = users.get_all_history()
    all_active_users = users.get_active_users_for_today()
    all_thanks = users.get_all_thanks()
    await bot.send_message(message.chat.id,
                           f"""
Активных пользователей сегодня: {all_active_users}
Количество открытых карт сегодня: {today_opened}

Всего пользователей в базе: {all_users}
Всего открытых карт: {all_history}
Количество “Спасибо”: {all_thanks}
                           """)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_log, admin_check_filter, commands=['log'], state='*')
    dp.register_message_handler(get_kpi, admin_check_filter, commands=['kpi'], state='*')