import sqlite3
import asyncio
import os

from datetime import datetime
from aiogram.types import Message, CallbackQuery


class Database:
    conn = sqlite3.connect('utils/users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY, user_id INT, first_name TEXT, '
                'name TEXT, energy INT, language TEXT, '
                'attempts_used INT, last_attempt DATETIME, is_first_try BOOL, join_at datetime);')
    cur.execute('CREATE TABLE IF NOT EXISTS fortune (id INTEGER NOT NULL PRIMARY KEY, user_id INT, first_name TEXT, '
                'card_type TEXT, answer TEXT, type_fortune TEXT, '
                'create_at datetime);')
    cur.execute('CREATE TABLE IF NOT EXISTS wisdom (id INTEGER NOT NULL PRIMARY KEY, user_id INT, first_name TEXT, '
                'message TEXT, create_at datetime);')
    cur.execute('CREATE TABLE IF NOT EXISTS history(id INTEGER NOT NULL PRIMARY KEY, user_id INT, card TEXT, '
                'text TEXT, create_at DATETIME);')
    cur.execute('CREATE TABLE IF NOT EXISTS questions(id INTEGER NOT NULL PRIMARY KEY, user_id INT, question TEXT, '
                'create_at DATETIME);')
    cur.execute('CREATE TABLE IF NOT EXISTS olivia(energy INT, max_energy INT);')
    cur.execute('CREATE TABLE IF NOT EXISTS decks(ru TEXT, en TEXT, reversed BOOL);')

    async def get_energy(self):
        while True:
            await asyncio.sleep(3600)
            max_energy = int(self.cur.execute('SELECT max_energy FROM olivia').fetchone()[0])
            energy = self.cur.execute('SELECT energy FROM olivia').fetchone()[0]
            if energy < max_energy:
                self.cur.execute(f'UPDATE olivia SET energy = energy+1')
            self.conn.commit()

    def add_new_table(self, table: str, remove_column: list, add_column: list):
        columns = []
        if remove_column:
            for column in self.cur.execute(f'PRAGMA table_info({table})').fetchall():
                if not column[1] in remove_column:
                    columns.append(column[1])
            name_columns = ', '.join(columns)
            self.cur.execute(f'CREATE TABLE copied AS SELECT {name_columns} FROM {table} WHERE 0')
            for column in self.cur.execute(f'SELECT {name_columns} FROM users').fetchall():
                text = '?,' * len(column)
                self.cur.execute(f'INSERT INTO copied({name_columns}) VALUES({text[:-1]})', column)
            self.cur.execute(f'DROP TABLE {table}')
            self.cur.execute(f'ALTER TABLE copied RENAME TO users')
        try:
            if add_column:
                for i in add_column:
                    self.cur.execute(f'ALTER TABLE {table} ADD COLUMN {i}')
        except sqlite3.OperationalError:
            print('Имя столбца сущевствует')
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

    def add_question(self, tg_user: Message or CallbackQuery, text: str):
        self.cur.execute('INSERT INTO questions(user_id, question, create_at) VALUES(?,?,?)', (tg_user.from_user.id,
                                                                                               text, datetime.now()))
        self.conn.commit()

    def create_user(self, tg_user: Message):
        tg_user = tg_user.from_user
        time = datetime.now()
        self.cur.execute('INSERT INTO users(user_id, first_name, name, energy, language, attempts_used, last_attempt, '
                         'is_first_try, join_at) '
                         'VALUES(?,?,?,?,?,?,?,?,?)',
                         (tg_user.id, tg_user.first_name, '', 100, 'ru', 0, time, False, time))
        self.cur.execute(f'UPDATE olivia SET max_energy = {self.get_all_users() * 3}')
        self.conn.commit()

    def update_name(self, tg_user: Message):
        self.cur.execute(f'UPDATE users SET name = "{tg_user.text}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def switch_language(self, language: str,
                        tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET language = "{language}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def get_last_5_history(self, tg_user: Message or CallbackQuery):
        return [i[0] for i in self.cur.execute(f'SELECT create_at FROM history WHERE user_id = {tg_user.from_user.id} ORDER BY '
                                               f'create_at').fetchall()][:5]

    def get_last_5_history_back(self, tg_user: Message or CallbackQuery):
        return [i[0]+'_back' for i in self.cur.execute(f'SELECT create_at FROM history WHERE user_id = {tg_user.from_user.id} ORDER BY '
                                               f'create_at').fetchall()][:5]

    def get_data_history(self):
        return [i[0] for i in self.cur.execute('SELECT create_at FROM history').fetchall()]

    def get_data_history_back(self):
        return [i[0]+'_back' for i in self.cur.execute('SELECT create_at FROM history').fetchall()]

    def get_all_users(self):
        return len(self.cur.execute(f'SELECT * FROM users').fetchall())

    def get_olivia_energy(self):
        return self.cur.execute(f'SELECT energy FROM olivia').fetchone()[0]

    def get_language(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT language FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def get_name(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT name FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def minus_energy(self):
        self.cur.execute(f'UPDATE olivia SET energy = energy-1')
        self.conn.commit()

    def plus_energy(self):
        self.cur.execute(f'UPDATE olivia SET energy = energy+1')
        self.conn.commit()


class Fortune(Database):
    def create_fortune(self, tg_user: Message or CallbackQuery,
                       card_type: str,
                       answer: str,
                       type_fortune: str):
        tg_user = tg_user.from_user
        self.cur.execute('INSERT INTO fortune(user_id, first_name, card_type, answer, type_fortune, create_at) '
                         'VALUES(?,?,?,?,?,?)',
                         (tg_user.id, tg_user.first_name, card_type, answer, type_fortune, datetime.now()))
        self.conn.commit()

    def add_history(self, tg_user: Message or CallbackQuery,
                    card: str,
                    text: str):
        self.cur.execute(f'INSERT INTO history(user_id, card, text, create_at) VALUES(?,?,?,?)',
                         (tg_user.from_user.id, card, text, datetime.now()))
        self.conn.commit()

    def get_history(self, tg_user: Message or CallbackQuery):
        return self.cur.execute(f'SELECT * FROM history WHERE user_id = {tg_user.from_user.id}').fetchall()

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


class Decks(Database):
    def update_reverse(self, lang: str, reverse: bool, text: str):
        reverse = False if reverse else True
        self.cur.execute(f'UPDATE decks SET reversed = {reverse} WHERE {lang} = "{text}"')
        self.conn.commit()

    def get_reversed(self, lang: str, text: str):
        return self.cur.execute(f'SELECT reversed FROM decks WHERE {lang} = "{text}"').fetchone()[0]
