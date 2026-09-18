"""
05_semantic_cache.py
====================
Semantic Caching: Sub-Millisecond Retrieval & Token Cost Reduction.

Why Semantic Caching?
Traditional key-value caches (like Redis) only match exact string matches.
If User A asks "How do I reset my password?" and User B asks "Where can I change my password?",
a standard cache fails and calls the expensive LLM again.

A Semantic Cache:
1. Converts the incoming query into a token vector representation.
2. Computes cosine similarity against previously answered questions.
3. If similarity >= threshold (e.g. 0.85), returns the cached response instantly.
"""

import sys
import time
from evals_core import SemanticCache

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def simulate_llm_inference(query: str) -> str:
    """Simulates an expensive 500ms network API call to an LLM."""
    time.sleep(0.4)
    return f"Official Answer for '{query}': Navigate to Settings > Security > Reset Credentials."


def main():
    print("=" * 70)
    print(" ⚡  EVALS 05: Semantic Caching for Latency & Token Optimization")
    print("=" * 70)

    # Initialize semantic cache with 80% similarity threshold
    cache = SemanticCache(similarity_threshold=0.80)

    queries = [
        # Query 1: Initial cold query (Cache Miss -> calls LLM)
        "How do I reset my account password?",

        # Query 2: Semantically equivalent question (Different wording -> Should Hit Cache!)
        "Where can I reset my account password?",

        # Query 3: Another close variation (Should Hit Cache!)
        "How to change my account password?",

        # Query 4: Unrelated query (Cache Miss -> calls LLM)
        "What are the office hours for support in Seattle?",

        # Query 5: Paraphrased variation of query 4 (Should Hit Cache!)
        "What are the Seattle support office hours?"
    ]

    for idx, q in enumerate(queries, 1):
        print(f"\n[Query #{idx}]: \"{q}\"")
        start_time = time.time()

        cached_hit = cache.get(q)
        if cached_hit:
            elapsed_ms = (time.time() - start_time) * 1000
            print(f"  ⚡ [CACHE HIT!] (Similarity: {cached_hit['similarity']})")
            print(f"  Matched previous query: \"{cached_hit['cached_query']}\"")
            print(f"  Latency: {elapsed_ms:.2f} ms (Cost: $0.00)")
            print(f"  Response: {cached_hit['response']}")
        else:
            print(f"  ⏳ [CACHE MISS] - Calling upstream LLM API...")
            response = simulate_llm_inference(q)
            cache.set(q, response)
            elapsed_ms = (time.time() - start_time) * 1000
            print(f"  Latency: {elapsed_ms:.2f} ms (API network cost incurred)")
            print(f"  Response: {response}")

    print("\n" + "=" * 70)
    print("✅ Semantic Cache demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
