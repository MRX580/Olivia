import os
from dateutil.relativedelta import relativedelta

import mysql.connector
from mysql.connector.errors import OperationalError, InterfaceError, DatabaseError
import asyncio
import pandas as pd

from datetime import datetime, date, timedelta
from typing import Union
from dotenv import load_dotenv, find_dotenv
from aiogram.types import Message, CallbackQuery, Update
from amplitude import Amplitude, BaseEvent

amplitude = Amplitude("bbdc22a8304dbf12f2aaff6cd40fbdd3")
load_dotenv(find_dotenv())


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connect_to_db()
        self.create_tables_if_not_exist()

    def connect_to_db(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE"),
                autocommit=True,
                pool_name='my_pool',
                pool_size=20
            )
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn = None

    def create_tables_if_not_exist(self):
        tables = {
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    first_name VARCHAR(100),
                    name VARCHAR(100),
                    energy INT,
                    language VARCHAR(10),
                    attempts_used INT,
                    last_attempt DATETIME,
                    is_first_try BOOLEAN,
                    join_at DATETIME,
                    phone_number VARCHAR(20),
                    username VARCHAR(100),
                    natal_data TEXT,
                    natal_city VARCHAR(100),
                    available_openings INT,
                    subscription VARCHAR(50),
                    subscription_expired DATETIME
                )
            """,
            "olivia": """
                CREATE TABLE IF NOT EXISTS olivia (
                    energy INT,
                    max_energy INT
                )
            """,
            "fortune": """
                CREATE TABLE IF NOT EXISTS fortune (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    first_name VARCHAR(100),
                    card_type VARCHAR(100),
                    answer TEXT,
                    type_fortune VARCHAR(100),
                    create_at DATETIME
                )
            """,
            "history": """
                CREATE TABLE IF NOT EXISTS history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    card VARCHAR(100),
                    text TEXT,
                    create_at DATETIME,
                    user_q TEXT,
                    reaction VARCHAR(100),
                    message_id INT,
                    thanks BOOLEAN,
                    full_text TEXT
                )
            """,
            "wisdom": """
                CREATE TABLE IF NOT EXISTS wisdom (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    first_name VARCHAR(100),
                    message TEXT,
                    create_at DATETIME
                )
            """,
            "web3_addresses": """
                CREATE TABLE IF NOT EXISTS web3_addresses (
                    user_id BIGINT PRIMARY KEY,
                    bitcoin VARCHAR(100),
                    ethereum VARCHAR(100),
                    ripple VARCHAR(100)
                )
            """,
            "temp_data": """
                CREATE TABLE IF NOT EXISTS temp_data (
                    user_id BIGINT PRIMARY KEY,
                    birth_request_sent BOOLEAN
                )
            """,
            "payment_data": """
                CREATE TABLE IF NOT EXISTS payment_data (
                    user_id BIGINT PRIMARY KEY,
                    birth_request_sent BOOLEAN
                )
            """
        }

        for table_name, create_table_query in tables.items():
            self.execute_update(create_table_query)

    def check_connection(self):
        try:
            if self.conn is None or not self.conn.is_connected():
                print("Соединение потеряно, пробуем восстановить...")
                self.connect_to_db()
        except (OperationalError, InterfaceError) as e:
            print(f"Ошибка проверки соединения: {e}")
            self.connect_to_db()

    def execute_query(self, query, params=None):
        self.check_connection()
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def execute_update(self, query, params=None):
        self.check_connection()
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                with self.conn.cursor() as cur:
                    cur.execute(query, params or ())
                    self.conn.commit()
                break
            except (OperationalError, InterfaceError) as e:
                print(f"Ошибка выполнения запроса, попытка {attempt + 1}/{retry_attempts}: {e}")
                self.check_connection()
            except DatabaseError as e:
                print(f"Критическая ошибка базы данных: {e}")
                self.conn.rollback()
                break
            except Exception as e:
                print(f"Неизвестная ошибка: {e}")
                self.conn.rollback()
                break

    async def get_energy(self):
        while True:
            await asyncio.sleep(3600)
            max_energy_query = 'SELECT max_energy FROM olivia'
            energy_query = 'SELECT energy FROM olivia'
            self.check_connection()
            with self.conn.cursor() as cur:
                cur.execute(max_energy_query)
                max_energy = int(cur.fetchall()[0][0])
                cur.execute(energy_query)
                energy = int(cur.fetchall()[0][0])
                if energy < max_energy:
                    cur.execute('UPDATE olivia SET energy = energy + 1')
                self.conn.commit()

    async def get_users_value(self):
        while True:
            await asyncio.sleep(600)
            count_query = 'SELECT COUNT(*) FROM users'
            self.check_connection()
            with self.conn.cursor() as cur:
                cur.execute(count_query)
                value_users = cur.fetchall()[0][0]
                amplitude.track(BaseEvent(event_type='PingUsers', user_id='currently_users',
                                          event_properties={'currently_users': value_users}))
                self.conn.commit()

    def convert_time(self, time: str):
        data = time[:-7].replace('-', ':').replace(' ', ':').split(':')
        return datetime(int(data[0]), int(data[1]), int(data[2]), int(data[3]), int(data[4]), int(data[5]))


def calculate_retention(valid_user_count, total_user_count):
    return valid_user_count / total_user_count if total_user_count else 0


def count_total_users(df):
    return df['user_id'].nunique()


def count_valid_users(df):
    df['create_at'] = pd.to_datetime(df['create_at'])

    def sessions_with_required_gap(group):
        group = group.sort_values(by='create_at')
        return group['create_at'].diff().dt.total_seconds().div(3600).gt(4).sum() >= 1

    valid_users = df.groupby('user_id').filter(lambda x: sessions_with_required_gap(x))
    return valid_users['user_id'].nunique()


class User(Database):
    def __init__(self):
        print(11)
        super().__init__()

    def is_user_exists(self, tg_user: Message):
        tg_user = tg_user.from_user
        query = 'SELECT * FROM users WHERE user_id = %s'
        user = self.execute_query(query, (tg_user.id,))
        return user if user else False

    def execute_batch_update(self, query, data):
        with self.conn.cursor() as cursor:
            cursor.executemany(query, data)
        self.conn.commit()

    def add_question(self, tg_user: Message or CallbackQuery, text: str):
        query = 'INSERT INTO questions(user_id, question, create_at) VALUES(%s,%s,%s)'
        self.execute_update(query, (tg_user.from_user.id, text, datetime.now()))

    def create_user(self, tg_user: Message):
        contact = tg_user.contact
        tg_user = tg_user.from_user
        time = datetime.now()
        user_query = '''INSERT INTO users(user_id, first_name, name, energy, language, attempts_used, last_attempt, 
                             is_first_try, join_at, phone_number, username, natal_data, natal_city, available_openings, subscription, subscription_expired) 
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        olivia_query = 'UPDATE olivia SET max_energy = %s'
        self.execute_update(user_query, (tg_user.id, tg_user.first_name, '', 100, None, 0, time, False, time,
                                         contact.phone_number if contact is not None else None, tg_user.username, None,
                                         None, 3, "basic", None))
        self.execute_update(olivia_query, (self.get_len_all_users() * 3,))

    def update_name(self, tg_user: Message):
        query = 'UPDATE users SET name = %s WHERE user_id = %s'
        self.execute_update(query, (tg_user.text, tg_user.from_user.id))

    def update_natal_data(self, tg_user: Message, natal_data):
        query = 'UPDATE users SET natal_data = %s WHERE user_id = %s'
        self.execute_update(query, (natal_data, tg_user.from_user.id))

    def update_natal_city(self, tg_user: Message, natal_city):
        query = 'UPDATE users SET natal_city = %s WHERE user_id = %s'
        self.execute_update(query, (natal_city, tg_user.from_user.id))

    def update_available_openings(self, tg_user: Message or int, available_openings):
        if isinstance(tg_user, Message):
            tg_user = tg_user.from_user.id
        query = 'UPDATE users SET available_openings = %s WHERE user_id = %s'
        self.execute_update(query, (available_openings, tg_user))

    def switch_language(self, language: str, tg_user: CallbackQuery or Message):
        query = 'UPDATE users SET language = %s WHERE user_id = %s'
        self.execute_update(query, (language, tg_user.from_user.id))

    def get_last_5_history(self, tg_user: Message or CallbackQuery):
        query = 'SELECT create_at FROM history WHERE user_id = %s ORDER BY create_at'
        return [i[0] for i in self.execute_query(query, (tg_user.from_user.id,))][:5]

    def get_last_5_history_back(self, tg_user: Message or CallbackQuery):
        query = 'SELECT create_at FROM history WHERE user_id = %s ORDER BY create_at'
        return [i[0] + '_back' for i in self.execute_query(query, (tg_user.from_user.id,))][:5]

    def get_data_history(self):
        query = 'SELECT create_at FROM history'
        return [i[0] for i in self.execute_query(query)]

    def get_data_history_back(self):
        query = 'SELECT create_at FROM history'
        return [i[0] + '_back' for i in self.execute_query(query)]

    def get_len_all_users(self):
        query = 'SELECT COUNT(*) FROM users'
        return self.execute_query(query)[0][0]

    def get_all_users(self):
        query = 'SELECT * FROM users'
        return self.execute_query(query)

    def get_olivia_energy(self):
        query = 'SELECT energy FROM olivia'
        result = self.execute_query(query)[0][0]
        return int(result)

    def get_language(self, tg_user: CallbackQuery or Message):
        if isinstance(tg_user, Update):
            tg_user = tg_user.message
        query = 'SELECT language FROM users WHERE user_id = %s'
        result = self.execute_query(query, (tg_user.from_user.id,))
        if not result:
            return None
        return result[0][0]

    def get_opened_cards(self, tg_user: CallbackQuery or Message):
        query = "SELECT COUNT(*) FROM history WHERE user_id = %s"
        result = self.execute_query(query, (tg_user.from_user.id,))[0][0]
        return result

    def get_days_with_olivia(self, tg_user: CallbackQuery or Message):
        query = 'SELECT join_at FROM users WHERE user_id = %s'
        join_at_date = self.execute_query(query, (tg_user.from_user.id,))[0][0]
        last_registration = datetime.strptime(join_at_date, "%Y-%m-%d %H:%M:%S.%f")
        current_date = datetime.now()
        time_difference = current_date - last_registration
        days = time_difference.days
        months = days // 30
        remaining_days = days % 30
        result = f"{months} месяцев, {remaining_days} дней"
        return result

    def get_name(self, tg_user: CallbackQuery or Message):
        query = 'SELECT name FROM users WHERE user_id = %s'
        result = self.execute_query(query, (tg_user.from_user.id,))
        if not result:
            return None
        return result[0][0]

    def minus_energy(self):
        query = 'UPDATE olivia SET energy = energy - 1'
        self.execute_update(query)

    def plus_energy(self):
        query = 'UPDATE olivia SET energy = energy + 1'
        self.execute_update(query)

    def get_all_history(self):
        query = 'SELECT COUNT(*) FROM history'
        return self.execute_query(query)[0][0]

    def change_last_attempt(self, tg_user: CallbackQuery or Message):
        time = datetime.now()
        query = 'UPDATE users SET last_attempt = %s WHERE user_id = %s'
        self.execute_update(query, (time, tg_user.from_user.id))

    def change_user_subscription(self, tg_user: CallbackQuery or Message, subscription: str):
        if isinstance(tg_user, Message) or isinstance(tg_user, CallbackQuery):
            tg_user = tg_user.from_user.id
        query = 'UPDATE users SET subscription = %s WHERE user_id = %s'
        self.execute_update(query, (subscription, tg_user))

    def change_user_subscription_expired(self, user_id: int, subscription_expired):
        query = 'UPDATE users SET subscription_expired = %s WHERE user_id = %s'
        self.execute_update(query, (subscription_expired, user_id))

    def set_subscription_expiration(self, tg_user: CallbackQuery or Message):
        query = 'UPDATE users SET subscription_expired = %s WHERE user_id = %s'
        self.execute_update(query, (datetime.now() + relativedelta(months=1), tg_user.from_user.id))

    def add_thanks(self, message_id):
        query = 'UPDATE history SET thanks = True WHERE message_id = %s'
        self.execute_update(query, (message_id,))

    def get_all_thanks(self):
        query = "SELECT thanks FROM history"
        list_thanks = self.execute_query(query)
        values = [x[0] for x in list_thanks]
        return values.count(True)

    def get_active_users_for_today(self):
        twenty_four_hours_ago = datetime.now() - timedelta(days=1)
        twenty_four_hours_ago_iso = twenty_four_hours_ago.strftime('%Y-%m-%d %H:%M:%S')
        query = "SELECT COUNT(*) FROM users WHERE last_attempt > %s"
        return self.execute_query(query, (twenty_four_hours_ago_iso,))[0][0]

    def get_active_users_for_last_week(self):
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        query = "SELECT COUNT(*) FROM users WHERE DATE(last_attempt) BETWEEN %s AND %s"
        return self.execute_query(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))[0][0]

    def get_active_users_for_last_month(self):
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        query = "SELECT COUNT(*) FROM users WHERE DATE(last_attempt) BETWEEN %s AND %s"
        return self.execute_query(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))[0][0]

    def get_all_active_users(self):
        query = "SELECT COUNT(*) FROM users WHERE is_first_try = %s"
        return self.execute_query(query, (True,))[0][0]

    def load_data(self, days):
        query = """
        SELECT user_id, create_at
        FROM history
        WHERE create_at >= %s
        """
        date_n_days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        return pd.read_sql_query(query, self.conn, params=[date_n_days_ago])

    def get_retention_data(self, days):
        data = self.load_data(days)
        valid_user_count = count_valid_users(data)
        total_user_count = count_total_users(data)
        retention_rate = calculate_retention(valid_user_count, total_user_count)
        return {
            "valid_user_count": valid_user_count,
            "total_user_count": total_user_count,
            "retention_rate": retention_rate
        }

    def get_subscription(self, tg_user: CallbackQuery or Message):
        query = 'SELECT subscription FROM users WHERE user_id = %s'
        subscription = self.execute_query(query, (tg_user.from_user.id,))[0][0]
        return subscription

    def get_all_user_subscriptions(self):
        query = 'SELECT user_id, subscription FROM users'
        result = self.execute_query(query)
        return {row[0]: row[1] for row in result}

    def get_user_available_openings(self, tg_user: CallbackQuery or Message):
        query = 'SELECT available_openings FROM users WHERE user_id = %s'
        available_openings = self.execute_query(query, (tg_user.from_user.id,))[0][0]
        return available_openings

    def get_user_subscription_expiration(self, tg_user: CallbackQuery or Message) -> datetime:
        query = 'SELECT subscription_expired FROM users WHERE user_id = %s'
        expiration = self.execute_query(query, (tg_user.from_user.id,))[0][0]
        return expiration

    def get_users_subscription_expiration(self):
        query = 'SELECT user_id, subscription_expired FROM users'
        result = self.execute_query(query)
        return {row[0]: row[1] for row in result}


class Fortune(Database):
    def __init__(self):
        print(33)
        super().__init__()

    def create_fortune(self, tg_user: Message or CallbackQuery,
                       card_type: str,
                       answer: str,
                       type_fortune: str):
        query = """INSERT INTO fortune(user_id, first_name, card_type, answer, type_fortune, create_at)
        VALUES(%s,%s,%s,%s,%s,%s)"""
        self.execute_update(query, (
            tg_user.from_user.id, tg_user.from_user.first_name, card_type, answer, type_fortune, datetime.now()))

    def add_history(self, tg_user: Message or CallbackQuery,
                    card: str,
                    text: str,
                    user_q: str,
                    message_id: int,
                    full_text: str):
        query = '''INSERT INTO history(user_id, card, text, create_at, user_q, reaction, message_id, thanks, 
                             full_text) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        self.execute_update(query, (
            tg_user.from_user.id, card, text, datetime.now(), user_q, None, message_id, False, full_text))

    def get_full_text_on_message_id(self, message_id: int):
        query = 'SELECT full_text FROM history WHERE message_id = %s'
        return self.execute_query(query, (message_id,))[0]

    def get_history(self, tg_user: Message or CallbackQuery):
        query = 'SELECT * FROM history WHERE user_id = %s ORDER BY create_at DESC'
        return self.execute_query(query, (tg_user.from_user.id,))[0]

    def check_session(self, tg_user: Message or CallbackQuery):
        query = 'SELECT create_at FROM fortune WHERE user_id = %s ORDER BY create_at DESC LIMIT 1'
        data = self.execute_query(query, (tg_user.from_user.id,))[0][0]
        return self.convert_time(data)

    def check_first_try(self, tg_user: Message or CallbackQuery):
        query = 'UPDATE users SET is_first_try = True WHERE user_id = %s'
        self.execute_update(query, (tg_user.from_user.id,))

    def is_first_try(self, tg_user: Message or CallbackQuery):
        query = 'SELECT is_first_try FROM users WHERE user_id = %s'
        return self.execute_query(query, (tg_user.from_user.id,))[0][0]

    def change_reaction(self, reaction, message_id):
        query = 'UPDATE history SET reaction = %s WHERE message_id = %s'
        self.execute_update(query, (reaction, message_id))


class Wisdom(Database):
    def __init__(self):
        print(44)
        super().__init__()

    def add_wisdom(self, tg_user: Message or CallbackQuery, msg: str):
        tg_user = tg_user.from_user
        query = "INSERT INTO wisdom(user_id, first_name, message, create_at) VALUES(%s,%s,%s,%s)"
        self.execute_update(query, (tg_user.id, tg_user.first_name, msg, datetime.now()))


class Decks(Database):
    def __init__(self):
        super().__init__()

    def update_reverse(self, lang: str, reverse: bool, text: str):
        reverse = not reverse
        query = "UPDATE decks SET reversed = %s WHERE {} = %s".format(lang)
        self.execute_update(query, (reverse, text))

    def get_reversed(self, lang: str, card_name: str) -> bool:
        query = 'SELECT reversed FROM decks WHERE {} = %s'.format(lang)
        result = self.execute_query(query, (card_name,))[0][0]
        return bool(int(result))

    def reset_all_cards(self):
        query = 'UPDATE decks SET reversed = 0'
        self.execute_update(query)

    def is_more_than_30_cards_flipped(self):
        query = 'SELECT COUNT(*) FROM decks WHERE reversed = 1'
        count = self.execute_query(query)[0][0]
        return count > 30


class Web3(Database):
    def __init__(self):
        print(55)
        super().__init__()

    def create_unique_address(self, blockchain, address, user_id):
        if not self.__is_user_in_database(user_id):
            self._create_user_row(user_id)
            query = "UPDATE web3_addresses SET {} = %s WHERE user_id = %s".format(blockchain)
            self.execute_update(query, (address, user_id))

    def __is_user_in_database(self, user_id):
        query = "SELECT * FROM web3_addresses WHERE user_id = %s"
        result = self.execute_query(query, (user_id,))
        return bool(result)

    def _create_user_row(self, user_id):
        query = '''
            INSERT INTO web3_addresses (user_id, bitcoin, ethereum, ripple)
            VALUES (%s, %s, %s, %s)
            '''
        self.execute_update(query, (user_id, '', '', ''))

    def get_blockchain_address(self, blockchain, user_id):
        if self.is_user_addresses_exists(blockchain, user_id):
            query = 'SELECT {} FROM web3_addresses WHERE user_id = %s'.format(blockchain)
            result_query = self.execute_query(query, (user_id,))[0]
            return result_query
        return None

    def is_user_addresses_exists(self, blockchain, user_id):
        if blockchain not in ['bitcoin', 'ethereum', 'ripple']:
            raise "Not correct blockchain, choice from - bitcoin, ethereum, ripple"

        query = 'SELECT {} FROM web3_addresses WHERE user_id = %s'.format(blockchain)
        try:
            result_query = self.execute_query(query, (user_id,))[0]
        except TypeError:
            return False
        return bool(result_query)


class Temp(Database):
    def __init__(self):
        print(66)
        super().__init__()

    def is_birth_exist(self, user_id):
        query = "SELECT birth_request_sent FROM temp_data WHERE user_id = %s"
        user = self.execute_query(query, (user_id,))[0]
        return bool(user)

    def check_entry(self, user_id, value=True):
        if self.is_birth_exist(user_id):
            query = 'UPDATE temp_data SET birth_request_sent = %s WHERE user_id = %s'
            self.execute_update(query, (True, user_id))
        else:
            query = 'INSERT INTO temp_data(user_id, birth_request_sent) VALUES(%s,%s)'
            self.execute_update(query, (user_id, value))

    async def get_birth_status(self, user_id) -> Union[None, bool]:
        query = 'SELECT birth_request_sent FROM temp_data WHERE user_id = %s'
        result = self.execute_query(query, (user_id,))[0]
        if result is None:
            return None
        return result[0]
