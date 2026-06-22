"""
One-shot ingestion script for new SEBI and RBI circular zips.

Usage:
    python ingest_new_circulars.py

Runs from inside the FinancialRag/ directory.
Extracts zips, creates metadata, extracts text, chunks, rebuilds index.
"""

import glob
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT           = Path(__file__).resolve().parent
RAW_RBI        = ROOT / "data" / "raw" / "rbi"
RAW_SEBI       = ROOT / "data" / "raw" / "sebi"
PROC_RBI       = ROOT / "data" / "processed" / "rbi"
PROC_SEBI      = ROOT / "data" / "processed" / "sebi"
CHUNKS_RBI     = ROOT / "data" / "chunks" / "rbi"
CHUNKS_SEBI    = ROOT / "data" / "chunks" / "sebi"
INDEX_DIR      = ROOT / "data" / "vector_store"

SEBI_ZIP = Path(r"C:\Users\mohak\Downloads\sebi guidelines.zip")
RBI_ZIP  = Path(r"C:\Users\mohak\Downloads\rbi.zip")

for d in [RAW_RBI, RAW_SEBI, PROC_RBI, PROC_SEBI, CHUNKS_RBI, CHUNKS_SEBI]:
    d.mkdir(parents=True, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def long(p):
    s = str(Path(p).resolve())
    return ("\\\\?\\" + s) if (os.name == "nt" and not s.startswith("\\\\?\\")) else s


def parse_rbi_date(stem):
    """RBI_circular_2024_07_03_CRILC → 2024-07-03"""
    m = re.search(r"(\d{4})_(\d{2})_(\d{2})", stem)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "unknown"


def stem_clean(name):
    """Remove double .pdf suffix that some files have."""
    s = name
    while s.lower().endswith(".pdf"):
        s = s[:-4]
    return s


def make_rbi_meta(pdf_path: Path) -> dict:
    stem = stem_clean(pdf_path.name)
    date = parse_rbi_date(stem)
    topic = re.sub(r"RBI_(?:circular|master[_-]circular|master-circular)_\d{4}_\d{2}_\d{2}_?", "", stem, flags=re.I).replace("_", " ").strip()
    doc_type = "Master Circular" if "master" in stem.lower() else "Circular"
    return {
        "filename": pdf_path.name,
        "domain": "RBI",
        "document_type": doc_type,
        "circular_number": f"RBI/{stem}",
        "title": topic,
        "date": date,
        "source_url": "https://rbi.org.in/Scripts/NotificationUser.aspx",
        "downloaded_at": "2026-06-22",
        "trusted_official_source": True,
        "is_scanned": False,
        "is_english": True,
        "notes": "added via ingest_new_circulars.py",
    }


def make_sebi_meta(pdf_path: Path) -> dict:
    stem = stem_clean(pdf_path.name)
    # Try to pull a year
    m = re.search(r"\b(19|20)\d{2}\b", stem)
    year = m.group(0) if m else "unknown"
    date = f"{year}-01-01" if year != "unknown" else "unknown"
    doc_type = "Master Circular" if "master" in stem.lower() else "Guidelines" if "guideline" in stem.lower() else "Circular"
    return {
        "filename": pdf_path.name,
        "domain": "SEBI",
        "document_type": doc_type,
        "circular_number": f"SEBI/{stem[:60]}",
        "title": stem,
        "date": date,
        "source_url": "https://www.sebi.gov.in/legal/circulars.html",
        "downloaded_at": "2026-06-22",
        "trusted_official_source": True,
        "is_scanned": False,
        "notes": "added via ingest_new_circulars.py",
    }


# ── Step 1: Extract zips ───────────────────────────────────────────────────────
print("\n[1/5] Extracting zips...")

def extract_zip(zip_path: Path, target_dir: Path, domain: str):
    if not zip_path.exists():
        print(f"  ⚠  Zip not found: {zip_path}")
        return 0
    added = 0
    with zipfile.ZipFile(zip_path, "r") as z:
        for entry in z.infolist():
            name = entry.filename
            if entry.is_dir() or not name.lower().endswith(".pdf"):
                continue
            # flatten — drop any subfolder prefix
            flat_name = Path(name).name
            dest = target_dir / flat_name
            if dest.exists():
                print(f"  skip (exists): {flat_name}")
                continue
            with z.open(entry) as src, open(long(dest), "wb") as dst:
                shutil.copyfileobj(src, dst)
            print(f"  extracted: {flat_name}")
            added += 1
    return added

n_rbi  = extract_zip(RBI_ZIP,  RAW_RBI,  "RBI")
n_sebi = extract_zip(SEBI_ZIP, RAW_SEBI, "SEBI")
print(f"  RBI: {n_rbi} new files | SEBI: {n_sebi} new files")


# ── Step 2: Create metadata JSONs ──────────────────────────────────────────────
print("\n[2/5] Creating metadata JSON files...")

def create_meta(pdf_path: Path, meta_fn):
    json_path = pdf_path.with_suffix("").with_suffix(".json") if pdf_path.name.lower().endswith(".pdf.pdf") else pdf_path.with_suffix(".json")
    # handle double-extension filenames
    if not json_path.exists():
        # try stripping one extra .pdf
        alt = Path(str(pdf_path)[:-4] + ".json") if pdf_path.name.lower().endswith(".pdf.pdf") else None
        if alt and not alt.exists():
            json_path = alt
    if json_path.exists():
        return  # already has metadata
    meta = meta_fn(pdf_path)
    with open(long(json_path), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"  created meta: {json_path.name}")

for p in RAW_RBI.glob("*.pdf"):
    create_meta(p, make_rbi_meta)
for p in RAW_SEBI.glob("*.pdf"):
    create_meta(p, make_sebi_meta)


# ── Step 3: Text extraction (Phase 2) ─────────────────────────────────────────
print("\n[3/5] Extracting text from PDFs...")

try:
    import fitz
    USE_FITZ = True
except ImportError:
    USE_FITZ = False
    print("  PyMuPDF not available, falling back to pdfplumber")
    import pdfplumber

def extract_text(pdf_path: Path) -> str:
    if USE_FITZ:
        doc = fitz.open(long(pdf_path))
        text = "".join(page.get_text() for page in doc)
        doc.close()
    else:
        with pdfplumber.open(long(pdf_path)) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    return text.strip()


def process_domain(raw_dir: Path, proc_dir: Path, domain: str):
    for pdf_path in raw_dir.glob("*.pdf"):
        stem = stem_clean(pdf_path.name)
        out_path = proc_dir / f"processed_{stem}.json"
        if out_path.exists():
            print(f"  skip (exists): {out_path.name}")
            continue
        # find metadata json
        json_path = raw_dir / (stem + ".json")
        if not json_path.exists():
            # try exact name with .pdf replaced
            candidates = list(raw_dir.glob(stem + "*.json"))
            json_path = candidates[0] if candidates else None
        if not json_path or not json_path.exists():
            print(f"  ⚠  no metadata for {pdf_path.name}, skipping")
            continue
        try:
            with open(long(json_path), "r", encoding="utf-8") as f:
                meta = json.load(f)
            text = extract_text(pdf_path)
            if not text:
                print(f"  ⚠  empty text: {pdf_path.name}")
                continue
            with open(long(out_path), "w", encoding="utf-8") as f:
                json.dump({"metadata": meta, "content": text}, f, indent=2, ensure_ascii=False)
            print(f"  ✓  {pdf_path.name} → {out_path.name}")
        except Exception as e:
            print(f"  ✗  {pdf_path.name}: {e}")

process_domain(RAW_RBI,  PROC_RBI,  "RBI")
process_domain(RAW_SEBI, PROC_SEBI, "SEBI")


# ── Step 4: Chunking (Phase 3) ─────────────────────────────────────────────────
print("\n[4/5] Chunking documents...")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "], length_function=len,
    )
except ImportError:
    # Fallback simple splitter
    class splitter:
        @staticmethod
        def split_text(text):
            size, overlap = 1500, 200
            chunks, i = [], 0
            while i < len(text):
                chunks.append(text[i:i+size])
                i += size - overlap
            return chunks


def chunk_domain(proc_dir: Path, chunk_dir: Path, domain: str):
    for json_file in proc_dir.glob("*.json"):
        out_path = chunk_dir / f"chunks_{json_file.name}"
        if out_path.exists():
            print(f"  skip (exists): {out_path.name}")
            continue
        try:
            with open(long(json_file), "r", encoding="utf-8") as f:
                doc = json.load(f)
            text = doc.get("content", "")
            meta = doc.get("metadata", {})
            if not text:
                continue
            chunks = splitter.split_text(text)
            circ = meta.get("circular_number", "unknown")
            objects = [
                {"chunk_id": f"{domain}_{circ}_{i}", "text": c, "metadata": meta}
                for i, c in enumerate(chunks)
            ]
            with open(long(out_path), "w", encoding="utf-8") as f:
                json.dump(objects, f, indent=2, ensure_ascii=False)
            print(f"  ✓  {json_file.name} → {len(chunks)} chunks")
        except Exception as e:
            print(f"  ✗  {json_file.name}: {e}")

chunk_domain(PROC_RBI,  CHUNKS_RBI,  "rbi")
chunk_domain(PROC_SEBI, CHUNKS_SEBI, "sebi")


# ── Step 5: Rebuild index ──────────────────────────────────────────────────────
print("\n[5/5] Rebuilding vector index (this will take a few minutes)...")

import chromadb
from sentence_transformers import SentenceTransformer

INDEX_INFO_PATH = INDEX_DIR / "INDEX_INFO.json"
COLLECTION_NAME = "regulatory_chunks"
MODEL_NAME = "BAAI/bge-base-en-v1.5"

# Load existing model name if already indexed
if INDEX_INFO_PATH.exists():
    with open(long(INDEX_INFO_PATH), "r", encoding="utf-8") as f:
        existing_info = json.load(f)
    MODEL_NAME = existing_info.get("model_name", MODEL_NAME)

print(f"  Loading model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# Get or create collection — never delete existing data
INDEX_DIR.mkdir(parents=True, exist_ok=True)
client = chromadb.PersistentClient(path=str(INDEX_DIR))
try:
    collection = client.get_collection(COLLECTION_NAME)
    print(f"  Using existing collection ({collection.count()} chunks already indexed).")
except Exception:
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print("  Created new collection.")

# Find which chunk_ids are already in the index so we skip them
print("  Checking which chunks are already indexed...")
existing_ids = set()
try:
    all_existing = collection.get(include=[])
    existing_ids = set(all_existing["ids"])
    print(f"  {len(existing_ids)} chunks already in index, will skip those.")
except Exception:
    pass

# Load all chunks
all_chunks = []
pattern = str(ROOT / "data" / "chunks" / "**" / "chunks_*.json")
for path in glob.glob(pattern, recursive=True):
    try:
        with open(long(path), "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            if item.get("text", "").strip():
                all_chunks.append(item)
    except Exception as e:
        print(f"  ⚠  {path}: {e}")

print(f"  Total chunks to index: {len(all_chunks)}")

# Filter junk
MIN_CHARS = 80
def is_junk(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(text) < MIN_CHARS:
        return True
    if len(lines) <= 2 and all(len(l) < 60 for l in lines):
        return True
    return False

good_chunks = [c for c in all_chunks if not is_junk(c["text"])]
print(f"  After quality filter: {len(good_chunks)} chunks")

# Only embed chunks not already in the index
good_chunks = [c for c in good_chunks if c.get("chunk_id", "") not in existing_ids]
print(f"  New chunks to embed: {len(good_chunks)}")

# Embed and upsert in batches
BATCH = 64
try:
    from tqdm import tqdm
    batches = range(0, len(good_chunks), BATCH)
    progress = tqdm(batches, desc="  Embedding", unit="batch")
except ImportError:
    progress = range(0, len(good_chunks), BATCH)

for start in progress:
    batch = good_chunks[start:start + BATCH]
    texts = [QUERY_PREFIX + c["text"] for c in batch]
    ids   = [c.get("chunk_id", f"chunk_{start+i}") for i, c in enumerate(batch)]
    metas = []
    for c in batch:
        m = {k: (str(v) if not isinstance(v, (str, int, float, bool)) else v)
             for k, v in c.get("metadata", {}).items()}
        metas.append(m)
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()
    docs = [c["text"] for c in batch]
    collection.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)

# Save index info with updated total
final_count = collection.count()
info = {
    "model_name": MODEL_NAME,
    "collection_name": COLLECTION_NAME,
    "total_chunks": final_count,
}
with open(long(INDEX_INFO_PATH), "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2)

print(f"\nDone! {len(good_chunks)} new chunks added. Total in index: {final_count}.")
print("Restart the server (uvicorn app:app --host 127.0.0.1 --port 8000) to load the new index.")
