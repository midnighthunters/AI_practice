"""
graph_topology.py
=================
GraphRAG Microservice Topology, Blast Radius Analysis & Dependency Engine
for AegisOps Autonomous SRE Platform.
"""

import sys
import json
from collections import deque
from typing import Dict, Any, List, Set, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class ServiceTier:
    TIER_0 = "CRITICAL_CORE"      # Direct checkout/auth impact
    TIER_1 = "PRIMARY_BUSINESS"   # High traffic user services
    TIER_2 = "SUPPORTING"         # Background async processing
    TIER_3 = "ANALYTICS"          # Offline batch, reporting


class MicroserviceTopology:
    """Directed Knowledge Graph of enterprise microservice dependencies."""

    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
        # Directed edge: A -> B means "A depends on B" (A calls B)
        self.dependencies: Dict[str, List[str]] = {}
        # Reverse edge: B -> A means "B is consumed by A" (if B dies, A is impacted)
        self.dependents: Dict[str, List[str]] = {}
        self._build_enterprise_topology()

    def add_service(
        self,
        service_id: str,
        name: str,
        tier: str,
        category: str,
        sla_target: str,
        health: str = "HEALTHY",
        runbook: str = ""
    ):
        self.services[service_id] = {
            "id": service_id,
            "name": name,
            "tier": tier,
            "category": category,
            "sla": sla_target,
            "health": health,
            "runbook": runbook
        }
        self.dependencies.setdefault(service_id, [])
        self.dependents.setdefault(service_id, [])

    def add_dependency(self, caller: str, callee: str):
        """Declares that 'caller' calls/depends on 'callee'."""
        if caller not in self.dependencies:
            self.dependencies[caller] = []
        if callee not in self.dependents:
            self.dependents[callee] = []

        if callee not in self.dependencies[caller]:
            self.dependencies[caller].append(callee)
        if caller not in self.dependents[callee]:
            self.dependents[callee].append(caller)

    def _build_enterprise_topology(self):
        """Constructs a realistic production e-commerce & financial architecture."""
        # Tier 0 Services
        self.add_service("api-gateway", "Kong API Gateway", ServiceTier.TIER_0, "GATEWAY", "99.99%", runbook="RB-01: Scale gateway pods, inspect TLS certs, check rate limiting.")
        self.add_service("auth-service", "Identity & Auth Service", ServiceTier.TIER_0, "AUTH", "99.99%", runbook="RB-02: Flush stale JWT tokens, inspect Redis session cache.")
        self.add_service("order-db-cluster", "PostgreSQL Order Shards", ServiceTier.TIER_0, "DATABASE", "99.999%", runbook="RB-03: Kill idle transaction locks, increase connection pool, failover replica.")
        self.add_service("ledger-aurora", "Financial Ledger Aurora DB", ServiceTier.TIER_0, "DATABASE", "99.999%", runbook="RB-04: Verify checksums, inspect read-replica lag, restart read-replica.")

        # Tier 1 Services
        self.add_service("checkout-service", "Cart & Checkout Engine", ServiceTier.TIER_1, "SERVICE", "99.95%", runbook="RB-05: Enable circuit breaker, bypass non-essential discount checks.")
        self.add_service("order-service", "Order Orchestration", ServiceTier.TIER_1, "SERVICE", "99.95%", runbook="RB-06: Drain dead-letter queues, restart order worker pool.")
        self.add_service("billing-engine", "Billing & Invoice Engine", ServiceTier.TIER_1, "SERVICE", "99.95%", runbook="RB-07: Verify Stripe idempotency keys, re-queue failed webhooks.")
        self.add_service("redis-session-cache", "Redis Primary Cluster", ServiceTier.TIER_1, "CACHE", "99.99%", runbook="RB-08: Flush invalid eviction keys, failover to hot standby node.")

        # Tier 2 & External Services
        self.add_service("inventory-service", "Warehouse Inventory", ServiceTier.TIER_2, "SERVICE", "99.9%", runbook="RB-09: Reconcile stock locks, purge cache.")
        self.add_service("kafka-event-bus", "Kafka Streaming Brokers", ServiceTier.TIER_1, "MESSAGE_BUS", "99.99%", runbook="RB-10: Rebalance partitions, increase consumer lag threshold.")
        self.add_service("stripe-payment-gw", "Stripe Payment Gateway", ServiceTier.TIER_1, "EXTERNAL_API", "99.95%", runbook="RB-11: Verify external status page, route via Adyen backup.")
        self.add_service("notification-hub", "Customer Push & Email Hub", ServiceTier.TIER_2, "ASYNC_WORKER", "99.5%", runbook="RB-12: Throttle SES outgoing queue, drop debug notifications.")

        # Wire Dependencies (caller -> callee)
        self.add_dependency("api-gateway", "auth-service")
        self.add_dependency("api-gateway", "checkout-service")
        self.add_dependency("api-gateway", "order-service")

        self.add_dependency("auth-service", "redis-session-cache")
        self.add_dependency("checkout-service", "order-service")
        self.add_dependency("checkout-service", "inventory-service")

        self.add_dependency("order-service", "order-db-cluster")
        self.add_dependency("order-service", "billing-engine")
        self.add_dependency("order-service", "kafka-event-bus")

        self.add_dependency("billing-engine", "stripe-payment-gw")
        self.add_dependency("billing-engine", "ledger-aurora")

        self.add_dependency("kafka-event-bus", "notification-hub")

    def calculate_blast_radius(self, failing_service: str) -> Dict[str, Any]:
        """Calculates downstream cascading failure reachability (who breaks if this service fails)."""
        if failing_service not in self.services:
            return {"impacted_services": [], "total_impacted": 0, "severity_recommendation": "P3"}

        impacted: Set[str] = set()
        queue = deque([failing_service])

        # Traverse reverse edges (dependents)
        while queue:
            curr = queue.popleft()
            for dep in self.dependents.get(curr, []):
                if dep not in impacted:
                    impacted.add(dep)
                    queue.append(dep)

        tier_0_hit = any(self.services[s]["tier"] == ServiceTier.TIER_0 for s in impacted) or self.services[failing_service]["tier"] == ServiceTier.TIER_0
        tier_1_hit = any(self.services[s]["tier"] == ServiceTier.TIER_1 for s in impacted) or self.services[failing_service]["tier"] == ServiceTier.TIER_1

        if tier_0_hit or len(impacted) >= 4:
            recommended_sev = "P0"
            est_customer_impact = 85
        elif tier_1_hit or len(impacted) >= 2:
            recommended_sev = "P1"
            est_customer_impact = 40
        else:
            recommended_sev = "P2"
            est_customer_impact = 10

        return {
            "origin_failure": failing_service,
            "origin_tier": self.services[failing_service]["tier"],
            "impacted_services": list(impacted),
            "total_impacted": len(impacted),
            "recommended_severity": recommended_sev,
            "est_customer_impact_pct": est_customer_impact
        }

    def trace_root_cause_path(self, symptom_service: str) -> List[Dict[str, str]]:
        """Traces upstream dependencies to identify potential root causes (who did this service call?)."""
        upstream_chain = []
        queue = deque([(symptom_service, 0)])
        visited = {symptom_service}

        while queue:
            curr, depth = queue.popleft()
            for callee in self.dependencies.get(curr, []):
                if callee not in visited:
                    visited.add(callee)
                    meta = self.services.get(callee, {})
                    upstream_chain.append({
                        "caller": curr,
                        "callee": callee,
                        "callee_name": meta.get("name", callee),
                        "callee_health": meta.get("health", "UNKNOWN"),
                        "runbook": meta.get("runbook", "N/A")
                    })
                    queue.append((callee, depth + 1))

        return upstream_chain

    def set_service_health(self, service_id: str, health_status: str):
        """Updates health status (HEALTHY, DEGRADED, OUTAGE)."""
        if service_id in self.services:
            self.services[service_id]["health"] = health_status

    def to_dict(self) -> Dict[str, Any]:
        """Serializes topology for the interactive Canvas graph visualizer."""
        edge_list = []
        for caller, callees in self.dependencies.items():
            for callee in callees:
                edge_list.append({
                    "source": caller,
                    "target": callee
                })

        return {
            "services": list(self.services.values()),
            "edges": edge_list
        }
