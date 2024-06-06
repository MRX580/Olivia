import os
import sqlite3


class DatabaseManager:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), db_file))
        self.cursor = self.conn.cursor()

    def create_column(self, table_name, column_name, data_type, default_value):
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type} {default_value}"
        self.cursor.execute(query)
        self.conn.commit()

    def get_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


desired_columns = {
    "history": [
        ("reaction", "TEXT", "DEFAULT 'None'"),
        ("message_id", "INT", "DEFAULT 0"),
        ("thanks", "BOOL", "DEFAULT False"),
        ("full_text", "TEXT", "DEFAULT ''")
    ],
    "users": [
        ("phone_number", "TEXT", "DEFAULT 'None'"),
        ("username", "TEXT", "DEFAULT 'None'"),
        ("natal_data", "TEXT", "DEFAULT 'None'"),
        ("natal_city", "TEXT", "DEFAULT 'None'")
    ],
    "web3_addresses": [
        ("bitcoin", "TEXT", "DEFAULT None"),
        ("ethereum", "TEXT", "DEFAULT None"),
        ("ripple", "TEXT", "DEFAULT None")
    ]
}


class Migration:
    @staticmethod
    def check_migrations():
        db_manager = DatabaseManager('utils/users.db')
        missing_migrations = []

        for table_name, columns in desired_columns.items():
            existing_columns = db_manager.get_columns(table_name)
            for column in columns:
                column_name, _, _ = column
                if not any(col[1] == column_name for col in existing_columns):
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

    @staticmethod
    def make_migrations():
        db_manager = DatabaseManager('utils/users.db')

        for table_name, columns in desired_columns.items():
            existing_columns = db_manager.get_columns(table_name)
            for column in columns:
                column_name, data_type, default_value = column
                if not any(col[1] == column_name for col in existing_columns):
                    db_manager.create_column(table_name, column_name, data_type, default_value)

        db_manager.close()


if __name__ == '__main__':
    Migration.make_migrations()