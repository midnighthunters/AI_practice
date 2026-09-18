"""
mcp_core.py
===========
Core MCP Protocol primitives, JSON-RPC message framing,
Resource Registry, Tool Registry, and Prompt Template Server.
"""

import sys
import os
import json
import uuid
import time
from typing import Dict, Any, Optional, List, Callable

# UTF-8 stdout configuration for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MCP_PROTOCOL_VERSION = "2024-11-05"


class MCPMessageBuilder:
    """Helper to construct compliant MCP JSON-RPC 2.0 messages."""

    @staticmethod
    def request(method: str, params: Optional[Dict[str, Any]] = None, msg_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": msg_id or str(uuid.uuid4())[:8],
            "method": method,
            "params": params or {}
        }

    @staticmethod
    def response(msg_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }

    @staticmethod
    def error(msg_id: str, code: int, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
        err: Dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": err
        }

    @staticmethod
    def notification(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }


class MCPResourceServer:
    """Resource provider exposing URI-based readable resources."""

    def __init__(self):
        self.resources: Dict[str, Dict[str, Any]] = {
            "system://telemetry/cluster": {
                "name": "Live Cluster Telemetry",
                "description": "Real-time CPU, memory, and active GPU cluster metrics.",
                "mimeType": "application/json",
                "content_fn": lambda: json.dumps({
                    "cluster_id": "nova-q8-east",
                    "status": "HEALTHY",
                    "gpu_utilization_pct": 74.2,
                    "active_inferences_per_sec": 1420,
                    "p99_latency_ms": 18.4,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                }, indent=2)
            },
            "docs://quantum/architecture": {
                "name": "Project Nova Architecture Overview",
                "description": "Technical specifications for hybrid optical-classical computing cluster.",
                "mimeType": "text/markdown",
                "content_fn": lambda: (
                    "# QuantumNova Optical Architecture\n\n"
                    "The Q-Core engine utilizes photonic silicon interconnects "
                    "operating at 1550nm wavelength with sub-nanosecond switching times."
                )
            },
            "config://security/policy": {
                "name": "Enterprise Data Policy",
                "description": "Compliance standards for PII handling and LLM token grounding.",
                "mimeType": "text/plain",
                "content_fn": lambda: "Level-1 Public | Level-2 Internal | Level-3 Confidential (Restricted)."
            }
        }
        self.subscribers: Dict[str, List[str]] = {}

    def list_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "uri": uri,
                "name": meta["name"],
                "description": meta["description"],
                "mimeType": meta["mimeType"]
            }
            for uri, meta in self.resources.items()
        ]

    def read_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        if uri not in self.resources:
            return None
        meta = self.resources[uri]
        return {
            "uri": uri,
            "mimeType": meta["mimeType"],
            "text": meta["content_fn"]()
        }


class MCPToolRegistry:
    """Tool provider exposing executable functions with JSON Schema validation."""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register(self, name: str, description: str, input_schema: Dict[str, Any], handler: Callable):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": handler
        }

    def _register_default_tools(self):
        self.register(
            name="calculate_compound_interest",
            description="Calculates future investment value with compound interest.",
            input_schema={
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "Starting investment amount in USD"},
                    "annual_rate": {"type": "number", "description": "Annual interest rate as percentage"},
                    "years": {"type": "integer", "description": "Number of compounding years"},
                    "compounds_per_year": {"type": "integer", "default": 12, "description": "Times compounded per year"}
                },
                "required": ["principal", "annual_rate", "years"]
            },
            handler=self._tool_calculate_interest
        )

        self.register(
            name="check_host_health",
            description="Performs an instant diagnostics check on a given host.",
            input_schema={
                "type": "object",
                "properties": {
                    "hostname": {"type": "string", "description": "Hostname or IP address (e.g. prod-db-01)"},
                    "check_disk": {"type": "boolean", "default": True, "description": "Inspect disk usage"}
                },
                "required": ["hostname"]
            },
            handler=self._tool_check_health
        )

    def _tool_calculate_interest(self, args: Dict[str, Any]) -> str:
        p = float(args["principal"])
        r = float(args["annual_rate"]) / 100.0
        t = float(args["years"])
        n = int(args.get("compounds_per_year", 12))
        amount = p * ((1 + (r / n)) ** (n * t))
        interest = amount - p
        return json.dumps({
            "initial_principal": p,
            "interest_rate_pct": args["annual_rate"],
            "years": t,
            "final_balance": round(amount, 2),
            "total_interest_earned": round(interest, 2)
        }, indent=2)

    def _tool_check_health(self, args: Dict[str, Any]) -> str:
        host = args["hostname"]
        return json.dumps({
            "target": host,
            "reachable": True,
            "latency_ms": 14.2,
            "cpu_load_pct": 28.5,
            "disk_free_gb": 412.0 if args.get("check_disk", True) else "SKIPPED",
            "status": "HEALTHY"
        }, indent=2)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": meta["description"],
                "inputSchema": meta["inputSchema"]
            }
            for name, meta in self.tools.items()
        ]

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            return {"content": [{"type": "text", "text": f"Error: Tool '{name}' not found."}], "isError": True}

        meta = self.tools[name]
        required = meta["inputSchema"].get("required", [])
        missing = [r for r in required if r not in args]
        if missing:
            return {"content": [{"type": "text", "text": f"Validation Error: Missing required fields: {missing}"}], "isError": True}

        try:
            output = meta["handler"](args)
            return {"content": [{"type": "text", "text": output}], "isError": False}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Execution Error: {str(e)}"}], "isError": True}


class MCPPromptServer:
    """Prompt template provider exposing reusable parameterized recipes."""

    def __init__(self):
        self.prompts: Dict[str, Dict[str, Any]] = {
            "code_review_security": {
                "name": "code_review_security",
                "description": "Performs an in-depth OWASP Top 10 security audit of code.",
                "arguments": [
                    {"name": "language", "description": "Programming language (e.g. Python, Go)", "required": True},
                    {"name": "code_snippet", "description": "Source code to audit", "required": True},
                    {"name": "compliance_level", "description": "STRICT or STANDARD", "required": False}
                ],
                "generator": self._gen_security_review
            },
            "root_cause_analysis": {
                "name": "root_cause_analysis",
                "description": "5-Whys incident post-mortem generator for system outages.",
                "arguments": [
                    {"name": "service_name", "description": "Name of failing service", "required": True},
                    {"name": "error_log", "description": "Captured error traceback or syslog", "required": True}
                ],
                "generator": self._gen_rca
            }
        }

    def _gen_security_review(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        lang = args["language"]
        code = args["code_snippet"]
        strict = args.get("compliance_level", "STANDARD")
        system_msg = (
            f"You are a Principal Application Security Auditor. Perform a {strict} review "
            f"for {lang} code. Focus on injection, improper auth, and memory safety."
        )
        user_msg = f"Audit this code:\n\n```{lang}\n{code}\n```"
        return [{"role": "user", "content": {"type": "text", "text": f"{system_msg}\n\n{user_msg}"}}]

    def _gen_rca(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        service = args["service_name"]
        logs = args["error_log"]
        return [{
            "role": "user",
            "content": {
                "type": "text",
                "text": (
                    f"Produce a 5-Whys Root Cause Analysis (RCA) report for incident on service '{service}'.\n"
                    f"Incident Logs:\n```\n{logs}\n```\n\n"
                    "Provide:\n1. Immediate Impact\n2. 5-Whys Chain\n3. Actionable Prevention Items"
                )
            }
        }]

    def list_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": meta["description"],
                "arguments": meta["arguments"]
            }
            for name, meta in self.prompts.items()
        ]

    def get_prompt(self, name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if name not in self.prompts:
            return None
        meta = self.prompts[name]
        for arg in meta["arguments"]:
            if arg.get("required") and arg["name"] not in args:
                raise ValueError(f"Missing required prompt argument: {arg['name']}")
        return {
            "description": meta["description"],
            "messages": meta["generator"](args)
        }


class UnifiedMCPServer:
    """Complete in-memory MCP Server dispatching all JSON-RPC methods."""

    def __init__(self, name: str = "DemoUnifiedMCPServer", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.resources = MCPResourceServer()
        self.tools = MCPToolRegistry()
        self.prompts = MCPPromptServer()
        self.initialized = False

    def handle_jsonrpc(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if "id" not in req:
            if req.get("method") == "notifications/initialized":
                self.initialized = True
            return None

        msg_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})

        if method == "initialize":
            return MCPMessageBuilder.response(msg_id, {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True}
                },
                "serverInfo": {"name": self.name, "version": self.version}
            })

        elif method == "ping":
            return MCPMessageBuilder.response(msg_id, {})

        elif method == "resources/list":
            return MCPMessageBuilder.response(msg_id, {"resources": self.resources.list_resources()})

        elif method == "resources/read":
            uri = params.get("uri", "")
            res = self.resources.read_resource(uri)
            if not res:
                return MCPMessageBuilder.error(msg_id, -32602, f"Resource not found: {uri}")
            return MCPMessageBuilder.response(msg_id, {"contents": [res]})

        elif method == "tools/list":
            return MCPMessageBuilder.response(msg_id, {"tools": self.tools.list_tools()})

        elif method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {})
            call_res = self.tools.call_tool(name, args)
            return MCPMessageBuilder.response(msg_id, call_res)

        elif method == "prompts/list":
            return MCPMessageBuilder.response(msg_id, {"prompts": self.prompts.list_prompts()})

        elif method == "prompts/get":
            name = params.get("name", "")
            args = params.get("arguments", {})
            try:
                p_res = self.prompts.get_prompt(name, args)
                if not p_res:
                    return MCPMessageBuilder.error(msg_id, -32602, f"Prompt not found: {name}")
                return MCPMessageBuilder.response(msg_id, p_res)
            except ValueError as ve:
                return MCPMessageBuilder.error(msg_id, -32602, str(ve))

        return MCPMessageBuilder.error(msg_id, -32601, f"Unknown method: {method}")
