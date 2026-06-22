"""
Phase 4: Build the vector index.

Reads every chunks_*.json file under CHUNKS_DIR (recursively),
filters out low-quality chunks (TOC, near-empty),
embeds them with a local sentence-transformers model,
and writes a persistent Chroma collection to INDEX_DIR.

Run:
    pip install -r requirements.txt
    python build_index.py
"""

import json
import glob
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# ---------- Config ----------
CHUNKS_DIR = "data/chunks"         # where chunks_*.json files live
INDEX_DIR       = "data/vector_store"       # where the Chroma DB will be persisted
COLLECTION_NAME = "regulatory_chunks"

# bge-base = 768-dim, good quality, ~10-15 min CPU for 10k chunks
# bge-large = 1024-dim, better quality, needs GPU or patience
# all-MiniLM-L6-v2 = 384-dim, fastest, lower quality
MODEL_NAME      = "BAAI/bge-base-en-v1.5"

BATCH_SIZE      = 32
RESET_INDEX     = True   # Set False to add to an existing collection instead of rebuilding
# ----------------------------


def is_low_quality(text: str) -> bool:
    """Drop TOC chunks (mostly dotted leaders) and near-empty chunks."""
    t = text.strip()
    if len(t) < 50:
        return True
    # Table-of-contents pages are >40% dot characters
    if t.count(".") / max(len(t), 1) > 0.40:
        return True
    return False


def sanitize_metadata(meta: dict) -> dict:
    """Chroma metadata values must be str, int, float, bool, or None."""
    out = {}
    for k, v in meta.items():
        if v is None or isinstance(v, (str, int, float, bool)):
            out[k] = v if v is not None else ""
        else:
            out[k] = str(v)
    return out


def load_all_chunks(chunks_dir: str) -> list[dict]:
    """Walk chunks_dir and return every chunk from every chunks_*.json file."""
    pattern = os.path.join(chunks_dir, "**", "chunks_*.json")
    files = glob.glob(pattern, recursive=True)
    print(f"Found {len(files)} chunk files under {chunks_dir}")

    all_chunks = []
    dropped = 0
    seen_ids = set()
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        for c in chunks:
            if is_low_quality(c["text"]):
                dropped += 1
                continue
            if c["chunk_id"] in seen_ids:
                # Skip accidental duplicates rather than crashing Chroma
                continue
            seen_ids.add(c["chunk_id"])
            all_chunks.append(c)

    print(f"Loaded {len(all_chunks)} chunks (dropped {dropped} low-quality)")
    return all_chunks


def build_index():
    Path(INDEX_DIR).mkdir(parents=True, exist_ok=True)

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    dim = model.get_sentence_embedding_dimension()
    print(f"Embedding dimension: {dim}")

    client = chromadb.PersistentClient(path=INDEX_DIR)

    if RESET_INDEX:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},   # cosine works best with normalized embeddings
    )

    chunks = load_all_chunks(CHUNKS_DIR)
    if not chunks:
        print("No chunks found. Check CHUNKS_DIR path.")
        return

    # Embed and add in batches
    for i in tqdm(range(0, len(chunks), BATCH_SIZE), desc="Indexing"):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [c["text"] for c in batch]

        # BGE-v1.5 needs no prefix on passages (only on queries — see query_index.py)
        embeddings = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            normalize_embeddings=True,    # cosine + normalized = correct similarity
            show_progress_bar=False,
        )

        collection.add(
            ids=[c["chunk_id"] for c in batch],
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[sanitize_metadata(c["metadata"]) for c in batch],
        )

    # Write a small info file so future-you remembers what model was used
    info = {
        "model_name": MODEL_NAME,
        "embedding_dim": dim,
        "collection_name": COLLECTION_NAME,
        "total_indexed_chunks": len(chunks),
        "distance_metric": "cosine",
    }
    info_path = os.path.join(INDEX_DIR, "INDEX_INFO.json")
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)

    print(f"\nDone. Indexed {len(chunks)} chunks.")
    print(f"Vector store: {INDEX_DIR}")
    print(f"Index info:   {info_path}")
    print(f"\nNext step: run `python query_index.py` to smoke-test retrieval.")


if __name__ == "__main__":
    build_index()