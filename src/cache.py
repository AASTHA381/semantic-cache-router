"""Semantic cache: return a stored answer when a new query is close enough in embedding space."""
import re
import time
from dataclasses import dataclass, field

import numpy as np


@dataclass
class CacheEntry:
    query: str
    answer: str
    created_at: float
    meta: dict = field(default_factory=dict)


@dataclass
class CacheLookup:
    hit: bool
    similarity: float | None  # best similarity found, even on a miss
    entry: CacheEntry | None
    bypassed: bool = False


class SemanticCache:
    def __init__(self, threshold: float, ttl_seconds: float | None = None,
                 no_cache_patterns: tuple[str, ...] = ()):
        self.threshold = threshold
        self.ttl_seconds = ttl_seconds
        self._patterns = [re.compile(p, re.I) for p in no_cache_patterns]
        self._vecs: np.ndarray | None = None
        self._entries: list[CacheEntry] = []

    def __len__(self) -> int:
        return len(self._entries)

    def should_bypass(self, query: str) -> bool:
        return any(p.search(query) for p in self._patterns)

    def lookup(self, query: str, query_vec: np.ndarray) -> CacheLookup:
        if self.should_bypass(query):
            return CacheLookup(False, None, None, bypassed=True)
        if self._vecs is None:
            return CacheLookup(False, None, None)

        sims = self._vecs @ query_vec
        now = time.time()
        # Expired entries are ignored rather than deleted, to keep indices aligned.
        if self.ttl_seconds is not None:
            for i, e in enumerate(self._entries):
                if now - e.created_at > self.ttl_seconds:
                    sims[i] = -1.0
        best = int(np.argmax(sims))
        best_sim = float(sims[best])
        if best_sim >= self.threshold:
            return CacheLookup(True, best_sim, self._entries[best])
        return CacheLookup(False, best_sim, None)

    def add(self, query: str, query_vec: np.ndarray, answer: str, meta: dict | None = None) -> None:
        if self.should_bypass(query):
            return
        entry = CacheEntry(query, answer, time.time(), meta or {})
        self._entries.append(entry)
        row = query_vec[None, :]
        self._vecs = row if self._vecs is None else np.vstack([self._vecs, row])

    def clear(self) -> None:
        self._vecs, self._entries = None, []
