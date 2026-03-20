# scripts/step1_collect.py
import requests
import time
import pandas as pd
from db import get_connection, init_db

HEADERS = {
    "User-Agent": "Bloodline/1.0 (music influence research project)"
}

def fetch_wiki_text(artist, album):
    search_url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{artist} {album} album",
        "format": "json"
    }
    response = requests.get(search_url, params=params, headers=HEADERS)
    data = response.json()
    
    if not data["query"]["search"]:
        print(f"Not found: {artist} - {album}")
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

def save_album(artist, album, year, genres, descriptors, wiki_page, wiki_text):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO albums 
            (artist, album, year, genres, descriptors, wiki_page, wiki_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (artist, album, year, genres, descriptors, wiki_page, wiki_text))
        conn.commit()
        print(f"Saved: {artist} - {album}")
    except Exception as e:
        print(f"Error saving {artist} - {album}: {e}")
    finally:
        conn.close()

def collect(artist, album, year, genres, descriptors):
    page_title, text = fetch_wiki_text(artist, album)
    if text:
        save_album(artist, album, year, genres, descriptors, page_title, text)
    time.sleep(1)

def load_rym_albums(limit=2):
    df = pd.read_csv("source/rym_clean1.csv")
    rows = []
    for _, row in df.head(limit).iterrows():
        rows.append((
            row["artist_name"],
            row["release_name"],
            str(row["release_date"])[:4],  # только год
            row["primary_genres"],
            row["descriptors"]
        ))
    return rows

if __name__ == "__main__":
    init_db()
    albums = load_rym_albums(limit=10)
    for artist, album, year, genres, descriptors in albums:
        print(f"Processing: {artist} - {album}")
        collect(artist, album, year, genres, descriptors)