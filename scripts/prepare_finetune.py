# scripts/prepare_finetune.py
# Converts labeling.csv → finetune.jsonl for Unsloth/QLoRA
# Format: instruction + input (chunk) → output (JSON list of artists)

import csv
import json
from collections import defaultdict

INPUT_CSV = "data/labeling.csv"
OUTPUT_JSONL = "data/finetune.jsonl"

SYSTEM_PROMPT = (
    "You extract musicians and bands that directly inspired the creation of an album. "
    "Only include artists explicitly stated as influences in the text. "
    "Return a JSON array only: [{\"artist\": \"...\"}]"
)

def build_dataset():
    # Group by (source_id, chunk_text) → list of correct artists
    chunks = defaultdict(lambda: {"album": "", "chunk_text": "", "artists": []})

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["source_id"], row["context"])
            chunks[key]["album"] = f"{row['album_artist']} - {row['album_title']}"
            chunks[key]["chunk_text"] = row["context"]
            if row["correct"] == "1":
                chunks[key]["artists"].append({"artist": row["extracted_artist"]})

    examples = []
    for (source_id, _), data in chunks.items():
        if not data["chunk_text"].strip():
            continue
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": data["chunk_text"]},
                {"role": "assistant", "content": json.dumps(data["artists"], ensure_ascii=False)}
            ]
        })

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"Generated {len(examples)} training examples → {OUTPUT_JSONL}")

if __name__ == "__main__":
    build_dataset()
