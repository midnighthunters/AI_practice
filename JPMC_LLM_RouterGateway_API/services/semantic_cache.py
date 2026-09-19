"""
In-Memory Semantic Cache for JPMorgan Chase LLM Suite
Delivers sub-10ms response times on frequent queries (e.g., standard policy queries,
statutory ratios, definition lookups) by matching query intent via cosine similarity.
"""

import math
import re
import time
from typing import Dict, List, Optional, Tuple
from schemas import CacheStats

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.88):
        self.similarity_threshold = similarity_threshold
        # entries: list of dicts: {"query": str, "tokens": set, "vector": dict, "response": str, "model": str, "timestamp": float}
        self.entries: List[Dict] = []
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.tokens_saved = 0
        self.usd_saved = 0.0
        self.cache_latencies: List[float] = []

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b\w+\b', text) if len(w) > 2]

    def _get_vector(self, tokens: List[str]) -> Dict[str, float]:
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        # Normalize
        norm = math.sqrt(sum(v * v for v in tf.values()))
        if norm > 0:
            for k in tf:
                tf[k] /= norm
        return tf

    def _cosine_similarity(self, v1: Dict[str, float], v2: Dict[str, float]) -> float:
        intersection = set(v1.keys()) & set(v2.keys())
        return sum(v1[k] * v2[k] for k in intersection)

    def lookup(self, query: str) -> Tuple[Optional[str], Optional[str], float]:
        """Returns (cached_response, model_name, similarity_score) or (None, None, 0.0)"""
        start = time.perf_counter()
        self.total_requests += 1

        tokens = self._tokenize(query)
        if not tokens:
            self.cache_misses += 1
            return None, None, 0.0

        q_vec = self._get_vector(tokens)
        best_match = None
        best_sim = 0.0

        for entry in self.entries:
            sim = self._cosine_similarity(q_vec, entry["vector"])
            if sim > best_sim:
                best_sim = sim
                best_match = entry

        latency_ms = (time.perf_counter() - start) * 1000
        self.cache_latencies.append(latency_ms)

        if best_match and best_sim >= self.similarity_threshold:
            self.cache_hits += 1
            # Estimate tokens saved (approx 1 token per 4 chars)
            saved = len(best_match["response"]) // 4 + len(query) // 4
            self.tokens_saved += saved
            self.usd_saved += (saved / 1000.0) * 0.005 # $5 per 1M tokens approx
            return best_match["response"], best_match["model"], best_sim
        else:
            self.cache_misses += 1
            return None, None, best_sim

    def store(self, query: str, response: str, model: str):
        tokens = self._tokenize(query)
        q_vec = self._get_vector(tokens)
        self.entries.append({
            "query": query,
            "vector": q_vec,
            "response": response,
            "model": model,
            "timestamp": time.time()
        })
        # Keep cache bounded to 1,000 active entries
        if len(self.entries) > 1000:
            self.entries.pop(0)

    def get_stats(self) -> CacheStats:
        hit_ratio = (self.cache_hits / self.total_requests * 100) if self.total_requests > 0 else 0.0
        avg_lat = (sum(self.cache_latencies) / len(self.cache_latencies)) if self.cache_latencies else 0.0
        return CacheStats(
            total_requests=self.total_requests,
            cache_hits=self.cache_hits,
            cache_misses=self.cache_misses,
            hit_ratio_pct=round(hit_ratio, 2),
            total_tokens_saved=self.tokens_saved,
            total_usd_saved=round(self.usd_saved, 4),
            avg_cache_latency_ms=round(avg_lat, 2)
        )

# Global semantic cache instance
semantic_cache = SemanticCache()

# Preload with common JPMorgan banking policy queries
semantic_cache.store(
    query="What is the statutory CET1 capital ratio requirement under Basel III for JPMC?",
    response="JPMorgan Chase is subject to a Basel III Common Equity Tier 1 (CET1) capital requirement of 11.9% as of 2024, including the G-SIB surcharge and stress capital buffer (SCB).",
    model="JPMC-Internal-FinLLM-Cache"
)
semantic_cache.store(
    query="What is the definition of ROCE in Corporate & Investment Banking?",
    response="Return on Common Equity (ROCE) measures net income available to common stockholders as a percentage of average common stockholders' equity, reflecting capital efficiency.",
    model="JPMC-Internal-FinLLM-Cache"
)
