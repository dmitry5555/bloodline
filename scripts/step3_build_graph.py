# scripts/step3_build_graph.py
import json
import time
import requests
from db import get_connection, init_db
from step2_extract import extract_influences

HEADERS = {"User-Agent": "Bloodline/1.0 (music influence research project)"}
MAX_DEPTH = 2


def fetch_wiki_text_for_artist(artist_name):
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{artist_name} musician",
        "format": "json"
    }
    response = requests.get(search_url, params=params, headers=HEADERS)
    data = response.json()

    if not data["query"]["search"]:
        print(f"  Wikipedia not found: {artist_name}")
        return None, None

    page_title = data["query"]["search"][0]["title"]

    content_params = {
        "action": "query",
        "titles": page_title,
        "prop": "extracts",
        "explaintext": True,
        "format": "json"
    }
    content = requests.get(search_url, params=content_params, headers=HEADERS)
    pages = content.json()["query"]["pages"]
    text = list(pages.values())[0].get("extract", "")
    return page_title, text


def get_or_create_artist(conn, name, depth):
    row = conn.execute("SELECT id FROM artists WHERE name = ?", (name,)).fetchone()
    if row:
        return row[0]
    conn.execute(
        "INSERT INTO artists (name, depth) VALUES (?, ?)",
        (name, depth)
    )
    conn.commit()
    return conn.execute("SELECT id FROM artists WHERE name = ?", (name,)).fetchone()[0]


def add_edge(conn, source_album_id, source_artist_id, target_artist_id):
    try:
        conn.execute("""
            INSERT OR IGNORE INTO edges (source_album_id, source_artist_id, target_artist_id)
            VALUES (?, ?, ?)
        """, (source_album_id, source_artist_id, target_artist_id))
        conn.commit()
    except Exception as e:
        print(f"  Edge error: {e}")


def process_artist(artist_id, artist_name, depth):
    if depth > MAX_DEPTH:
        return

    conn = get_connection()
    already = conn.execute(
        "SELECT processed FROM artists WHERE id = ?", (artist_id,)
    ).fetchone()
    conn.close()

    if already and already[0] == 1:
        return

    print(f"  Fetching wiki for artist: {artist_name} (depth={depth})")
    wiki_page, wiki_text = fetch_wiki_text_for_artist(artist_name)
    time.sleep(1)

    if not wiki_text:
        conn = get_connection()
        conn.execute("UPDATE artists SET processed=1 WHERE id=?", (artist_id,))
        conn.commit()
        conn.close()
        return

    print(f"  Extracting influences for: {artist_name}")
    influences = extract_influences(wiki_text)
    print(f"  Found: {[i['artist'] for i in influences]}")

    conn = get_connection()
    conn.execute("""
        UPDATE artists SET wiki_page=?, wiki_text=?, influences_raw=?, processed=1
        WHERE id=?
    """, (wiki_page, wiki_text, json.dumps(influences), artist_id))
    conn.commit()

    for inf in influences:
        target_name = inf["artist"]
        target_id = get_or_create_artist(conn, target_name, depth + 1)
        add_edge(conn, None, artist_id, target_id)

    conn.close()

    if depth + 1 <= MAX_DEPTH:
        conn = get_connection()
        next_artists = conn.execute("""
            SELECT a.id, a.name FROM artists a
            JOIN edges e ON e.target_artist_id = a.id
            WHERE e.source_artist_id = ? AND a.processed = 0
        """, (artist_id,)).fetchall()
        conn.close()

        for next_id, next_name in next_artists:
            process_artist(next_id, next_name, depth + 1)


def build_graph():
    init_db()
    conn = get_connection()

    # Берём все обработанные альбомы с influences
    albums = conn.execute("""
        SELECT id, artist, album, influences_raw FROM albums
        WHERE processed = 1 AND influences_raw IS NOT NULL
    """).fetchall()
    conn.close()

    for album_id, artist, album, influences_raw in albums:
        print(f"\nAlbum: {artist} - {album}")
        try:
            influences = json.loads(influences_raw)
        except json.JSONDecodeError:
            continue

        for inf in influences:
            target_name = inf["artist"]
            conn = get_connection()
            target_id = get_or_create_artist(conn, target_name, depth=1)
            add_edge(conn, album_id, None, target_id)
            conn.close()

            process_artist(target_id, target_name, depth=1)


if __name__ == "__main__":
    build_graph()
