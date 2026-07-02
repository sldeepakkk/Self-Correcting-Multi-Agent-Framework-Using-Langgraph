import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from config import (
    SEMANTIC_CACHE_THRESHOLD,
    EMBEDDING_MODEL,
    CACHE_INDEX_PATH,
    CACHE_STORE_PATH
)


class SemanticCache:
    """
    Query-level semantic cache using FAISS + cosine similarity.

    Embeds every incoming query using all-MiniLM-L6-v2 (local, CPU).
    Normalizes the vector and does inner product search against stored
    embeddings. Inner product on L2-normalized vectors = cosine similarity.

    On a hit (score >= threshold), returns the stored response immediately.
    No retrieval, no LLM call, no cost.

    Persists to disk so cache warms up across sessions.
    """

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.dimension = 384            # all-MiniLM-L6-v2 output dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        self.store: list[dict] = []     # parallel list to FAISS index
                                        # each entry: {query, response, path_taken}
        self._load()

    def _embed(self, text: str) -> np.ndarray:
        """Embed and L2-normalize so inner product = cosine similarity."""
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding.astype(np.float32)

    def get(self, query: str) -> dict | None:
        """
        Check cache for a semantically similar query.
        Returns stored entry if similarity >= threshold, else None.
        """
        if self.index.ntotal == 0:
            return None

        embedding = self._embed(query)
        scores, indices = self.index.search(embedding, 1)

        top_score = float(scores[0][0])
        top_index = int(indices[0][0])

        if top_score >= SEMANTIC_CACHE_THRESHOLD:
            cached = self.store[top_index]
            print(f"[CACHE HIT] score={top_score:.4f} | matched: '{cached['query']}'")
            return cached

        print(f"[CACHE MISS] top score={top_score:.4f}")
        return None

    def add(self, query: str, response: str, path_taken: str) -> None:
        """
        Add a new query-response pair to the cache.
        Saves to disk immediately — cache persists across sessions.
        """
        embedding = self._embed(query)
        self.index.add(embedding)
        self.store.append({
            "query": query,
            "response": response,
            "path_taken": path_taken
        })
        self._save()
        print(f"[CACHE ADD] '{query[:60]}...' | path={path_taken}")

    def _save(self) -> None:
        """Persist FAISS index and store to disk."""
        os.makedirs(os.path.dirname(CACHE_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, CACHE_INDEX_PATH)
        with open(CACHE_STORE_PATH, "w") as f:
            json.dump(self.store, f, indent=2)

    def _load(self) -> None:
        """Load persisted cache from disk on startup if it exists."""
        if os.path.exists(CACHE_INDEX_PATH) and os.path.exists(CACHE_STORE_PATH):
            self.index = faiss.read_index(CACHE_INDEX_PATH)
            with open(CACHE_STORE_PATH, "r") as f:
                self.store = json.load(f)
            print(f"[CACHE LOADED] {self.index.ntotal} entries from disk")
        else:
            print("[CACHE INIT] No existing cache found. Starting fresh.")

    @property
    def size(self) -> int:
        return self.index.ntotal