"""
02_resource_provider.py
========================
Model Context Protocol (MCP) - Exposing & Reading Resources.
"""

import sys
import json
from mcp_core import UnifiedMCPServer, MCPMessageBuilder

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" [MCP 02] Resource Discovery & Content Streaming")
    print("=" * 70)

    server = UnifiedMCPServer()

    # 1. Discover resources
    list_req = MCPMessageBuilder.request("resources/list")
    list_resp = server.handle_jsonrpc(list_req)
    print("\n1. Discovered Resources:")
    for r in list_resp["result"]["resources"]:
        print(f"   - {r['uri']} ({r['mimeType']}): {r['name']}")

    # 2. Read telemetry resource
    read_req = MCPMessageBuilder.request("resources/read", {"uri": "system://telemetry/cluster"})
    read_resp = server.handle_jsonrpc(read_req)
    print("\n2. Read 'system://telemetry/cluster':")
    print(read_resp["result"]["contents"][0]["text"])

    # 3. Read markdown docs resource
    doc_req = MCPMessageBuilder.request("resources/read", {"uri": "docs://quantum/architecture"})
    doc_resp = server.handle_jsonrpc(doc_req)
    print("\n3. Read 'docs://quantum/architecture':")
    print(doc_resp["result"]["contents"][0]["text"])

    print("\n Resource retrieval successful!")


if __name__ == "__main__":
    main()
