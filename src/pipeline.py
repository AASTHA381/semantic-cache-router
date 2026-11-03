"""Request pipeline: embed -> cache lookup (+verify) -> retrieve -> route -> generate -> store -> log."""
import time
import uuid

from .cache import SemanticCache
from .config import CONFIG, Config
from .embedder import Embedder, get_embedder
from .llm import cost_usd, make_llm, verify_same_intent
from .metrics import MetricsLogger, RequestLog
from .retriever import DocIndex
from .router import route_query

MODES = {
    "baseline": (False, False),  # always large model, no cache
    "cache": (True, False),  # cache + always large model
    "router": (False, True),  # router only
    "cache_router": (True, True),
}


class Pipeline:
    def __init__(self, mode: str, cfg: Config = CONFIG, embedder: Embedder | None = None,
                 index: DocIndex | None = None, run_id: str | None = None, logger: MetricsLogger | None = None):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {list(MODES)}")
        self.mode, self.cfg = mode, cfg
        self.use_cache, self.use_router = MODES[mode]
        self.embedder = embedder or get_embedder(cfg.embedding_model)
        self.index = index or DocIndex(cfg.docs_path, get_embedder(cfg.retrieval_embedding_model))
        self.cache = SemanticCache(cfg.cache_threshold, cfg.cache_ttl_seconds, cfg.no_cache_patterns)
        self.llm = make_llm(cfg)
        self.run_id = run_id or uuid.uuid4().hex[:8]
        self.logger = logger or MetricsLogger(cfg.log_path)

    def handle(self, query: str, query_id: str = "") -> RequestLog:
        cfg = self.cfg
        t_start = time.perf_counter()
        ts = time.time()

        t0 = time.perf_counter()
        qvec = self.embedder.embed([query])[0]
        embed_ms = (time.perf_counter() - t0) * 1000

        lookup = self.cache.lookup(query, qvec) if self.use_cache else None

        # Verification cost is part of this request's cost whether or not the hit survives.
        verify, v_cost, v_in, v_out, v_ms = "", 0.0, 0, 0, 0.0
        if lookup and lookup.hit and lookup.similarity < cfg.verify_below:
            ok, vres = verify_same_intent(self.llm, cfg.small_model, query, lookup.entry.query)
            verify = "pass" if ok else "fail"
            v_cost = cost_usd(cfg.small_model, vres.input_tokens, vres.output_tokens)
            v_in, v_out, v_ms = vres.input_tokens, vres.output_tokens, vres.latency_ms

        if lookup and lookup.hit and verify != "fail":
            row = RequestLog(
                run_id=self.run_id, mode=self.mode, query_id=query_id, query=query, timestamp=ts,
                cache_hit=True, cache_bypassed=False, similarity=lookup.similarity, verify=verify,
                matched_query=lookup.entry.query, model_used="cache", tier="cache", route_score=None,
                route_reason="cache_hit", retrieved_docs=lookup.entry.meta.get("docs", ""),
                embed_ms=embed_ms, retrieval_ms=0.0, llm_ms=v_ms,
                latency_ms=(time.perf_counter() - t_start) * 1000,
                input_tokens=v_in, output_tokens=v_out, cost_usd=v_cost, provider=cfg.provider,
                answer=lookup.entry.answer,
            )
            self.logger.write(row)
            return row

        t0 = time.perf_counter()
        hits = self.index.search(query, cfg.top_k_hard)
        retrieval_ms = (time.perf_counter() - t0) * 1000

        if self.use_router:
            route = route_query(query, sorted((s for _, s in hits), reverse=True)[: cfg.top_k], cfg.router_hard_score)
            tier, score, reason = route.tier, route.score, ",".join(route.reasons)
        else:
            tier, score, reason = "large", None, "always_large"
        model = cfg.small_model if tier == "small" else cfg.large_model

        # Easy queries get the narrow context; hard ones get the wider one.
        used = hits if tier == "large" else hits[: cfg.top_k]
        chunks = [d.text for d, _ in used]
        doc_ids = "|".join(d.id for d, _ in used)

        res = self.llm.generate(model, query, chunks, cfg.max_output_tokens)

        if self.use_cache:
            self.cache.add(query, qvec, res.text, meta={"docs": doc_ids})

        row = RequestLog(
            run_id=self.run_id, mode=self.mode, query_id=query_id, query=query, timestamp=ts,
            cache_hit=False, cache_bypassed=bool(lookup and lookup.bypassed),
            similarity=lookup.similarity if lookup else None, verify=verify, matched_query="",
            model_used=model.name, tier=tier, route_score=score, route_reason=reason, retrieved_docs=doc_ids,
            embed_ms=embed_ms, retrieval_ms=retrieval_ms, llm_ms=res.latency_ms + v_ms,
            latency_ms=(time.perf_counter() - t_start) * 1000,
            input_tokens=res.input_tokens + v_in, output_tokens=res.output_tokens + v_out,
            cost_usd=cost_usd(model, res.input_tokens, res.output_tokens) + v_cost, provider=cfg.provider,
            answer=res.text,
        )
        self.logger.write(row)
        return row
