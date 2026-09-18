"""
04_hybrid_graphrag_pipeline.py
==============================
Hybrid GraphRAG: Combining Dense Vector Retrieval with Knowledge Graph Expansion.

Comparison:
- Standard RAG: Only retrieves isolated chunks matching query keywords.
- Hybrid GraphRAG:
  1. Retrieves top chunks via text similarity.
  2. Extracts entities mentioned in the query.
  3. Traverses the Knowledge Graph to extract relational triplets.
  4. Augments the prompt with both factual triples and raw text chunks.
"""

import sys
import json
from graph_core import KnowledgeGraph, TripletExtractor, HybridGraphRAG

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" 🕸️  GRAPHRAG 04: Hybrid Graph + Vector RAG Pipeline")
    print("=" * 70)

    # Sample Document Corpus
    corpus = [
        {
            "id": "doc-sat",
            "title": "NovaStar Launch Specs",
            "content": "Project NovaStar is an orbital communications satellite system. Launch is scheduled aboard the Falcon Heavy."
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
        }
    ]

    kg = TripletExtractor.extract_from_corpus(corpus)
    pipeline = HybridGraphRAG(kg, corpus)

    query = "How is Dr. Elena Vance connected to the photonic technology developed at QuantumNova?"
    print(f"\nUser Multi-Hop Question: \"{query}\"\n")

    # Execute Hybrid Retrieval
    result = pipeline.retrieve(query, top_k_docs=2, graph_hops=2)

    print("1. Identified Query Entities:")
    print("  ", result["matched_entities"])

    print(f"\n2. Knowledge Graph Traversal (Expanded {result['connected_entity_count']} connected nodes):")
    for trip in result["graph_triplets"][:5]:
        print(f"   ({trip['subject']}) ──[{trip['predicate']}]──► ({trip['object']})")

    print("\n3. Retrieved Document Chunks:")
    for doc in result["retrieved_documents"]:
        print(f"   [{doc['id']}]: {doc['content']}")

    print("\n4. Final Enriched Prompt Context delivered to LLM:")
    print("=" * 60)
    print(result["enriched_context"])
    print("=" * 60)

    print("\n✅ Hybrid GraphRAG pipeline executed successfully!")


if __name__ == "__main__":
    main()
