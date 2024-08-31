import asyncio
import datetime

import aiogram.utils.exceptions

from handlers import user, fortunes, admin, channels
from callbacks.user import register_handlers_callback
from handlers.admin import ADMINS_ID, get_kpi
from aiogram import executor
from create_bot import dp, CODE_MODE, bot
from utils.database import Database, User, Temp
from utils.languages import lang
from migrations import Migration
from middleware.main import middleware_register
from aiogram_calendar import DialogCalendar

database = Database()
database_user = User()
database_temp = Temp()


async def send_kpi():
    while True:
        now = datetime.datetime.now()
        if now.hour == 10 and now.minute == 0:
            user_ids = ADMINS_ID

            for user_id in user_ids:
                await bot.send_message(user_id, await get_kpi())
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)


async def refresh_available_openings():
    while True:
        now = datetime.datetime.now()

        if now.hour == 23 and now.minute == 59:
            user_ids = ADMINS_ID

            # Получаем всех пользователей и их подписки одним запросом
            user_subscriptions = database_user.get_all_user_subscriptions()

            updates = []
            for user_id, subscription in user_subscriptions.items():
                updated_cards = 3  # Значение по умолчанию

                if subscription == 'standard':
                    updated_cards = 10

                updates.append((updated_cards, user_id))

            # Выполняем пакетное обновление данных
            query = 'UPDATE users SET available_openings = %s WHERE user_id = %s'
            database_user.execute_batch_update(query, updates)

            for user_id, user_date_expire in database_user.get_users_subscription_expiration().items():
                if user_date_expire is None:
                    continue
                if user_date_expire < datetime.datetime.now():
                    database_user.change_user_subscription_expired(user_id, None)
                    database_user.change_user_subscription(user_id, 'basic')
                    await asyncio.gather(
                        *[bot.send_message(user_id, f"У ID - {user_id}. Закончилась месячная подписка") for user_id in
                          user_ids]
                    )


            await asyncio.gather(
                *[bot.send_message(user_id, "Карты наших любимых пользователей были обновлены") for user_id in user_ids]
            )

            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)



async def get_date_from_users():
    users = database_user.get_all_users()
    for i in users:
        is_birth = await database_temp.get_birth_status(i[1])
        if is_birth is None:
            try:
                await bot.send_message(i[1], lang[i[5]]['get_date_start'],
                                       reply_markup=await DialogCalendar(language=i[5]).start_calendar(year=1995))
                database_temp.check_entry(i[1], False)
            except (aiogram.utils.exceptions.BotBlocked, aiogram.utils.exceptions.UserDeactivated):
                pass


# async def send_letter_to_users():
#     users = database_user.get_all_users()
#     keyboard = Kb
#     for user in users:
#         try:
#             await bot.send_message(user[1], lang[user[5]]['first_april'], reply_markup=keyboard.FIRST_APRIL(user[5]))
#         except (aiogram.utils.exceptions.BotBlocked, aiogram.utils.exceptions.UserDeactivated):
#             pass


async def runnable(dp):
    asyncio.create_task(database.get_energy())
    asyncio.create_task(send_kpi())
    asyncio.create_task(refresh_available_openings())
    # asyncio.create_task(send_letter_to_users())
    if CODE_MODE == 'PROD':
        asyncio.create_task(database.get_users_value())
    # await get_date_from_users()


if __name__ == "__main__":
    fortunes.register_handlers_client(dp)
    user.register_handlers_client(dp)
    admin.register_handlers_client(dp)
    channels.register_handlers_client(dp)
    register_handlers_callback(dp)
    middleware_register(dp)
    if not Migration.is_perform_migrations():
        print("ONLINE")
        executor.start_polling(dp, skip_updates=True, on_startup=runnable)
