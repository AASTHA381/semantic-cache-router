"""Central configuration. Edit values here or override via environment / .env."""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class ModelSpec:
    name: str
    # USD per 1M tokens. Check your provider's current price page; prices change.
    input_per_m: float
    output_per_m: float


@dataclass
class Config:
    # "mock" runs fully offline (no API key). "openai" uses any OpenAI-compatible API.
    provider: str = os.getenv("LLM_PROVIDER", "mock")
    # Cache embeddings: the cache threshold is tuned to this model, so change both together.
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    retrieval_embedding_model: str = os.getenv("RETRIEVAL_EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")

    # Defaults are Groq models with prices verified 2026-11-03 (console.groq.com/docs/model/...). Prices
    # change; override via env vars (SMALL/LARGE_MODEL, *_PRICE_IN/OUT) if they do. Cached-input discounts are not modeled.
    small_model: ModelSpec = field(
        default_factory=lambda: ModelSpec(
            os.getenv("SMALL_MODEL", "openai/gpt-oss-20b"),
            float(os.getenv("SMALL_PRICE_IN", "0.075")), float(os.getenv("SMALL_PRICE_OUT", "0.30")))
    )
    large_model: ModelSpec = field(
        default_factory=lambda: ModelSpec(
            os.getenv("LARGE_MODEL", "openai/gpt-oss-120b"),
            float(os.getenv("LARGE_PRICE_IN", "0.15")), float(os.getenv("LARGE_PRICE_OUT", "0.60")))
    )

    top_k: int = 3
    top_k_hard: int = 6  # used when the router marks a query hard (multi-doc questions)
    max_output_tokens: int = 800

    # Semantic cache
    cache_threshold: float = float(os.getenv("CACHE_THRESHOLD", "0.85"))
    # Hits with similarity below this are double-checked by the small model before reuse. 0 disables.
    verify_below: float = float(os.getenv("VERIFY_BELOW", "0.93"))
    cache_ttl_seconds: float | None = None  # None = never expire
    # Queries matching any of these regexes are never cached (personalized / time-sensitive).
    no_cache_patterns: tuple[str, ...] = (r"\bmy (order|invoice) #?\d+", r"\b(right now|today's|status of)\b")

    # Router: query is "hard" when its score reaches this value
    router_hard_score: int = 2

    docs_path: Path = ROOT / "data" / "docs.json"
    queries_path: Path = ROOT / "data" / "test_queries.json"
    log_path: Path = ROOT / "logs" / "requests.csv"


CONFIG = Config()
