"""
04_prompt_templates.py
======================
Model Context Protocol (MCP) - Server-Provided Prompt Templates.
"""

import sys
import json
from mcp_core import UnifiedMCPServer, MCPMessageBuilder

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" [MCP 04] Prompt Templates & Dynamic Parameterization")
    print("=" * 70)

    server = UnifiedMCPServer()

    # 1. Discover prompts
    list_req = MCPMessageBuilder.request("prompts/list")
    list_resp = server.handle_jsonrpc(list_req)
    print("\n1. Discovered Prompt Templates:")
    for p in list_resp["result"]["prompts"]:
        print(f"   * Template: {p['name']}")
        print(f"     Description: {p['description']}")
        print(f"     Arguments: {[a['name'] for a in p['arguments']]}")

    # 2. Render Security Code Review Prompt
    get_req = MCPMessageBuilder.request("prompts/get", {
        "name": "code_review_security",
        "arguments": {
            "language": "Python",
            "code_snippet": "query = f'SELECT * FROM users WHERE user = \"{user_input}\"'\ncursor.execute(query)",
            "compliance_level": "STRICT"
        }
    })
    print("\n2. Rendered 'code_review_security' Prompt:")
    p_res = server.handle_jsonrpc(get_req)
    rendered_text = p_res["result"]["messages"][0]["content"]["text"]
    print("-" * 50)
    print(rendered_text)
    print("-" * 50)

    print("\n Prompt generation verified!")


if __name__ == "__main__":
    main()
