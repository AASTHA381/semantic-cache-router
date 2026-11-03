import numpy as np

from src.cache import SemanticCache


def vec(*xs):
    v = np.array(xs, dtype=np.float32)
    return v / np.linalg.norm(v)


def test_hit_and_miss():
    c = SemanticCache(threshold=0.9)
    c.add("a", vec(1, 0), "answer-a")
    assert c.lookup("a2", vec(1, 0.1)).hit
    miss = c.lookup("b", vec(0, 1))
    assert not miss.hit and miss.similarity < 0.9


def test_empty_cache_misses():
    assert not SemanticCache(0.5).lookup("q", vec(1, 0)).hit


def test_bypass_pattern_never_cached():
    c = SemanticCache(0.5, no_cache_patterns=(r"my order #\d+",))
    c.add("where is my order #123", vec(1, 0), "x")
    assert len(c) == 0
    assert c.lookup("where is my order #123", vec(1, 0)).bypassed


def test_ttl_expires_entries():
    c = SemanticCache(0.5, ttl_seconds=-1)
    c.add("a", vec(1, 0), "x")
    assert not c.lookup("a", vec(1, 0)).hit
