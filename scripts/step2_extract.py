# scripts/step2_extract.py
import json
import ollama
from db import get_connection

def extract_influences(wiki_text):
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
Do NOT use your own knowledge. Only use what is written in the text below.
Do NOT include the artist themselves or their own previous albums.
Return only JSON array, no other text:
[{{"artist": "..."}}]

Text:
{chunk}"""

        response = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw = response["message"]["content"].strip()
        
        try:
            influences = json.loads(raw)
            if influences and isinstance(influences[0], list):
                influences = [{"artist": a} for sublist in influences for a in sublist]

            for inf in influences:
                if isinstance(inf, dict) and "artist" in inf:
                    artist = inf["artist"]
                    if isinstance(artist, dict):
                        artist = artist.get("artist") or artist.get("name")
                    if not isinstance(artist, str) or not artist:
                        continue
                    if artist not in seen_artists:
                        seen_artists.add(artist)
                        all_influences.append({"artist": artist})
                elif isinstance(inf, str):
                    if inf not in seen_artists:
                        seen_artists.add(inf)
                        all_influences.append({"artist": inf})
        except json.JSONDecodeError:
            print(f"JSON parse error chunk {i}: {raw[:100]}")
            continue
    
    return all_influences

def process_unprocessed():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, artist, album, wiki_text 
        FROM albums 
        WHERE processed = 0 AND wiki_text IS NOT NULL
    """).fetchall()
    conn.close()

    for row in rows:
        id, artist, album, wiki_text = row
        print(f"Processing: {artist} - {album}")
        
        influences = extract_influences(wiki_text)
        print(f"Found: {influences}")
        
        conn = get_connection()
        conn.execute("""
            UPDATE albums 
            SET influences_raw = ?, processed = 1
            WHERE id = ?
        """, (json.dumps(influences), id))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    process_unprocessed()