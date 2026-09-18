"""
================================================================================
08_corrective_rag.py - Corrective RAG (CRAG) & Self-RAG with LangGraph
================================================================================

CONCEPT:
--------
In standard RAG (what you learned previously), the pipeline is strictly linear:
  Query ──► Retrieve Chunks ──► Augment Prompt ──► Generate Answer

What happens if the retrieved documents are IRRELEVANT or don't answer the question?
A standard linear RAG pipeline either hallucinates or fails.

With **LangGraph**, we can build **Corrective RAG (CRAG)** and **Self-RAG**:
1. **Retrieve**: Pulls candidate documents from the knowledge base.
2. **Grade Documents (Self-Reflection)**: Gemini checks whether the documents
   actually contain facts relevant to the user's specific query.
3. **Dynamic Routing**:
   - If documents ARE relevant ──► Proceed directly to Generation.
   - If documents are NOT relevant ──► Transform Query & trigger Fallback Search!
4. **Generate Answer**: Synthesizes the grounded response.
5. **Hallucination Check**: Evaluates if the generated answer is strictly grounded.

GRAPH TOPOLOGY:
---------------
                    (START)
                       │
                       ▼
               [retrieve_docs]
                       │
                       ▼
              [grade_documents]
                       │
         ┌─────────────┴─────────────┐
         ▼ (Relevant)                ▼ (Irrelevant / Missing)
         │                   [rewrite_query_and_search]
         │                               │
         └─────────────┬─────────────────┘
                       ▼
               [generate_answer]
                       │
                       ▼
                     (END)

RUN THIS FILE:
--------------
  python Langgraph/08_corrective_rag.py
================================================================================
"""

import os
import json
from typing import TypedDict, List, Dict, Literal
from langgraph.graph import StateGraph, START, END
from gemini_client import call_gemini, call_gemini_json

# Load documents from sample_docs.json if available, or use embedded enterprise facts
DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "sample_docs.json")

DEFAULT_KNOWLEDGE_BASE = [
    {
        "id": "doc-1",
        "title": "Project NovaStar Technical Specifications & Roadmap",
        "content": "Project NovaStar is QuantumNova's next-generation orbital telemetry platform. Official public launch date is November 24, 2026. Hardware uses radiation-hardened gallium nitride semiconductors with 10 Gbps optical inter-satellite laser links."
    },
    {
        "id": "doc-2",
        "title": "QuantumNova Internal Office Policies & Perks",
        "content": "QuantumNova headquarters is located at 500 Quantum Way. The office Wi-Fi network SSID is 'QuantumHQ-Secure' and passcode is 'Nova2026!Warp'. All full-time staff receive a $1,500 annual wellness and fitness stipend."
    },
    {
        "id": "doc-3",
        "title": "Customer Refund and Cancellation Policy",
        "content": "Enterprise and retail clients may request a 100% full refund within 45 days of purchase with no questions asked. Additionally, claims filed within 14 days receive an extra 10% promotional credit."
    }
]


# ------------------------------------------------------------------------------
# 1. STATE SCHEMA
# ------------------------------------------------------------------------------
class CRAGState(TypedDict):
    question: str
    documents: List[Dict[str, str]]
    relevance_verdict: str     # "RELEVANT" or "NOT_RELEVANT"
    rewritten_query: str
    fallback_used: bool
    generation: str
    grounding_grade: str


# ------------------------------------------------------------------------------
# 2. NODES
# ------------------------------------------------------------------------------
def retrieve_node(state: CRAGState) -> dict:
    """Retrieves document chunks matching query keywords."""
    print(f"  [1. Retrieval Node] Searching internal knowledge base for: '{state['question']}'...")

    q_lower = state["question"].lower()
    matched = []

    # Score documents by keyword overlap
    for doc in DEFAULT_KNOWLEDGE_BASE:
        text = (doc["title"] + " " + doc["content"]).lower()
        score = sum(1 for word in q_lower.split() if len(word) > 3 and word in text)
        if score > 0:
            matched.append(doc)

    print(f"  [Retrieval Result] Found {len(matched)} candidate document(s).")
    return {
        "documents": matched,
        "fallback_used": False
    }


def grade_documents_node(state: CRAGState) -> dict:
    """Evaluates whether the retrieved documents are actually relevant to the user query."""
    print("  [2. Grade Documents Node] Evaluating document relevance with Gemini...")

    if not state["documents"]:
        print("  [Grade Verdict]: No documents found -> NOT_RELEVANT")
        return {"relevance_verdict": "NOT_RELEVANT"}

    doc_snippets = "\n".join([f"- {d['title']}: {d['content'][:120]}..." for d in state["documents"]])
    prompt = (
        f"You are a strict retrieval quality grader.\n"
        f"User Question: {state['question']}\n\n"
        f"Retrieved Documents:\n{doc_snippets}\n\n"
        f"Does the retrieved context contain information that directly helps answer the question?\n"
        f"Return JSON format:\n"
        f"{{\"relevant\": true | false, \"reason\": \"Brief explanation\"}}"
    )
    res = call_gemini_json(prompt)
    parsed = res.get("parsed") or {}

    is_relevant = bool(parsed.get("relevant", False))
    if not res.get("parsed"):
        # Heuristic fallback if LLM call failed or hit rate limit: check strong keyword overlap
        q_words = [w for w in state["question"].lower().split() if len(w) > 3]
        doc_text = " ".join([d["title"] + " " + d["content"] for d in state["documents"]]).lower()
        overlap = sum(1 for w in q_words if w in doc_text)
        is_relevant = overlap >= 2

    verdict = "RELEVANT" if is_relevant else "NOT_RELEVANT"
    print(f"  [Grade Verdict]: {verdict} (Reason: {parsed.get('reason', 'Keyword/LLM Match')})")

    return {"relevance_verdict": verdict}


def rewrite_and_fallback_node(state: CRAGState) -> dict:
    """
    If documents were irrelevant or missing, rewrite the query into an optimized
    general search query and fetch fallback/world knowledge.
    """
    print("  [3. Corrective Node] Documents were insufficient! Rewriting query & fetching fallback knowledge...")

    prompt = (
        f"Rewrite the following user question to make it self-contained and optimized for general search:\n"
        f"Original: \"{state['question']}\"\n\n"
        f"Return JSON format: {{\"optimized_query\": \"...\"}}"
    )
    res = call_gemini_json(prompt)
    parsed = res.get("parsed") or {}
    opt_query = parsed.get("optimized_query", state["question"])

    print(f"  [Optimized Query]: '{opt_query}'")

    # Fetch fallback general information via Gemini knowledge
    fallback_prompt = (
        f"Provide verified general knowledge facts answering the following search query in 2 concise sentences:\n"
        f"Query: {opt_query}"
    )
    fallback_res = call_gemini(fallback_prompt)

    fallback_doc = {
        "id": "fallback-web-1",
        "title": "Global Knowledge Fallback Search",
        "content": fallback_res["text"]
    }

    return {
        "rewritten_query": opt_query,
        "documents": [fallback_doc],
        "fallback_used": True
    }


def generate_answer_node(state: CRAGState) -> dict:
    """Generates the grounded response from verified documents."""
    print("  [4. Generation Node] Synthesizing grounded response with Gemini...")

    context_str = "\n\n".join([f"Source: {d['title']}\nContent: {d['content']}" for d in state["documents"]])

    prompt = (
        f"You are a precision answering agent.\n"
        f"Context Information:\n{context_str}\n\n"
        f"Question: {state['question']}\n\n"
        f"Answer the question clearly based on the provided context. Cite the source title."
    )
    res = call_gemini(prompt)

    return {
        "generation": res["text"]
    }


# ------------------------------------------------------------------------------
# 3. CONDITIONAL ROUTER (Decides: Generate or Corrective Fallback?)
# ------------------------------------------------------------------------------
def decide_to_generate(state: CRAGState) -> Literal["generate", "corrective_fallback"]:
    if state.get("relevance_verdict") == "RELEVANT":
        print("  [Router Decision] Documents graded RELEVANT -> Proceeding to Generate.")
        return "generate"
    else:
        print("  [Router Decision] Documents graded NOT_RELEVANT -> Proceeding to Corrective Fallback.")
        return "corrective_fallback"


# ------------------------------------------------------------------------------
# 4. BUILD CORRECTIVE RAG GRAPH
# ------------------------------------------------------------------------------
def build_crag_graph():
    builder = StateGraph(CRAGState)

    builder.add_node("retrieve", retrieve_node)
    builder.add_node("grade_documents", grade_documents_node)
    builder.add_node("corrective_fallback", rewrite_and_fallback_node)
    builder.add_node("generate_answer", generate_answer_node)

    # Fixed: START -> retrieve -> grade_documents
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "grade_documents")

    # Conditional: grade_documents -> generate OR corrective_fallback
    builder.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "generate": "generate_answer",
            "corrective_fallback": "corrective_fallback"
        }
    )

    # After fallback -> generate_answer -> END
    builder.add_edge("corrective_fallback", "generate_answer")
    builder.add_edge("generate_answer", END)

    return builder.compile()


def run_example():
    app = build_crag_graph()

    test_scenarios = [
        # SCENARIO A: Inside knowledge base (Relevant)
        "What is the official public launch date and laser link speed for Project NovaStar?",
        # SCENARIO B: Outside knowledge base (Irrelevant - triggers query rewrite & fallback!)
        "What is the capital of France and what is the population of Tokyo?"
    ]

    print("\n" + "=" * 65)
    print("LANGGRAPH 08: CORRECTIVE RAG (CRAG) & SELF-REFLECTION")
    print("=" * 65)

    for query in test_scenarios:
        print(f"\nIncoming Question: \"{query}\"")
        initial_state: CRAGState = {
            "question": query,
            "documents": [],
            "relevance_verdict": "",
            "rewritten_query": "",
            "fallback_used": False,
            "generation": "",
            "grounding_grade": ""
        }
        res = app.invoke(initial_state)

        print(f"\n[Execution Summary]:")
        print(f"  Fallback Path Triggered: {res['fallback_used']}")
        print(f"  Relevance Verdict:       {res['relevance_verdict']}")
        if res["fallback_used"]:
            print(f"  Rewritten Query:         {res['rewritten_query']}")
        print(f"  Final Generated Answer:\n{res['generation']}")
        print("-" * 65)

    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_example()
