"""Run the test queries through a pipeline mode and print a summary.

    python -m scripts.run_queries --mode cache_router --threshold 0.92

Queries are replayed in an order that puts each canonical FAQ before its paraphrases,
which is what a warm cache would see in production.
"""
import argparse
import dataclasses
import json
import statistics as st

from src.config import CONFIG
from src.embedder import get_embedder
from src.pipeline import MODES, Pipeline


def summarize(rows, intents_by_query):
    n = len(rows)
    hits = [r for r in rows if r.cache_hit]
    wrong = [r for r in hits if intents_by_query[r.matched_query] != intents_by_query[r.query]]
    lat = sorted(r.latency_ms for r in rows)
    p = lambda q: lat[min(len(lat) - 1, int(q * len(lat)))]
    large = sum(r.tier == "large" for r in rows)
    small = sum(r.tier == "small" for r in rows)
    print(f"\nrequests            : {n}")
    print(f"cache hits          : {len(hits)} ({len(hits) / n:.0%})")
    print(f"wrong cache hits    : {len(wrong)} ({(len(wrong) / len(hits)) if hits else 0:.0%} of hits)")
    for r in wrong:
        print(f"   - '{r.query}' got answer for '{r.matched_query}' (sim {r.similarity:.3f})")
    vf = sum(r.verify == "fail" for r in rows)
    vp = sum(r.verify == "pass" for r in rows)
    print(f"verifier pass/fail  : {vp}/{vf}")
    dk = [r for r in rows if "know" in r.answer.lower() and ("don't" in r.answer.lower() or "don’t" in r.answer.lower())]
    print(f"'don't know' answers: {len(dk)}")
    print(f"routed small/large  : {small}/{large}")
    print(f"total cost (USD)    : {sum(r.cost_usd for r in rows):.6f}")
    print(f"avg cost / request  : {st.mean(r.cost_usd for r in rows):.6f}")
    print(f"latency p50/p95 (ms): {p(0.5):.1f} / {p(0.95):.1f}")
    if CONFIG.provider == "mock":
        print("NOTE: provider=mock -> cost uses estimated tokens and latency excludes any real LLM call.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=list(MODES), default="cache_router")
    ap.add_argument("--threshold", type=float, default=CONFIG.cache_threshold)
    ap.add_argument("--verify-below", type=float, default=CONFIG.verify_below,
                    help="verify cache hits with similarity below this; 0 disables")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    cfg = dataclasses.replace(CONFIG, cache_threshold=args.threshold, verify_below=args.verify_below)
    queries = json.loads(cfg.queries_path.read_text())
    order = {"faq": 0, "hard": 1, "paraphrase": 2, "nearmiss": 3}
    queries.sort(key=lambda q: (order[q["group"]], q["id"]))
    if args.limit:
        queries = queries[: args.limit]
    intents = {q["query"]: q["intent"] for q in queries}

    pipe = Pipeline(args.mode, cfg, embedder=get_embedder(cfg.embedding_model))
    print(f"run_id={pipe.run_id} mode={args.mode} threshold={args.threshold} verify_below={args.verify_below} provider={cfg.provider}")
    rows = [pipe.handle(q["query"], q["id"]) for q in queries]
    summarize(rows, intents)


if __name__ == "__main__":
    main()
