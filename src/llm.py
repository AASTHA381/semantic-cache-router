"""LLM clients. `mock` is offline and deterministic so the pipeline can be tested without an API key.
Mock results are NOT real model quality or cost evidence; use provider=openai for your actual evaluation."""
import os
import time
from dataclasses import dataclass

from openai import RateLimitError

from .config import Config, ModelSpec

SYSTEM_PROMPT = (
    "You are a support assistant for StashBox. Answer using only the provided context. "
    "If the context does not contain the answer, say you don't know."
)


@dataclass
class LLMResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


def build_prompt(query: str, context_chunks: list[str]) -> str:
    ctx = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(context_chunks))
    return f"Context:\n{ctx}\n\nQuestion: {query}"


def _approx_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


class MockLLM:
    """Returns the top context chunk as the 'answer'; token counts are word-count estimates."""

    def chat(self, model: ModelSpec, system: str, user: str, max_tokens: int) -> LLMResult:
        t0 = time.perf_counter()
        if "same answer" in user:  # verifier prompt: the mock always approves
            answer = "yes"
        else:
            answer = user.split("[1] ", 1)[1].split("\n\n", 1)[0] if "[1] " in user else "I don't know."
        return LLMResult(answer, _approx_tokens(system + user), min(_approx_tokens(answer), max_tokens),
                         (time.perf_counter() - t0) * 1000)

    def generate(self, model: ModelSpec, query: str, context_chunks: list[str], max_tokens: int) -> LLMResult:
        return self.chat(model, SYSTEM_PROMPT, build_prompt(query, context_chunks), max_tokens)


class OpenAILLM:
    """Any OpenAI-compatible chat API (OpenAI itself, or Groq via base_url)."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, model: ModelSpec, system: str, user: str, max_tokens: int) -> LLMResult:
        t0 = time.perf_counter()
        extra = {"reasoning_effort": "low"} if "gpt-oss" in model.name else {}
        for attempt in range(5):
            try:
                resp = self._client.chat.completions.create(
                    model=model.name,
                    max_tokens=max_tokens,
                    temperature=0,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    **extra,
                )
                break
            except RateLimitError:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        # Latency covers the successful call plus any retry waits.
        latency = (time.perf_counter() - t0) * 1000
        return LLMResult(resp.choices[0].message.content or "", resp.usage.prompt_tokens,
                         resp.usage.completion_tokens, latency)

    def generate(self, model: ModelSpec, query: str, context_chunks: list[str], max_tokens: int) -> LLMResult:
        return self.chat(model, SYSTEM_PROMPT, build_prompt(query, context_chunks), max_tokens)


VERIFY_SYSTEM = (
    "You judge whether two customer questions are interchangeable. Reply with exactly one word: yes or no."
)


def verify_same_intent(llm, model: ModelSpec, new_query: str, cached_query: str, max_tokens: int = 300) -> tuple[bool, LLMResult]:
    """True only if one answer would be fully correct for both questions (strict: anything but 'yes' is a no)."""
    user = (
        f"Question A: {cached_query}\nQuestion B: {new_query}\n\n"
        "Would the same answer be fully correct and complete for both questions? "
        "Different topics, different scope (e.g. account vs file, mobile vs desktop) or different "
        "specifics mean no. Reply yes or no."
    )
    res = llm.chat(model, VERIFY_SYSTEM, user, max_tokens)
    return res.text.strip().lower().startswith("yes"), res


def make_llm(cfg: Config):
    if cfg.provider == "openai":
        return OpenAILLM()
    if cfg.provider == "groq":
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to .env (never commit it).")
        return OpenAILLM(api_key=key, base_url="https://api.groq.com/openai/v1")
    if cfg.provider == "mock":
        return MockLLM()
    raise ValueError(f"Unknown LLM_PROVIDER: {cfg.provider}")


def cost_usd(model: ModelSpec, input_tokens: int, output_tokens: int) -> float:
    return (input_tokens * model.input_per_m + output_tokens * model.output_per_m) / 1_000_000
