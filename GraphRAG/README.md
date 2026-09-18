# 🕸️ GraphRAG: Knowledge Graphs & Multi-Hop Reasoning

A production-grade implementation and interactive studio for **GraphRAG**, the hybrid retrieval architecture that unifies dense vector search with structured Knowledge Graphs.

---

## 💡 Why Vector RAG Fails at Complex Questions

Standard Vector RAG searches for nearest neighbors using text embeddings:
- It excels at **local, direct needle-in-a-haystack lookups** (e.g., *"What is the payload weight of Falcon Heavy?"*).
- It **fails completely at global synthesis and multi-hop queries** (e.g., *"How is the leadership of QuantumNova connected to the contractor building the satellite transponders?"*).

### The Multi-Hop Problem
If Entity A connects to Entity B, and Entity B connects to Entity C across separate documents, a vector query about Entity A will never fetch Document C because there is zero keyword or embedding overlap!

```
[Traditional Vector Search]
Query: "Dr. Elena Vance" ──► [Only retrieves doc-staff] ──► Fails to connect to Falcon Heavy!

[GraphRAG Knowledge Traversal]
(Dr. Elena Vance)
       │
       ▼ [VP_ENGINEERING_AT]
(QuantumNova)
       │
       ▼ [OWNS_PROJECT]
(Project NovaStar)
       │
       ▼ [LAUNCHES_ON]
(Falcon Heavy) ──► 100% Grounded, Complete Multi-Hop Discovery!
```

---

## 🧩 GraphRAG Core Building Blocks

1. **Entity Extraction (NER)**:
   Extracts typed entities: Organizations, Projects, People, Technologies, Locations, and Vehicles.
2. **SPO Triplet Extraction**:
   Extracts `(Subject) ──[Predicate]──► (Object)` relations from unstructured text.
3. **Directed Knowledge Graph**:
   Maintains adjacency lists, node properties, edge types, and degree centrality.
4. **Multi-Hop Traversal**:
   BFS path finding and $N$-hop neighborhood expansion to retrieve all contextual entities around the query.
5. **Hybrid Vector + Graph Synthesis**:
   Augments the final prompt with both retrieved document chunks AND the traversed relational graph paths.

---

## 🏃 Standalone Runnable Tutorials

```bash
cd GraphRAG

# 1. Entity and Triplet Extraction from unstructured text
python 01_entity_relation_extraction.py

# 2. Knowledge Graph Construction, Adjacency & Centrality
python 02_knowledge_graph_builder.py

# 3. Multi-Hop Graph Traversal and Path Finding
python 03_graph_traversal_search.py

# 4. End-to-End Hybrid GraphRAG Retrieval Pipeline
python 04_hybrid_graphrag_pipeline.py
```

---

## 🖥️ Interactive GraphRAG Web Studio

```bash
cd GraphRAG
python app.py
# Opens at: http://127.0.0.1:5005
```

Features:
- **🕸️ Canvas Graph Visualizer**: Live rendering of nodes, hub degrees, and directed relationships.
- **🧭 Path Finder**: Discover shortest multi-hop connection paths between any two entities.
- **⚡ Hybrid Query Engine**: Run complex multi-entity queries and inspect traversed graph paths alongside document chunks.

---

## 🧪 Running Automated Tests

```bash
python GraphRAG/test_graphrag.py
```
