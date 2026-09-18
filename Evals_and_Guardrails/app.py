"""
app.py
======
Interactive LLM Evaluations, Safety Guardrails & Semantic Cache Studio.
Runs on Port 5004.
"""

import os
import sys
import json
import time
from flask import Flask, jsonify, request, send_from_directory

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from evals_core import LLMAsAJudge, RAGTriadEvaluator, SafetyGuardrails, SemanticCache

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
cache = SemanticCache(similarity_threshold=0.75)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/eval/judge", methods=["POST"])
def eval_judge():
    data = request.json or {}
    q = data.get("question", "")
    a = data.get("answer", "")
    ctx = data.get("context", "")
    res = LLMAsAJudge.evaluate(q, a, ctx)
    return jsonify(res)


@app.route("/api/eval/rag-triad", methods=["POST"])
def eval_rag_triad():
    data = request.json or {}
    q = data.get("question", "")
    contexts = data.get("contexts", [])
    a = data.get("answer", "")
    res = RAGTriadEvaluator.evaluate_triad(q, contexts, a)
    return jsonify(res)


@app.route("/api/guard/input", methods=["POST"])
def guard_input():
    data = request.json or {}
    text = data.get("text", "")
    res = SafetyGuardrails.scan_input(text)
    return jsonify(res)


@app.route("/api/guard/output", methods=["POST"])
def guard_output():
    data = request.json or {}
    text = data.get("text", "")
    schema = data.get("schema")
    res = SafetyGuardrails.scan_output(text, schema)
    return jsonify(res)


@app.route("/api/cache/query", methods=["POST"])
def cache_query():
    data = request.json or {}
    q = data.get("query", "").strip()
    if not q:
        return jsonify({"error": "Query required"}), 400

    start = time.time()
    hit = cache.get(q)
    if hit:
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return jsonify({
            "cache_hit": True,
            "similarity": hit["similarity"],
            "matched_query": hit["cached_query"],
            "response": hit["response"],
            "latency_ms": elapsed_ms,
            "token_cost": 0.0
        })

    # Simulate generating fresh answer
    fresh_response = f"Generated Answer for '{q}': QuantumNova delivers unified AI infrastructure."
    cache.set(q, fresh_response)
    elapsed_ms = round((time.time() - start) * 1000 + 350.0, 2)
    return jsonify({
        "cache_hit": False,
        "similarity": 0.0,
        "matched_query": None,
        "response": fresh_response,
        "latency_ms": elapsed_ms,
        "token_cost": 0.0004
    })


if __name__ == "__main__":
    print("🚀 Starting Evaluations & Guardrails Studio on http://127.0.0.1:5004")
    app.run(host="127.0.0.1", port=5004, debug=False)
