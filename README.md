# Semantic Cache + Cost-Aware Router (RAG cost layer)

A small RAG assistant (fictional "StashBox" cloud-storage FAQ) with a layer in front of the LLM that:

1. **Caches** answers by query-embedding similarity (skip the LLM when a near-duplicate was already answered).
2. **Routes** each remaining query to a small or large model using transparent heuristics.
3. **Logs** cost, latency, tokens, cache hit and model per request to `logs/requests.csv` (dashboard comes in Week 2).

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m scripts.run_queries --mode baseline
.venv/bin/python -m scripts.run_queries --mode cache_router --threshold 0.85
.venv/bin/python -m pytest
```

Modes: `baseline` (large model, no cache), `cache`, `router`, `cache_router`.

The first run downloads a small embedding model (~130 MB).

### Real LLM vs mock
Default `LLM_PROVIDER=mock` runs offline: the "answer" is the top retrieved chunk and token counts are
word-count estimates. **Mock numbers are for testing the pipeline only. Do not quote them.**
For real results copy `.env.example` to `.env`, set `LLM_PROVIDER=openai` and `OPENAI_API_KEY`, and
check the model prices in `src/config.py` (verified 2026-11-03 for the Groq defaults).

## Layout
| Path | Purpose |
|---|---|
| `src/cache.py` | Semantic cache (threshold, TTL, no-cache patterns) |
| `src/router.py` | Heuristic small/large router with logged reasons |
| `src/pipeline.py` | embed → cache → route → retrieve → generate → store → log |
| `src/metrics.py` | Per-request CSV logging |
| `data/docs.json` | Knowledge base (24 docs) |
| `data/test_queries.json` | 60 queries: 20 FAQ, 20 paraphrases, 10 near-misses, 10 hard multi-doc |
| `scripts/run_queries.py` | Replay the test set and print a summary |

## Week 1 findings (Groq: openai/gpt-oss-20b small, openai/gpt-oss-120b large; bge-small embeddings)
Prices in `src/config.py` were verified on 2026-11-03 against Groq's model pages (gpt-oss-20b $0.075 in / $0.30 out,
gpt-oss-120b $0.15 in / $0.60 out per 1M tokens). The cost model ignores Groq's cached-input discount, so absolute
costs are slightly overstated. Judge-model cost (Qwen) is excluded because it is evaluation overhead, not product cost.

| Run (60 queries) | Cache hits | Wrong hits | Total cost | "Don't know" |
|---|---|---|---|---|
| baseline (large model, top_k=6) | 0 | - | $0.0080 | 3 |
| cache + router, no verifier (threshold 0.85) | 8 | 2 | $0.0044 | 1 |
| cache + router + verifier (verify_below 0.93) | 5 | 0 | $0.0047 | 1 |

- Adaptive retrieval (top_k 3 for easy, 6 for hard) cut "don't know" answers on hard queries from 3/10 to 1/10.
- The verifier (small-model yes/no check on grey-zone cache hits) removed both wrong hits. It rejected 3 of 8
  candidates, one of which was probably a correct reuse, so it is conservative. It costs about $0.0004 per 60 queries.
- Latency swings a lot between runs (p50 0.5 s to 2.5 s for the same config) because of API variance. Do not
  compare latency from single runs.
- Still open: h08 still fails (retrieval misses the pricing doc), router untested on unseen queries, answer quality
  not yet rated, and the test set is small (60), so differences of 1-3 queries are noise.

## Held-out router check (`python -m scripts.eval_router`, no LLM calls)
12 queries in `data/heldout_queries.json` (expected tiers labeled before running). Written by me, not an independent
tester, so it is still a weak test.
- Router: 10/12 correct. u02 ("Why was my reset link rejected?") was over-routed to large (costs money). u09
  ("Is it better to give contractors Editor access ... or expiring links?") was under-routed to small (risks a poor
  answer), because it has no trigger keywords.
- Retrieval: expected docs were missing for u04 (pricing, small tier) and u11 (support).
- If the router is tuned against these 12, they stop being held-out; write a fresh set to re-test.

## Quality evaluation (`python -m scripts.evaluate`)
72 queries (60 + 12 held-out), baseline vs cache+router+verifier, judged 1-5 against the reference docs by
`qwen/qwen3.8-27b` (different model family from the answer models). Judge is unvalidated until the human spot
check in `data/spot_check.md` is filled in.

| | Baseline | System |
|---|---|---|
| Mean score | 4.43 | 4.33 |
| Answers scoring >= 4 | 65/72 | 64/72 |
| Answers scoring <= 2 | 4 | 7 |
| Total cost | $0.0099 | $0.0062 (-37%) |

- Of 72 queries: 4 improved, 8 dropped by 1 point (mostly minor omissions by the small model), 2 dropped by 2+
  (u04: retrieval missed the pricing doc; p02: small model invented refund details).
- h10 (support/data residency) also failed in the system because retrieval missed the support doc.
- Remaining quality loss is mostly retrieval gaps and small-model terseness, not cache errors (cache hits scored 4.8 vs 5.0).

### Human spot check of the judge (15 items)
Sample = the 10 regressions + 5 random queries, so it over-represents hard cases. Human (author) vs judge:
exact agreement 8/15, within 1 point 14/15, correlation 0.84, mean 4.00 human vs 3.60 judge.
- Judge is about 0.4 points stricter than the human, mostly 4-vs-5 on minor omissions. Biggest gap: h05 (human 4, judge 2).
- Both agreed on the three real failures (h10, p02, u04). One item (u08) the judge was more lenient.
- Implication: the 1-point regressions are the least reliable part of the quality numbers. Treat the true quality
  drop as <= the measured 0.10. Single human rater, n=15.

## Retrieval fix (hybrid search)
Problem: expected docs were missing from the retrieved context (u04 pricing, u11/h10 support), causing wrong "I don't know" answers.
`scripts/eval_retrieval.py` compared variants (recall of expected docs; easy at k=3, multi-doc at k=6; 72 queries):

| Retrieval | easy@3 | multi@6 | all expected docs found |
|---|---|---|---|
| dense bge-small (before) | 0.96 | 0.85 | 64/72 |
| hybrid (dense + BM25 + title), bge-small | 1.00 | 0.90 | 68/72 |
| hybrid (dense + BM25 + title), bge-base (chosen) | 1.00 | 0.98 | 71/72 |

Retrieval uses bge-base; the cache stays on bge-small because the cache threshold (0.85) was tuned on it.
Variant choice was made on the same 72 queries used for evaluation (a mild overfitting risk, only a handful of variants tried).

Quality re-run after the fix (same judge, same 72 queries):

| | Before | After |
|---|---|---|
| Baseline mean / system mean | 4.43 / 4.33 | 4.49 / 4.46 |
| System answers scoring <= 2 | 7 | 3 |
| System answers scoring >= 4 | 64/72 | 67/72 |
| Cost: baseline vs system | $0.0099 vs $0.0062 | $0.0102 vs $0.0065 (-37%) |

u04 5 (was 1), h10 4 (was 2), u11 5 (was 3). Still failing: p02 (small model hallucinated refund details) and h08.
LLM and judge variance between runs is roughly +/-0.05 on the mean, so the 0.10 -> 0.03 change is suggestive, not proven.

## Dashboard
```bash
.venv/bin/streamlit run dashboard.py     # opens http://localhost:8501
```
Reads `logs/requests.csv` (written by `scripts.run_queries` / `scripts.evaluate`) and `logs/judge_results.csv`.
Shows total/avg cost, cache hit rate, small-vs-large routing, p50/p95 latency, cumulative cost vs baseline,
per-route cost and latency, a monthly cost projection, per-query savings and judge quality scores. Pick any
system run and baseline run in the sidebar (defaults to the latest).
