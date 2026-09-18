import os
from flask import Flask, jsonify, request, send_from_directory
from rag_engine import RAGEngine

app = Flask(__name__, static_folder="static", static_url_path="")
engine = RAGEngine()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/documents", methods=["GET"])
def get_documents():
    return jsonify({
        "success": True,
        "count": len(engine.documents),
        "documents": engine.documents
    })

@app.route("/api/documents", methods=["POST"])
def add_document():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    category = data.get("category", "General").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({"success": False, "error": "Title and content are required."}), 400

    new_doc = engine.add_document(title, category, content)
    return jsonify({
        "success": True,
        "document": new_doc,
        "documents": engine.documents
    })

@app.route("/api/documents/<doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    engine.delete_document(doc_id)
    return jsonify({
        "success": True,
        "documents": engine.documents
    })

@app.route("/api/documents/reset", methods=["POST"])
def reset_documents():
    docs = engine.reset_documents()
    return jsonify({
        "success": True,
        "documents": docs
    })

@app.route("/api/retrieve-only", methods=["POST"])
def retrieve_only():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    top_k = int(data.get("top_k", 2))

    if not query:
        return jsonify({"success": False, "error": "Query is required."}), 400

    scored_docs = engine.retrieve(query, top_k=top_k)
    return jsonify({
        "success": True,
        "query": query,
        "top_k": top_k,
        "documents": scored_docs
    })

@app.route("/api/query", methods=["POST"])
def run_query():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    top_k = int(data.get("top_k", 2))
    model = data.get("model", "gemini-flash-lite-latest")
    mode = data.get("mode", "advanced")

    if not query:
        return jsonify({"success": False, "error": "Query string is required."}), 400

    result = engine.execute_rag_pipeline(query, top_k=top_k, model=model, mode=mode)
    return jsonify({
        "success": True,
        "data": result
    })

@app.route("/api/compare-all", methods=["POST"])
def compare_all():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    top_k = int(data.get("top_k", 2))
    model = data.get("model", "gemini-flash-lite-latest")

    if not query:
        return jsonify({"success": False, "error": "Query string is required."}), 400

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_naive = executor.submit(engine.execute_rag_pipeline, query, top_k=top_k, model=model, mode="naive")
        f_adv = executor.submit(engine.execute_rag_pipeline, query, top_k=top_k, model=model, mode="advanced")
        naive_res = f_naive.result()
        adv_res = f_adv.result()

    return jsonify({
        "success": True,
        "query": query,
        "naive": naive_res,
        "advanced": adv_res
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting RAG Explainer App on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
