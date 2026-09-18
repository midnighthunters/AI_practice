"""
app.py
======
AegisOps: Autonomous SRE & Incident Commander Mission Control Server.
Runs on Port 5006.
"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from orchestrator import AegisOpsOrchestrator

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
orchestrator = AegisOpsOrchestrator()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/topology", methods=["GET"])
def get_topology():
    return jsonify(orchestrator.topology.to_dict())


@app.route("/api/incidents", methods=["GET"])
def list_incidents():
    incidents = [inc.to_dict() for inc in orchestrator.active_incidents.values()]
    return jsonify({"incidents": incidents})


@app.route("/api/incident/<incident_id>", methods=["GET"])
def get_incident(incident_id):
    inc = orchestrator.active_incidents.get(incident_id)
    if not inc:
        return jsonify({"error": "Incident not found"}), 404
    return jsonify(inc.to_dict())


@app.route("/api/incident/trigger", methods=["POST"])
def trigger_incident():
    data = request.json or {}
    title = data.get("title", "High Error Rate Detected")
    desc = data.get("description", "Service reported excessive 5xx HTTP codes.")
    service = data.get("service", "checkout-service")

    incident = orchestrator.trigger_incident(title, desc, service)
    return jsonify({
        "success": True,
        "incident": incident.to_dict()
    })


@app.route("/api/incident/approve", methods=["POST"])
def approve_remediation():
    data = request.json or {}
    incident_id = data.get("incident_id")
    approver = data.get("approver", "Nikhil Goyal (Staff SRE)")

    res = orchestrator.approve_and_execute_remediation(incident_id, approver)
    if not res.get("success"):
        return jsonify(res), 400

    inc = orchestrator.active_incidents[incident_id]
    return jsonify({
        "success": True,
        "incident": inc.to_dict(),
        "execution_logs": res.get("execution_logs", []),
        "post_mortem": res.get("post_mortem", "")
    })


@app.route("/api/mcp/inspect", methods=["GET"])
def inspect_mcp():
    tools = orchestrator.mcp_server.handle_request({"method": "tools/list", "id": "t1"})
    resources = orchestrator.mcp_server.handle_request({"method": "resources/list", "id": "r1"})
    return jsonify({
        "tools": tools.get("result", {}).get("tools", []),
        "resources": resources.get("result", {}).get("resources", [])
    })


if __name__ == "__main__":
    print("🚀 Starting AegisOps Mission Control on http://127.0.0.1:5006")
    app.run(host="127.0.0.1", port=5006, debug=False)
