import sqlite3

conn = sqlite3.connect('utils/users.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(history)")
columns = cursor.fetchall()

desired_columns = [
    ("reaction", "TEXT", "DEFAULT 'None'"),
    ("message_id", "INT", "DEFAULT 0"),
    ("thanks", "BOOL", "DEFAULT False")
]

for column in desired_columns:
    column_name = column[0]
    if not any(col[1] == column_name for col in columns):
        query = f"ALTER TABLE history ADD COLUMN {column_name} {column[1]} {column[2]}"
        cursor.execute(query)
        conn.commit()


conn.close()