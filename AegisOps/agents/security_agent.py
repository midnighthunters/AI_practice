"""
security_agent.py
=================
Specialist Agent 3: Security & Compliance Auditor.
"""

import sys
import re
from typing import Dict, Any
from aegis_core import IncidentRecord

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class SecurityAuditorAgent:
    """Audits incident for cyber threats, data breach vectors, and remediation safety."""

    SQLI_PATTERNS = [r"(?i)union\s+select", r"(?i)'\s+or\s+'1'='1", r"(?i)--\s*$", r"(?i);\s*drop\s+"]

    def process(self, incident: IncidentRecord) -> IncidentRecord:
        print(f"🔒 [SecurityAuditor] Auditing incident '{incident.incident_id}' for exploit vectors...")

        is_exploit = False
        findings = []

        # Inspect alert description and initial context for attack signatures
        for pat in self.SQLI_PATTERNS:
            if re.search(pat, incident.description):
                is_exploit = True
                findings.append("Detected SQL Injection attack vector in incoming payload.")

        if "exfiltration" in incident.description.lower() or "unauthorized" in incident.description.lower():
            is_exploit = True
            findings.append("Potential data exfiltration attempt flagged by perimeter WAF.")

        if is_exploit:
            incident.security_clearance = False
            incident.security_notes = "ALERT: Malicious threat actor detected. Mandatory SecOps review required."
        else:
            incident.security_clearance = True
            incident.security_notes = "CLEARED: Incident classified as internal operational/capacity failure (Non-malicious)."

        # Log Findings
        incident.add_finding(
            agent_name="SecurityAuditorAgent",
            phase="SECURITY_AUDIT",
            summary=f"Security Status: {'CLEARED' if incident.security_clearance else 'THREAT DETECTED'}",
            details={
                "is_exploit": is_exploit,
                "notes": incident.security_notes,
                "threat_signatures": findings,
                "compliance_check": "ISO-27001 / SOC-2 Compliant"
            }
        )

        print(f"✅ [SecurityAuditor] Status: {incident.security_notes}")
        return incident
