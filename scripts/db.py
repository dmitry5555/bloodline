import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data/bloodline.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT NOT NULL,
            title TEXT NOT NULL,
            year INTEGER,
            genres TEXT,
            descriptors TEXT,
            cover_url TEXT,
            UNIQUE(artist, title)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            photo_url TEXT,
            depth INTEGER NOT NULL DEFAULT 1,
            fetched INTEGER DEFAULT 0,
            extracted INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            source_type TEXT NOT NULL,
            url TEXT,
            raw_text TEXT,
            extracted_json TEXT,
            fetched_at TEXT,
            model TEXT,
            prompt_version TEXT,
            fetched INTEGER DEFAULT 0,
            extracted INTEGER DEFAULT 0,
            UNIQUE(entity_type, entity_id, source_type)
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
