import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data/bloodline.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            year INTEGER,
            genres TEXT,
            descriptors TEXT,
            wiki_page TEXT,
            wiki_text TEXT,
            influences_raw TEXT,
            processed INTEGER DEFAULT 0,
            UNIQUE(artist, album)
        )
    """)
    conn.commit()
    conn.close()
    print("DB initialized")

if __name__ == "__main__":
    init_db()