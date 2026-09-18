"""
app.py
======
Interactive GraphRAG Studio, Knowledge Graph Visualizer & Query Engine.
Runs on Port 5005.
"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from graph_core import KnowledgeGraph, TripletExtractor, HybridGraphRAG

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

DOCS = [
    {
        "id": "doc-sat",
        "title": "NovaStar Launch Specs",
        "content": "Project NovaStar is an orbital communications satellite system. Launch is scheduled aboard the Falcon Heavy rocket."
    },
    {
        "id": "doc-qcore",
        "title": "Quantum Computing Division",
        "content": "QuantumNova developed the Q-Core optical computing processor utilizing photonic silicon interconnects."
    },
    {
        "id": "doc-staff",
        "title": "Leadership Directory",
        "content": "Dr. Elena Vance is VP of Engineering at QuantumNova and serves as chief architect for optical computing platforms."
    },
    {
        "id": "doc-contractor",
        "title": "Vendor Partnerships",
        "content": "Orbital Dynamics Corp is the primary contractor manufacturing the satellite bus and Ka-band transponders."
    }
]

kg = TripletExtractor.extract_from_corpus(DOCS)
hybrid_rag = HybridGraphRAG(kg, DOCS)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/graph/data", methods=["GET"])
def get_graph_data():
    centrality = kg.degree_centrality()
    data = kg.to_dict()
    for n in data["nodes"]:
        n["degree"] = centrality.get(n["id"], 0)
    return jsonify(data)


@app.route("/api/graph/path", methods=["POST"])
def find_path():
    data = request.json or {}
    src = data.get("source", "").strip()
    tgt = data.get("target", "").strip()
    path = kg.find_path(src, tgt)
    return jsonify({
        "source": src,
        "target": tgt,
        "found": path is not None,
        "path": path or []
    })


@app.route("/api/graph/query", methods=["POST"])
def graph_query():
    data = request.json or {}
    q = data.get("query", "").strip()
    if not q:
        return jsonify({"error": "Query required"}), 400

    hops = int(data.get("hops", 1))
    retrieval = hybrid_rag.retrieve(q, top_k_docs=2, graph_hops=hops)

    # Deterministic synthesis
    synthesis = (
        f"Hybrid GraphRAG Answer for: \"{q}\"\n\n"
        f"Key Entities Connected: {', '.join(retrieval['matched_entities']) or 'General Query'}\n"
        f"Relational Graph Traversal:\n" +
        ("\n".join([f"• {t}" for t in retrieval['graph_triplets_formatted'][:6]]) or "• None directly linked.") +
        f"\n\nDocument Grounding Chunks: {len(retrieval['retrieved_documents'])} retrieved."
    )

    return jsonify({
        "query": q,
        "retrieval": retrieval,
        "synthesis": synthesis
    })


if __name__ == "__main__":
    print("🚀 Starting GraphRAG Studio on http://127.0.0.1:5005")
    app.run(host="127.0.0.1", port=5005, debug=False)
