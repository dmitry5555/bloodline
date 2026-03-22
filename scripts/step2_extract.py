# scripts/step2_extract.py
import json
from datetime import datetime, timezone
import ollama
from db import get_connection

OLLAMA_HOST = "http://192.168.1.42:11434"
MODEL = "qwen2.5:7b"
PROMPT_VERSION_ALBUM = "album_v5"
PROMPT_VERSION_ARTIST = "artist_v3"
SYSTEM_MESSAGE = "You are a music researcher. Output only valid JSON arrays, no markdown, no explanation."

client = ollama.Client(host=OLLAMA_HOST)

ALBUM_PROMPT = """Extract musicians and bands that directly inspired the creation of this album.

Examples of CORRECT influences:
- "Michael was inspired by the music of Antônio Carlos Jobim" → {{"artist": "Antônio Carlos Jobim"}}
- "The band cited Can and Kraftwerk as key influences" → {{"artist": "Can"}}, {{"artist": "Kraftwerk"}}

Examples of what to SKIP:
- "Gary Barlow's song kept them off #1" → skip (chart competitor)
- "The album inspired Adele and Lana Del Rey" → skip (they influenced others, not this album)
- "free jazz and musique concrète elements" → skip (genres/styles)
- "Meddle was referenced in interviews" → skip (album title, not artist)
- "Malcolm X's speeches influenced the lyrics" → skip (not a musician)
- "producer Jon Douglas shaped the sound" → skip (producer, not musical influence)

Only real musicians and bands. Only those who inspired THIS album.
Only use what is written in the text below. Do NOT use your own knowledge.
Do NOT include "{artist}" themselves or their own previous albums.
Return only JSON array, no other text:
[{{"artist": "..."}}]

Text:
{chunk}"""

ARTIST_PROMPT = """Extract musicians and bands that influenced {artist}'s music.
Only artists who inspired {artist} — not artists {artist} inspired or worked with.
Real musicians and bands only. No genres, no albums, no non-musicians.
Only use what is written in the text below.
Return JSON array: [{{"artist": "..."}}]

Text:
{chunk}"""


def extract_influences(wiki_text, artist, entity_type="album"):
    if entity_type == "artist":
        chunks = [wiki_text[:40000]]
    else:
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

    template = ALBUM_PROMPT if entity_type == "album" else ARTIST_PROMPT

    for i, chunk in enumerate(chunks):
        prompt = template.format(artist=artist, chunk=chunk)

        response = client.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ],
            options={"num_ctx": 16384}
        )

        raw = response["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

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
        row = conn.execute("SELECT artist, title FROM albums WHERE id=?", (entity_id,)).fetchone()
        return f"{row['artist']} - {row['title']}" if row else None
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

        prompt_version = PROMPT_VERSION_ALBUM if entity_type == "album" else PROMPT_VERSION_ARTIST
        print(f"Processing '{name}' (source id={source_id})")
        influences = extract_influences(wiki_text, name, entity_type)
        print(f"  Found: {[i['artist'] for i in influences]}")

        conn = get_connection()
        conn.execute("""
            UPDATE sources
            SET extracted_json = ?, extracted = 1, model = ?, prompt_version = ?
            WHERE id = ?
        """, (json.dumps(influences), MODEL, prompt_version, source_id))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    process_unprocessed()
