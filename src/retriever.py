"""Hybrid retrieval over the knowledge base: dense body + dense title + BM25 keyword, fused with
reciprocal-rank fusion (RRF). Brute force; fine for a few thousand docs."""
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .embedder import Embedder

TOKEN = re.compile(r"[a-z0-9]+")
STOP = set("a an the and or of to is are do does can i my me you your we our it in on for with how what when "
           "if be this that at by from as will not have has".split())


def tokenize(text: str) -> list[str]:
    return [w for w in TOKEN.findall(text.lower()) if w not in STOP]


class BM25:
    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75):
        self.docs = [Counter(tokenize(t)) for t in texts]
        self.len = np.array([sum(d.values()) for d in self.docs], dtype=float)
        self.avg = self.len.mean()
        df = Counter(w for d in self.docs for w in d)
        n = len(texts)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
        self.k1, self.b = k1, b

    def scores(self, query: str) -> np.ndarray:
        out = np.zeros(len(self.docs))
        for w in set(tokenize(query)):
            if w not in self.idf:
                continue
            for i, d in enumerate(self.docs):
                f = d.get(w, 0)
                if f:
                    norm = self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
                    out[i] += self.idf[w] * f * (self.k1 + 1) / (f + norm)
        return out


def rrf(rank_lists: list[list[int]], k: int = 60) -> list[int]:
    score: dict[int, float] = defaultdict(float)
    for ranks in rank_lists:
        for pos, i in enumerate(ranks):
            score[i] += 1 / (k + pos + 1)
    return sorted(score, key=lambda i: -score[i])


@dataclass
class Doc:
    id: str
    title: str
    text: str


class DocIndex:
    def __init__(self, docs_path: Path, embedder: Embedder):
        self.docs = [Doc(**d) for d in json.loads(Path(docs_path).read_text())]
        self._embedder = embedder
        self._body = embedder.embed([f"{d.title}. {d.text}" for d in self.docs])
        self._title = embedder.embed([d.title for d in self.docs])
        self._bm25 = BM25([f"{d.title} {d.title} {d.text}" for d in self.docs])

    def search(self, query: str, k: int) -> list[tuple[Doc, float]]:
        """Top-k docs in hybrid order, each paired with its dense cosine similarity (used by the router)."""
        qv = self._embedder.embed([query])[0]
        body = self._body @ qv
        ranked = rrf([
            list(np.argsort(-body)),
            list(np.argsort(-self._bm25.scores(query))),
            list(np.argsort(-(self._title @ qv))),
        ])
        return [(self.docs[i], float(body[i])) for i in ranked[:k]]
