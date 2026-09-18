"""
app.py
======
Interactive Model Context Protocol (MCP) Inspector & Agent Studio Server.
Runs on Port 5003.
"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mcp_core import UnifiedMCPServer, MCPMessageBuilder

load_dotenv()

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
server = UnifiedMCPServer("QuantumNova-Enterprise-MCP", "2.1.0")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/mcp/init", methods=["POST"])
def mcp_init():
    req = MCPMessageBuilder.request("initialize", {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "MCP-Web-Inspector", "version": "1.0.0"}
    })
    resp = server.handle_jsonrpc(req)
    ack = MCPMessageBuilder.notification("notifications/initialized")
    server.handle_jsonrpc(ack)
    return jsonify({"request": req, "response": resp, "notification": ack})


@app.route("/api/mcp/resources", methods=["GET"])
def get_resources():
    req = MCPMessageBuilder.request("resources/list")
    resp = server.handle_jsonrpc(req)
    return jsonify(resp)


@app.route("/api/mcp/resource/read", methods=["POST"])
def read_resource():
    data = request.json or {}
    uri = data.get("uri", "")
    req = MCPMessageBuilder.request("resources/read", {"uri": uri})
    resp = server.handle_jsonrpc(req)
    return jsonify(resp)


@app.route("/api/mcp/tools", methods=["GET"])
def get_tools():
    req = MCPMessageBuilder.request("tools/list")
    resp = server.handle_jsonrpc(req)
    return jsonify(resp)


@app.route("/api/mcp/tools/call", methods=["POST"])
def call_tool():
    data = request.json or {}
    name = data.get("name", "")
    args = data.get("arguments", {})
    req = MCPMessageBuilder.request("tools/call", {"name": name, "arguments": args})
    resp = server.handle_jsonrpc(req)
    return jsonify({"request": req, "response": resp})


@app.route("/api/mcp/prompts", methods=["GET"])
def get_prompts():
    req = MCPMessageBuilder.request("prompts/list")
    resp = server.handle_jsonrpc(req)
    return jsonify(resp)


@app.route("/api/mcp/prompts/get", methods=["POST"])
def get_prompt():
    data = request.json or {}
    name = data.get("name", "")
    args = data.get("arguments", {})
    req = MCPMessageBuilder.request("prompts/get", {"name": name, "arguments": args})
    resp = server.handle_jsonrpc(req)
    return jsonify({"request": req, "response": resp})


@app.route("/api/mcp/agent/run", methods=["POST"])
def run_agent():
    data = request.json or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query required"}), 400

    # Match tool by intent
    if "interest" in query.lower() or "invest" in query.lower() or "principal" in query.lower():
        tool_name = "calculate_compound_interest"
        principal = 25000
        rate = 9.2
        years = 4
        # simple regex extraction if numbers present
        import re
        nums = [float(s) for s in re.findall(r"[-+]?(?:\d*\.\d+|\d+)", query.replace("$", "").replace(",", ""))]
        if len(nums) >= 1:
            principal = nums[0]
        if len(nums) >= 2:
            rate = nums[1]
        if len(nums) >= 3:
            years = int(nums[2])
        tool_args = {"principal": principal, "annual_rate": rate, "years": years}
    elif "health" in query.lower() or "host" in query.lower() or "server" in query.lower():
        tool_name = "check_host_health"
        host = "quantum-db-01"
        for w in query.split():
            if "-" in w or "." in w:
                host = w.strip(".,;:?!")
                break
        tool_args = {"hostname": host, "check_disk": True}
    else:
        tool_name = "calculate_compound_interest"
        tool_args = {"principal": 10000, "annual_rate": 7.5, "years": 3}

    # Step 1: MCP Call
    call_req = MCPMessageBuilder.request("tools/call", {"name": tool_name, "arguments": tool_args})
    tool_resp = server.handle_jsonrpc(call_req)
    raw_content = tool_resp.get("result", {}).get("content", [{}])[0].get("text", "")

    # Step 2: Synthesis
    synthesis = ""
    try:
        parsed = json.loads(raw_content)
        if "final_balance" in parsed:
            synthesis = (
                f"Investment calculation complete via MCP financial tool:\n"
                f"• Starting Principal: ${parsed.get('initial_principal'):,.2f}\n"
                f"• Rate: {parsed.get('interest_rate_pct')}% per annum over {parsed.get('years')} years\n"
                f"• Accumulated Interest: ${parsed.get('total_interest_earned'):,.2f}\n"
                f"• Total Value: ${parsed.get('final_balance'):,.2f}"
            )
        elif "latency_ms" in parsed:
            synthesis = (
                f"Diagnostics complete for '{parsed.get('target')}':\n"
                f"• Status: {parsed.get('status')} | Reachable: {parsed.get('reachable')}\n"
                f"• Latency: {parsed.get('latency_ms')} ms | CPU Load: {parsed.get('cpu_load_pct')}%\n"
                f"• Disk Space Remaining: {parsed.get('disk_free_gb')} GB"
            )
    except Exception:
        synthesis = raw_content

    return jsonify({
        "query": query,
        "selected_tool": tool_name,
        "tool_args": tool_args,
        "mcp_request": call_req,
        "mcp_response": tool_resp,
        "final_synthesis": synthesis
    })


if __name__ == "__main__":
    print("🚀 Starting MCP Web Studio on http://127.0.0.1:5003")
    app.run(host="127.0.0.1", port=5003, debug=False)
