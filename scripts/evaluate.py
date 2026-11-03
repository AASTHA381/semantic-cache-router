"""Answer-quality evaluation: run baseline and cache_router on all queries, then judge every answer.

    python -m scripts.evaluate

The judge is a different model family (Qwen) from the answer models (gpt-oss) to limit self-preference bias.
It scores each answer 1-5 against the reference docs. A sample is exported for a human spot check.
"""
import argparse
import csv
import json
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

from src.config import CONFIG, ModelSpec
from src.embedder import get_embedder
from src.llm import make_llm
from src.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
JUDGE = ModelSpec("qwen/qwen3.8-27b", 0.0, 0.0)  # judge cost is not part of the product cost

JUDGE_SYSTEM = "You are a strict grader of customer-support answers. Reply with JSON only."
JUDGE_PROMPT = """Reference documents (the only ground truth):
{ref}

Customer question: {query}

Answer to grade:
{answer}

Score the answer from 1 to 5:
5 = correct and complete according to the reference
4 = correct, minor omission
3 = partly correct or missing a key part of the question
2 = mostly wrong or misleading
1 = wrong, contradicts the reference, or says it doesn't know although the reference contains the answer
Also report:
- "abstained": true if the answer says it does not know / cannot answer
- "unsupported": true if the answer states facts that are not in the reference documents

Reply exactly: {{"score": <1-5>, "abstained": <true|false>, "unsupported": <true|false>, "reason": "<one sentence>"}}"""


def load_queries():
    main = json.loads((ROOT / "data" / "test_queries.json").read_text())
    order = {"faq": 0, "hard": 1, "paraphrase": 2, "nearmiss": 3}
    main.sort(key=lambda q: (order[q["group"]], q["id"]))
    held = json.loads((ROOT / "data" / "heldout_queries.json").read_text())
    for q in held:
        q["group"] = "heldout"
    return main + held


def judge(llm, query, answer, ref):
    prompt = JUDGE_PROMPT.format(ref=ref, query=query, answer=answer or "(empty)")
    for _ in range(3):
        res = llm.chat(JUDGE, JUDGE_SYSTEM, prompt, 1500)
        m = re.search(r"\{.*\}", res.text, re.S)
        if m:
            try:
                d = json.loads(m.group(0))
                return int(d["score"]), bool(d.get("abstained")), bool(d.get("unsupported")), str(d.get("reason", ""))
            except (ValueError, KeyError):
                pass
    return 0, False, False, "judge_parse_failure"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot", type=int, default=15)
    args = ap.parse_args()

    queries = load_queries()
    docs = {d["id"]: d for d in json.loads(CONFIG.docs_path.read_text())}
    cfg = CONFIG
    llm = make_llm(cfg)

    results = {}
    for mode in ("baseline", "cache_router"):
        pipe = Pipeline(mode, cfg, embedder=get_embedder(cfg.embedding_model))
        print(f"running {mode} run_id={pipe.run_id} on {len(queries)} queries")
        for q in queries:
            row = pipe.handle(q["query"], q["id"])
            ref = "\n".join(f"- {docs[d]['title']}: {docs[d]['text']}" for d in q["expected_docs"])
            s, ab, un, why = judge(llm, q["query"], row.answer, ref)
            results[(mode, q["id"])] = dict(row=row, score=s, abstained=ab, unsupported=un, reason=why, ref=ref)

    out = ROOT / "logs" / "judge_results.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "query_id", "group", "tier", "cache_hit", "verify", "cost_usd", "score",
                    "abstained", "unsupported", "reason", "query", "answer"])
        for q in queries:
            for mode in ("baseline", "cache_router"):
                r = results[(mode, q["id"])]
                row = r["row"]
                w.writerow([mode, q["id"], q["group"], row.tier, row.cache_hit, row.verify, f"{row.cost_usd:.8f}",
                            r["score"], r["abstained"], r["unsupported"], r["reason"], q["query"], row.answer])

    print("\ngroup        n  baseline  system  drop   abst(b/s)  unsupported(b/s)")
    by = defaultdict(list)
    for q in queries:
        by[q["group"]].append(q["id"])
        by["ALL"].append(q["id"])
    for g, ids in by.items():
        b = [results[("baseline", i)] for i in ids]
        s = [results[("cache_router", i)] for i in ids]
        mb, ms = st.mean(x["score"] for x in b), st.mean(x["score"] for x in s)
        print(f"{g:11} {len(ids):3}  {mb:7.2f}  {ms:6.2f}  {mb - ms:+.2f}  "
              f"{sum(x['abstained'] for x in b)}/{sum(x['abstained'] for x in s)}        "
              f"{sum(x['unsupported'] for x in b)}/{sum(x['unsupported'] for x in s)}")
    worse = [i for i in by["ALL"] if results[("cache_router", i)]["score"] < results[("baseline", i)]["score"]]
    print(f"\nqueries where system scored below baseline: {len(worse)} -> {worse}")
    fails = [i for i in by["ALL"] if results[("cache_router", i)]["reason"] == "judge_parse_failure"]
    print(f"judge parse failures (system): {len(fails)}")
    print(f"total cost baseline: ${sum(results[('baseline', i)]['row'].cost_usd for i in by['ALL']):.5f} | "
          f"system: ${sum(results[('cache_router', i)]['row'].cost_usd for i in by['ALL']):.5f}")

    # Spot-check sample: all regressions first, then random fill across the rest.
    rnd = random.Random(7)
    rest = [i for i in by["ALL"] if i not in worse]
    rnd.shuffle(rest)
    pick = (worse + rest)[: args.spot]
    lines = ["# Human spot check\n",
             "For each item, read the question, the reference, and the answer, then fill in YOUR score (1-5) "
             "using the same rubric as the judge (5 = correct and complete, 1 = wrong or wrongly 'don't know').\n"]
    for n, i in enumerate(pick, 1):
        q = next(x for x in queries if x["id"] == i)
        r = results[("cache_router", i)]
        lines += [f"## {n}. {i} ({q['group']}; tier={r['row'].tier}; cache_hit={r['row'].cache_hit})",
                  f"**Question:** {q['query']}\n", f"**Reference:**\n{r['ref']}\n",
                  f"**Answer:** {r['row'].answer}\n",
                  f"**Judge:** {r['score']} - {r['reason']}\n", "**Your score:** ___\n"]
    (ROOT / "data" / "spot_check.md").write_text("\n".join(lines))
    print(f"\nwrote {out.name} and data/spot_check.md ({len(pick)} items)")


if __name__ == "__main__":
    main()
