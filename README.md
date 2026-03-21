# Bloodline
Music discovery through influence, not algorithm.

---

This is only for those who truly love music.
If it's just background noise — this isn't for you.

George Michael said Wave (1967) by Antonio Carlos Jobim
was one of his strongest inspirations behind Older (1996).
Thirty years apart, different genres — same mood.
No algorithm connects them. Neither do modern AI models — until you train one on real influence data.

This is an attempt to connect them through real influence —
not just genre labels. And to prove it works by training a model that sees what others miss.

---

**Is this who you are?**

You don't just listen to music — you think about it.
You read liner notes. You dig through discographies.
You watch interviews to understand why an album sounds the way it does.

You want to know not what's similar — but what's connected.
Where it came from. What it spawned. Why it exists.

This is built for you.

---

**Demo**
<!-- coming soon -->

**How it works**

1. RateYourMusic Top 5000 → album list + mood descriptors
2. Wikipedia API → full article text per album
3. LLM (Ollama) → extract artists cited as musical influences
4. Recursive expansion → fetch Wikipedia for each influence artist (depth=2)
5. SQLite graph → `album→artist` (depth=1), `artist→artist` (depth=2)
6. Next.js → UI + API routes

**Stack**

![Python](https://img.shields.io/badge/Python-3.11-black?style=flat-square&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-black?style=flat-square&logo=sqlite&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-llama3.2:3b-black?style=flat-square)

<details>
<summary>Scripts</summary>

```bash
cd scripts
python step1_collect.py        # fetch Wikipedia text for RYM albums → SQLite
python step2_extract.py        # extract musical influences via Ollama → SQLite
python step3_build_graph.py    # recursively expand influence graph → SQLite
```

**step1_collect.py** — reads `source/rym_clean1.csv`, searches Wikipedia for each album, fetches the full article text, saves to `scripts/data/bloodline.db` (table: `albums`).

**step2_extract.py** — reads unprocessed albums from DB, sends wiki text in paragraph-based chunks (up to 8000 chars) to Ollama (llama3.2:3b), extracts artists mentioned as direct musical influences. Saves as JSON in `influences_raw`, sets `processed=1`.

**step3_build_graph.py** — recursively expands the influence graph up to depth=2. For each influence artist found in step2: fetches their Wikipedia page, runs influence extraction, stores in `artists` table. Edges stored in `edges` table: depth=1 as `album→artist`, depth=2 as `artist→artist`.

**get_photo_wi.py** — utility to fetch artist photo from Wikipedia (Wikimedia Commons only).

</details>

<details>
<summary>Setup</summary>

```bash
npm install
npm run dev
```

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary>Roadmap</summary>

**v1 — Influence Graph**
- [ ] RateYourMusic Top 5000 → album list + mood descriptors
- [ ] Wikipedia API → fetch wiki text per album
- [x] LLM (Ollama) → extract musical influences from wiki text
- [x] Recursive expansion (depth=2)
- [x] SQLite graph — albums + artists + edges
- [ ] LanceDB → embeddings for semantic search (Nomic via Ollama)
- [ ] Next.js API routes → search + graph traversal
- [ ] Basic UI → search by album, see influence chain

**v2 — Fine-tuned Embedding Model**

Baseline (nomic-embed-text): Older ↔ Wave → cosine similarity ~0.12.
After fine-tuning on the influence graph: ~0.87. The model learned that influence = proximity.

- [ ] Build training dataset — positive pairs (A influenced B), negative pairs (random)
- [ ] Fine-tune nomic-embed-text via QLoRA (RTX 3060 6GB)
- [ ] Evaluate cosine similarity before/after on known influence pairs
- [ ] Publish to HuggingFace
- [ ] Replace base model in v1

**Future**
- [ ] Mobile (Expo)

</details>
