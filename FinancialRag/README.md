# FinancialRag

A retrieval-augmented generation (RAG) system over Indian financial regulatory circulars from the **Reserve Bank of India (RBI)** and the **Securities and Exchange Board of India (SEBI)**. Ask natural-language questions and get source-grounded answers cited back to specific circulars.

## What's here

- **20 RBI circulars** (2015–2025) and **19 SEBI circulars** (2025–2026), processed from PDF into chunked JSON.
- A **Chroma vector index** of 5,954 chunks built with `BAAI/bge-base-en-v1.5` (768-dim embeddings, cosine).
- **Hybrid retrieval** combining semantic search and a built-in BM25 keyword scorer.
- A **FastAPI** backend with a static HTML/JS frontend.
- Optional **Hugging Face RBI enrichment** (assignment + lirus18) kept as a separate experimental index.

## Layout

```
FinancialRag/
├── app.py                         # FastAPI backend (Phase 7)
├── phase2.py                      # PDF -> processed JSON
├── phase3.py                      # processed JSON -> chunks
├── build_index_phase4.py          # chunks -> Chroma vector store
├── query_index_phase4.py          # CLI vector query
├── phase5_6_rag.py                # Hybrid retrieval + answer generation
├── hf_enrichment.py               # Optional HF RBI dataset enrichment
├── generate_rbi_json.py           # RBI metadata helper
├── requirements.txt
├── PHASE5_6_RUN_GUIDE.md          # Detailed run instructions
├── static/                        # Frontend (index.html, app.js, styles.css)
└── data/
    ├── raw/{rbi,sebi}/            # Source PDFs + per-doc metadata JSONs
    ├── processed/{rbi,sebi}/      # Cleaned text + metadata per document
    ├── chunks/{rbi,sebi}/         # Chunked text ready for embedding
    ├── vector_store/              # Chroma index (regulatory_chunks)
    ├── hf_experimental/           # Optional HF enrichment data
    └── vector_store_hf_experimental/
```

## Install

```powershell
python -m pip install -r requirements.txt
```

## Run the API + UI

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000

## CLI examples

Retrieval only (no LLM):
```powershell
python phase5_6_rag.py "What is the rating process for credit rating agencies?" --domain SEBI --no-llm
```

With local Ollama (free):
```powershell
python phase5_6_rag.py "Main rules for P2P lending platforms?" --domain RBI --provider ollama --ollama-model qwen2.5-coder:7b
```

With OpenAI:
```powershell
$env:OPENAI_API_KEY="your_key_here"
python phase5_6_rag.py "What does RBI say about P2P lending?" --domain RBI
```

Domain filters: `all`, `SEBI`, `RBI`, `IncomeTax` *(IncomeTax has no data ingested yet)*.

See [`PHASE5_6_RUN_GUIDE.md`](PHASE5_6_RUN_GUIDE.md) for full details, including the optional HF enrichment workflow.

## Rebuilding the index from scratch

```powershell
python phase2.py        # raw PDFs -> processed JSON
python phase3.py        # processed JSON -> chunks
python build_index_phase4.py
```

## Notes

- The `data/vector_store/chroma.sqlite3` file is checked in for one-clone-and-run convenience. It can always be rebuilt via the phase scripts.
- Chunk files (`data/chunks/`) carry full document metadata embedded per chunk, so retrieval and citations don't depend on the per-doc metadata JSONs in `data/raw/`.
