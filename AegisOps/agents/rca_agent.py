"""
rca_agent.py
============
Specialist Agent 2: Forensic Root-Cause Investigator (RCA).
"""

import sys
import json
from typing import Dict, Any
from aegis_core import IncidentRecord, IncidentStatus
from graph_topology import MicroserviceTopology
from mcp_sre_server import MCPSREServer

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class RCAInvestigatorAgent:
    """Discovers underlying failure source across logs, telemetry, and topology."""

    def __init__(self, topology: MicroserviceTopology, mcp_server: MCPSREServer):
        self.topology = topology
        self.mcp_server = mcp_server

    def process(self, incident: IncidentRecord) -> IncidentRecord:
        print(f"🔍 [RCAInvestigator] Tracing root cause from symptom '{incident.initial_service}'...")
        incident.status = IncidentStatus.INVESTIGATING

        # 1. Trace upstream dependency chain
        upstream_dependencies = self.topology.trace_root_cause_path(incident.initial_service)
        suspect_nodes = [incident.initial_service] + [u["callee"] for u in upstream_dependencies]

        # 2. Inspect telemetry & logs via Model Context Protocol (MCP)
        suspect_telemetry = {}
        culprit_service = incident.initial_service
        evidence_found = []

        for node in suspect_nodes:
            # MCP Read Metrics Resource
            req_metrics = {
                "jsonrpc": "2.0",
                "id": "rca-met",
                "method": "resources/read",
                "params": {"uri": f"metrics://service/{node}"}
            }
            met_resp = self.mcp_server.handle_request(req_metrics)
            if "result" in met_resp:
                raw_text = met_resp["result"]["contents"][0]["text"]
                try:
                    suspect_telemetry[node] = json.loads(raw_text)
                except Exception:
                    pass

            # MCP Read Logs Resource
            req_logs = {
                "jsonrpc": "2.0",
                "id": "rca-logs",
                "method": "resources/read",
                "params": {"uri": f"logs://service/{node}/tail"}
            }
            log_resp = self.mcp_server.handle_request(req_logs)
            if "result" in log_resp:
                log_lines = log_resp["result"]["contents"][0]["text"]
                if "connection pool 'orders_pool' exhausted" in log_lines or "deadlock detected" in log_lines:
                    culprit_service = "order-db-cluster"
                    evidence_found.append("PostgreSQL pg_bouncer connection pool 100% exhausted with transaction deadlocks.")
                elif "OOM command not allowed" in log_lines:
                    culprit_service = "redis-session-cache"
                    evidence_found.append("Redis memory exhausted above maxmemory limit; evictions causing cascading cache misses.")

        # If metrics point to database exhaustion
        db_met = suspect_telemetry.get("order-db-cluster", {})
        if db_met.get("connection_utilization_pct", 0) > 95:
            culprit_service = "order-db-cluster"
            evidence_found.append(f"Database active connections: {db_met.get('active_connections')}/{db_met.get('max_connections')} ({db_met.get('connection_utilization_pct')}%)")

        if not evidence_found:
            evidence_found.append(f"Telemetry drift detected on {incident.initial_service}.")

        incident.root_cause_summary = f"Root cause isolated to '{culprit_service}'. Evidence: {'; '.join(evidence_found)}"

        # 3. Log Findings
        incident.add_finding(
            agent_name="RCAInvestigatorAgent",
            phase="INVESTIGATION",
            summary=f"Culprit isolated: '{culprit_service}'.",
            details={
                "culprit_node": culprit_service,
                "inspected_nodes": suspect_nodes,
                "evidence": evidence_found,
                "telemetry_snapshots": suspect_telemetry
            }
        )

        print(f"✅ [RCAInvestigator] Culprit Identified: {culprit_service}")
        return incident
