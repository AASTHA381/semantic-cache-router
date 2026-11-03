"""Aggregations for the dashboard (pure pandas so they can be unit tested)."""
import pandas as pd


def load_requests(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["cache_hit"] = df["cache_hit"].astype(str).str.lower() == "true"
    df["verify"] = df["verify"].fillna("")
    return df.sort_values(["run_id", "timestamp"]).reset_index(drop=True)


def run_table(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("run_id").agg(mode=("mode", "first"), n=("query_id", "count"), started=("timestamp", "min"))
    return g.sort_values("started", ascending=False).reset_index()


def summarize(run: pd.DataFrame) -> dict:
    n = len(run)
    llm_rows = run[~run["cache_hit"]]
    lat = run["latency_ms"]
    return {
        "requests": n,
        "total_cost": run["cost_usd"].sum(),
        "avg_cost": run["cost_usd"].mean() if n else 0.0,
        "hit_rate": run["cache_hit"].mean() if n else 0.0,
        "small_share": (llm_rows["tier"] == "small").mean() if len(llm_rows) else 0.0,
        "p50_ms": lat.quantile(0.5) if n else 0.0,
        "p95_ms": lat.quantile(0.95) if n else 0.0,
        "verify_pass": int((run["verify"] == "pass").sum()),
        "verify_fail": int((run["verify"] == "fail").sum()),
    }


def tier_breakdown(run: pd.DataFrame) -> pd.DataFrame:
    g = run.groupby("tier").agg(requests=("query_id", "count"), cost=("cost_usd", "sum"),
                                p50_ms=("latency_ms", lambda s: s.quantile(0.5)),
                                p95_ms=("latency_ms", lambda s: s.quantile(0.95)))
    return g.reset_index()


def cumulative_cost(run: pd.DataFrame, label: str) -> pd.DataFrame:
    out = pd.DataFrame({"request": range(1, len(run) + 1), "cumulative_cost": run["cost_usd"].cumsum().values})
    out["run"] = label
    return out


def project_monthly(avg_cost: float, requests_per_day: float, days: int = 30) -> float:
    return avg_cost * requests_per_day * days
