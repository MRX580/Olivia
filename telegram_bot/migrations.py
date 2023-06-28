import sqlite3

conn = sqlite3.connect('utils/users.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(history)")
columns = cursor.fetchall()

desired_columns = [
    ("history", "reaction", "TEXT", "DEFAULT 'None'"),
    ('history', "message_id", "INT", "DEFAULT 0"),
    ('history', "thanks", "BOOL", "DEFAULT False"),
    ('users', "phone_number", "TEXT", "DEFAULT 'None'"),
    ('users', "username", "TEXT", "DEFAULT 'None'")
]

for column in desired_columns:
    table_name = column[0]
    column_name = column[1]
    type_of_data = column[2]
    default_value = column[3]
    if not any(col[1] == column_name for col in columns):
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {type_of_data} {default_value}"
        cursor.execute(query)
        conn.commit()


conn.close()