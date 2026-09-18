"""
02_knowledge_graph_builder.py
=============================
GraphRAG: Knowledge Graph Construction, Adjacency Lists & Centrality.

Concepts:
- Directed Graph Data Structure with Node Attributes and Typed Edges.
- Adjacency Matrices / Lists (Forward and Reverse lookups).
- Degree Centrality: Identifying the most influential hub entities in the corpus.
"""

import sys
import json
from graph_core import KnowledgeGraph, TripletExtractor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" 🕸️  GRAPHRAG 02: Knowledge Graph Construction & Centrality")
    print("=" * 70)

    kg = TripletExtractor.extract_from_corpus([])

    # 1. Inspect Graph Size
    print(f"\nGraph Topology:")
    print(f"  • Total Entities (Nodes):     {len(kg.nodes)}")
    print(f"  • Total Relationships (Edges): {len(kg.to_dict()['edges'])}")

    # 2. Compute Degree Centrality
    centrality = kg.degree_centrality()
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    print("\nTop Hub Entities by Degree Centrality (Most Connected Concepts):")
    for nid, degree in sorted_nodes[:5]:
        meta = kg.nodes[nid]
        print(f"  • {nid:22} | Degree: {degree} | Type: {meta['type']}")

    # 3. Inspect Specific Node Neighborhood
    hub = "Project NovaStar"
    print(f"\nDirect Relational Edges for '{hub}':")
    for edge in kg.adj.get(hub, []):
        print(f"  [OUTGOING] ──[{edge['relation']}]──► {edge['target']}")
    for edge in kg.rev_adj.get(hub, []):
        print(f"  [INCOMING] ◄──[{edge['relation']}]── {edge['source']}")

    print("\n✅ Knowledge Graph construction and metrics verified!")


if __name__ == "__main__":
    main()
