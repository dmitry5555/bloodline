# Bloodline
Music discovery through influence, not algorithm.

---

This is only for those who truly love music.
If it's just background noise — this isn't for you.

You found that album. You want more.
Not similar. Connected.

George Michael said Wave (1967) by Antonio Carlos Jobim
was one of his strongest inspirations behind Older (1996).
Thirty years apart, different genres — same mood.
No algorithm connects them. Neither do modern AI models.

This is an attempt to connect them through real influence —
not just genre labels.

---

## Demo
<!-- coming soon -->

## How it works
1. RateYourMusic Top 5000 — source list of albums + mood descriptors
2. Wikipedia API — fetch influences
3. Graph — build influence edges: (Older) → (Wave)
4. LanceDB — store graph + embeddings
5. Next.js — UI + API routes

## Stack
Next.js · LanceDB · Nomic · Ollama · NetworkX · Python

## Setup
```bash
npm install
npm run dev
```

# data collection (Python)
pip install -r requirements.txt
python scripts/collect_pitchfork.py
python scripts/collect_wikipedia.py
python scripts/build_graph.py

## Scripts

Data collection pipeline — run in order:

```bash
cd scripts
python step1_collect.py   # fetch Wikipedia text for albums from RYM CSV → SQLite
python step2_extract.py   # extract musical influences from wiki text via Ollama → SQLite
python step3_build_graph.py  # build influence graph from extracted data → LanceDB
```

**step1_collect.py** — reads `source/rym_clean1.csv`, searches Wikipedia for each album, fetches the full article text, and saves it to the local SQLite database (`scripts/data/bloodline.db`).

**step2_extract.py** — reads unprocessed albums from the database, sends wiki text in chunks to a local LLM (Ollama / llama3.2:3b), and extracts artists mentioned as direct musical influences. Saves results as JSON in `influences_raw`.

**step3_build_graph.py** — builds a directed influence graph from extracted data using NetworkX, then stores it alongside embeddings in LanceDB for search and traversal.

## Roadmap

### v1 — RAG + Influence Graph
- [ ] RateYourMusic dataset → album list + mood descriptors
- [ ] Wikipedia API → fetch influences per album
- [ ] Build influence graph (NetworkX)
- [ ] LanceDB → store graph + text embeddings (Nomic via Ollama)
- [ ] Next.js API routes → search + graph traversal
- [ ] Basic UI → search by album/mood, see influence chain

### v2 — Fine-tuned Embedding Model
- [ ] Build training dataset from v1 graph (positive/negative pairs)
- [ ] Fine-tune nomic-embed-text on RYM mood descriptors via QLoRA (RTX 3060 6GB local)
- [ ] Evaluate: cosine similarity before/after
- [ ] Publish model to HuggingFace
- [ ] Replace Nomic base with fine-tuned model in v1

### Future
- [ ] Mobile (Expo)