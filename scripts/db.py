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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            wiki_page TEXT,
            wiki_text TEXT,
            influences_raw TEXT,
            processed INTEGER DEFAULT 0,
            depth INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_album_id INTEGER REFERENCES albums(id),
            source_artist_id INTEGER REFERENCES artists(id),
            target_artist_id INTEGER NOT NULL REFERENCES artists(id),
            UNIQUE(source_album_id, source_artist_id, target_artist_id)
        )
    """)
    conn.commit()
    conn.close()
    print("DB initialized")

if __name__ == "__main__":
    init_db()