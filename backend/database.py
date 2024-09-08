import os
import mysql.connector

from datetime import datetime, date, timedelta
from dotenv import load_dotenv, find_dotenv
from aiogram.types import Message, CallbackQuery, Update
from dateutil.relativedelta import relativedelta

load_dotenv(find_dotenv())

class Database:
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

            )
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn = None

    def create_tables_if_not_exist(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS payments (
                payment_id VARCHAR(100) PRIMARY KEY,
                user_id BIGINT,
                payment_description VARCHAR(255),
                payment_name VARCHAR(255),
                payment_amount DECIMAL(10, 2),
                payment_currency VARCHAR(10),
                payment_status VARCHAR(50),
                created_at DATETIME,
                expires_at DATETIME,
                success_url TEXT,
                failure_url TEXT
            )
        """
        self.execute_update(create_table_query)

    def insert_payment(self, payment_id, user_id, description, name, amount, currency, status, created_at, expires_at,
                       success_url, failure_url):
        query = """
            INSERT INTO payments (
                payment_id, user_id, payment_description, payment_name, payment_amount, payment_currency, payment_status, created_at, expires_at, success_url, failure_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (payment_id, user_id, description, name, amount, currency, status, created_at, expires_at, success_url,
                  failure_url)
        self.execute_update(query, params)

    def update_payment_status(self, payment_id, status):
        """Метод для обновления статуса платежа."""
        query = """
            UPDATE payments
            SET payment_status = %s
            WHERE payment_id = %s
        """
        params = (status, payment_id)
        self.execute_update(query, params)

    def update_user_subscription(self, user_id, subscription):
        """Метод для обновления подписки пользователя."""
        query = """
            UPDATE users 
            SET subscription = %s
            WHERE user_id = %s
        """
        self.execute_update(query, (subscription, user_id))

    def update_user_savailable_openings(self, user_id, available_openings):
        """Метод для обновления подписки пользователя."""
        query = """
            UPDATE users 
            SET available_openings = %s
            WHERE user_id = %s
        """
        self.execute_update(query, (available_openings, user_id))

    def set_subscription_expiration(self, user_id: int):
        query = 'UPDATE users SET subscription_expired = %s WHERE user_id = %s'
        self.execute_update(query, (datetime.now() + relativedelta(months=1), user_id))


    def check_connection(self):
        if self.conn is None or not self.conn.is_connected():
            self.connect_to_db()

    def execute_query(self, query, params=None):
        self.check_connection()
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def execute_update(self, query, params=None):
        self.check_connection()
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            self.conn.commit()