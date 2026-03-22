# scripts/step1_collect.py
from datetime import datetime, timezone
import pandas as pd
from db import get_connection, init_db
from wiki import fetch_wiki_text


def save_source(conn, entity_type, entity_id, wiki_page, wiki_text):
    conn.execute("""
        INSERT OR IGNORE INTO sources
            (entity_type, entity_id, source_type, url, raw_text, fetched_at, fetched)
        VALUES (?, ?, 'wikipedia', ?, ?, ?, 1)
    """, (entity_type, entity_id, wiki_page, wiki_text, datetime.now(timezone.utc).isoformat()))
    conn.commit()


def collect_album(artist, title, year, genres, descriptors):
    conn = get_connection()

    # пропускаем если уже собрано
    existing = conn.execute("""
        SELECT s.id FROM sources s
        JOIN albums a ON a.id = s.entity_id
        WHERE a.artist = ? AND a.title = ?
          AND s.entity_type = 'album' AND s.source_type = 'wikipedia'
          AND s.fetched = 1
    """, (artist, title)).fetchone()
    conn.close()

    if existing:
        print(f"  Skip (already fetched): {artist} - {title}")
        return

    print(f"  Fetching: {artist} - {title}")
    wiki_page, wiki_text = fetch_wiki_text(f"{artist} {title} album")
    if not wiki_text:
        print(f"  Not found: {artist} - {title}")
        return

    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO albums (artist, title, year, genres, descriptors)
        VALUES (?, ?, ?, ?, ?)
    """, (artist, title, year, genres, descriptors))
    conn.commit()

    album = conn.execute(
        "SELECT id FROM albums WHERE artist = ? AND title = ?", (artist, title)
    ).fetchone()
    save_source(conn, "album", album["id"], wiki_page, wiki_text)
    conn.close()


def collect_artists():
    """Качает Wikipedia для артистов которые добавил step3 но ещё не fetched."""
    conn = get_connection()
    artists = conn.execute("""
        SELECT a.id, a.name FROM artists a
        WHERE a.fetched = 0
    """).fetchall()
    conn.close()

    for row in artists:
        artist_id, name = row["id"], row["name"]
        print(f"  Fetching artist: {name}")
        wiki_page, wiki_text = fetch_wiki_text(f"{name} musician")

        conn = get_connection()
        if not wiki_text:
            print(f"  Not found: {name}")
            conn.execute("UPDATE artists SET fetched=1 WHERE id=?", (artist_id,))
            conn.commit()
            conn.close()
            continue

        conn.execute("""
            INSERT OR IGNORE INTO sources
                (entity_type, entity_id, source_type, url, raw_text, fetched_at, fetched)
            VALUES ('artist', ?, 'wikipedia', ?, ?, ?, 1)
        """, (artist_id, wiki_page, wiki_text, datetime.now(timezone.utc).isoformat()))
        conn.execute("UPDATE artists SET fetched=1 WHERE id=?", (artist_id,))
        conn.commit()
        conn.close()


SEED_ALBUMS = [
    ("George Michael", "Older", "1996", "Pop", ""),
    ("Boards of Canada", "Geogaddi", "2002", "Electronic", ""),
    ("Portishead", "Dummy", "1994", "Trip Hop", ""),
    ("Nick Drake", "Pink Moon", "1972", "Folk", ""),
    ("Kraftwerk", "Trans-Europe Express", "1977", "Electronic", ""),
]

def load_rym_albums():
    df = pd.read_csv("source/rym_clean1.csv")
    rows = []
    for _, row in df.iterrows():
        rows.append((
            row["artist_name"],
            row["release_name"],
            str(row["release_date"])[:4],
            row["primary_genres"],
            row["descriptors"]
        ))
    return rows


if __name__ == "__main__":
    init_db()
    for artist, title, year, genres, descriptors in SEED_ALBUMS:
        collect_album(artist, title, year, genres, descriptors)
    for artist, title, year, genres, descriptors in load_rym_albums():
        collect_album(artist, title, year, genres, descriptors)
    collect_artists()
