"""
01_entity_relation_extraction.py
================================
GraphRAG: Entity & Subject-Predicate-Object (SPO) Triplet Extraction.

In GraphRAG, text is not merely treated as unstructured chunks of characters.
Instead, we extract semantic entities and relationships structured as triplets:
(Subject) ──[Predicate]──► (Object)

Example:
(QuantumNova) ──[OWNS_PROJECT]──► (Project NovaStar)
(Project NovaStar) ──[LAUNCHES_ON]──► (Falcon Heavy)
"""

import sys
import json
from graph_core import KnowledgeGraph, TripletExtractor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" 🕸️  GRAPHRAG 01: Entity & Triplet Extraction")
    print("=" * 70)

    # Document sample
    raw_document = (
        "QuantumNova develops the revolutionary Q-Core optical computing processor. "
        "Dr. Elena Vance serves as the VP of Engineering at QuantumNova and is the "
        "lead architect of Q-Core, which utilizes photonic interconnect technology."
    )

    print(f"\nRaw Unstructured Document:\n\"{raw_document}\"")

    # Build Knowledge Graph through Triplet Extraction
    kg = TripletExtractor.extract_from_corpus([])

    print("\nExtracted Entities by Type:")
    by_type = {}
    for node in kg.nodes.values():
        by_type.setdefault(node["type"], []).append(node["id"])

    for etype, items in by_type.items():
        print(f"  • {etype:12}: {', '.join(items)}")

    print("\nExtracted Subject-Predicate-Object (SPO) Triples:")
    for edge in kg.to_dict()["edges"][:8]:
        print(f"  ({edge['source']}) ──[{edge['relation']}]──► ({edge['target']})")

    print("\n✅ Triplet extraction complete!")


if __name__ == "__main__":
    main()
