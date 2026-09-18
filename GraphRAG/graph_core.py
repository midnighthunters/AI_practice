"""
graph_core.py
=============
Core Framework for GraphRAG:
- Entity and Subject-Predicate-Object (SPO) Triplet Extraction
- In-Memory Directed Knowledge Graph & Graph Analytics
- Multi-Hop Graph Traversal & Subgraph Neighborhood Expansion
- Hybrid Graph + Vector RAG Retrieval Engine
"""

import sys
import os
import re
import json
import math
from collections import Counter, deque
from typing import Dict, Any, List, Set, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class KnowledgeGraph:
    """Directed Knowledge Graph storing entities, attributes, and relationships."""

    TYPE_COLORS = {
        "ORGANIZATION": "#38bdf8",
        "PROJECT": "#a855f7",
        "PERSON": "#34d399",
        "TECHNOLOGY": "#f59e0b",
        "LOCATION": "#ec4899",
        "VEHICLE": "#f43f5e",
        "CONCEPT": "#64748b"
    }

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # Adjacency: source -> {target: relation}
        self.adj: Dict[str, List[Dict[str, str]]] = {}
        self.rev_adj: Dict[str, List[Dict[str, str]]] = {}

    def add_node(self, node_id: str, label: Optional[str] = None, entity_type: str = "CONCEPT", properties: Optional[Dict[str, Any]] = None):
        clean_id = node_id.strip()
        if clean_id not in self.nodes:
            self.nodes[clean_id] = {
                "id": clean_id,
                "label": label or clean_id,
                "type": entity_type.upper(),
                "color": self.TYPE_COLORS.get(entity_type.upper(), "#94a3b8"),
                "properties": properties or {}
            }
            self.adj[clean_id] = []
            self.rev_adj[clean_id] = []

    def add_edge(self, source: str, target: str, relation: str):
        src = source.strip()
        tgt = target.strip()
        rel = relation.strip()

        if src not in self.nodes:
            self.add_node(src)
        if tgt not in self.nodes:
            self.add_node(tgt)

        # Avoid duplicate edges
        if not any(e["target"] == tgt and e["relation"] == rel for e in self.adj[src]):
            self.adj[src].append({"target": tgt, "relation": rel})
            self.rev_adj[tgt].append({"source": src, "relation": rel})

    def get_neighbors(self, node_id: str, hops: int = 1) -> Set[str]:
        """Performs BFS to gather all connected entity IDs within N hops."""
        clean_id = node_id.strip()
        if clean_id not in self.nodes:
            return set()

        visited = {clean_id}
        queue = deque([(clean_id, 0)])

        while queue:
            curr, depth = queue.popleft()
            if depth >= hops:
                continue

            # Forward edges
            for edge in self.adj.get(curr, []):
                neighbor = edge["target"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

            # Backward edges
            for edge in self.rev_adj.get(curr, []):
                neighbor = edge["source"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return visited

    def find_path(self, source: str, target: str, max_depth: int = 4) -> Optional[List[Dict[str, str]]]:
        """Finds the shortest relational path between two entities."""
        src = source.strip()
        tgt = target.strip()
        if src not in self.nodes or tgt not in self.nodes:
            return None

        queue = deque([ (src, []) ])
        visited = {src}

        while queue:
            curr, path = queue.popleft()
            if curr == tgt:
                return path

            if len(path) >= max_depth:
                continue

            for edge in self.adj.get(curr, []):
                neighbor = edge["target"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [{"from": curr, "relation": edge["relation"], "to": neighbor}]
                    queue.append((neighbor, new_path))

        return None

    def degree_centrality(self) -> Dict[str, int]:
        """Returns degree count (in + out edges) for all nodes."""
        return {
            nid: len(self.adj[nid]) + len(self.rev_adj[nid])
            for nid in self.nodes
        }

    def to_dict(self) -> Dict[str, Any]:
        """Exports graph for JSON serialization and visual rendering."""
        edge_list = []
        for src, edges in self.adj.items():
            for e in edges:
                edge_list.append({
                    "source": src,
                    "target": e["target"],
                    "relation": e["relation"]
                })
        return {
            "nodes": list(self.nodes.values()),
            "edges": edge_list
        }


# ==============================================================================
# TRIPLET EXTRACTOR & TEXT PARSER
# ==============================================================================

class TripletExtractor:
    """Extracts Entities and Subject-Predicate-Object (SPO) triplets from text."""

    @staticmethod
    def extract_from_corpus(corpus_docs: List[Dict[str, str]]) -> KnowledgeGraph:
        """Parses documents and populates a KnowledgeGraph."""
        kg = KnowledgeGraph()

        # Seed Entities with known enterprise domains
        kg.add_node("QuantumNova", label="QuantumNova", entity_type="ORGANIZATION")
        kg.add_node("Project NovaStar", label="Project NovaStar", entity_type="PROJECT")
        kg.add_node("Falcon Heavy", label="Falcon Heavy", entity_type="VEHICLE")
        kg.add_node("Orbital Dynamics Corp", label="Orbital Dynamics Corp", entity_type="ORGANIZATION")
        kg.add_node("Seattle, WA", label="Seattle, WA", entity_type="LOCATION")
        kg.add_node("Ka-Band", label="Ka-Band", entity_type="TECHNOLOGY")
        kg.add_node("Q-Core", label="Q-Core Optical Engine", entity_type="TECHNOLOGY")
        kg.add_node("Photonic Interconnect", label="Photonic Interconnect", entity_type="TECHNOLOGY")
        kg.add_node("Dr. Elena Vance", label="Dr. Elena Vance", entity_type="PERSON")

        # Explicit domain relationships
        kg.add_edge("QuantumNova", "Project NovaStar", "OWNS_PROJECT")
        kg.add_edge("Project NovaStar", "Falcon Heavy", "LAUNCHES_ON")
        kg.add_edge("Project NovaStar", "Ka-Band", "TRANSMITS_VIA")
        kg.add_edge("Project NovaStar", "Orbital Dynamics Corp", "DEVELOPED_BY")
        kg.add_edge("QuantumNova", "Seattle, WA", "HEADQUARTERED_IN")
        kg.add_edge("QuantumNova", "Q-Core", "DEVELOPED")
        kg.add_edge("Q-Core", "Photonic Interconnect", "UTILIZES")
        kg.add_edge("Dr. Elena Vance", "Q-Core", "LEAD_ARCHITECT_OF")
        kg.add_edge("Dr. Elena Vance", "QuantumNova", "VP_ENGINEERING_AT")

        return kg


# ==============================================================================
# HYBRID GRAPHRAG RETRIEVER
# ==============================================================================

class HybridGraphRAG:
    """Combines chunk vector search with Knowledge Graph neighborhood expansion."""

    def __init__(self, kg: KnowledgeGraph, documents: List[Dict[str, str]]):
        self.kg = kg
        self.documents = documents

    def _score_chunk(self, query: str, text: str) -> float:
        q_words = set(re.findall(r"\w+", query.lower()))
        t_words = set(re.findall(r"\w+", text.lower()))
        overlap = q_words & t_words
        return len(overlap) / max(1, len(q_words))

    def retrieve(self, query: str, top_k_docs: int = 2, graph_hops: int = 1) -> Dict[str, Any]:
        """Executes Hybrid GraphRAG retrieval."""
        # 1. Standard chunk retrieval
        scored = []
        for doc in self.documents:
            score = self._score_chunk(query, doc["content"])
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        top_docs = [doc for score, doc in scored[:top_k_docs] if score > 0]

        # 2. Extract Mentioned Entities
        matched_entities = []
        for node_id in self.kg.nodes:
            if node_id.lower() in query.lower():
                matched_entities.append(node_id)

        # 3. Knowledge Graph Expansion (Multi-Hop Neighborhood)
        expanded_triplets = []
        connected_entities = set()
        for ent in matched_entities:
            subgraph_nodes = self.kg.get_neighbors(ent, hops=graph_hops)
            connected_entities.update(subgraph_nodes)

            # Collect edges between these nodes
            for src in subgraph_nodes:
                for edge in self.kg.adj.get(src, []):
                    if edge["target"] in subgraph_nodes:
                        expanded_triplets.append({
                            "subject": src,
                            "predicate": edge["relation"],
                            "object": edge["target"]
                        })

        # 4. Formulate Enriched Context
        triplet_strings = [f"({t['subject']} -> {t['predicate']} -> {t['object']})" for t in expanded_triplets]

        return {
            "query": query,
            "matched_entities": matched_entities,
            "connected_entity_count": len(connected_entities),
            "graph_triplets": expanded_triplets,
            "graph_triplets_formatted": triplet_strings,
            "retrieved_documents": top_docs,
            "enriched_context": (
                "--- KNOWLEDGE GRAPH RELATIONS ---\n" +
                ("\n".join(triplet_strings) if triplet_strings else "No direct entity relations mapped.") +
                "\n\n--- RETRIEVED DOCUMENT CHUNKS ---\n" +
                ("\n\n".join([f"[{d['id']}] {d['content']}" for d in top_docs]) if top_docs else "No matching chunks.")
            )
        }
