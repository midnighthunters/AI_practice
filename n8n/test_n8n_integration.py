import json
import os
import time
import unittest
import requests

from simulator.server import app, API_KEY, GEMINI_URL, call_gemini_api

class TestN8nIntegration(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.workflows_dir = os.path.join(os.path.dirname(__file__), "workflows")
        time.sleep(1.0)

    def test_workflow_json_files_exist_and_valid(self):
        """Verifies that all 4 exported n8n workflow JSONs are structurally valid."""
        expected_files = [
            "01_gemini_http_request.json",
            "02_smart_customer_triage.json",
            "03_n8n_rag_pipeline.json",
            "04_gemini_ai_agent_tools.json"
        ]

        for filename in expected_files:
            filepath = os.path.join(self.workflows_dir, filename)
            self.assertTrue(os.path.exists(filepath), f"Missing workflow file: {filename}")
            
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.assertIn("name", data)
            self.assertIn("nodes", data)
            self.assertIn("connections", data)
            self.assertGreaterEqual(len(data["nodes"]), 4)

            # Check that Gemini endpoint or model is referenced
            raw_text = json.dumps(data)
            self.assertTrue("gemini-flash-latest" in raw_text)

    def test_direct_gemini_api_call(self):
        """Tests live call to Google Gemini with the exact prompt and user's API Key."""
        res = call_gemini_api("Explain how AI works in a few words")
        self.assertTrue(res["success"], f"Gemini API failed: {res.get('error')}")
        self.assertEqual(res["status_code"], 200)
        self.assertGreater(len(res["text"]), 5)
        print(f"\n[Test Gemini API Response]: {res['text'].strip()}")

    def test_simulator_workflows_list(self):
        """Tests /api/workflows endpoint."""
        resp = self.client.get("/api/workflows")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["workflows"]), 4)

    def test_simulate_workflow_01(self):
        """Simulates Workflow 1: Direct Gemini cURL / HTTP."""
        resp = self.client.post("/api/simulate", json={
            "workflow_id": "01_gemini_http_request",
            "input": "Explain how AI works in a few words"
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["workflow_id"], "01_gemini_http_request")
        self.assertIn("generatedText", data["final_result"])
        self.assertGreater(len(data["final_result"]["generatedText"]), 5)

    def test_simulate_workflow_02(self):
        """Simulates Workflow 2: Support Ticket Triage."""
        resp = self.client.post("/api/simulate", json={
            "workflow_id": "02_smart_customer_triage",
            "input": "I demand an immediate refund! Your service had a major outage today."
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["workflow_id"], "02_smart_customer_triage")
        res = data["final_result"]
        self.assertIn("analysis", res)
        self.assertIn("isUrgent", res)

    def test_simulate_workflow_03_rag(self):
        """Simulates Workflow 3: Enterprise RAG Knowledge Base."""
        resp = self.client.post("/api/simulate", json={
            "workflow_id": "03_n8n_rag_pipeline",
            "input": "What is the launch date for Project NovaStar?"
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["workflow_id"], "03_n8n_rag_pipeline")
        res = data["final_result"]
        self.assertIn("retrievedDocuments", res)
        self.assertIn("answer", res)
        self.assertTrue("2026" in res["answer"] or "NovaStar" in res["answer"])

    def test_simulate_workflow_04_agent(self):
        """Simulates Workflow 4: Gemini AI Agent with Tools."""
        resp = self.client.post("/api/simulate", json={
            "workflow_id": "04_gemini_ai_agent_tools",
            "input": "Check tracking status for order ORD-102 and calculate a 15% discount on $420"
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["workflow_id"], "04_gemini_ai_agent_tools")
        res = data["final_result"]
        self.assertIn("tools_invoked", res)
        self.assertIn("output", res)


if __name__ == "__main__":
    unittest.main()
