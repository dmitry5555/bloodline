import sqlite3

conn = sqlite3.connect("data/pitchfork.sqlite")

# смотрим таблицы
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", tables)

# смотрим структуру
for table in tables:
    name = table[0]
    print(f"\n=== {name} ===")
    rows = conn.execute(f"SELECT * FROM {name} LIMIT 3").fetchall()
    for row in rows:
        print(row)

conn.close()