"""
Phase 5 and 6: hybrid retrieval plus source-grounded answer generation.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Iterable


PROJECT_ROOT = Path(__file__).resolve().parent
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
INDEX_DIR = PROJECT_ROOT / "data" / "vector_store"
INDEX_INFO = INDEX_DIR / "INDEX_INFO.json"
HF_CHUNKS_DIR = PROJECT_ROOT / "data" / "hf_experimental" / "chunks"
HF_INDEX_DIR = PROJECT_ROOT / "data" / "vector_store_hf_experimental"
HF_INDEX_INFO = HF_INDEX_DIR / "INDEX_INFO.json"
COLLECTION_NAME = "regulatory_chunks"
HF_COLLECTION_NAME = "rbi_hf_experimental"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:7b"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
LANGUAGE_NAMES = {
    "english": "English",
    "hindi": "Hindi",
    "bengali": "Bengali",
    "gujarati": "Gujarati",
    "kannada": "Kannada",
    "malayalam": "Malayalam",
    "marathi": "Marathi",
    "odia": "Odia",
    "punjabi": "Punjabi",
    "tamil": "Tamil",
    "telugu": "Telugu",
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Module-level caches (loaded once, reused across all requests) ──────────────
_model_cache: dict = {}          # keyed by model_name
_chroma_client_cache: dict = {}  # keyed by index_dir path
_chunks_cache: dict = {}         # keyed by (domain, include_hf)


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    metadata: dict
    semantic_score: float = 0.0
    bm25_score: float = 0.0

    @property
    def source_key(self) -> str:
        circular = self.metadata.get("circular_number") or self.metadata.get("source") or self.chunk_id
        date = self.metadata.get("date") or ""
        return f"{circular}|{date}"

    @property
    def final_score(self) -> float:
        return 0.72 * self.semantic_score + 0.28 * self.bm25_score


def _long_path(path: str | Path) -> str:
    resolved = str(Path(path).resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return "\\\\?\\" + resolved
    return resolved


def normalize_domain(domain: str | None) -> str | None:
    if not domain or domain.lower() == "all":
        return None
    value = domain.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "sebi": "SEBI",
        "rbi": "RBI",
        "income_tax": "IncomeTax",
        "incometax": "IncomeTax",
        "it": "IncomeTax",
    }
    if value not in aliases:
        raise ValueError("domain must be one of: all, SEBI, RBI, IncomeTax")
    return aliases[value]


def load_index_config() -> dict:
    with open(_long_path(INDEX_INFO), "r", encoding="utf-8") as f:
        return json.load(f)


def load_hf_index_config() -> dict:
    with open(_long_path(HF_INDEX_INFO), "r", encoding="utf-8") as f:
        return json.load(f)


def _get_embedding_model(model_name: str):
    """Return a cached SentenceTransformer, loading it only on first call."""
    if model_name not in _model_cache:
        from sentence_transformers import SentenceTransformer
        _model_cache[model_name] = SentenceTransformer(model_name)
    return _model_cache[model_name]


def _get_chroma_client(index_dir: Path):
    """Return a cached ChromaDB client for the given index directory."""
    key = str(index_dir)
    if key not in _chroma_client_cache:
        import chromadb
        _chroma_client_cache[key] = chromadb.PersistentClient(path=str(index_dir))
    return _chroma_client_cache[key]


def load_semantic_dependencies():
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Semantic retrieval needs chromadb and sentence-transformers. "
            "Install them with: python -m pip install -r requirements.txt"
        ) from exc
    return chromadb, SentenceTransformer


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9./_-]*", text.lower())


def _load_chunks_from_disk(domain: str | None = None) -> list[RetrievedChunk]:
    pattern = str(CHUNKS_DIR / "**" / "chunks_*.json")
    chunks: list[RetrievedChunk] = []
    for path in glob.glob(pattern, recursive=True):
        with open(_long_path(path), "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            metadata = item.get("metadata", {})
            if domain and metadata.get("domain") != domain:
                continue
            chunks.append(
                RetrievedChunk(
                    chunk_id=item.get("chunk_id", ""),
                    text=item.get("text", ""),
                    metadata=metadata,
                )
            )
    return chunks


def load_chunks(domain: str | None = None) -> list[RetrievedChunk]:
    """Load chunks from cache; fall back to disk on first access."""
    key = domain or "all"
    if key not in _chunks_cache:
        _chunks_cache[key] = _load_chunks_from_disk(domain)
    return _chunks_cache[key]


def _load_hf_chunks_from_disk(domain: str | None = None) -> list[RetrievedChunk]:
    if domain and domain != "RBI":
        return []
    if not HF_CHUNKS_DIR.exists():
        return []
    chunks: list[RetrievedChunk] = []
    for path in glob.glob(str(HF_CHUNKS_DIR / "chunks_*.json")):
        with open(_long_path(path), "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            metadata = item.get("metadata", {})
            chunks.append(
                RetrievedChunk(
                    chunk_id=item.get("chunk_id", ""),
                    text=item.get("text", ""),
                    metadata=metadata,
                )
            )
    return chunks


def load_hf_chunks(domain: str | None = None) -> list[RetrievedChunk]:
    key = f"hf_{domain or 'all'}"
    if key not in _chunks_cache:
        _chunks_cache[key] = _load_hf_chunks_from_disk(domain)
    return _chunks_cache[key]


def warm_up_caches() -> None:
    """Pre-load the embedding model and chunk corpus at server startup."""
    if not INDEX_INFO.exists():
        return
    try:
        with open(_long_path(INDEX_INFO), "r", encoding="utf-8") as f:
            info = json.load(f)
        model_name = info["model_name"]
        print(f"[startup] Loading embedding model: {model_name}", flush=True)
        _get_embedding_model(model_name)
        print("[startup] Embedding model ready.", flush=True)

        print("[startup] Pre-loading chunk corpus...", flush=True)
        load_chunks(None)
        load_chunks("SEBI")
        load_chunks("RBI")
        print(f"[startup] Chunk corpus ready ({len(_chunks_cache)} domain slices).", flush=True)

        print("[startup] Connecting ChromaDB client...", flush=True)
        _get_chroma_client(INDEX_DIR)
        print("[startup] ChromaDB ready.", flush=True)
    except Exception as exc:
        print(f"[startup] warm_up_caches failed (non-fatal): {exc}", flush=True)


def bm25_search(query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
    query_terms = tokenize(query)
    if not query_terms or not chunks:
        return []

    documents = [tokenize(chunk.text) for chunk in chunks]
    doc_count = len(documents)
    avgdl = sum(len(doc) for doc in documents) / max(doc_count, 1)

    doc_freq: dict[str, int] = {}
    for doc in documents:
        for term in set(doc):
            doc_freq[term] = doc_freq.get(term, 0) + 1

    k1 = 1.5
    b = 0.75
    scored: list[tuple[float, RetrievedChunk]] = []
    for chunk, doc in zip(chunks, documents):
        if not doc:
            continue
        tf: dict[str, int] = {}
        for term in doc:
            tf[term] = tf.get(term, 0) + 1

        score = 0.0
        for term in query_terms:
            frequency = tf.get(term, 0)
            if frequency == 0:
                continue
            idf = math.log(1 + (doc_count - doc_freq.get(term, 0) + 0.5) / (doc_freq.get(term, 0) + 0.5))
            numerator = frequency * (k1 + 1)
            denominator = frequency + k1 * (1 - b + b * len(doc) / max(avgdl, 1))
            score += idf * numerator / denominator
        if score > 0:
            scored.append((score, chunk))

    if not scored:
        return []

    max_score = max(score for score, _ in scored)
    ranked = []
    for score, chunk in scored:
        ranked.append(
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                metadata=chunk.metadata,
                bm25_score=score / max_score,
            )
        )
    ranked.sort(key=lambda item: item.bm25_score, reverse=True)
    return ranked[:top_k]


def semantic_search(
    query: str,
    domain: str | None,
    top_k: int,
    index_dir: Path = INDEX_DIR,
    index_info: Path = INDEX_INFO,
    default_collection: str = COLLECTION_NAME,
) -> list[RetrievedChunk]:
    if not index_info.exists():
        return []
    with open(_long_path(index_info), "r", encoding="utf-8") as f:
        info = json.load(f)

    model = _get_embedding_model(info["model_name"])
    query_embedding = model.encode(QUERY_PREFIX + query, normalize_embeddings=True)

    client = _get_chroma_client(index_dir)
    collection = client.get_collection(info.get("collection_name", default_collection))
    kwargs = {
        "query_embeddings": [query_embedding.tolist()],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if domain:
        kwargs["where"] = {"domain": domain}
    results = collection.query(**kwargs)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results.get("ids", [[]])[0]

    chunks = []
    for index, (doc, meta, distance) in enumerate(zip(documents, metadatas, distances)):
        chunks.append(
            RetrievedChunk(
                chunk_id=ids[index] if index < len(ids) else f"semantic_{index}",
                text=doc,
                metadata=meta,
                semantic_score=max(0.0, 1.0 - float(distance)),
            )
        )
    return chunks


def merge_results(*result_sets: Iterable[RetrievedChunk], limit: int) -> list[RetrievedChunk]:
    merged: dict[str, RetrievedChunk] = {}
    for result_set in result_sets:
        for chunk in result_set:
            existing = merged.get(chunk.chunk_id)
            if existing is None:
                merged[chunk.chunk_id] = chunk
                continue
            existing.semantic_score = max(existing.semantic_score, chunk.semantic_score)
            existing.bm25_score = max(existing.bm25_score, chunk.bm25_score)
    return sorted(merged.values(), key=lambda item: item.final_score, reverse=True)[:limit]


def retrieve(
    query: str,
    domain: str | None = None,
    top_k: int = 8,
    include_hf_experimental: bool = False,
) -> list[RetrievedChunk]:
    normalized_domain = normalize_domain(domain)
    semantic = semantic_search(query, normalized_domain, top_k=max(top_k, 8))
    semantic_sets = [semantic]
    lexical_corpus = load_chunks(normalized_domain)

    if include_hf_experimental and normalized_domain in (None, "RBI"):
        hf_semantic = semantic_search(
            query,
            "RBI",
            top_k=max(top_k, 8),
            index_dir=HF_INDEX_DIR,
            index_info=HF_INDEX_INFO,
            default_collection=HF_COLLECTION_NAME,
        )
        semantic_sets.append(hf_semantic)
        lexical_corpus = list(lexical_corpus) + list(load_hf_chunks(normalized_domain))

    lexical = bm25_search(query, lexical_corpus, top_k=max(top_k, 8))
    return merge_results(*semantic_sets, lexical, limit=top_k)


def citation_label(chunk: RetrievedChunk, index: int) -> str:
    meta = chunk.metadata
    circular = meta.get("circular_number") or meta.get("title") or meta.get("source") or chunk.chunk_id
    date = meta.get("date") or "date not available"
    domain = meta.get("domain") or "Unknown"
    return f"[S{index}] {domain} | {circular} | {date}"


def build_context(chunks: list[RetrievedChunk], max_chars_per_chunk: int = 1800) -> str:
    sections = []
    for index, chunk in enumerate(chunks, 1):
        source_url = chunk.metadata.get("source_url") or chunk.metadata.get("url") or ""
        body = chunk.text.strip().replace("\r\n", "\n")
        if len(body) > max_chars_per_chunk:
            body = body[:max_chars_per_chunk].rsplit(" ", 1)[0] + "..."
        sections.append(
            "\n".join(
                [
                    citation_label(chunk, index),
                    f"URL: {source_url}" if source_url else "URL: not available",
                    body,
                ]
            )
        )
    return "\n\n---\n\n".join(sections)


def normalize_language(language: str | None) -> str:
    value = (language or "english").strip().lower()
    aliases = {
        "auto": "auto",
        "en": "english",
        "english": "english",
        "hi": "hindi",
        "hindi": "hindi",
        "bn": "bengali",
        "bengali": "bengali",
        "gu": "gujarati",
        "gujarati": "gujarati",
        "kn": "kannada",
        "kanada": "kannada",
        "kannada": "kannada",
        "ml": "malayalam",
        "malayalam": "malayalam",
        "mr": "marathi",
        "marathi": "marathi",
        "or": "odia",
        "odia": "odia",
        "oriya": "odia",
        "pa": "punjabi",
        "punjabi": "punjabi",
        "ta": "tamil",
        "tamil": "tamil",
        "te": "telugu",
        "telugu": "telugu",
    }
    if value not in aliases:
        raise ValueError(
            "language must be one of: auto, english, hindi, bengali, gujarati, "
            "kannada, malayalam, marathi, odia, punjabi, tamil, telugu"
        )
    return aliases[value]


def detect_question_language(question: str) -> str:
    bengali   = sum(1 for c in question if "ঀ" <= c <= "৿")
    devanagari = sum(1 for c in question if "ऀ" <= c <= "ॿ")
    gujarati  = sum(1 for c in question if "઀" <= c <= "૿")
    kannada   = sum(1 for c in question if "ಀ" <= c <= "೿")
    malayalam = sum(1 for c in question if "ഀ" <= c <= "ൿ")
    odia      = sum(1 for c in question if "଀" <= c <= "୿")
    punjabi   = sum(1 for c in question if "਀" <= c <= "੿")
    tamil     = sum(1 for c in question if "஀" <= c <= "௿")
    telugu    = sum(1 for c in question if "ఀ" <= c <= "౿")
    counts = {
        "bengali": bengali, "hindi": devanagari, "gujarati": gujarati,
        "kannada": kannada, "malayalam": malayalam, "odia": odia,
        "punjabi": punjabi, "tamil": tamil, "telugu": telugu,
    }
    language, count = max(counts.items(), key=lambda item: item[1])
    return language if count > 0 else "english"


def build_messages(
    question: str,
    chunks: list[RetrievedChunk],
    answer_language: str = "english",
) -> list[dict[str, str]]:
    language = LANGUAGE_NAMES[normalize_language(answer_language)]
    system = (
        "You are a regulatory intelligence assistant for Indian financial regulations. "
        "Answer only from the provided context. If the context is insufficient, say so. "
        "Always cite the source labels like [S1] and include the circular number and date "
        "when they are available. Keep the answer plain-language and practical. "
        f"Write the final answer in {language}."
    )
    user = (
        f"Question: {question}\n\n"
        "Context:\n"
        f"{build_context(chunks)}\n\n"
        f"Write the answer in {language} with a short source list at the end."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def generate_answer(
    question: str,
    chunks: list[RetrievedChunk],
    model: str = DEFAULT_LLM_MODEL,
    answer_language: str = "english",
) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("LLM generation needs openai. Install it with: python -m pip install openai") from exc

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=build_messages(question, chunks, answer_language),
        temperature=0.1,
    )
    return response.choices[0].message.content or ""


def generate_answer_stream_openai(
    question: str,
    chunks: list[RetrievedChunk],
    model: str = DEFAULT_LLM_MODEL,
    answer_language: str = "english",
) -> Generator[str, None, None]:
    from openai import OpenAI
    client = OpenAI()
    stream = client.chat.completions.create(
        model=model,
        messages=build_messages(question, chunks, answer_language),
        temperature=0.1,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def generate_ollama_answer(
    question: str,
    chunks: list[RetrievedChunk],
    model: str = DEFAULT_OLLAMA_MODEL,
    timeout: int = 600,
    answer_language: str = "english",
) -> str:
    return "".join(generate_ollama_answer_stream(question, chunks, model, timeout, answer_language))


def generate_ollama_answer_stream(
    question: str,
    chunks: list[RetrievedChunk],
    model: str = DEFAULT_OLLAMA_MODEL,
    timeout: int = 600,
    answer_language: str = "english",
) -> Generator[str, None, None]:
    payload = {
        "model": model,
        "messages": build_messages(question, chunks, answer_language),
        "stream": True,
        "options": {
            "temperature": 0.1,
            "num_ctx": 4096,
        },
    }
    request = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
                if data.get("done"):
                    break
    except TimeoutError as exc:
        raise RuntimeError(
            f"Ollama did not finish within {timeout} seconds. "
            "Try a lower top-k, increase ollama-timeout, or use a smaller model."
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not reach Ollama at http://localhost:11434. "
            "Start Ollama and make sure the model is available."
        ) from exc


def translate_question_openai(question: str, target_language: str = "english", model: str = DEFAULT_LLM_MODEL) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("OpenAI translation needs openai. Install it with: python -m pip install openai") from exc

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"Translate the user's question to {LANGUAGE_NAMES[normalize_language(target_language)]}. "
                    "Return only the translated question. Preserve regulatory terms, circular numbers, dates, and acronyms."
                ),
            },
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return (response.choices[0].message.content or question).strip()


def translate_question_ollama(
    question: str,
    target_language: str = "english",
    model: str = DEFAULT_OLLAMA_MODEL,
    timeout: int = 120,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"Translate the user's question to {LANGUAGE_NAMES[normalize_language(target_language)]}. "
                    "Return only the translated question. Preserve regulatory terms, circular numbers, dates, and acronyms."
                ),
            },
            {"role": "user", "content": question},
        ],
        "stream": False,
        "options": {"temperature": 0, "num_ctx": 2048},
    }
    request = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return (data.get("message", {}).get("content") or question).strip()


def generate_mock_answer(question: str, chunks: list[RetrievedChunk], max_points: int = 5) -> str:
    query_terms = set(tokenize(question))
    selected: list[tuple[int, str]] = []

    for source_index, chunk in enumerate(chunks, 1):
        sentences = re.split(r"(?<=[.!?])\s+|\n+", chunk.text.strip())
        scored_sentences = []
        for sentence in sentences:
            clean = re.sub(r"\s+", " ", sentence).strip()
            if len(clean) < 40:
                continue
            overlap = len(query_terms.intersection(tokenize(clean)))
            if overlap:
                scored_sentences.append((overlap, clean))
        scored_sentences.sort(key=lambda item: item[0], reverse=True)
        for _, sentence in scored_sentences[:2]:
            selected.append((source_index, sentence))
            if len(selected) >= max_points:
                break
        if len(selected) >= max_points:
            break

    if not selected:
        return "The retrieved context does not contain enough direct information to answer this question."

    lines = ["Offline Phase 6 test answer:", "", "Based only on the retrieved context:"]
    for source_index, sentence in selected:
        lines.append(f"- {sentence} [S{source_index}]")
    lines.append("")
    lines.append("Sources:")
    seen: set[int] = set()
    for source_index, _ in selected:
        if source_index in seen:
            continue
        seen.add(source_index)
        lines.append(f"- {citation_label(chunks[source_index - 1], source_index)}")
    return "\n".join(lines)


def print_retrieval(chunks: list[RetrievedChunk]) -> None:
    for index, chunk in enumerate(chunks, 1):
        snippet = re.sub(r"\s+", " ", chunk.text).strip()[:260]
        print(f"\n{citation_label(chunk, index)}")
        print(f"score={chunk.final_score:.3f} semantic={chunk.semantic_score:.3f} bm25={chunk.bm25_score:.3f}")
        print(snippet)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 5/6 RAG query runner")
    parser.add_argument("question", help="User question to answer")
    parser.add_argument("--domain", default="all")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--include-hf-experimental", action="store_true")
    parser.add_argument("--model", default=DEFAULT_LLM_MODEL)
    parser.add_argument("--provider", choices=["openai", "ollama"], default="openai")
    parser.add_argument("--ollama-model", default=DEFAULT_OLLAMA_MODEL)
    parser.add_argument("--ollama-timeout", type=int, default=600)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--mock-llm", action="store_true")
    args = parser.parse_args()

    chunks = retrieve(args.question, args.domain, args.top_k, args.include_hf_experimental)
    print_retrieval(chunks)

    if args.mock_llm:
        print("\nAnswer:\n")
        print(generate_mock_answer(args.question, chunks))
        return

    if args.no_llm or not os.getenv("OPENAI_API_KEY"):
        if args.provider == "ollama" and not args.no_llm:
            print("\nAnswer:\n")
            for token in generate_ollama_answer_stream(args.question, chunks, args.ollama_model, args.ollama_timeout):
                print(token, end="", flush=True)
            print()
            return
        print("\nLLM generation skipped.")
        print("\nGrounded prompt context:\n")
        print(build_context(chunks))
        return

    print("\nAnswer:\n")
    if args.provider == "ollama":
        for token in generate_ollama_answer_stream(args.question, chunks, args.ollama_model, args.ollama_timeout):
            print(token, end="", flush=True)
        print()
    else:
        print(generate_answer(args.question, chunks, args.model))


if __name__ == "__main__":
    main()
