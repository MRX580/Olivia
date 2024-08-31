import os
import mysql.connector
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class DatabaseManager:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        self.cursor = self.conn.cursor()

    def create_column(self, table_name, column_name, data_type, default_value=None):
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type}"
        if default_value is not None:
            query += f" DEFAULT {default_value}"
        self.cursor.execute(query)
        self.conn.commit()

    def get_columns(self, table_name):
        self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()


desired_columns = {
    "history": [
        ("reaction", "VARCHAR(255)", "'None'"),
        ("message_id", "INT", "0"),
        ("thanks", "BOOLEAN", "False"),
        ("full_text", "TEXT", "''")
    ],
    "users": [
        ("phone_number", "VARCHAR(255)", "'None'"),
        ("username", "VARCHAR(255)", "'None'"),
        ("natal_data", "TEXT", "'None'"),
        ("natal_city", "VARCHAR(255)", "'None'"),
        ("available_openings", "INT", "3"),
        ("subscription", "VARCHAR(50)", "'basic'"),
        ("subscription_expired", "DATETIME", "NULL")
    ],
    "web3_addresses": [
        ("bitcoin", "VARCHAR(255)", "NULL"),
        ("ethereum", "VARCHAR(255)", "NULL"),
        ("ripple", "VARCHAR(255)", "NULL")
    ]
}


class Migration:
    @staticmethod
    def check_migrations():
        db_manager = DatabaseManager()
        missing_migrations = []

        for table_name, columns in desired_columns.items():
            existing_columns = db_manager.get_columns(table_name)
            existing_column_names = [col[0] for col in existing_columns]
            for column in columns:
                column_name, _, _ = column
                if column_name not in existing_column_names:
                    missing_migrations.append((table_name, column_name))

        db_manager.close()
        return missing_migrations

    @staticmethod
    def is_perform_migrations() -> bool:
        missing_migrations = Migration.check_migrations()

        if missing_migrations:
            print("Необходимо выполнить миграции:")
            for migration in missing_migrations:
                table_name, column_name = migration
                print(f" - Добавить столбец {column_name} в таблицу {table_name}")
            return True
        else:
            print("Миграции не требуются.")
            return False

    @staticmethod
    def make_migrations():
        db_manager = DatabaseManager()

        for table_name, columns in desired_columns.items():
            existing_columns = db_manager.get_columns(table_name)
            existing_column_names = [col[0] for col in existing_columns]
            for column in columns:
                column_name, data_type, default_value = column
                if column_name not in existing_column_names:
                    db_manager.create_column(table_name, column_name, data_type, default_value)

        db_manager.close()


if __name__ == '__main__':
    if Migration.is_perform_migrations():
        Migration.make_migrations()
