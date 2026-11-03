# Decision memo: cutting the cost of a RAG support assistant

**Author:** Aastha Saini · **Status:** prototype, evaluated on 72 test queries · **Repo:** `semantic-cache-router`

## 1. Problem and unit economics
A RAG assistant pays for an LLM call on every question, and most questions do not need the most expensive model. Cost per request scales linearly with traffic, so it decides whether the product has a margin. The goal: **reduce cost per request without a noticeable drop in answer quality**, and make cost and latency visible per request so the trade-offs can be managed.

Test product: a support assistant for a fictional cloud-storage service ("StashBox"), 24 help articles. Models on Groq: `gpt-oss-20b` (small) and `gpt-oss-120b` (large).

## 2. Options considered

| Option | What it does | Verdict |
|---|---|---|
| Baseline | Large model for every request | Highest cost; used as the comparison |
| Semantic cache | Reuse a stored answer when a new question is similar enough | Cheap, but risks serving a wrong answer |
| Cost-aware router | Small model for simple questions, large model for hard ones | Biggest saving; risks under-serving hard questions |
| Cache + router + verifier (chosen) | Both, plus a cheap check on borderline cache hits | Best trade-off found |

## 3. Key decisions and why
1. **Cache threshold: 0.85 similarity, with a verifier below 0.93.** Paraphrases and near-miss questions overlap in similarity (paraphrases median 0.82; "recover a deleted account" vs "recover a deleted file" scored 0.87). No single threshold separates them. At 0.80 the cache had 27% hits with 4 of 16 wrong; at 0.85, 13% hits with 2 of 8 wrong. Instead of raising the threshold and losing most hits, borderline hits are checked by the small model ("would the same answer be correct for both?").
2. **Router: transparent heuristics, not a trained model.** Query length, comparison keywords, multi-part phrasing, and how many docs are relevant. The reason for each routing decision is logged. Reasoning: with 72 labeled queries there is not enough data to train a classifier honestly.
3. **Retrieval: hybrid search (embeddings + keyword + title).** Missing documents caused wrong "I don't know" answers. Hybrid retrieval found all expected docs in 71 of 72 queries, up from 64. The cache keeps its own embedding model so its threshold stays valid.
4. **Wider context for hard questions** (6 docs instead of 3).

## 4. Results (72 queries; baseline vs. cache + router + verifier)

| Metric | Baseline | System |
|---|---|---|
| Total cost | $0.0102 | $0.0064 (**-37%**) |
| Mean answer quality (LLM judge, 1-5) | 4.49 | 4.46 |
| Answers scoring 4 or higher | 67 / 72 | 67 / 72 |
| Answers scoring 2 or lower | 2 | 3 |
| Cache hit rate | - | 7% (5 hits; verifier rejected 3 more) |
| Routed to small model | - | 76% of non-cached requests (51 of 67) |
| Median latency | 1.77 s | 0.51 s (cache hit), 0.59 s (small), 1.06 s (large) |

- Most of the saving comes from the **router**, not the cache. In an early run (before the verifier and retrieval fix) the cache alone saved about 10%.
- Quality is measured by an LLM judge (a different model family from the answer models). I spot-checked it on 15 answers: it agreed with me within 1 point on 14 of 15 (correlation 0.84), and it was about 0.4 points stricter than me.
- Small-routed answers scored 4.55 vs. 4.57 for the baseline on the same queries.

## 5. Risks and what I did about them

| Risk | Who is harmed | Mitigation | Remaining gap |
|---|---|---|---|
| Wrong cached answer (the model answers a different question) | The customer, and trust in the product | Verifier on borderline hits; no-cache patterns for personalized or time-sensitive queries; TTL support | 5 hits were checked in the final run (none wrong), but the sample is tiny |
| Stale answers after docs change | Customer | TTL setting exists | Needs cache invalidation when docs update; not built |
| Hard question routed to the small model | Customer gets a thinner answer | Logged routing reason; hard-question detection | Router got 10 of 12 right on held-out queries; one hard question (contractor access) was under-routed |
| Small model invents details | Customer | "Answer only from context" prompt | One case remained (refund details when asked how to cancel) |
| Verifier adds cost and latency | Margin, response time | Used only on borderline hits | Verified hits take about 0.5 s, so they are not as fast as plain cache hits |

## 6. Limits of this evidence (what I would not claim)
- **Small and synthetic:** 72 queries I wrote against 24 docs I wrote. The router and retrieval were developed on the same data they were measured on. Differences of one or two queries are noise.
- **Cache benefit is understated or overstated depending on traffic:** the test set was built with paraphrases, but real traffic repetition is unknown. Production hit rates could differ a lot.
- **Prices:** verified on 2026-11-03 against Groq's model pages (gpt-oss-20b $0.075/$0.30, gpt-oss-120b $0.15/$0.60 per 1M input/output tokens). Prices change, and the cost model ignores Groq's cached-input discount, so absolute dollars are slightly overstated; percent savings depend on the price ratio between the two models.
- **Latency** varies run to run because of API variance, so treat it as directional.
- **One human rater** for the judge check.

## 7. Recommendation and rollout
Ship the router and verifier-gated cache behind a flag, in stages:
1. **Shadow mode:** run the system alongside the current setup on real traffic; log cost and compare answers. No customer impact.
2. **Small rollout (5-10%)** with a thumbs-up/down signal and the dashboard watching cost, hit rate, routing split and complaint rate.
3. **Guardrails to stop the rollout:** wrong-cache-hit rate (from sampled review), customer dissatisfaction vs. control, and escalation rate.
4. **Before scaling:** re-check prices (they change), build cache invalidation on doc updates, collect real queries to retrain or replace the heuristic router, and replace the judge's reference docs with real support-agent ground truth.

**Decision requested:** a quality drop of up to about 0.1 points (on a 1-5 scale) is acceptable for a roughly one-third cost cut on this evidence. The product owner should confirm what drop and what wrong-answer rate are acceptable for a support product before rollout.
