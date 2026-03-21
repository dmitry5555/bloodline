# scripts/step3_build_graph.py
import json
from db import get_connection, init_db

MAX_DEPTH = 2


def get_or_create_artist(conn, name, depth):
    row = conn.execute("SELECT id FROM artists WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    conn.execute("INSERT INTO artists (name, depth) VALUES (?, ?)", (name, depth))
    conn.commit()
    return conn.execute("SELECT id FROM artists WHERE name = ?", (name,)).fetchone()["id"]


def add_edge(conn, source_album_id, source_artist_id, target_artist_id):
    conn.execute("""
        INSERT OR IGNORE INTO edges (source_album_id, source_artist_id, target_artist_id)
        VALUES (?, ?, ?)
    """, (source_album_id, source_artist_id, target_artist_id))
    conn.commit()


def build_graph():
    init_db()
    conn = get_connection()

    # рёбра из альбомов (depth=1)
    album_sources = conn.execute("""
        SELECT a.id, a.artist, a.title, s.extracted_json
        FROM albums a
        JOIN sources s ON s.entity_id = a.id
        WHERE s.entity_type = 'album'
          AND s.source_type = 'wikipedia'
          AND s.extracted = 1
          AND s.extracted_json IS NOT NULL
    """).fetchall()
    conn.close()

    for row in album_sources:
        album_id, artist, title, extracted_json = (
            row["id"], row["artist"], row["title"], row["extracted_json"]
        )
        print(f"Album: {artist} - {title}")

        try:
            influences = json.loads(extracted_json)
        except json.JSONDecodeError:
            continue

        for inf in influences:
            target_name = inf["artist"]
            conn = get_connection()
            target_id = get_or_create_artist(conn, target_name, depth=1)
            add_edge(conn, album_id, None, target_id)
            conn.close()

    # рёбра из артистов (depth=2)
    conn = get_connection()
    artist_sources = conn.execute("""
        SELECT a.id, a.name, a.depth, s.extracted_json
        FROM artists a
        JOIN sources s ON s.entity_id = a.id
        WHERE s.entity_type = 'artist'
          AND s.source_type = 'wikipedia'
          AND s.extracted = 1
          AND s.extracted_json IS NOT NULL
          AND a.depth < ?
    """, (MAX_DEPTH,)).fetchall()
    conn.close()

    for row in artist_sources:
        artist_id, name, depth, extracted_json = (
            row["id"], row["name"], row["depth"], row["extracted_json"]
        )
        print(f"Artist: {name} (depth={depth})")

        try:
            influences = json.loads(extracted_json)
        except json.JSONDecodeError:
            continue

        for inf in influences:
            target_name = inf["artist"]
            conn = get_connection()
            target_id = get_or_create_artist(conn, target_name, depth=depth + 1)
            add_edge(conn, None, artist_id, target_id)
            conn.close()


if __name__ == "__main__":
    build_graph()
