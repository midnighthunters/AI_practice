"""
01_protocol_framing.py
======================
Model Context Protocol (MCP) - Core Framing & JSON-RPC 2.0 Basics.
"""

import sys
import json
from mcp_core import MCPMessageBuilder, UnifiedMCPServer, MCP_PROTOCOL_VERSION

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" [MCP 01] Protocol Framing & Handshake Initialization")
    print("=" * 70)

    server = UnifiedMCPServer("EchoServer", "1.0.0")

    # 1. Initialize Handshake
    init_req = MCPMessageBuilder.request("initialize", {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": {"roots": {"listChanged": True}},
        "clientInfo": {"name": "TestClient", "version": "1.0.0"}
    })
    print("\n1. Client -> 'initialize' request:")
    print(json.dumps(init_req, indent=2))

    resp = server.handle_jsonrpc(init_req)
    print("\n2. Server -> Handshake Response:")
    print(json.dumps(resp, indent=2))

    # 2. Client confirms with initialized notification
    init_ack = MCPMessageBuilder.notification("notifications/initialized")
    server.handle_jsonrpc(init_ack)
    print("\n3. Client -> 'notifications/initialized' sent.")

    # 3. Ping
    ping_req = MCPMessageBuilder.request("ping")
    ping_resp = server.handle_jsonrpc(ping_req)
    print("\n4. Ping / Pong check:")
    print("Ping Req:", ping_req)
    print("Ping Resp:", ping_resp)

    print("\n Handshake complete. Session established!")


if __name__ == "__main__":
    main()
