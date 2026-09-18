"""
guardrails_engine.py
====================
Production SRE Guardrails, Threat Defense & Semantic Playbook Cache
for AegisOps Autonomous Incident Commander.
"""

import sys
import re
import math
import time
from collections import Counter
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class SRESecurityGuardrail:
    """Detects security threats in alert payloads and sanitizes operational credentials."""

    # SRE Injection Attack Vectors (e.g., trying to trick remediation agent into running destructive commands)
    DESTRUCTIVE_COMMAND_PATTERNS = [
        r"(?i)\brm\s+-rf\s+/",
        r"(?i)\bdd\s+if=/dev/zero",
        r"(?i)\bmkfs\b",
        r"(?i)\bdrop\s+database\b",
        r"(?i)\bdrop\s+table\b",
        r"(?i)\btruncate\s+table\b",
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"(?i)disable\s+firewall",
        r"(?i)curl\s+.*\|\s*(bash|sh)"
    ]

    # Sensitive Infrastructure Secrets
    SECRET_PATTERNS = {
        "DB_CONNECTION_STRING": r"(?i)(postgres(ql)?|mysql|mongodb)://[^\s]+",
        "JWT_BEARER_TOKEN": r"Bearer\s+ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "AWS_ACCESS_KEY": r"\b(AKIA|ABIA|ACCA)[0-9A-Z]{16}\b",
        "API_SECRET_KEY": r"(?i)(api[_-]?key|secret[_-]?key)[\s:=]+['\"]?([A-Za-z0-9_\-\.]{24,})['\"]?"
    }

    @classmethod
    def sanitize_alert_and_logs(cls, raw_text: str) -> Dict[str, Any]:
        """Scans for destructive attacks and masks credentials from telemetry/logs."""
        # 1. Threat Detection
        malicious = False
        threat_detail = None
        for pattern in cls.DESTRUCTIVE_COMMAND_PATTERNS:
            match = re.search(pattern, raw_text)
            if match:
                malicious = True
                threat_detail = match.group(0)
                break

        # 2. Secret Redaction
        sanitized = raw_text
        redacted_count = 0
        for secret_type, regex in cls.SECRET_PATTERNS.items():
            matches = list(re.finditer(regex, sanitized))
            if matches:
                redacted_count += len(matches)
                sanitized = re.sub(regex, f"[REDACTED_{secret_type}]", sanitized)

        return {
            "allowed": not malicious,
            "threat_detected": malicious,
            "threat_detail": threat_detail,
            "secrets_redacted_count": redacted_count,
            "sanitized_text": sanitized
        }


class SemanticPlaybookCache:
    """Caches proven incident remediations by alert pattern similarity."""

    def __init__(self, similarity_threshold: float = 0.80):
        self.threshold = similarity_threshold
        self.cache: List[Dict[str, Any]] = []
        self._seed_production_playbooks()

    def _stem(self, word: str) -> str:
        w = word.lower()
        for suffix in ("ing", "es", "ed", "s"):
            if w.endswith(suffix) and len(w) > len(suffix) + 2:
                return w[:-len(suffix)]
        return w

    def _tokenize(self, text: str) -> Counter:
        words = re.findall(r"\w+", text.lower())
        return Counter([self._stem(w) for w in words if len(w) > 2])

    def _cosine_similarity(self, vec1: Counter, vec2: Counter) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        num = sum([vec1[x] * vec2[x] for x in intersection])
        denom = math.sqrt(sum([v ** 2 for v in vec1.values()])) * math.sqrt(sum([v ** 2 for v in vec2.values()]))
        return (num / denom) if denom else 0.0

    def _seed_production_playbooks(self):
        # Seed proven enterprise runbooks
        self.cache.append({
            "alert_pattern": "PostgreSQL connection pool exhausted 500/500 active locks deadlock detected",
            "action": "kill_database_idle_locks",
            "playbook_id": "PB-ORDER-DB-01",
            "vector": self._tokenize("PostgreSQL connection pool exhausted 500/500 active locks deadlock detected"),
            "target_service": "order-db-cluster",
            "commands": ["mcp_call: kill_database_idle_locks(cluster_id='order-db-cluster', max_age_seconds=30)"]
        })
        self.cache.append({
            "alert_pattern": "Redis OOM used memory maxmemory cache eviction performance throttled",
            "action": "flush_redis_cache_pattern",
            "playbook_id": "PB-REDIS-OOM-02",
            "vector": self._tokenize("Redis OOM used memory maxmemory cache eviction performance throttled"),
            "target_service": "redis-session-cache",
            "commands": ["mcp_call: flush_redis_cache_pattern(pattern='session:stale:*')"]
        })

    def lookup(self, alert_description: str) -> Optional[Dict[str, Any]]:
        """Finds cached playbook if cosine similarity >= threshold."""
        query_vec = self._tokenize(alert_description)
        best_sim = 0.0
        best_item = None

        for item in self.cache:
            sim = self._cosine_similarity(query_vec, item["vector"])
            if sim > best_sim:
                best_sim = sim
                best_item = item

        if best_item and best_sim >= self.threshold:
            return {
                "matched_playbook_id": best_item["playbook_id"],
                "similarity": round(best_sim, 3),
                "action": best_item["action"],
                "target_service": best_item["target_service"],
                "commands": best_item["commands"],
                "cache_hit": True
            }

        return None
