"""One row per request, appended to a CSV that the dashboard (Day 4) will read."""
import csv
from dataclasses import asdict, dataclass, fields
from pathlib import Path


@dataclass
class RequestLog:
    run_id: str
    mode: str
    query_id: str
    query: str
    timestamp: float
    cache_hit: bool
    cache_bypassed: bool
    similarity: float | None
    verify: str  # "", "pass" or "fail"
    matched_query: str
    model_used: str
    tier: str
    route_score: int | None
    route_reason: str
    retrieved_docs: str
    embed_ms: float
    retrieval_ms: float
    llm_ms: float
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    provider: str
    answer: str


class MetricsLogger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, row: RequestLog) -> None:
        new_file = not self.path.exists()
        with self.path.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[x.name for x in fields(RequestLog)])
            if new_file:
                w.writeheader()
            w.writerow(asdict(row))
