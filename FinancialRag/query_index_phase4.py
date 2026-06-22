"""
Phase 4 smoke test: query the vector store and eyeball results.

Run after build_index.py:
    python query_index.py
"""

import json
import os

import chromadb
from sentence_transformers import SentenceTransformer


INDEX_DIR       = "data/vector_store"
COLLECTION_NAME = "regulatory_chunks"

# BGE recommends this exact prefix for queries (NOT for passages)
QUERY_PREFIX    = "Represent this sentence for searching relevant passages: "

TEST_QUERIES = [
    "What is the rating process for credit rating agencies?",
    "Disclosure requirements for structured finance products",
    "Withdrawal of credit ratings procedure",
    "Who can be appointed as a debenture trustee?",
    "Penalty for non-cooperation by issuer",
]

TOP_K = 5


def load_model():
    info_path = os.path.join(INDEX_DIR, "INDEX_INFO.json")
    with open(info_path) as f:
        info = json.load(f)
    print(f"Loading model: {info['model_name']}")
    return SentenceTransformer(info["model_name"])


def search(collection, model, query: str, top_k: int = TOP_K):
    query_emb = model.encode(
        QUERY_PREFIX + query,
        normalize_embeddings=True,
    )
    results = collection.query(
        query_embeddings=[query_emb.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return results


def pretty_print(query: str, results):
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        sim = 1 - dist  # cosine distance -> similarity
        snippet = doc[:300].replace("\n", " ")
        print(f"\n[#{rank}] sim={sim:.3f}  domain={meta.get('domain')}  "
              f"circular={meta.get('circular_number')}  date={meta.get('date')}")
        print(f"    {snippet}...")


def main():
    client = chromadb.PersistentClient(path=INDEX_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' has {collection.count()} chunks")

    model = load_model()

    for q in TEST_QUERIES:
        results = search(collection, model, q)
        pretty_print(q, results)

    # Example with metadata filter — retrieve only from SEBI
    print("\n\n" + "#" * 80)
    print("# Filtered search: same query, SEBI only")
    print("#" * 80)
    q = TEST_QUERIES[0]
    query_emb = model.encode(QUERY_PREFIX + q, normalize_embeddings=True)
    filtered = collection.query(
        query_embeddings=[query_emb.tolist()],
        n_results=TOP_K,
        where={"domain": "SEBI"},
        include=["documents", "metadatas", "distances"],
    )
    pretty_print(q + "  [domain=SEBI]", filtered)


if __name__ == "__main__":
    main()