"""
test_aegisops.py
================
Automated Integration & Chaos Engineering Test Suite for AegisOps.
"""

import unittest
from aegis_core import IncidentSeverity, IncidentStatus
from graph_topology import MicroserviceTopology
from mcp_sre_server import MCPSREServer
from guardrails_engine import SRESecurityGuardrail, SemanticPlaybookCache
from orchestrator import AegisOpsOrchestrator


class TestAegisOpsPlatform(unittest.TestCase):
    def setUp(self):
        self.orchestrator = AegisOpsOrchestrator()

    def test_topology_blast_radius(self):
        topo = MicroserviceTopology()
        # If database fails, downstream order-service, checkout-service, api-gateway break!
        blast = topo.calculate_blast_radius("order-db-cluster")
        self.assertIn("order-service", blast["impacted_services"])
        self.assertIn("checkout-service", blast["impacted_services"])
        self.assertEqual(blast["recommended_severity"], "P0")
        self.assertGreaterEqual(blast["est_customer_impact_pct"], 80)

    def test_security_guardrail_injection_defense(self):
        attack_alert = "ALERT: High latency. rm -rf / && kill all processes"
        scan = SRESecurityGuardrail.sanitize_alert_and_logs(attack_alert)
        self.assertFalse(scan["allowed"])
        self.assertTrue(scan["threat_detected"])

        # Legitimate alert with credentials
        alert_with_secret = "DB timeout at postgresql://admin:SuperSecretPass2026!@order-db-cluster:5432/orders"
        scan_sec = SRESecurityGuardrail.sanitize_alert_and_logs(alert_with_secret)
        self.assertTrue(scan_sec["allowed"])
        self.assertIn("[REDACTED_DB_CONNECTION_STRING]", scan_sec["sanitized_text"])

    def test_semantic_playbook_cache(self):
        cache = SemanticPlaybookCache(similarity_threshold=0.75)
        # Similar to connection pool exhaustion
        hit = cache.lookup("PostgreSQL database connection pool 500/500 active locks deadlock detected")
        self.assertIsNotNone(hit)
        self.assertEqual(hit["action"], "kill_database_idle_locks")

    def test_mcp_sre_server(self):
        server = MCPSREServer()
        # Test reading metrics resource
        req = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "resources/read",
            "params": {"uri": "metrics://service/order-db-cluster"}
        }
        res = server.handle_request(req)
        self.assertIn("result", res)

        # Test executing tool
        tool_req = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/call",
            "params": {"name": "kill_database_idle_locks", "arguments": {"cluster_id": "order-db-cluster"}}
        }
        tool_res = server.handle_request(tool_req)
        self.assertFalse(tool_res["result"].get("isError", False))

    def test_full_autonomous_agent_lifecycle_with_hitl(self):
        # 1. Trigger realistic P0 incident
        alert_title = "High 5xx Failure Rate on Checkout"
        alert_desc = "OrderWorker connection timeout: PostgreSQL connection pool exhausted (500/500 active) with deadlock on orders_pool."
        service = "checkout-service"

        incident = self.orchestrator.trigger_incident(alert_title, alert_desc, service)

        # Assert Triage results
        self.assertEqual(incident.severity, IncidentSeverity.P0_CRITICAL)
        self.assertGreater(len(incident.blast_radius), 0)

        # Assert RCA Investigator results
        self.assertIn("order-db-cluster", incident.root_cause_summary)

        # Assert Security Clearance
        self.assertTrue(incident.security_clearance)

        # Assert Remediation synthesis & HITL pause
        self.assertEqual(incident.status, IncidentStatus.PENDING_APPROVAL)
        self.assertIsNotNone(incident.remediation_plan)
        self.assertEqual(incident.remediation_plan.target_service, "order-db-cluster")

        # 2. Simulate Human-in-the-Loop SRE Approval
        approval_res = self.orchestrator.approve_and_execute_remediation(incident.incident_id, "Nikhil Goyal (Staff SRE)")
        self.assertTrue(approval_res["success"])
        self.assertEqual(incident.status, IncidentStatus.RESOLVED)

        # Assert Post-Mortem authoring
        self.assertIn("5-Whys", incident.post_mortem_report)
        self.assertIn("MTTR", incident.post_mortem_report)
        self.assertIn("Nikhil Goyal", incident.post_mortem_report)


if __name__ == "__main__":
    unittest.main()
