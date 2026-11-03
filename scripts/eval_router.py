"""Check router decisions and retrieval coverage on held-out queries. Makes no LLM calls (free).

    python -m scripts.eval_router
"""
import json
from pathlib import Path

from src.config import CONFIG
from src.embedder import get_embedder
from src.retriever import DocIndex
from src.router import route_query

HELDOUT = Path(__file__).resolve().parent.parent / "data" / "heldout_queries.json"


def main():
    qs = json.loads(HELDOUT.read_text())
    index = DocIndex(CONFIG.docs_path, get_embedder(CONFIG.retrieval_embedding_model))
    correct = 0
    for q in qs:
        hits = index.search(q["query"], CONFIG.top_k_hard)
        top_sims = sorted((s for _, s in hits), reverse=True)[: CONFIG.top_k]
        route = route_query(q["query"], top_sims, CONFIG.router_hard_score)
        ok = route.tier == q["expected_tier"]
        correct += ok
        k = CONFIG.top_k_hard if route.tier == "large" else CONFIG.top_k
        got = {d.id for d, _ in hits[:k]}
        missing = [d for d in q["expected_docs"] if d not in got]
        print(f"{'OK ' if ok else 'BAD'} {q['id']} expected={q['expected_tier']:5} got={route.tier:5} "
              f"score={route.score} {','.join(route.reasons)} | missing_docs={missing or '-'}")
    print(f"\nrouter accuracy: {correct}/{len(qs)}")


if __name__ == "__main__":
    main()
