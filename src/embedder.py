"""Query/document embeddings. Vectors are L2-normalised so dot product == cosine similarity."""
from functools import lru_cache

import numpy as np


class Embedder:
    def __init__(self, model_name: str):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        vecs = np.array(list(self._model.embed(texts)), dtype=np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs / np.clip(norms, 1e-12, None)


@lru_cache(maxsize=4)
def get_embedder(model_name: str) -> Embedder:
    return Embedder(model_name)
