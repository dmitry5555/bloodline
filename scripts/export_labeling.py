# scripts/export_labeling.py
# Generates a CSV for manual labeling of extracted influences
import json
import csv
from db import get_connection

def export_for_labeling(output_path="data/labeling.csv"):
    conn = get_connection()

    rows = conn.execute("""
        SELECT s.id, s.raw_text, s.extracted_json, a.artist, a.title
        FROM sources s
        JOIN albums a ON a.id = s.entity_id
        WHERE s.entity_type = 'album'
          AND s.source_type = 'wikipedia'
          AND s.extracted = 1
          AND s.extracted_json IS NOT NULL
    """).fetchall()
    conn.close()

    records = []
    for row in rows:
        source_id = row["id"]
        artist = row["artist"]
        title = row["title"]
        raw_text = row["raw_text"]

        try:
            influences = json.loads(row["extracted_json"])
        except json.JSONDecodeError:
            continue

        # чанки из raw_text (те же параметры что в step2)
        chunk_size = 8000
        paragraphs = raw_text.split("\n\n")
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

        for inf in influences:
            inf_artist = inf.get("artist", "")
            if not inf_artist:
                continue

            # находим чанк где упоминается этот артист
            context = ""
            for chunk in chunks:
                if inf_artist.lower() in chunk.lower():
                    # берем 300 символов вокруг упоминания
                    idx = chunk.lower().find(inf_artist.lower())
                    start = max(0, idx - 150)
                    end = min(len(chunk), idx + 150)
                    context = chunk[start:end].replace("\n", " ").strip()
                    break

            records.append({
                "source_id": source_id,
                "album_artist": artist,
                "album_title": title,
                "extracted_artist": inf_artist,
                "context": context,
                "correct": ""  # 1 = yes, 0 = no
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_id", "album_artist", "album_title", "extracted_artist", "context", "correct"])
        writer.writeheader()
        writer.writerows(records)

    print(f"Exported {len(records)} rows to {output_path}")

if __name__ == "__main__":
    export_for_labeling()
