"""Heuristic query-difficulty router. Transparent and cheap; swap for a classifier once you have labels."""
import re
from dataclasses import dataclass

HARD_KEYWORDS = re.compile(
    r"\b(compare|comparison|difference|versus|vs\.?|trade-?offs?|recommend|should i|"
    r"why|walk me through|step by step|explain|both|which one|pros and cons)\b",
    re.I,
)


@dataclass
class Route:
    tier: str  # "small" | "large"
    score: int
    reasons: list[str]


def route_query(query: str, retrieval_scores: list[float], hard_score: int = 2) -> Route:
    score, reasons = 0, []

    words = len(query.split())
    if words > 20:
        score += 1
        reasons.append(f"long_query({words}w)")

    kw = set(m.group(0).lower() for m in HARD_KEYWORDS.finditer(query))
    if kw:
        score += min(len(kw), 2)
        reasons.append("keywords:" + "|".join(sorted(kw)))

    if len(re.findall(r"\band\b", query, re.I)) >= 2 or query.count("?") > 1 or "," in query:
        score += 1
        reasons.append("multi_part")

    # Several retrieved docs with similar relevance suggests the answer spans multiple sources.
    if len(retrieval_scores) >= 3 and retrieval_scores[2] >= 0.85 * retrieval_scores[0]:
        score += 1
        reasons.append("multi_doc_context")

    tier = "large" if score >= hard_score else "small"
    return Route(tier, score, reasons or ["default_simple"])
