from telegram_bot.create_bot import bot
from aiogram import types, Dispatcher
from telegram_bot.utils.database import User

ADMINS_ID = [951679992, 272433944]

database_user = User()


def is_admin(user_id):
    return user_id in ADMINS_ID


def admin_check_filter(message):
    user_id = message.from_user.id
    return is_admin(user_id)


async def get_log(message: types.Message):
    await bot.send_message(message.chat.id, 'Отправляю логи...')
    await bot.send_document(message.chat.id, open('bot.log', 'rb'))


async def get_kpi(message: types.Message = None):
    active_opened = database_user.get_all_active_users()
    all_users = database_user.get_len_all_users()
    all_history = database_user.get_all_history()
    all_active_users_today = database_user.get_active_users_for_today()
    all_active_users_week = database_user.get_active_users_for_last_week()
    all_active_users_month = database_user.get_active_users_for_last_month()
    all_thanks = database_user.get_all_thanks()
    rd7 = database_user.get_retention_data(7)
    rd30 = database_user.get_retention_data(30)

    return f"""
Активных пользователей:
Сегодня: {all_active_users_today}
Неделя: {all_active_users_week}
Месяц: {all_active_users_month}

Зарегестрированые пользователи: {active_opened}

7-Day Retention valid users: {rd7['valid_user_count']}
30-Day Retention  valid users: {rd30['valid_user_count']}

Всего пользователей в базе: {all_users}
Количество “Спасибо”: {all_thanks}
Всего открытых карт: {all_history}
"""


async def send_kpi(message: types.Message):
    await bot.send_message(message.chat.id,
                           await get_kpi(message))


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_log, admin_check_filter, commands=['log'], state='*')
    dp.register_message_handler(send_kpi, admin_check_filter, commands=['kpi'], state='*')