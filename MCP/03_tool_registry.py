"""
03_tool_registry.py
===================
Model Context Protocol (MCP) - Tool Definition, Validation & Invocation.
"""

import sys
import json
from mcp_core import UnifiedMCPServer, MCPMessageBuilder

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" [MCP 03] Tool Registry, JSON Schema Validation & Execution")
    print("=" * 70)

    server = UnifiedMCPServer()

    # 1. List tools
    list_req = MCPMessageBuilder.request("tools/list")
    list_resp = server.handle_jsonrpc(list_req)
    print("\n1. Discovered Tools:")
    for t in list_resp["result"]["tools"]:
        print(f"   * [{t['name']}]: {t['description']}")
        print(f"     Required args: {t['inputSchema'].get('required', [])}")

    # 2. Call compound interest tool
    call_req_1 = MCPMessageBuilder.request("tools/call", {
        "name": "calculate_compound_interest",
        "arguments": {"principal": 10000, "annual_rate": 8.5, "years": 5}
    })
    print("\n2. Calling 'calculate_compound_interest' ($10,000 at 8.5% for 5 years):")
    res1 = server.handle_jsonrpc(call_req_1)
    print(res1["result"]["content"][0]["text"])

    # 3. Call diagnostics
    call_req_2 = MCPMessageBuilder.request("tools/call", {
        "name": "check_host_health",
        "arguments": {"hostname": "quantum-db-cluster-01"}
    })
    print("\n3. Calling 'check_host_health':")
    res2 = server.handle_jsonrpc(call_req_2)
    print(res2["result"]["content"][0]["text"])

    # 4. Error case: Missing required argument
    bad_req = MCPMessageBuilder.request("tools/call", {
        "name": "calculate_compound_interest",
        "arguments": {"principal": 5000}
    })
    print("\n4. Missing argument validation test:")
    res_bad = server.handle_jsonrpc(bad_req)
    print("isError:", res_bad["result"].get("isError"))
    print("Message:", res_bad["result"]["content"][0]["text"])

    print("\n Tool invocation verification complete!")


if __name__ == "__main__":
    main()
