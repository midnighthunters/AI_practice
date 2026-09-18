"""
03_graph_traversal_search.py
============================
GraphRAG: Multi-Hop Relational Traversal & Path Finding.

Why Multi-Hop Traversal is Essential:
Traditional vector search looks at individual chunk similarity.
If a question requires connecting Entity A -> Entity B -> Entity C,
vector retrieval often misses Entity C because Entity C has no direct
keyword or semantic overlap with the original question about Entity A.

Graph Traversal solves this by following relational edges across multiple hops.
"""

import sys
import json
from graph_core import KnowledgeGraph, TripletExtractor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" 🕸️  GRAPHRAG 03: Multi-Hop Traversal & Path Finding")
    print("=" * 70)

    kg = TripletExtractor.extract_from_corpus([])

    # Test 1: N-Hop Neighborhood Expansion
    center_entity = "QuantumNova"
    print(f"\n1. Exploring Multi-Hop Neighbors of '{center_entity}':")
    hops_1 = kg.get_neighbors(center_entity, hops=1)
    print(f"  • 1-Hop Neighbors: {len(hops_1)} entities -> {hops_1}")

    hops_2 = kg.get_neighbors(center_entity, hops=2)
    print(f"  • 2-Hop Neighbors: {len(hops_2)} entities -> {hops_2}")

    # Test 2: Multi-Hop Relational Path Finding
    src = "Dr. Elena Vance"
    dst = "Photonic Interconnect"
    print(f"\n2. Finding Shortest Relational Path: '{src}' ──► '{dst}'")
    path = kg.find_path(src, dst)

    if path:
        print(f"  Found connection ({len(path)} hops):")
        for step in path:
            print(f"  ({step['from']}) ──[{step['relation']}]──► ({step['to']})")
    else:
        print("  No path found.")

    # Test 3: Path between distant entities
    src2 = "Dr. Elena Vance"
    dst2 = "Falcon Heavy"
    print(f"\n3. Finding Shortest Relational Path: '{src2}' ──► '{dst2}'")
    path2 = kg.find_path(src2, dst2)
    if path2:
        print(f"  Found connection ({len(path2)} hops):")
        for step in path2:
            print(f"  ({step['from']}) ──[{step['relation']}]──► ({step['to']})")

    print("\n✅ Multi-hop traversal and path finding complete!")


if __name__ == "__main__":
    main()
