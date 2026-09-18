"""
orchestrator.py
===============
AegisOps Multi-Agent Orchestrator & Human-in-the-Loop Workflow Engine.
"""

import sys
import json
import time
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from aegis_core import IncidentRecord, IncidentStatus
from graph_topology import MicroserviceTopology
from mcp_sre_server import MCPSREServer
from guardrails_engine import SRESecurityGuardrail, SemanticPlaybookCache
from agents import (
    TriageAgent,
    RCAInvestigatorAgent,
    SecurityAuditorAgent,
    RemediationEngineerAgent,
    PostMortemScribeAgent
)


class AegisOpsOrchestrator:
    """Master Orchestrator coordinating the 5 autonomous agents and Human-in-the-Loop approval."""

    def __init__(self):
        self.topology = MicroserviceTopology()
        self.mcp_server = MCPSREServer()
        self.playbook_cache = SemanticPlaybookCache()

        # Initialize the 5 Specialist Agents
        self.triage_agent = TriageAgent(self.topology)
        self.rca_agent = RCAInvestigatorAgent(self.topology, self.mcp_server)
        self.security_agent = SecurityAuditorAgent()
        self.remediation_agent = RemediationEngineerAgent(self.playbook_cache)
        self.postmortem_agent = PostMortemScribeAgent()

        # In-memory active incident registry
        self.active_incidents: Dict[str, IncidentRecord] = {}

    def trigger_incident(self, title: str, description: str, initial_service: str) -> IncidentRecord:
        """Entrypoint for an alert: Runs Security Guardrail -> Triage -> RCA -> Security -> Remediation."""
        print("\n" + "=" * 70)
        print(f"🚨 [AEGISOPS] INCOMING ALERT: {title} on '{initial_service}'")
        print("=" * 70)

        # 1. Ingress Security Guardrail: Check for malicious injection & sanitize credentials
        scan = SRESecurityGuardrail.sanitize_alert_and_logs(description)
        if not scan["allowed"]:
            print(f"🛑 [FIREWALL BLOCKED] Alert payload contained dangerous command: {scan['threat_detail']}")
            incident = IncidentRecord(title=title, description=f"[BLOCKED INJECTION] {description}", initial_service=initial_service)
            incident.status = IncidentStatus.REJECTED
            incident.root_cause_summary = f"Threat injection attempt blocked: {scan['threat_detail']}"
            self.active_incidents[incident.incident_id] = incident
            return incident

        clean_description = scan["sanitized_text"]
        incident = IncidentRecord(title=title, description=clean_description, initial_service=initial_service)
        self.active_incidents[incident.incident_id] = incident

        # Update initial service health in topology
        self.topology.set_service_health(initial_service, "OUTAGE")

        # 2. Phase 1: Triage Agent (Blast radius & severity)
        incident = self.triage_agent.process(incident)

        # 3. Phase 2: RCA Investigator Agent (Microservice topology & MCP inspection)
        incident = self.rca_agent.process(incident)

        # 4. Phase 3: Security & Compliance Auditor Agent
        incident = self.security_agent.process(incident)

        # 5. Phase 4: Remediation Engineer Agent (Synthesize repair plan & pause for HITL)
        incident = self.remediation_agent.process(incident)

        print(f"\n⏸️ [AegisOps] Paused at Human-in-the-Loop Gateway for Incident: {incident.incident_id}")
        return incident

    def approve_and_execute_remediation(self, incident_id: str, approver_name: str = "Lead SRE Engineer") -> Dict[str, Any]:
        """Human-in-the-Loop Gate: Approves and triggers automated repair via MCP tools."""
        if incident_id not in self.active_incidents:
            return {"success": False, "error": f"Incident {incident_id} not found."}

        incident = self.active_incidents[incident_id]
        if incident.status != IncidentStatus.PENDING_APPROVAL:
            return {"success": False, "error": f"Incident is not pending approval (Status: {incident.status.value})."}

        print(f"\n👤 [HITL Approval] Approved by {approver_name} for {incident_id}!")
        incident.human_approved_by = approver_name
        incident.status = IncidentStatus.REMEDIATING

        # Execute remediation commands via MCP
        execution_logs = []
        if incident.remediation_plan:
            plan = incident.remediation_plan
            print(f"⚡ [MCP Execution] Dispatching tools for plan: {plan.action_name}...")

            if "kill_database_idle_locks" in str(plan.commands):
                req = {
                    "jsonrpc": "2.0",
                    "id": "hitl-exec-1",
                    "method": "tools/call",
                    "params": {"name": "kill_database_idle_locks", "arguments": {"cluster_id": "order-db-cluster"}}
                }
                res = self.mcp_server.handle_request(req)
                execution_logs.append(res.get("result", {}).get("content", [{}])[0].get("text", "Executed"))

            if "flush_redis_cache_pattern" in str(plan.commands):
                req = {
                    "jsonrpc": "2.0",
                    "id": "hitl-exec-2",
                    "method": "tools/call",
                    "params": {"name": "flush_redis_cache_pattern", "arguments": {"pattern": "session:stale:*"}}
                }
                res = self.mcp_server.handle_request(req)
                execution_logs.append(res.get("result", {}).get("content", [{}])[0].get("text", "Executed"))

        incident.remediation_result = "\n".join(execution_logs) if execution_logs else "SUCCESS: Infrastructure state restored."

        # Restore service health in topology
        self.topology.set_service_health(incident.initial_service, "HEALTHY")
        if incident.remediation_plan:
            self.topology.set_service_health(incident.remediation_plan.target_service, "HEALTHY")

        incident.mark_resolved()

        # 6. Phase 5: Post-Mortem Scribe Agent (Executive RCA authoring)
        incident = self.postmortem_agent.process(incident)

        print(f"🎉 [AegisOps] Incident {incident.incident_id} RESOLVED! MTTR: {incident.mttr_seconds}s")
        return {
            "success": True,
            "incident_id": incident.incident_id,
            "status": incident.status.value,
            "execution_logs": execution_logs,
            "post_mortem": incident.post_mortem_report
        }
