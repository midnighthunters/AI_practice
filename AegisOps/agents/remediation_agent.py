"""
remediation_agent.py
====================
Specialist Agent 4: Remediation Engineer & Playbook Synthesizer.
"""

import sys
from typing import Dict, Any, Optional
from aegis_core import IncidentRecord, RemediationPlan, IncidentStatus
from guardrails_engine import SemanticPlaybookCache

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class RemediationEngineerAgent:
    """Synthesizes surgical remediation actions and prepares Human-in-the-Loop execution plan."""

    def __init__(self, playbook_cache: SemanticPlaybookCache):
        self.playbook_cache = playbook_cache

    def process(self, incident: IncidentRecord) -> IncidentRecord:
        print(f"🛠️ [RemediationEngineer] Synthesizing repair plan for incident '{incident.incident_id}'...")

        # 1. Check Semantic Playbook Cache
        cached_hit = self.playbook_cache.lookup(incident.description + " " + incident.root_cause_summary)

        if "order-db-cluster" in incident.root_cause_summary or (cached_hit and cached_hit.get("action") == "kill_database_idle_locks"):
            plan = RemediationPlan(
                action_name="Terminate Deadlocked Transactions & Reset Pool",
                target_service="order-db-cluster",
                command_type="DATABASE_MCP",
                commands=[
                    "mcp_tool_call: kill_database_idle_locks(cluster_id='order-db-cluster', max_age_seconds=30)",
                    "kubectl scale deployment/order-service --replicas=8",
                    "pg_isready -h order-db-cluster -p 5432 -U app_user"
                ],
                rollback_plan=[
                    "kubectl scale deployment/order-service --replicas=3",
                    "pg_ctlcluster 16 main reload"
                ],
                risk_level="MEDIUM (Production Connection Reset)"
            )
        elif "redis" in incident.root_cause_summary or (cached_hit and cached_hit.get("action") == "flush_redis_cache_pattern"):
            plan = RemediationPlan(
                action_name="Evict Stale Session Keys & Relieve OOM",
                target_service="redis-session-cache",
                command_type="REDIS_MCP",
                commands=[
                    "mcp_tool_call: flush_redis_cache_pattern(pattern='session:stale:*')",
                    "redis-cli -h redis-session-cache config set maxmemory-policy volatile-lru"
                ],
                rollback_plan=[
                    "redis-cli -h redis-session-cache config set maxmemory-policy allkeys-lru"
                ],
                risk_level="LOW (Safe Session Key Eviction)"
            )
        else:
            plan = RemediationPlan(
                action_name="Scale Service Replicas & Engage Circuit Breaker",
                target_service=incident.initial_service,
                command_type="KUBERNETES_MCP",
                commands=[
                    f"kubectl scale deployment/{incident.initial_service} --replicas=10",
                    f"mcp_tool_call: enable_circuit_breaker(service_id='{incident.initial_service}', target_dependency='order-service')"
                ],
                rollback_plan=[
                    f"kubectl scale deployment/{incident.initial_service} --replicas=3"
                ],
                risk_level="LOW (Horizontal Pod Autoscaling)"
            )

        incident.remediation_plan = plan
        incident.status = IncidentStatus.PENDING_APPROVAL

        # Log Findings
        incident.add_finding(
            agent_name="RemediationEngineerAgent",
            phase="REMEDIATION_SYNTHESIS",
            summary=f"Synthesized Plan: {plan.action_name}. Pausing for Human-in-the-Loop approval.",
            details={
                "action": plan.action_name,
                "target": plan.target_service,
                "commands": plan.commands,
                "rollback": plan.rollback_plan,
                "risk": plan.risk_level,
                "semantic_cache_hit": cached_hit is not None
            }
        )

        print(f"🛑 [RemediationEngineer] Plan generated. Pausing at Human-in-the-Loop Gateway: {plan.action_name}")
        return incident
