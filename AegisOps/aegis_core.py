"""
aegis_core.py
=============
Core Data Structures, Incident State Models, and Checkpointed Session Store
for the AegisOps Autonomous SRE & Incident Commander Platform.
"""

import sys
import os
import json
import time
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class IncidentSeverity(str, Enum):
    P0_CRITICAL = "P0 - CRITICAL (System Outage / Data Hazard)"
    P1_HIGH = "P1 - HIGH (Severe Degradation / Cascading Risk)"
    P2_MEDIUM = "P2 - MEDIUM (Isolated Service Impairment)"
    P3_LOW = "P3 - LOW (Minor Anomaly / Telemetry Drift)"


class IncidentStatus(str, Enum):
    TRIGGERED = "TRIGGERED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    REMEDIATING = "REMEDIATING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class AgentFinding:
    """Structured report item produced by an autonomous specialist agent."""

    def __init__(self, agent_name: str, phase: str, summary: str, details: Dict[str, Any]):
        self.agent_name = agent_name
        self.phase = phase
        self.summary = summary
        self.details = details
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "phase": self.phase,
            "summary": self.summary,
            "details": self.details,
            "timestamp": self.timestamp
        }


class RemediationPlan:
    """Surgical remediation actions synthesized for human review."""

    def __init__(
        self,
        action_name: str,
        target_service: str,
        command_type: str,
        commands: List[str],
        rollback_plan: List[str],
        risk_level: str = "HIGH"
    ):
        self.action_name = action_name
        self.target_service = target_service
        self.command_type = command_type  # e.g. "KUBERNETES", "DATABASE", "REDIS", "NETWORK"
        self.commands = commands
        self.rollback_plan = rollback_plan
        self.risk_level = risk_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_name": self.action_name,
            "target_service": self.target_service,
            "command_type": self.command_type,
            "commands": self.commands,
            "rollback_plan": self.rollback_plan,
            "risk_level": self.risk_level
        }


class IncidentRecord:
    """Central representation of an operational incident lifecycle."""

    def __init__(
        self,
        title: str,
        description: str,
        initial_service: str,
        incident_id: Optional[str] = None
    ):
        self.incident_id = incident_id or f"INC-2026-{str(uuid.uuid4())[:6].upper()}"
        self.title = title
        self.description = description
        self.initial_service = initial_service
        self.severity: IncidentSeverity = IncidentSeverity.P2_MEDIUM
        self.status: IncidentStatus = IncidentStatus.TRIGGERED
        self.start_time = time.time()
        self.resolution_time: Optional[float] = None

        # Topology and Blast Radius
        self.blast_radius: List[str] = []
        self.impacted_customers_est: int = 0

        # Specialist Agent Outputs
        self.findings: List[AgentFinding] = []
        self.root_cause_summary: str = ""
        self.security_clearance: bool = True
        self.security_notes: str = ""
        self.remediation_plan: Optional[RemediationPlan] = None
        self.remediation_result: Optional[str] = None
        self.human_approved_by: Optional[str] = None
        self.post_mortem_report: str = ""

    def add_finding(self, agent_name: str, phase: str, summary: str, details: Dict[str, Any]):
        finding = AgentFinding(agent_name, phase, summary, details)
        self.findings.append(finding)

    def mark_resolved(self):
        self.status = IncidentStatus.RESOLVED
        self.resolution_time = time.time()

    @property
    def mttd_seconds(self) -> float:
        """Mean Time to Detect / Triage."""
        return 4.2  # Simulated real-time autonomous detection in seconds

    @property
    def mttr_seconds(self) -> float:
        """Mean Time to Remediate."""
        if self.resolution_time:
            return round(self.resolution_time - self.start_time, 2)
        return 28.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "initial_service": self.initial_service,
            "severity": self.severity.value if isinstance(self.severity, IncidentSeverity) else str(self.severity),
            "status": self.status.value if isinstance(self.status, IncidentStatus) else str(self.status),
            "blast_radius": self.blast_radius,
            "impacted_customers_est": self.impacted_customers_est,
            "root_cause_summary": self.root_cause_summary,
            "security_clearance": self.security_clearance,
            "security_notes": self.security_notes,
            "remediation_plan": self.remediation_plan.to_dict() if self.remediation_plan else None,
            "remediation_result": self.remediation_result,
            "human_approved_by": self.human_approved_by,
            "post_mortem_report": self.post_mortem_report,
            "mttd_seconds": self.mttd_seconds,
            "mttr_seconds": self.mttr_seconds,
            "findings_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings]
        }
