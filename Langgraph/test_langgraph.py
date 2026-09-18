"""
================================================================================
test_langgraph.py - Automated Test Suite for LangGraph Educational Modules
================================================================================
Runs automated assertions against all 9 LangGraph workflows, the Gemini client,
and the Flask web server endpoints.
"""

import os
import sys
import unittest
import json

# Ensure Langgraph directory is on sys.path
LANGGRAPH_DIR = os.path.dirname(os.path.abspath(__file__))
if LANGGRAPH_DIR not in sys.path:
    sys.path.insert(0, LANGGRAPH_DIR)

from gemini_client import call_gemini, call_gemini_json
import app as flask_app_module


class TestLangGraphSuite(unittest.TestCase):

    def setUp(self):
        self.app = flask_app_module.app.test_client()

    def test_01_gemini_client(self):
        """Test direct Gemini REST invocation with user's API key."""
        res = call_gemini("Say 'LangGraph Test OK' in 3 words.")
        self.assertTrue(res["success"], f"Gemini call failed: {res.get('error')}")
        self.assertIn("text", res)
        self.assertGreater(len(res["text"]), 0)

    def test_02_basic_graph_compilation(self):
        """Test Module 01: Basic StateGraph compilation and execution."""
        from importlib import import_module
        mod = import_module("01_basic_graph")
        graph = mod.build_basic_graph()
        self.assertIsNotNone(graph)
        
        # Test invocation with dummy input
        initial = {
            "input_text": "Quantum computing is rapidly advancing.",
            "analysis": "",
            "summary": "",
            "step_history": []
        }
        res = graph.invoke(initial)
        self.assertIn("analysis", res)
        self.assertIn("summary", res)
        self.assertEqual(len(res["step_history"]), 2)

    def test_03_state_reducers(self):
        """Test Module 02: operator.add reducer accumulates audit trail without overwriting."""
        from importlib import import_module
        mod = import_module("02_state_reducers")
        graph = mod.build_reducer_graph()
        self.assertIsNotNone(graph)

        initial = {
            "input_text": "Normal customer query about office hours.",
            "sentiment_findings": "",
            "security_findings": "",
            "final_verdict": "",
            "audit_trail": ["[Audit] Start."]
        }
        res = graph.invoke(initial)
        # Should have at least 4 audit trail entries accumulated
        self.assertGreaterEqual(len(res["audit_trail"]), 4)

    def test_04_conditional_routing(self):
        """Test Module 03: Dynamic conditional routing logic."""
        from importlib import import_module
        mod = import_module("03_conditional_routing")
        
        # Test routing decision function directly
        self.assertEqual(mod.route_by_intent({"intent": "technical"}), "tech_path")
        self.assertEqual(mod.route_by_intent({"intent": "billing"}), "billing_path")
        self.assertEqual(mod.route_by_intent({"intent": "casual"}), "casual_path")

    def test_05_cyclical_loop_guard(self):
        """Test Module 04: Loop condition evaluates score and iteration threshold."""
        from importlib import import_module
        mod = import_module("04_cyclical_agent_loop")

        # Score < 8 should trigger revise
        state_low_score = {"quality_score": 5, "iteration_count": 1, "max_iterations": 3}
        self.assertEqual(mod.evaluate_loop_condition(state_low_score), "revise")

        # Score >= 8 should finish
        state_high_score = {"quality_score": 9, "iteration_count": 1, "max_iterations": 3}
        self.assertEqual(mod.evaluate_loop_condition(state_high_score), "finish")

        # Max iterations reached should finish
        state_maxed = {"quality_score": 6, "iteration_count": 3, "max_iterations": 3}
        self.assertEqual(mod.evaluate_loop_condition(state_maxed), "finish")

    def test_06_tool_calling_functions(self):
        """Test Module 05: ReAct tools return valid responses."""
        from importlib import import_module
        mod = import_module("05_tool_calling_agent")

        calc_res = mod.tool_calculator("15 * 4")
        self.assertIn("60", calc_res)

        telemetry_res = mod.tool_cluster_telemetry("singapore-beta")
        self.assertIn("Singapore Cluster", telemetry_res)

    def test_07_memory_checkpoints(self):
        """Test Module 06: MemorySaver maintains state and isolates threads."""
        from importlib import import_module
        mod = import_module("06_memory_and_checkpoints")
        graph = mod.build_memory_graph()

        config_a = {"configurable": {"thread_id": "thread-test-a"}}
        config_b = {"configurable": {"thread_id": "thread-test-b"}}

        # Turn 1 for A
        graph.invoke({"messages": [{"role": "user", "content": "My secret code is Alpha99"}]}, config=config_a)
        state_a = graph.get_state(config_a)
        self.assertGreaterEqual(len(state_a.values["messages"]), 2)

        # B should have empty/separate state
        state_b = graph.get_state(config_b)
        self.assertEqual(len(state_b.values), 0)

    def test_08_hitl_interrupt(self):
        """Test Module 07: Execution halts before sensitive node."""
        from importlib import import_module
        mod = import_module("07_human_in_the_loop")
        graph = mod.build_hitl_graph()
        config = {"configurable": {"thread_id": "hitl-test-thread"}}

        initial = {
            "request": "Transfer $1,000 to vendor X",
            "recipient": "",
            "amount_usd": 0.0,
            "reason": "",
            "human_approval": "PENDING",
            "execution_status": "WAITING",
            "transaction_id": ""
        }

        # Step 1: Run to breakpoint
        graph.invoke(initial, config=config)
        state_bp = graph.get_state(config)
        # Should be paused before execute_transfer
        self.assertTrue(bool(state_bp.next))
        self.assertIn("execute_transfer", state_bp.next)

        # Step 2: Approve and resume
        graph.update_state(config, {"human_approval": "APPROVED"}, as_node="draft_transaction")
        graph.invoke(None, config=config)
        final_state = graph.get_state(config)
        self.assertIn("SUCCESS", final_state.values["execution_status"])

    def test_09_crag_routing(self):
        """Test Module 08: Corrective RAG router branches properly."""
        from importlib import import_module
        mod = import_module("08_corrective_rag")

        self.assertEqual(mod.decide_to_generate({"relevance_verdict": "RELEVANT"}), "generate")
        self.assertEqual(mod.decide_to_generate({"relevance_verdict": "NOT_RELEVANT"}), "corrective_fallback")

    def test_10_multi_agent_routing(self):
        """Test Module 09: Supervisor routing logic."""
        from importlib import import_module
        mod = import_module("09_multi_agent_supervisor")

        self.assertEqual(mod.route_supervisor({"next_worker": "researcher"}), "researcher")
        self.assertEqual(mod.route_supervisor({"next_worker": "coder"}), "coder")
        self.assertEqual(mod.route_supervisor({"next_worker": "FINISH"}), "synthesize")

    def test_11_web_api_workflows(self):
        """Test Flask API: /api/workflows returns 9 modules."""
        resp = self.app.get("/api/workflows")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["workflows"]), 9)

    def test_12_web_api_run_basic(self):
        """Test Flask API: /api/run/01_basic executes and returns steps."""
        resp = self.app.post(
            "/api/run/01_basic",
            json={"text": "Test pipeline input for automated check."}
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertIn("steps", data)
        self.assertIn("final_state", data)


if __name__ == "__main__":
    unittest.main()
