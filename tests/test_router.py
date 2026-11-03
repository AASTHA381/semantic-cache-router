from src.router import route_query


def test_simple_question_goes_small():
    assert route_query("How do I reset my password?", [0.9, 0.6, 0.5]).tier == "small"


def test_comparison_goes_large():
    q = "Compare the Pro and Team plans and explain which is better for a 5-person company."
    assert route_query(q, [0.9, 0.6, 0.5]).tier == "large"


def test_reasons_are_reported():
    r = route_query("Why does sync fail, and should I upgrade?", [0.9, 0.5, 0.4])
    assert r.reasons and r.score >= 2
