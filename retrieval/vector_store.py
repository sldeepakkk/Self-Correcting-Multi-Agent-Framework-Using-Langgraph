import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from config import (
    EMBEDDING_MODEL,
    VECTOR_STORE_PATH,
    VECTOR_STORE_DOCS_PATH
)


class VectorStore:
    """
    FAISS document store for NSE context documents.

    Different from SemanticCache:
    - Cache: stores query → response pairs, searched by query
    - VectorStore: stores document chunks → metadata, searched by sub-query

    Each document chunk is embedded and indexed.
    Search returns top-k chunks with relevance scores.
    Results feed into the judge for relevance scoring.
    """

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.dimension = 384
        self.index = faiss.IndexFlatIP(self.dimension)
        self.docs: list[dict] = []      # parallel list to FAISS index
                                        # each: {"content": str, "source": str, "ticker": str}
        self._load()

    def _embed(self, text: str) -> np.ndarray:
        return self.model.encode([text], normalize_embeddings=True).astype(np.float32)

    def _embed_batch(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True).astype(np.float32)

    def add_documents(self, documents: list[dict]) -> None:
        """
        Add documents to the store.
        Each document: {"content": str, "source": str, "ticker": str}
        """
        if not documents:
            return

        texts = [d["content"] for d in documents]
        embeddings = self._embed_batch(texts)
        self.index.add(embeddings)
        self.docs.extend(documents)
        self._save()
        print(f"[VECTOR STORE] Added {len(documents)} documents. Total: {self.index.ntotal}")

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        """
        Search for most relevant documents given a sub-query.
        Returns list of dicts with content, source, ticker, score.
        """
        if self.index.ntotal == 0:
            print("[VECTOR STORE] Empty — no documents to search")
            return []

        embedding = self._embed(query)
        scores, indices = self.index.search(embedding, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            doc = self.docs[idx].copy()
            doc["score"] = float(score)
            results.append(doc)

        return results

    def search_multi(self, sub_queries: list[str], top_k_per_query: int = 5) -> list[dict]:
        """
        Search multiple sub-queries, merge results, deduplicate by content hash.
        This is what the retriever node calls.
        """
        seen = set()
        merged = []

        for sub_query in sub_queries:
            results = self.search(sub_query, top_k=top_k_per_query)
            for doc in results:
                key = doc["content"][:100]      # first 100 chars as dedup key
                if key not in seen:
                    seen.add(key)
                    merged.append(doc)

        # sort by score descending
        merged.sort(key=lambda x: x["score"], reverse=True)
        return merged

    def _save(self) -> None:
        os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
        faiss.write_index(self.index, VECTOR_STORE_PATH)
        with open(VECTOR_STORE_DOCS_PATH, "w") as f:
            json.dump(self.docs, f, indent=2)

    def _load(self) -> None:
        if os.path.exists(VECTOR_STORE_PATH) and os.path.exists(VECTOR_STORE_DOCS_PATH):
            self.index = faiss.read_index(VECTOR_STORE_PATH)
            with open(VECTOR_STORE_DOCS_PATH, "r") as f:
                self.docs = json.load(f)
            print(f"[VECTOR STORE] Loaded {self.index.ntotal} documents from disk")
        else:
            print("[VECTOR STORE INIT] Empty store. Run seed_data.py first.")

    @property
    def size(self) -> int:
        return self.index.ntotal