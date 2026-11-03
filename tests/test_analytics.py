import pandas as pd

from src.analytics import cumulative_cost, project_monthly, summarize, tier_breakdown


def sample():
    return pd.DataFrame({
        "query_id": ["a", "b", "c", "d"],
        "cache_hit": [False, True, False, False],
        "tier": ["large", "cache", "small", "small"],
        "verify": ["", "pass", "", ""],
        "cost_usd": [0.004, 0.0001, 0.001, 0.001],
        "latency_ms": [1000.0, 20.0, 500.0, 600.0],
    })


def test_summarize():
    s = summarize(sample())
    assert s["requests"] == 4
    assert abs(s["total_cost"] - 0.0061) < 1e-12
    assert s["hit_rate"] == 0.25
    assert abs(s["small_share"] - 2 / 3) < 1e-9
    assert s["verify_pass"] == 1 and s["verify_fail"] == 0


def test_tier_breakdown_and_cumulative():
    tb = tier_breakdown(sample()).set_index("tier")
    assert tb.loc["small", "requests"] == 2
    cum = cumulative_cost(sample(), "x")
    assert abs(cum["cumulative_cost"].iloc[-1] - 0.0061) < 1e-12 and len(cum) == 4


def test_projection():
    assert project_monthly(0.001, 1000) == 30.0
