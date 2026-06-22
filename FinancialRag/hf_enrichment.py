"""
Safely add Hugging Face RBI QA datasets as an experimental retrieval source.

This does not modify the original Chroma vector store. It writes to:
    data/hf_experimental/raw
    data/hf_experimental/chunks
    data/vector_store_hf_experimental

Run:
    python hf_enrichment.py all --assignment-limit 2000 --lirus-limit 1710
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parent
HF_ROOT = PROJECT_ROOT / "data" / "hf_experimental"
RAW_DIR = HF_ROOT / "raw"
CHUNKS_DIR = HF_ROOT / "chunks"
INDEX_DIR = PROJECT_ROOT / "data" / "vector_store_hf_experimental"
COLLECTION_NAME = "rbi_hf_experimental"
MODEL_NAME = "BAAI/bge-base-en-v1.5"
BATCH_SIZE = 32
DATASETS_SERVER = "https://datasets-server.huggingface.co/rows"

DATASETS = {
    "assignment_rbi_notifications": {
        "dataset": "AISimplyExplained/Assignment_RBI_Notifications",
        "config": "default",
        "split": "train",
        "question_field": "input",
        "answer_field": "output",
    },
    "lirus18_rbi": {
        "dataset": "lirus18/rbi",
        "config": "default",
        "split": "train",
        "text_field": "text",
    },
}


def long_path(path: str | Path) -> str:
    resolved = str(Path(path).resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return "\\\\?\\" + resolved
    return resolved


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def fetch_rows(dataset_info: dict, limit: int, page_size: int = 100) -> list[dict]:
    rows = []
    offset = 0
    while len(rows) < limit:
        length = min(page_size, limit - len(rows))
        query = urllib.parse.urlencode(
            {
                "dataset": dataset_info["dataset"],
                "config": dataset_info["config"],
                "split": dataset_info["split"],
                "offset": offset,
                "length": length,
            }
        )
        url = f"{DATASETS_SERVER}?{query}"
        payload = None
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=60) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt == 4:
                    raise
                wait = 2 * (attempt + 1)
                print(f"HF server returned {exc.code}; retrying in {wait}s")
                time.sleep(wait)
            except urllib.error.URLError:
                if attempt == 4:
                    raise
                wait = 2 * (attempt + 1)
                print(f"HF request failed; retrying in {wait}s")
                time.sleep(wait)
        batch = [row["row"] for row in payload.get("rows", [])]
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        time.sleep(0.2)
    return rows


def parse_lirus_text(text: str) -> tuple[str, str]:
    match = re.search(r"\[INST\](.*?)\[/INST\](.*?)(?:</s>)?$", text, flags=re.DOTALL)
    if not match:
        return text.strip(), ""
    question = re.sub(r"\s+", " ", match.group(1)).strip()
    answer = re.sub(r"\s+", " ", match.group(2)).strip()
    return question, answer


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(long_path(path), "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def fetch_command(args: argparse.Namespace) -> None:
    ensure_dirs()
    limits = {
        "assignment_rbi_notifications": args.assignment_limit,
        "lirus18_rbi": args.lirus_limit,
    }
    for name, limit in limits.items():
        if limit <= 0:
            continue
        info = DATASETS[name]
        print(f"Fetching {limit} rows from {info['dataset']}")
        rows = fetch_rows(info, limit=limit)
        write_jsonl(RAW_DIR / f"{name}.jsonl", rows)
        print(f"Wrote {len(rows)} rows to {RAW_DIR / f'{name}.jsonl'}")


def row_to_chunk(dataset_name: str, row_index: int, row: dict) -> dict | None:
    info = DATASETS[dataset_name]
    if dataset_name == "lirus18_rbi":
        question, answer = parse_lirus_text(str(row.get(info["text_field"], "")))
    else:
        question = str(row.get(info["question_field"], "")).strip()
        answer = str(row.get(info["answer_field"], "")).strip()

    if len(question) < 8 or len(answer) < 2:
        return None

    text = f"Question: {question}\nAnswer: {answer}"
    chunk_id = f"hf_{dataset_name}_{row_index}"
    return {
        "chunk_id": chunk_id,
        "text": text,
        "metadata": {
            "domain": "RBI",
            "source_type": "huggingface_dataset_qa",
            "trusted_official_source": False,
            "dataset_name": info["dataset"],
            "source_url": f"https://huggingface.co/datasets/{info['dataset']}",
            "circular_number": f"HF QA row {row_index}",
            "date": "",
            "row_index": row_index,
            "question": question[:500],
        },
    }


def chunks_command(_: argparse.Namespace) -> None:
    ensure_dirs()
    total = 0
    for raw_file in RAW_DIR.glob("*.jsonl"):
        dataset_name = raw_file.stem
        chunks = []
        with open(long_path(raw_file), "r", encoding="utf-8") as f:
            for row_index, line in enumerate(f):
                row = json.loads(line)
                chunk = row_to_chunk(dataset_name, row_index, row)
                if chunk:
                    chunks.append(chunk)
        out_path = CHUNKS_DIR / f"chunks_{dataset_name}.json"
        with open(long_path(out_path), "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        total += len(chunks)
        print(f"Wrote {len(chunks)} chunks to {out_path}")
    print(f"Total HF experimental chunks: {total}")


def sanitize_metadata(metadata: dict) -> dict:
    clean = {}
    for key, value in metadata.items():
        if value is None:
            clean[key] = ""
        elif isinstance(value, (str, int, float, bool)):
            clean[key] = value
        else:
            clean[key] = str(value)
    return clean


def load_chunks() -> list[dict]:
    chunks = []
    for path in CHUNKS_DIR.glob("chunks_*.json"):
        with open(long_path(path), "r", encoding="utf-8") as f:
            chunks.extend(json.load(f))
    return chunks


def index_command(_: argparse.Namespace) -> None:
    ensure_dirs()
    chunks = load_chunks()
    if not chunks:
        raise SystemExit("No HF chunks found. Run `python hf_enrichment.py chunks` first.")

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    dim = model.get_sentence_embedding_dimension()

    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    for start in tqdm(range(0, len(chunks), BATCH_SIZE), desc="Indexing HF"):
        batch = chunks[start : start + BATCH_SIZE]
        embeddings = model.encode(
            [chunk["text"] for chunk in batch],
            batch_size=BATCH_SIZE,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        collection.add(
            ids=[chunk["chunk_id"] for chunk in batch],
            embeddings=embeddings.tolist(),
            documents=[chunk["text"] for chunk in batch],
            metadatas=[sanitize_metadata(chunk["metadata"]) for chunk in batch],
        )

    info = {
        "model_name": MODEL_NAME,
        "embedding_dim": dim,
        "collection_name": COLLECTION_NAME,
        "total_indexed_chunks": len(chunks),
        "distance_metric": "cosine",
        "source_type": "huggingface_dataset_qa",
        "safe_mode": "separate_vector_store",
    }
    with open(long_path(INDEX_DIR / "INDEX_INFO.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    print(f"Indexed {len(chunks)} HF experimental chunks into {INDEX_DIR}")


def all_command(args: argparse.Namespace) -> None:
    fetch_command(args)
    chunks_command(args)
    index_command(args)


def main() -> None:
    parser = argparse.ArgumentParser(description="HF experimental RBI enrichment pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_limits(p: argparse.ArgumentParser) -> None:
        p.add_argument("--assignment-limit", type=int, default=2000)
        p.add_argument("--lirus-limit", type=int, default=1710)

    fetch_parser = subparsers.add_parser("fetch")
    add_limits(fetch_parser)
    fetch_parser.set_defaults(func=fetch_command)

    chunks_parser = subparsers.add_parser("chunks")
    chunks_parser.set_defaults(func=chunks_command)

    index_parser = subparsers.add_parser("index")
    index_parser.set_defaults(func=index_command)

    all_parser = subparsers.add_parser("all")
    add_limits(all_parser)
    all_parser.set_defaults(func=all_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
