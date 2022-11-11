import sqlite3
import asyncio

from datetime import datetime
from aiogram.types import Message, CallbackQuery


class Database:
    conn = sqlite3.connect('utils/users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INT, first_name TEXT, energy INT, language TEXT, '
                'join_at datetime);')
    cur.execute('CREATE TABLE IF NOT EXISTS fortune (user_id INT, card_type TEXT, create_at datetime);')

    async def get_energy_all(self):
        while True:
            await asyncio.sleep(3600)
            users = self.cur.execute('SELECT energy FROM users').fetchall()
            for user in users:
                energy = user[0]
                if energy < 100:
                    print('GET')
                    self.cur.execute('UPDATE users SET energy = energy+10')
                    self.conn.commit()


class User(Database):
    def is_user_exists(self, tg_user: Message):
        tg_user = tg_user.from_user
        user = self.cur.execute(f'SELECT * FROM users WHERE user_id = {tg_user.id}').fetchone()
        if user:
            return user
        self.cur.execute('INSERT INTO users(user_id, first_name, energy, language, join_at) VALUES(?,?,?,?,?)',
                         (tg_user.id, tg_user.first_name, 100, 'ru', datetime.utcnow()))
        self.conn.commit()
        return '[INFO] New user created'

    def switch_language(self, language: str,
                        tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET language = "{language}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def get_language(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT language FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def get_energy(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT energy FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def minus_energy(self, tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET energy = energy-50 WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()


class Fortune(Database):
    def create_fortune(self, tg_user: Message,
                       card_type: str):
        tg_user = tg_user.from_user
        self.cur.execute('INSERT INTO users(user_id, card_type, create_at) VALUES(?,?,?)',
                         (tg_user.id, card_type, datetime.utcnow()))
        self.conn.commit()