"""
test_graphrag.py
================
Automated Unit Test Suite for GraphRAG & Knowledge Graphs.
"""

import unittest
from graph_core import KnowledgeGraph, TripletExtractor, HybridGraphRAG


class TestGraphRAG(unittest.TestCase):
    def setUp(self):
        self.kg = TripletExtractor.extract_from_corpus([])

    def test_graph_nodes_and_edges(self):
        self.assertIn("QuantumNova", self.kg.nodes)
        self.assertIn("Project NovaStar", self.kg.nodes)
        self.assertGreaterEqual(len(self.kg.to_dict()["edges"]), 8)

    def test_multi_hop_path_finding(self):
        # 2 hops: Vance -> Q-Core -> Photonic Interconnect
        path = self.kg.find_path("Dr. Elena Vance", "Photonic Interconnect")
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0]["to"], "Q-Core")
        self.assertEqual(path[1]["to"], "Photonic Interconnect")

        # 3 hops: Vance -> QuantumNova -> NovaStar -> Falcon Heavy
        path3 = self.kg.find_path("Dr. Elena Vance", "Falcon Heavy")
        self.assertIsNotNone(path3)
        self.assertEqual(len(path3), 3)

    def test_degree_centrality(self):
        centrality = self.kg.degree_centrality()
        self.assertIn("QuantumNova", centrality)
        # QuantumNova is one of the top hubs
        self.assertGreaterEqual(centrality["QuantumNova"], 3)

    def test_neighborhood_expansion(self):
        neighbors_1 = self.kg.get_neighbors("QuantumNova", hops=1)
        neighbors_2 = self.kg.get_neighbors("QuantumNova", hops=2)
        self.assertGreater(len(neighbors_2), len(neighbors_1))
        self.assertIn("Falcon Heavy", neighbors_2)

    def test_hybrid_retrieval(self):
        corpus = [
            {"id": "doc1", "title": "Specs", "content": "Project NovaStar is a satellite."}
        ]
        rag = HybridGraphRAG(self.kg, corpus)
        result = rag.retrieve("Tell me about Project NovaStar and Falcon Heavy", top_k_docs=1, graph_hops=1)
        self.assertIn("Project NovaStar", result["matched_entities"])
        self.assertGreaterEqual(len(result["graph_triplets"]), 1)
        self.assertIn("KNOWLEDGE GRAPH RELATIONS", result["enriched_context"])


if __name__ == "__main__":
    unittest.main()
