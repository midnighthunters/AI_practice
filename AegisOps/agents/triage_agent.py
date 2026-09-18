"""
triage_agent.py
===============
Specialist Agent 1: Incident Triage & Blast Radius Assessment.
"""

import sys
from typing import Dict, Any
from aegis_core import IncidentRecord, IncidentSeverity, IncidentStatus
from graph_topology import MicroserviceTopology

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class TriageAgent:
    """Classifies incident severity, assesses cascading impact, and determines priority."""

    def __init__(self, topology: MicroserviceTopology):
        self.topology = topology

    def process(self, incident: IncidentRecord) -> IncidentRecord:
        print(f"🚨 [TriageAgent] Ingesting alert for service '{incident.initial_service}'...")

        # 1. Calculate Topology Blast Radius
        blast = self.topology.calculate_blast_radius(incident.initial_service)
        incident.blast_radius = blast["impacted_services"]
        incident.impacted_customers_est = blast["est_customer_impact_pct"]

        # 2. Determine Severity
        sev_rec = blast["recommended_severity"]
        if sev_rec == "P0" or "outage" in incident.description.lower() or "500/500" in incident.description.lower():
            incident.severity = IncidentSeverity.P0_CRITICAL
        elif sev_rec == "P1":
            incident.severity = IncidentSeverity.P1_HIGH
        elif sev_rec == "P2":
            incident.severity = IncidentSeverity.P2_MEDIUM
        else:
            incident.severity = IncidentSeverity.P3_LOW

        incident.status = IncidentStatus.TRIAGED

        # 3. Log Findings
        incident.add_finding(
            agent_name="TriageAgent",
            phase="TRIAGE",
            summary=f"Classified as {incident.severity.value}. Downstream blast radius: {len(incident.blast_radius)} services.",
            details={
                "initial_service": incident.initial_service,
                "tier": blast.get("origin_tier", "TIER_1"),
                "downstream_impacted": incident.blast_radius,
                "est_customer_impact_pct": f"{incident.impacted_customers_est}%",
                "recommended_action": "Initiate forensic RCA on upstream dependencies immediately."
            }
        )

        print(f"✅ [TriageAgent] Severity: {incident.severity.value} | Blast: {incident.blast_radius}")
        return incident
