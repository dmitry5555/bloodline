# scripts/step2_extract.py
import json
from datetime import datetime, timezone
import ollama
from db import get_connection

OLLAMA_HOST = "http://192.168.1.42:11434"
MODEL = "qwen2.5:7b"
PROMPT_VERSION = "v2"

client = ollama.Client(host=OLLAMA_HOST)

def extract_influences(wiki_text, artist):
    chunk_size = 8000
    paragraphs = wiki_text.split("\n\n")
    chunks = []
    current = []
    current_len = 0
    for para in paragraphs:
        if current_len + len(para) > chunk_size and current:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para)
    if current:
        chunks.append("\n\n".join(current))

    all_influences = []
    seen_artists = set()

    for i, chunk in enumerate(chunks):
        prompt = f"""Read this text and extract ONLY artists explicitly mentioned as musical inspirations or influences.
Do NOT include artists mentioned only as comparisons, collaborators, or critics.
Do NOT use your own knowledge. Only use what is written in the text below.
Do NOT include the artist "{artist}" themselves or their own previous albums.
Do NOT include artists who were influenced BY this album — only artists who influenced it.
Return only JSON array, no other text:
[{{"artist": "..."}}]

Text:
{chunk}"""

        response = client.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response["message"]["content"].strip()

        try:
            influences = json.loads(raw)
            if influences and isinstance(influences[0], list):
                influences = [{"artist": a} for sublist in influences for a in sublist]

            for inf in influences:
                if isinstance(inf, dict) and "artist" in inf:
                    artist_name = inf["artist"]
                    if isinstance(artist_name, dict):
                        artist_name = artist_name.get("artist") or artist_name.get("name")
                    if not isinstance(artist_name, str) or not artist_name:
                        continue
                    if artist_name not in seen_artists:
                        seen_artists.add(artist_name)
                        all_influences.append({"artist": artist_name})
                elif isinstance(inf, str):
                    if inf not in seen_artists:
                        seen_artists.add(inf)
                        all_influences.append({"artist": inf})
        except json.JSONDecodeError:
            print(f"  JSON parse error chunk {i}: {raw[:100]}")
            continue

    return all_influences

def get_entity_name(conn, entity_type, entity_id):
    if entity_type == "album":
        row = conn.execute("SELECT artist FROM albums WHERE id=?", (entity_id,)).fetchone()
        return row["artist"] if row else None
    elif entity_type == "artist":
        row = conn.execute("SELECT name FROM artists WHERE id=?", (entity_id,)).fetchone()
        return row["name"] if row else None
    return None


def process_unprocessed():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, entity_type, entity_id, raw_text FROM sources
        WHERE source_type = 'wikipedia'
          AND fetched = 1
          AND extracted = 0
          AND raw_text IS NOT NULL
    """).fetchall()
    conn.close()

    for row in rows:
        source_id, entity_type, entity_id, wiki_text = (
            row["id"], row["entity_type"], row["entity_id"], row["raw_text"]
        )

        conn = get_connection()
        name = get_entity_name(conn, entity_type, entity_id)
        conn.close()

        if not name:
            continue

        print(f"Processing {entity_type} '{name}' (source id={source_id})")
        influences = extract_influences(wiki_text, name)
        print(f"  Found: {[i['artist'] for i in influences]}")

        conn = get_connection()
        conn.execute("""
            UPDATE sources
            SET extracted_json = ?, extracted = 1, model = ?, prompt_version = ?
            WHERE id = ?
        """, (json.dumps(influences), MODEL, PROMPT_VERSION, source_id))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    process_unprocessed()
