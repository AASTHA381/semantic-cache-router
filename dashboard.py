"""Cost & latency dashboard.   Run:  .venv/bin/streamlit run dashboard.py"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.analytics import (cumulative_cost, load_requests, project_monthly, run_table, summarize,
                           tier_breakdown)

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "logs" / "requests.csv"
JUDGE = ROOT / "logs" / "judge_results.csv"

st.set_page_config(page_title="RAG cost layer", layout="wide")
st.title("Semantic cache + cost-aware router: cost & latency")

if not LOG.exists():
    st.error("No logs yet. Run `python -m scripts.run_queries --mode cache_router` first.")
    st.stop()

df = load_requests(LOG)
runs = run_table(df)
runs["label"] = runs.apply(lambda r: f"{r['mode']} · {r['run_id']} · {r['n']} queries", axis=1)

base_runs = runs[runs["mode"] == "baseline"]
sys_runs = runs[runs["mode"] != "baseline"]
if base_runs.empty or sys_runs.empty:
    st.warning("Need at least one baseline run and one cache/router run to compare.")
    st.stop()

with st.sidebar:
    st.header("Runs")
    sys_label = st.selectbox("System run", sys_runs["label"], index=0)
    base_label = st.selectbox("Baseline run", base_runs["label"], index=0)
    st.caption("Defaults to the most recent runs. Pick runs with the same number of queries for a fair comparison.")
    st.header("Projection")
    rpd = st.number_input("Requests per day", min_value=100, value=10_000, step=1000)

sys_id = sys_runs.loc[sys_runs["label"] == sys_label, "run_id"].iloc[0]
base_id = base_runs.loc[base_runs["label"] == base_label, "run_id"].iloc[0]
sysd, based = df[df["run_id"] == sys_id], df[df["run_id"] == base_id]
S, B = summarize(sysd), summarize(based)

st.warning("Prices (verified 2026-11-03 on Groq's model pages) ignore Groq's cached-input discount, so costs are "
           "slightly overstated. "
           "Latency varies a lot between runs (API variance), so don't compare single runs.")
if S["requests"] != B["requests"]:
    st.warning(f"Runs have different sizes ({S['requests']} vs {B['requests']} queries): comparison is not like-for-like.")

saving = 1 - S["total_cost"] / B["total_cost"] if B["total_cost"] else 0.0
c = st.columns(5)
c[0].metric("Total cost (system)", f"${S['total_cost']:.4f}", f"{-saving:.0%} vs baseline", delta_color="inverse")
c[1].metric("Avg cost / request", f"${S['avg_cost']:.5f}", f"baseline ${B['avg_cost']:.5f}", delta_color="off")
c[2].metric("Cache hit rate", f"{S['hit_rate']:.0%}", f"{S['verify_fail']} hits rejected by verifier", delta_color="off")
c[3].metric("Routed to small model", f"{S['small_share']:.0%}", "of non-cached requests", delta_color="off")
c[4].metric("Latency p50 / p95", f"{S['p50_ms']:.0f} / {S['p95_ms']:.0f} ms",
            f"baseline {B['p50_ms']:.0f} / {B['p95_ms']:.0f}", delta_color="off")

left, right = st.columns(2)
with left:
    st.subheader("Cumulative cost")
    cum = pd.concat([cumulative_cost(sysd, "system"), cumulative_cost(based, "baseline")])
    st.altair_chart(alt.Chart(cum).mark_line().encode(x="request:Q", y="cumulative_cost:Q", color="run:N")
                    .properties(height=300), width="stretch")
with right:
    st.subheader("Where requests went")
    tb = tier_breakdown(sysd)
    st.altair_chart(alt.Chart(tb).mark_bar().encode(x="tier:N", y="requests:Q", color="tier:N", tooltip=list(tb.columns))
                    .properties(height=300), width="stretch")

st.subheader("Cost and latency by route")
tb_show = tb.copy()
tb_show["cost"] = tb_show["cost"].map(lambda x: f"${x:.5f}")
tb_show[["p50_ms", "p95_ms"]] = tb_show[["p50_ms", "p95_ms"]].round(0)
st.dataframe(tb_show, hide_index=True, width="stretch")

st.subheader("Projected monthly cost (extrapolation)")
pm_s, pm_b = project_monthly(S["avg_cost"], rpd), project_monthly(B["avg_cost"], rpd)
p = st.columns(3)
p[0].metric("Baseline / month", f"${pm_b:,.2f}")
p[1].metric("System / month", f"${pm_s:,.2f}")
p[2].metric("Saved / month", f"${pm_b - pm_s:,.2f}")
st.caption("Assumes real traffic looks like this test set. The test set was built with many paraphrases, so the "
           "real cache hit rate may be lower or higher. Use as an order-of-magnitude illustration only.")

st.subheader("Per-query savings")
m = based[["query_id", "query", "cost_usd"]].merge(
    sysd[["query_id", "cost_usd", "tier", "cache_hit", "verify", "similarity", "route_reason"]],
    on="query_id", suffixes=("_baseline", "_system"))
m["saved"] = m["cost_usd_baseline"] - m["cost_usd_system"]
st.dataframe(m.sort_values("saved", ascending=False), hide_index=True, width="stretch")

if JUDGE.exists():
    st.subheader("Answer quality (LLM judge, 1-5)")
    j = pd.read_csv(JUDGE)
    st.caption("From the latest `scripts.evaluate` run only, which may not match the runs selected above. "
               "Judge agreed with a human reviewer within 1 point on 14/15 spot-checked items (round 1).")
    q = j.pivot_table(index="group", columns="mode", values="score", aggfunc="mean").round(2)
    q.loc["ALL"] = j.groupby("mode")["score"].mean().round(2)
    st.dataframe(q, width="stretch")
