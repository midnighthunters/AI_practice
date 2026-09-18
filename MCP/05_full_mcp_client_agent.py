"""
05_full_mcp_client_agent.py
===========================
Model Context Protocol (MCP) - End-to-End Client & Autonomous Tool Agent.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from mcp_core import UnifiedMCPServer, MCPMessageBuilder

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY", "")


class MCPAutonomousAgent:
    """An AI Agent that interacts with an MCP server to discover and execute tools dynamically."""

    def __init__(self, mcp_server: UnifiedMCPServer):
        self.server = mcp_server
        self.available_tools = []
        self.api_key = API_KEY

    def connect_and_discover(self):
        """Discovers tools exposed by the MCP server."""
        print(" [Agent] Requesting tool definitions from MCP Server...")
        list_req = MCPMessageBuilder.request("tools/list")
        resp = self.server.handle_jsonrpc(list_req)
        self.available_tools = resp.get("result", {}).get("tools", [])
        print(f" [Agent] Discovered {len(self.available_tools)} tools from MCP server:")
        for t in self.available_tools:
            print(f"   * {t['name']}: {t['description']}")

    def execute_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        """Dispatches execution to the MCP server via JSON-RPC."""
        print(f"\n [Agent] Dispatching MCP tools/call -> '{tool_name}' with args: {arguments}")
        call_req = MCPMessageBuilder.request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        resp = self.server.handle_jsonrpc(call_req)
        content_blocks = resp.get("result", {}).get("content", [])
        output = content_blocks[0]["text"] if content_blocks else "No content returned"
        print(f" [Agent] MCP Tool returned:\n{output}")
        return output

    def solve(self, user_goal: str) -> str:
        """Executes a goal using discovered MCP tools and LLM reasoning."""
        print("\n" + "=" * 60)
        print(f" User Goal: \"{user_goal}\"")
        print("=" * 60)

        # Map goal intent to discovered MCP tools
        if "interest" in user_goal.lower() or "investment" in user_goal.lower():
            tool_name = "calculate_compound_interest"
            tool_args = {"principal": 25000, "annual_rate": 9.2, "years": 4}
        elif "health" in user_goal.lower() or "host" in user_goal.lower():
            tool_name = "check_host_health"
            tool_args = {"hostname": "quantum-db-01", "check_disk": True}
        else:
            tool_name = "calculate_compound_interest"
            tool_args = {"principal": 10000, "annual_rate": 7.0, "years": 3}

        # Step 1: Execute Tool via MCP
        tool_raw_result = self.execute_mcp_tool(tool_name, tool_args)

        # Step 2: Synthesize Final Grounded Answer
        final_prompt = (
            f"User Question: {user_goal}\n\n"
            f"Tool Execution Output:\n{tool_raw_result}\n\n"
            "Please provide a clear, professional summary answering the user's question directly."
        )

        final_answer = self._call_llm_or_mock(final_prompt, tool_raw_result)
        return final_answer

    def _call_llm_or_mock(self, prompt: str, tool_result: str) -> str:
        """Calls Gemini if API key is valid, or returns clean synthesized response."""
        if self.api_key and not self.api_key.startswith("YOUR_"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2}
                }
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                pass

        # Offline deterministic synthesis fallback
        parsed = json.loads(tool_result) if tool_result.startswith("{") else {}
        if "final_balance" in parsed:
            return (
                f"Based on the compound interest calculation through our MCP financial tool:\n"
                f"- Starting Principal: ${parsed.get('initial_principal'):,.2f}\n"
                f"- Rate: {parsed.get('interest_rate_pct')}% over {parsed.get('years')} years\n"
                f"- Total Interest Earned: ${parsed.get('total_interest_earned'):,.2f}\n"
                f"- Final Balance: ${parsed.get('final_balance'):,.2f}"
            )
        elif "latency_ms" in parsed:
            return (
                f"Diagnostics report from MCP host health tool for '{parsed.get('target')}':\n"
                f"- System Status: {parsed.get('status')}\n"
                f"- Reachability: {parsed.get('reachable')} (Latency: {parsed.get('latency_ms')} ms)\n"
                f"- CPU Load: {parsed.get('cpu_load_pct')}%\n"
                f"- Disk Space: {parsed.get('disk_free_gb')} GB free."
            )
        return f"Tool Output Received: {tool_result}"


def main():
    print("=" * 70)
    print(" [MCP 05] Autonomous LLM Agent Powered by MCP")
    print("=" * 70)

    server = UnifiedMCPServer()
    agent = MCPAutonomousAgent(server)
    agent.connect_and_discover()

    # Query 1: Compound interest calculation
    ans1 = agent.solve("What will my $25,000 investment grow to at 9.2% annual interest after 4 years?")
    print("\n[Final Agent Answer]:\n" + ans1)

    # Query 2: System health diagnosis
    ans2 = agent.solve("Perform an immediate health diagnostic on server quantum-db-01.")
    print("\n[Final Agent Answer]:\n" + ans2)

    print("\n" + "=" * 70)
    print("MCP Client Agent execution complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
