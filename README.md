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
1. Pitchfork Kaggle — source list of albums
2. Wikipedia API — fetch influences
3. Graph — build influence edges: (Older) → (Wave)
4. LanceDB — store graph + embeddings
5. Next.js — UI + API routes

## Stack
Next.js · LanceDB · Nomic · Ollama · NetworkX · Python

# Setup
```bash
npm install
npm run dev
```

# data collection (Python)
pip install -r requirements.txt
python scripts/collect_pitchfork.py
python scripts/collect_wikipedia.py
python scripts/build_graph.py

## Roadmap

### v1 — RAG + Influence Graph
- [ ] Pitchfork Kaggle dataset → album list
- [ ] Wikipedia API → fetch influences per album
- [ ] Build influence graph (NetworkX)
- [ ] LanceDB → store graph + text embeddings (Nomic via Ollama)
- [ ] Next.js API routes → search + graph traversal
- [ ] Basic UI → search by album/mood, see influence chain

### v2 — Fine-tuned Embedding Model
- [ ] Build training dataset from v1 graph (positive/negative pairs)
- [ ] Fine-tune nomic-embed-text via QLoRA (RTX 3060 6GB local)
- [ ] Evaluate: cosine similarity before/after
- [ ] Publish model to HuggingFace
- [ ] Replace Nomic base with fine-tuned model in v1

### Future
- [ ] Mobile (Expo)