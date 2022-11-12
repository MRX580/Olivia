import sqlite3
import asyncio

from datetime import datetime, timedelta
from aiogram.types import Message, CallbackQuery


class Database:
    conn = sqlite3.connect('utils/users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INT, first_name TEXT, name TEXT, energy INT, language TEXT, '
                'day datetime, week datetime, month datetime, is_first_try BOOL, join_at datetime);')
    cur.execute('CREATE TABLE IF NOT EXISTS fortune (user_id INT, first_name TEXT, card_type TEXT, answer TEXT, '
                'create_at datetime);')
    cur.execute('CREATE TABLE IF NOT EXISTS wisdom (user_id INT, first_name TEXT, message TEXT, create_at datetime);')

    async def get_energy_all(self):
        while True:
            await asyncio.sleep(3600)
            users = self.cur.execute('SELECT * FROM users').fetchall()
            for user in users:
                user_id = user[0]
                energy = user[2]
                if energy < 100:
                    self.cur.execute(f'UPDATE users SET energy = energy+10 WHERE user_id = {user_id}')
                    self.conn.commit()

    def convert_time(self, time: str):
        data = time[:-7].replace('-', ':').replace(' ', ':').split(':')
        return datetime(int(data[0]), int(data[1]), int(data[2]), int(data[3]), int(data[4]), int(data[5]))


class User(Database):
    def is_user_exists(self, tg_user: Message):
        tg_user = tg_user.from_user
        user = self.cur.execute(f'SELECT * FROM users WHERE user_id = {tg_user.id}').fetchone()
        if user:
            return user
        return False

    def create_user(self, tg_user: Message,
                    name: str):
        tg_user = tg_user.from_user
        time = datetime.now()
        self.cur.execute('INSERT INTO users(user_id, first_name, name, energy, language, day, week, month, '
                         'is_first_try, join_at) '
                         'VALUES(?,?,?,?,?,?,?,?,?,?)',
                         (tg_user.id, tg_user.first_name, name, 100, 'ru', time, time, time, False, time))
        self.conn.commit()

    def switch_language(self, language: str,
                        tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET language = "{language}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def get_language(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT language FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def get_energy(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT energy FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def get_name(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT name FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def get_day(self, tg_user: CallbackQuery or Message):
        return self.convert_time(self.cur.execute(f'SELECT day FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0])

    def get_week(self, tg_user: CallbackQuery or Message):
        return self.convert_time(self.cur.execute(f'SELECT week FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0])

    def get_month(self, tg_user: CallbackQuery or Message):
        return self.convert_time(self.cur.execute(f'SELECT month FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0])

    def update_day(self, tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET day = "{datetime.now()+timedelta(days=1)}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def update_week(self, tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET week = "{datetime.now()+timedelta(weeks=1)}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def update_month(self, tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET month = "{datetime.now()+timedelta(days=30)}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def minus_energy(self, tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET energy = energy-50 WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()


class Fortune(Database):
    def create_fortune(self, tg_user: Message or CallbackQuery,
                       card_type: str,
                       answer: str):
        tg_user = tg_user.from_user
        self.cur.execute('INSERT INTO fortune(user_id, first_name, card_type, answer, create_at) VALUES(?,?,?,?,?)',
                         (tg_user.id, tg_user.first_name, card_type, answer, datetime.now()))
        self.conn.commit()

    def check_session(self, tg_user: Message or CallbackQuery):
        data = self.cur.execute(f'SELECT create_at FROM fortune WHERE user_id = {tg_user.from_user.id} ORDER BY '
                                f'create_at').fetchall()[-1][0]
        return self.convert_time(data)

    def check_first_try(self, tg_user: Message or CallbackQuery):
        self.cur.execute(f'UPDATE users SET is_first_try = True WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def is_first_try(self, tg_user: Message or CallbackQuery):
        return self.cur.execute(f'SELECT is_first_try FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]


class Wisdom(Database):
    def add_wisdom(self, tg_user: Message or CallbackQuery,
                   msg: str):
        tg_user = tg_user.from_user
        self.cur.execute('INSERT INTO wisdom(user_id, first_name, message, create_at) VALUES(?,?,?,?)',
                         (tg_user.id, tg_user.first_name, msg, datetime.now()))
        self.conn.commit()