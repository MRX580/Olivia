import psycopg2
import asyncio
import json

from datetime import datetime, date
from typing import Union

from aiogram.types import Message, CallbackQuery, Update
from amplitude import Amplitude, BaseEvent

amplitude = Amplitude("bbdc22a8304dbf12f2aaff6cd40fbdd3")


class Database:
    conn = psycopg2.connect(**{
        'dbname': 'olivia_test',
        'user': 'digimagic',
        'password': 'digiolivia457',
        'host': '185.67.0.198',
        'port': '5432'
    })
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, user_id INT, first_name TEXT, '
                'name TEXT, energy INT, language TEXT, '
                'attempts_used INT, last_attempt TIMESTAMP, is_first_try BOOLEAN, join_at TIMESTAMP, phone_number TEXT, '
                'username TEXT, natal_data TEXT, natal_city TEXT);')

    cur.execute('CREATE TABLE IF NOT EXISTS wisdom (id SERIAL PRIMARY KEY, user_id INT, first_name TEXT, '
                'message TEXT, create_at TIMESTAMP);')

    cur.execute('CREATE TABLE IF NOT EXISTS history(user_id INT, card TEXT, '
                'text TEXT, create_at TIMESTAMP, user_q TEXT, reaction TEXT, message_id INT, thanks BOOLEAN, full_text '
                'TEXT);')

    cur.execute('CREATE TABLE IF NOT EXISTS questions(id SERIAL PRIMARY KEY, user_id INT, question TEXT, '
                'create_at TIMESTAMP);')

    cur.execute('CREATE TABLE IF NOT EXISTS olivia(energy INT, max_energy INT);')

    cur.execute('CREATE TABLE IF NOT EXISTS decks(ru TEXT, en TEXT, reversed BOOLEAN);')

    cur.execute('CREATE TABLE IF NOT EXISTS web3_addresses(user_id INT, bitcoin TEXT, ethereum TEXT, ripple TEXT);')

    cur.execute('CREATE TABLE IF NOT EXISTS temp_data(user_id INT, birth_request_sent BOOLEAN);')

    conn.commit()

    cur.execute('SELECT * FROM decks')
    decks = cur.fetchall()

    if not decks:
        with open('utils/sample.json', 'r', encoding='utf-8') as f:
            data_decks = json.load(f)
        for item in data_decks:
            cur.execute('INSERT INTO "decks"(ru, en, reversed) VALUES(%s, %s, %s)', (item[0], item[1], item[2]))
            conn.commit()

    cur.execute('SELECT * FROM olivia')
    data = cur.fetchone()
    if data is None:
        cur.execute('INSERT INTO olivia(energy, max_energy) VALUES(%s, %s)', (3, 3))
        conn.commit()

    async def get_energy(self):
        while True:
            await asyncio.sleep(3600)
            self.cur.execute('SELECT max_energy FROM olivia')
            max_energy = int(self.cur.fetchone()[0])
            self.cur.execute('SELECT energy FROM olivia')
            energy = self.cur.fetchone()[0]
            if energy < max_energy:
                self.cur.execute(f'UPDATE olivia SET energy = energy+1')
            self.conn.commit()

    async def get_users_value(self):
        while True:
            await asyncio.sleep(600)
            self.cur.execute('SELECT * FROM users')
            value_users = len(self.cur.fetchall()[0])
            amplitude.track(BaseEvent(event_type='PingUsers', user_id='currently_users',
                                      event_properties={'currently_users': value_users}))

    def convert_time(self, time: str):
        data = time[:-7].replace('-', ':').replace(' ', ':').split(':')
        return datetime(int(data[0]), int(data[1]), int(data[2]), int(data[3]), int(data[4]), int(data[5]))


class User(Database):
    def is_user_exists(self, tg_user: Message):
        tg_user = tg_user.from_user
        self.cur.execute(f'SELECT * FROM users WHERE user_id = %s', (tg_user.id,))
        user = self.cur.fetchone()
        if user:
            return user
        return False

    def add_question(self, tg_user: Message or CallbackQuery, text: str):
        self.cur.execute('INSERT INTO questions(user_id, question, create_at) VALUES(%s,%s,%s)', (tg_user.from_user.id,
                                                                                                  text, datetime.now()))
        self.conn.commit()

    def create_user(self, tg_user: Message):
        contact = tg_user.contact
        tg_user = tg_user.from_user
        time = datetime.now()
        self.cur.execute('INSERT INTO users(user_id, first_name, name, energy, language, attempts_used, last_attempt, '
                         'is_first_try, join_at, phone_number, username, natal_data, natal_city) '
                         'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                         (tg_user.id, tg_user.first_name, '', 100, 'ru', 0, time, False, time,
                          contact.phone_number if contact is not None else None, tg_user.username, None, None))
        self.cur.execute(f'UPDATE olivia SET max_energy = %s', (self.get_len_all_users() * 3,))
        self.conn.commit()

    def update_name(self, tg_user: Message):
        self.cur.execute(f'UPDATE users SET name = %s WHERE user_id = %s', (tg_user.text, tg_user.from_user.id))
        self.conn.commit()

    def update_natal_data(self, tg_user: Message, natal_data):
        self.cur.execute(f'UPDATE users SET natal_data = %s WHERE user_id = %s', (natal_data, tg_user.from_user.id))
        self.conn.commit()

    def update_natal_city(self, tg_user: Message, natal_city):
        self.cur.execute(f'UPDATE users SET natal_city = %s WHERE user_id = %s', (natal_city, tg_user.from_user.id))
        self.conn.commit()

    def switch_language(self, language: str,
                        tg_user: CallbackQuery or Message):
        self.cur.execute(f'UPDATE users SET language = %s WHERE user_id = %s', (language, tg_user.from_user.id))
        self.conn.commit()

    def get_len_all_users(self):
        self.cur.execute(f'SELECT * FROM users')
        return len(self.cur.fetchall())

    def get_all_users(self):
        self.cur.execute(f'SELECT * FROM users')
        return self.cur.fetchall()

    def get_olivia_energy(self):
        self.cur.execute(f'SELECT energy FROM olivia')
        return self.cur.fetchone()[0]

    def get_language(self, tg_user: CallbackQuery or Message):
        if type(tg_user) == Update:
            tg_user = tg_user.message
        self.cur.execute(f'SELECT language FROM users WHERE user_id = %s', (tg_user.from_user.id, ))
        return self.cur.fetchone()[0]

    def get_name(self, tg_user: CallbackQuery or Message):
        self.cur.execute(f'SELECT name FROM users WHERE user_id = %s', (tg_user.from_user.id, ))
        return self.cur.fetchone()[0]

    def minus_energy(self):
        self.cur.execute(f'UPDATE olivia SET energy = energy-1')
        self.conn.commit()

    def plus_energy(self):
        self.cur.execute(f'UPDATE olivia SET energy = energy+1')
        self.conn.commit()

    def get_all_users_for_today(self):
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        self.cur.execute(f"SELECT * FROM history WHERE DATE(create_at) = %s", (today_str, ))
        rows = self.cur.fetchall()
        return len(rows)

    def get_all_history(self):
        self.cur.execute(f'SELECT * FROM history')
        return len(self.cur.fetchall())

    def change_last_attempt(self, tg_user: CallbackQuery or Message):
        time = datetime.now()
        self.cur.execute(f'UPDATE users SET last_attempt = %s WHERE user_id = %s', (time, tg_user.from_user.id))
        self.conn.commit()

    def add_thanks(self, message_id):
        self.cur.execute(f'UPDATE history SET thanks = True WHERE message_id = %s', (message_id,))
        self.conn.commit()

    def get_all_thanks(self):
        self.cur.execute("SELECT thanks FROM history")
        list_thanks = self.cur.fetchall()
        values = [x[0] for x in list_thanks]
        return values.count(True)

    def get_active_users_for_today(self):
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        self.cur.execute(f"SELECT * FROM users WHERE DATE(last_attempt) = %s", (today_str,))
        rows = self.cur.fetchall()
        return len(rows)


class Fortune(Database):

    def add_history(self, tg_user: Message or CallbackQuery,
                    card: str,
                    text: str,
                    user_q: str,
                    message_id: int,
                    full_text: str):
        self.cur.execute(f'INSERT INTO history(user_id, card, text, create_at, user_q, reaction, message_id, thanks, '
                         f'full_text)'
                         f' VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                         (tg_user.from_user.id, card, text, datetime.now(), user_q, None, message_id, False, full_text))
        self.conn.commit()

    def get_history(self, tg_user: Message or CallbackQuery):
        self.cur.execute(f'SELECT * FROM history WHERE user_id = %s', (tg_user.from_user.id,))
        return self.cur.fetchall()[::-1]

    def check_first_try(self, tg_user: Message or CallbackQuery):
        self.cur.execute(f'UPDATE users SET is_first_try = True WHERE user_id = %s', (tg_user.from_user.id,))
        self.conn.commit()

    def change_reaction(self, reaction, message_id):
        self.cur.execute(f'UPDATE history SET reaction = %s WHERE message_id = %s', (reaction, reaction))
        self.conn.commit()


class Wisdom(Database):
    def add_wisdom(self, tg_user: Message or CallbackQuery,
                   msg: str):
        tg_user = tg_user.from_user
        self.cur.execute('INSERT INTO wisdom(user_id, first_name, message, create_at) VALUES(%s,%s,%s,%s)',
                         (tg_user.id, tg_user.first_name, msg, datetime.now()))
        self.conn.commit()


class Decks(Database):
    def update_reverse(self, lang: str, reverse: bool, text: str):
        reverse = False if reverse else True
        self.cur.execute(f'UPDATE decks SET reversed = %s WHERE {lang} = %s', (reverse, text))
        self.conn.commit()

    def get_reversed(self, lang: str, text: str):
        self.cur.execute(f'SELECT reversed FROM decks WHERE {lang} = %s', (text,))
        return self.cur.fetchone()[0]


class Web3(Database):
    def create_unique_address(self, blockchain, address, user_id):
        if not self.__is_user_in_database(user_id):
            self._create_user_row(user_id)

        self.cur.execute(f'UPDATE web3_addresses SET {blockchain} = %s WHERE user_id = %s', (address, user_id))
        self.conn.commit()

    def __is_user_in_database(self, user_id):
        sql_query = f"SELECT * FROM web3_addresses WHERE user_id = %s"
        self.cur.execute(sql_query, (user_id,))
        result = self.cur.fetchall()
        if not result:
            return False
        return True

    def _create_user_row(self, user_id):
        sql_query = '''
            INSERT INTO web3_addresses (user_id, bitcoin, ethereum, ripple)
            VALUES (%s, %s, %s, %s)
            '''

        self.cur.execute(sql_query, (user_id, '', '', ''))
        self.conn.commit()

    def get_blockchain_address(self, blockchain, user_id):
        if self.is_user_addresses_exists(blockchain, user_id):
            self.cur.execute(f'SELECT {blockchain} FROM web3_addresses WHERE user_id = %s', (user_id,))
            result_query = self.cur.fetchone()[0]

            return result_query
        return None

    def is_user_addresses_exists(self, blockchain, user_id):
        if blockchain not in ['bitcoin', 'ethereum', 'ripple']:
            raise "Not correct blockchain, choice from - bitcoin, ethereum, ripple"

        try:
            self.cur.execute(f'SELECT {blockchain} FROM web3_addresses WHERE user_id = %s', (user_id, ))
            result_query = self.cur.fetchone()[0]
        except TypeError:
            return False
        if not result_query:
            return False
        return True


class Temp(Database):

    def insert_birth_status(self, user_id, value=True):
        self.cur.execute('INSERT INTO temp_data(user_id, birth_request_sent) VALUES(%s,%s)', (user_id, value))
        self.conn.commit()

    def update_birth_status(self, user_id, value=True):
        self.cur.execute('UPDATE temp_data SET birth_request_sent = %s WHERE user_id = %s', (value, user_id))
        self.conn.commit()

    def get_birth_status(self, user_id) -> Union[None, bool]:
        self.cur.execute(f'SELECT birth_request_sent FROM temp_data WHERE user_id = %s', (user_id,))
        result = self.cur.fetchone()

        if result is None:
            return None
        return result[0]
