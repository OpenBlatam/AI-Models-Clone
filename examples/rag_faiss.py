import os
import sys
import json
import numpy as np


def try_import_faiss():
    try:
        import faiss  # type: ignore
        return faiss
    except Exception as exc:  # pragma: no cover
        print("FAISS not installed. Install with: pip install faiss-cpu", file=sys.stderr)
        print(f"Reason: {exc}", file=sys.stderr)
        return None


def embed_texts_dummy(texts, dim=384, seed=42):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(len(texts), dim)).astype("float32")


def build_index(embeddings):
    faiss = try_import_faiss()
    if faiss is None:
        return None
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index


def search(index, query_emb, top_k=5):
    import faiss  # type: ignore
    faiss.normalize_L2(query_emb)
    scores, ids = index.search(query_emb, top_k)
    return scores[0].tolist(), ids[0].tolist()


def main():
    docs_path = os.getenv("DOCS_JSON", None)
    if docs_path and os.path.exists(docs_path):
        with open(docs_path, "r", encoding="utf-8") as f:
            docs = json.load(f)
        texts = [d.get("text", "") for d in docs]
    else:
        texts = [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning enables computers to learn from data.",
            "Transformers are powerful models for sequence tasks.",
            "Vector databases power RAG systems.",
            "FAISS provides efficient similarity search.",
        ]

    embeddings = embed_texts_dummy(texts)
    index = build_index(embeddings)
    if index is None:
        sys.exit(1)

    query = os.getenv("QUERY", "What is FAISS?")
    query_emb = embed_texts_dummy([query])
    scores, ids = search(index, query_emb, top_k=3)

    results = [{"id": int(i), "score": float(s), "text": texts[int(i)]} for s, i in zip(scores, ids)]
    print(json.dumps({"query": query, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()





