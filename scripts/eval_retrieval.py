"""Retrieval recall experiment (no LLM calls).

    python -m scripts.eval_retrieval

Recall@k = share of a query's expected docs found in the top k. Easy queries are judged at k=3,
multi-doc queries at k=6, matching the pipeline.
"""
import json
from pathlib import Path

import numpy as np

from src.config import CONFIG
from src.embedder import Embedder
from src.retriever import BM25, rrf

ROOT = Path(__file__).resolve().parent.parent
def main():
    docs = json.loads(CONFIG.docs_path.read_text())
    ids = [d["id"] for d in docs]
    qs = json.loads((ROOT / "data" / "test_queries.json").read_text()) + \
        json.loads((ROOT / "data" / "heldout_queries.json").read_text())
    for q in qs:
        q["multi"] = len(q["expected_docs"]) > 1

    def variants(model_name):
        emb = Embedder(model_name)
        full = emb.embed([f"{d['title']}. {d['text']}" for d in docs])
        title = emb.embed([d["title"] for d in docs])
        bm = BM25([f"{d['title']} {d['title']} {d['text']}" for d in docs])
        qv = emb.embed([q["query"] for q in qs])
        out = {}
        out["dense"] = [list(np.argsort(-(full @ v))) for v in qv]
        out["bm25"] = [list(np.argsort(-bm.scores(q["query"]))) for q in qs]
        out["hybrid_rrf"] = [rrf([a, b]) for a, b in zip(out["dense"], out["bm25"])]
        out["dense_title+body"] = [list(np.argsort(-(0.5 * (full @ v) + 0.5 * (title @ v)))) for v in qv]
        out["hybrid+title"] = [rrf([a, b, list(np.argsort(-(title @ v)))])
                               for a, b, v in zip(out["dense"], out["bm25"], qv)]
        return out

    for model in [CONFIG.embedding_model, "BAAI/bge-base-en-v1.5"]:
        print(f"\n=== embedding: {model}")
        print(f"{'variant':20} {'easy@3':>7} {'multi@6':>8} {'all-docs-found':>15}")
        for name, ranks in variants(model).items():
            easy, multi, full_ok = [], [], 0
            for q, r in zip(qs, ranks):
                k = 6 if q["multi"] else 3
                top = {ids[i] for i in r[:k]}
                rec = sum(d in top for d in q["expected_docs"]) / len(q["expected_docs"])
                (multi if q["multi"] else easy).append(rec)
                full_ok += rec == 1
            print(f"{name:20} {np.mean(easy):7.2f} {np.mean(multi):8.2f} {full_ok:>10}/{len(qs)}")


if __name__ == "__main__":
    main()
