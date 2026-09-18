"""
mcp_sre_server.py
=================
Model Context Protocol (MCP) Server for Site Reliability Engineering (SRE).
Exposes real-time telemetry resources and executable infrastructure tools.
"""

import sys
import json
import time
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class MCPSREServer:
    """Enterprise SRE Tool & Resource Server adhering to Model Context Protocol."""

    def __init__(self):
        # Simulated live system telemetry
        self.metrics_store = {
            "order-db-cluster": {
                "active_connections": 498,
                "max_connections": 500,
                "connection_utilization_pct": 99.6,
                "deadlocks_detected": 14,
                "lock_wait_timeout_count": 82,
                "p99_query_latency_ms": 4200.0,
                "status": "CRITICAL"
            },
            "redis-session-cache": {
                "used_memory_mb": 7840,
                "max_memory_mb": 8192,
                "eviction_rate_per_sec": 4200,
                "hit_rate_pct": 42.1,  # Severe drop from normal 98%
                "status": "DEGRADED"
            },
            "api-gateway": {
                "http_5xx_rate_pct": 34.2,
                "requests_per_second": 18500,
                "p99_latency_ms": 3800.0,
                "status": "DEGRADED"
            },
            "checkout-service": {
                "http_5xx_rate_pct": 78.4,
                "requests_per_second": 4200,
                "status": "OUTAGE"
            }
        }

        # Simulated live container logs
        self.logs_store = {
            "order-db-cluster": [
                "[FATAL] 2026-09-18T16:04:12Z postgres[9041]: remaining connection slots are reserved for non-replication superuser connections",
                "[ERROR] 2026-09-18T16:04:15Z postgres[9044]: process 9044 deadlock detected: Process 9044 waits for ExclusiveLock on transaction 88402; blocked by process 9012.",
                "[WARN]  2026-09-18T16:04:22Z pg_bouncer: client connection pool 'orders_pool' exhausted (500/500 active)"
            ],
            "order-service": [
                "[ERROR] 2026-09-18T16:04:18Z OrderWorker-4: org.postgresql.util.PSQLException: Connection to order-db-cluster:5432 refused (connection timeout: 5000ms)",
                "[ERROR] 2026-09-18T16:04:19Z OrderWorker-7: CircuitBreaker 'order-db' OPEN. Fast failing incoming checkout calls.",
                "[WARN]  2026-09-18T16:04:25Z RetryQueue: 1420 orders buffered in memory, queue overflow imminent."
            ],
            "checkout-service": [
                "[ERROR] 2026-09-18T16:04:20Z CheckoutController: Failed to commit checkout transaction for customer_id=84021: Downstream order-service returned 503 Service Unavailable"
            ],
            "redis-session-cache": [
                "[WARN]  2026-09-18T16:04:01Z redis-server[1]: OOM command not allowed when used memory > 'maxmemory'. Key evictions throttling performance."
            ]
        }

        # Executable Tools registry
        self.tools = {
            "kill_database_idle_locks": {
                "name": "kill_database_idle_locks",
                "description": "Kills deadlocked and idle in-transaction queries blocking the database connection pool.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cluster_id": {"type": "string", "description": "Database cluster name (e.g., order-db-cluster)"},
                        "max_age_seconds": {"type": "integer", "default": 30, "description": "Max query age in seconds"}
                    },
                    "required": ["cluster_id"]
                },
                "handler": self._tool_kill_db_locks
            },
            "scale_service_replicas": {
                "name": "scale_service_replicas",
                "description": "Scales Kubernetes pod replica count to handle traffic spikes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string", "description": "Microservice identifier"},
                        "replicas": {"type": "integer", "description": "Target replica count (e.g. 10)"}
                    },
                    "required": ["service_id", "replicas"]
                },
                "handler": self._tool_scale_service
            },
            "flush_redis_cache_pattern": {
                "name": "flush_redis_cache_pattern",
                "description": "Flushes corrupted or high-memory keys matching a Redis glob pattern.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Key pattern (e.g., 'session:stale:*' or 'cart:*')"}
                    },
                    "required": ["pattern"]
                },
                "handler": self._tool_flush_redis
            },
            "enable_circuit_breaker": {
                "name": "enable_circuit_breaker",
                "description": "Trips an immediate circuit breaker to protect upstream services from cascading latency.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string", "description": "Service to protect"},
                        "target_dependency": {"type": "string", "description": "Failing dependency to isolate"}
                    },
                    "required": ["service_id", "target_dependency"]
                },
                "handler": self._tool_enable_circuit_breaker
            }
        }

    # --- Tool Handlers ---
    def _tool_kill_db_locks(self, args: Dict[str, Any]) -> str:
        cluster = args["cluster_id"]
        # Update simulated metrics to demonstrate immediate remediation recovery!
        if cluster in self.metrics_store:
            self.metrics_store[cluster]["active_connections"] = 84
            self.metrics_store[cluster]["connection_utilization_pct"] = 16.8
            self.metrics_store[cluster]["deadlocks_detected"] = 0
            self.metrics_store[cluster]["p99_query_latency_ms"] = 18.2
            self.metrics_store[cluster]["status"] = "HEALTHY"

        return json.dumps({
            "action": "kill_database_idle_locks",
            "cluster": cluster,
            "terminated_pids_count": 42,
            "released_locks_count": 86,
            "new_connection_utilization_pct": 16.8,
            "status": "SUCCESS: Connection pool freed. Deadlocks resolved."
        }, indent=2)

    def _tool_scale_service(self, args: Dict[str, Any]) -> str:
        svc = args["service_id"]
        reps = args["replicas"]
        return json.dumps({
            "action": "scale_service_replicas",
            "service": svc,
            "previous_replicas": 3,
            "target_replicas": reps,
            "active_pods": [f"{svc}-pod-{i+1}" for i in range(reps)],
            "status": f"SUCCESS: Deployment {svc} scaled to {reps} replicas."
        }, indent=2)

    def _tool_flush_redis(self, args: Dict[str, Any]) -> str:
        pat = args["pattern"]
        if "redis-session-cache" in self.metrics_store:
            self.metrics_store["redis-session-cache"]["used_memory_mb"] = 2100
            self.metrics_store["redis-session-cache"]["hit_rate_pct"] = 97.8
            self.metrics_store["redis-session-cache"]["status"] = "HEALTHY"

        return json.dumps({
            "action": "flush_redis_cache_pattern",
            "pattern": pat,
            "keys_evicted": 128400,
            "memory_reclaimed_mb": 5740,
            "status": "SUCCESS: Redis memory pressure relieved."
        }, indent=2)

    def _tool_enable_circuit_breaker(self, args: Dict[str, Any]) -> str:
        svc = args["service_id"]
        dep = args["target_dependency"]
        return json.dumps({
            "action": "enable_circuit_breaker",
            "source_service": svc,
            "isolated_dependency": dep,
            "fallback_strategy": "STATIC_DEGRADED_RESPONSE",
            "status": f"SUCCESS: Isolated {dep} from {svc}. Cascading failure halted."
        }, indent=2)

    # --- MCP JSON-RPC Protocol Dispatcher ---
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        msg_id = request.get("id", "1")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "AegisOps-MCP-SRE-Server", "version": "3.0.0"}
                }
            }

        elif method == "resources/list":
            resources = []
            for svc in self.metrics_store:
                resources.append({
                    "uri": f"metrics://service/{svc}",
                    "name": f"Telemetry Metrics for {svc}",
                    "mimeType": "application/json"
                })
            for svc in self.logs_store:
                resources.append({
                    "uri": f"logs://service/{svc}/tail",
                    "name": f"Container Log Tail for {svc}",
                    "mimeType": "text/plain"
                })
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"resources": resources}}

        elif method == "resources/read":
            uri = params.get("uri", "")
            if uri.startswith("metrics://service/"):
                svc = uri.replace("metrics://service/", "")
                data = self.metrics_store.get(svc, {"error": "Service metrics not found"})
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(data, indent=2)}]}
                }
            elif uri.startswith("logs://service/"):
                parts = uri.replace("logs://service/", "").split("/")
                svc = parts[0]
                logs = self.logs_store.get(svc, ["[INFO] No anomalous logs detected."])
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"contents": [{"uri": uri, "mimeType": "text/plain", "text": "\n".join(logs)}]}
                }
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": f"Resource URI not found: {uri}"}}

        elif method == "tools/list":
            tools_list = [
                {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
                for t in self.tools.values()
            ]
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools_list}}

        elif method == "tools/call":
            t_name = params.get("name")
            args = params.get("arguments", {})
            if t_name not in self.tools:
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": f"Tool '{t_name}' not found."}], "isError": True}}

            try:
                res = self.tools[t_name]["handler"](args)
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": res}], "isError": False}}
            except Exception as e:
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": str(e)}], "isError": True}}

        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method {method} not found"}}
