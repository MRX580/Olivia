import sqlite3
import asyncio
import json

from datetime import datetime, date
from typing import Union

from aiogram.types import Message, CallbackQuery, Update
from amplitude import Amplitude, BaseEvent

amplitude = Amplitude("bbdc22a8304dbf12f2aaff6cd40fbdd3")


class Database:
    conn = sqlite3.connect('utils/users.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY, user_id INT, first_name TEXT, '
                'name TEXT, energy INT, language TEXT, '
                'attempts_used INT, last_attempt DATETIME, is_first_try BOOL, join_at datetime, phone_number TEXT, '
                'username TEXT, natal_data TEXT, natal_city);')

    cur.execute('CREATE TABLE IF NOT EXISTS fortune (id INTEGER NOT NULL PRIMARY KEY, user_id INT, first_name TEXT, '
                'card_type TEXT, answer TEXT, type_fortune TEXT, '
                'create_at datetime);')

    cur.execute('CREATE TABLE IF NOT EXISTS wisdom (id INTEGER NOT NULL PRIMARY KEY, user_id INT, first_name TEXT, '
                'message TEXT, create_at datetime);')

    cur.execute('CREATE TABLE IF NOT EXISTS history(user_id INT, card TEXT, '
                'text TEXT, create_at DATETIME, user_q TEXT, reaction TEXT, message_id INT, thanks BOOL, full_text '
                'TEXT);')

    cur.execute('CREATE TABLE IF NOT EXISTS questions(id INTEGER NOT NULL PRIMARY KEY, user_id INT, question TEXT, '
                'create_at DATETIME);')

    cur.execute('CREATE TABLE IF NOT EXISTS olivia(energy INT, max_energy INT);')

    cur.execute('CREATE TABLE IF NOT EXISTS decks(ru TEXT, en TEXT, reversed BOOL);')

    cur.execute('CREATE TABLE IF NOT EXISTS web3_addresses(user_id INT, bitcoin TEXT, ethereum TEXT, ripple TEXT);')

    cur.execute('CREATE TABLE IF NOT EXISTS temp_data(user_id INT, birth_request_sent BOOL);')

    decks = cur.execute('SELECT * FROM decks').fetchone()
    if decks is None:
        with open('utils/sample.json', 'r', encoding='utf-8') as f:
            data_decks = json.load(f)
        for item in data_decks:
            cur.execute('INSERT INTO decks(ru, en, reversed) VALUES(?,?,?)', (item[0], item[1], item[2]))
            conn.commit()

    data = cur.execute('SELECT * FROM olivia').fetchone()
    if data is None:
        cur.execute('INSERT INTO olivia(energy, max_energy) VALUES(?,?)', (3, 3))
        conn.commit()

    async def get_energy(self):
        while True:
            await asyncio.sleep(3600)
            max_energy = int(self.cur.execute('SELECT max_energy FROM olivia').fetchone()[0])
            energy = self.cur.execute('SELECT energy FROM olivia').fetchone()[0]
            if energy < max_energy:
                self.cur.execute(f'UPDATE olivia SET energy = energy+1')
            self.conn.commit()

    async def get_users_value(self):
        while True:
            await asyncio.sleep(600)
            value_users = len(self.cur.execute('SELECT * FROM users').fetchall()[0])
            amplitude.track(BaseEvent(event_type='PingUsers', user_id='currently_users',
                                      event_properties={'currently_users': value_users}))
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
        contact = tg_user.contact
        tg_user = tg_user.from_user
        time = datetime.now()
        self.cur.execute('INSERT INTO users(user_id, first_name, name, energy, language, attempts_used, last_attempt, '
                         'is_first_try, join_at, phone_number, username, natal_data, natal_city) '
                         'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                         (tg_user.id, tg_user.first_name, '', 100, 'ru', 0, time, False, time,
                          contact.phone_number if contact is not None else None, tg_user.username, None, None))
        self.cur.execute(f'UPDATE olivia SET max_energy = {self.get_len_all_users() * 3}')
        self.conn.commit()

    def update_name(self, tg_user: Message):
        self.cur.execute(f'UPDATE users SET name = "{tg_user.text}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def update_natal_data(self, tg_user: Message, natal_data):
        print(123)
        self.cur.execute(f'UPDATE users SET natal_data = {natal_data} WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()
        print(123, True)

    def update_natal_city(self, tg_user: Message, natal_city):
        print(321)
        self.cur.execute(f'UPDATE users SET natal_city = "{natal_city}" WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()
        print(321, True)

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

    def get_len_all_users(self):
        return len(self.cur.execute(f'SELECT * FROM users').fetchall())

    def get_all_users(self):
        return self.cur.execute(f'SELECT * FROM users').fetchall()

    def get_olivia_energy(self):
        return self.cur.execute(f'SELECT energy FROM olivia').fetchone()[0]

    def get_language(self, tg_user: CallbackQuery or Message):
        if type(tg_user) == Update:
            tg_user = tg_user.message
        return self.cur.execute(f'SELECT language FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def get_opened_cards(self, tg_user: CallbackQuery or Message):
        self.cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ?", (tg_user.from_user.id,))
        result = self.cur.fetchone()[0]
        return result

    def get_days_with_olivia(self, tg_user: CallbackQuery or Message):
        query = self.cur.execute(f'SELECT join_at FROM users WHERE user_id = {tg_user.from_user.id}')
        join_at_date = query.fetchone()[0]
        last_registration = datetime.strptime(join_at_date, "%Y-%m-%d %H:%M:%S.%f")

        current_date = datetime.now()

        time_difference = current_date - last_registration

        days = time_difference.days

        months = days // 30
        remaining_days = days % 30

        result = f"{months} месяцев, {remaining_days} дней"
        return result

    def get_name(self, tg_user: CallbackQuery or Message):
        return self.cur.execute(f'SELECT name FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def minus_energy(self):
        self.cur.execute(f'UPDATE olivia SET energy = energy-1')
        self.conn.commit()

    def plus_energy(self):
        self.cur.execute(f'UPDATE olivia SET energy = energy+1')
        self.conn.commit()

    def get_all_users_for_today(self):
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        sql_query = f"SELECT * FROM history WHERE DATE(create_at) = '{today_str}'"
        self.cur.execute(sql_query)
        rows = self.cur.fetchall()
        return len(rows)

    def get_all_history(self):
        return len(self.cur.execute(f'SELECT * FROM history').fetchall())

    def change_last_attempt(self, tg_user: CallbackQuery or Message):
        time = datetime.now()
        self.cur.execute(f'UPDATE users SET last_attempt = ? WHERE user_id = ?', (time, tg_user.from_user.id))
        self.conn.commit()

    def add_thanks(self, message_id):
        self.cur.execute(f'UPDATE history SET thanks = True WHERE message_id = ?', (message_id, ))
        self.conn.commit()

    def get_all_thanks(self):
        list_thanks = self.cur.execute("SELECT thanks FROM history").fetchall()
        values = [x[0] for x in list_thanks]
        return values.count(True)

    def get_active_users_for_today(self):
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        sql_query = f"SELECT * FROM users WHERE DATE(last_attempt) = '{today_str}'"
        self.cur.execute(sql_query)
        rows = self.cur.fetchall()
        return len(rows)


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
                    text: str,
                    user_q: str,
                    message_id: int,
                    full_text: str):
        self.cur.execute(f'INSERT INTO history(user_id, card, text, create_at, user_q, reaction, message_id, thanks, '
                         f'full_text)'
                         f' VALUES(?,?,?,?,?,?,?,?,?)',
                         (tg_user.from_user.id, card, text, datetime.now(), user_q, None, message_id, False, full_text))
        self.conn.commit()

    def get_full_text_on_message_id(self, message_id: int):
        return self.cur.execute(f'SELECT full_text FROM history WHERE message_id = {message_id}').fetchone()

    def get_history(self, tg_user: Message or CallbackQuery):
        return self.cur.execute(f'SELECT * FROM history WHERE user_id = {tg_user.from_user.id}').fetchall()[::-1]

    def check_session(self, tg_user: Message or CallbackQuery):
        data = self.cur.execute(f'SELECT create_at FROM fortune WHERE user_id = {tg_user.from_user.id} ORDER BY '
                                f'create_at').fetchall()[-1][0]
        return self.convert_time(data)

    def check_first_try(self, tg_user: Message or CallbackQuery):
        self.cur.execute(f'UPDATE users SET is_first_try = True WHERE user_id = {tg_user.from_user.id}')
        self.conn.commit()

    def is_first_try(self, tg_user: Message or CallbackQuery):
        return self.cur.execute(f'SELECT is_first_try FROM users WHERE user_id = {tg_user.from_user.id}').fetchone()[0]

    def change_reaction(self, reaction, message_id):
        self.cur.execute(f'UPDATE history SET reaction = "{reaction}" WHERE message_id = {message_id}')
        self.conn.commit()


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


class Web3(Database):
    def create_unique_address(self, blockchain, address, user_id):
        if not self.__is_user_in_database(user_id):
            self._create_user_row(user_id)

        self.cur.execute(f'UPDATE web3_addresses SET {blockchain} = "{address}" WHERE user_id = "{user_id}"')
        self.conn.commit()

    def __is_user_in_database(self, user_id):
        sql_query = f"SELECT * FROM web3_addresses WHERE user_id = ?"
        self.cur.execute(sql_query, (user_id,))
        result = self.cur.fetchall()
        if not result:
            return False
        return True

    def _create_user_row(self, user_id):
        sql_query = '''
            INSERT INTO web3_addresses (user_id, bitcoin, ethereum, ripple)
            VALUES (?, ?, ?, ?)
            '''

        self.cur.execute(sql_query, (user_id, '', '', ''))
        self.conn.commit()

    def get_blockchain_address(self, blockchain, user_id):
        if self.is_user_addresses_exists(blockchain, user_id):
            query = f'SELECT {blockchain} FROM web3_addresses WHERE user_id = {user_id}'
            result_query = self.cur.execute(query).fetchone()[0]

            return result_query
        return None

    def is_user_addresses_exists(self, blockchain, user_id):
        if blockchain not in ['bitcoin', 'ethereum', 'ripple']:
            raise "Not correct blockchain, choice from - bitcoin, ethereum, ripple"

        query = f'SELECT {blockchain} FROM web3_addresses WHERE user_id = {user_id}'
        try:
            result_query = self.cur.execute(query).fetchone()[0]
        except TypeError:
            return False
        if not result_query:
            return False
        return True


class Temp(Database):

    def check_entry(self, user_id, value=True):
        print('check')
        self.cur.execute('INSERT INTO temp_data(user_id, birth_request_sent) VALUES(?,?)', (user_id, value))
        self.conn.commit()
        print('check', True)

    def get_birth_status(self, user_id) -> Union[None, bool]:
        result = self.cur.execute(f'SELECT birth_request_sent FROM temp_data WHERE user_id = {user_id}')
        result = result.fetchone()

        if result is None:
            return None
        return result[0]

