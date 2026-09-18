"""
test_mcp.py
===========
Automated Unit & Integration Test Suite for Model Context Protocol (MCP).
"""

import unittest
import json
from mcp_core import UnifiedMCPServer, MCPMessageBuilder, MCP_PROTOCOL_VERSION


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = UnifiedMCPServer("TestMCPServer", "1.0.0")

    def test_initialize_handshake(self):
        req = MCPMessageBuilder.request("initialize", {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "clientInfo": {"name": "UnitTestRunner", "version": "1.0"}
        })
        resp = self.server.handle_jsonrpc(req)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertIn("capabilities", resp["result"])
        self.assertIn("tools", resp["result"]["capabilities"])
        self.assertIn("resources", resp["result"]["capabilities"])
        self.assertIn("prompts", resp["result"]["capabilities"])

    def test_list_and_read_resources(self):
        # List
        req = MCPMessageBuilder.request("resources/list")
        resp = self.server.handle_jsonrpc(req)
        resources = resp["result"]["resources"]
        self.assertGreaterEqual(len(resources), 2)
        uris = [r["uri"] for r in resources]
        self.assertIn("system://telemetry/cluster", uris)

        # Read valid resource
        read_req = MCPMessageBuilder.request("resources/read", {"uri": "system://telemetry/cluster"})
        read_resp = self.server.handle_jsonrpc(read_req)
        self.assertIn("contents", read_resp["result"])
        text = read_resp["result"]["contents"][0]["text"]
        data = json.loads(text)
        self.assertEqual(data["status"], "HEALTHY")

        # Read invalid resource
        bad_req = MCPMessageBuilder.request("resources/read", {"uri": "nonexistent://path"})
        bad_resp = self.server.handle_jsonrpc(bad_req)
        self.assertIn("error", bad_resp)
        self.assertEqual(bad_resp["error"]["code"], -32602)

    def test_tools_execution_and_validation(self):
        # List tools
        t_list_req = MCPMessageBuilder.request("tools/list")
        t_list = self.server.handle_jsonrpc(t_list_req)["result"]["tools"]
        tool_names = [t["name"] for t in t_list]
        self.assertIn("calculate_compound_interest", tool_names)
        self.assertIn("check_host_health", tool_names)

        # Successful tool call
        call_req = MCPMessageBuilder.request("tools/call", {
            "name": "calculate_compound_interest",
            "arguments": {"principal": 1000, "annual_rate": 10, "years": 1}
        })
        call_resp = self.server.handle_jsonrpc(call_req)
        self.assertFalse(call_resp["result"].get("isError", False))
        res_data = json.loads(call_resp["result"]["content"][0]["text"])
        self.assertAlmostEqual(res_data["final_balance"], 1104.71, delta=0.5)

        # Missing argument error
        bad_call = MCPMessageBuilder.request("tools/call", {
            "name": "calculate_compound_interest",
            "arguments": {"principal": 1000}
        })
        bad_resp = self.server.handle_jsonrpc(bad_call)
        self.assertTrue(bad_resp["result"]["isError"])

    def test_prompts_generation(self):
        p_list = self.server.handle_jsonrpc(MCPMessageBuilder.request("prompts/list"))["result"]["prompts"]
        self.assertGreaterEqual(len(p_list), 1)

        get_req = MCPMessageBuilder.request("prompts/get", {
            "name": "code_review_security",
            "arguments": {
                "language": "Python",
                "code_snippet": "os.system(user_input)"
            }
        })
        get_resp = self.server.handle_jsonrpc(get_req)
        self.assertIn("messages", get_resp["result"])
        msg_text = get_resp["result"]["messages"][0]["content"]["text"]
        self.assertIn("Principal Application Security Auditor", msg_text)


if __name__ == "__main__":
    unittest.main()
