"""
Prompt Injection & Adversarial Jailbreak Firewall
Blocks unauthorized instruction overrides, DAN exploits, and system prompt exfiltration.
"""

import re
from typing import List
from schemas import ThreatDetection

INJECTION_PATTERNS = [
    (r"\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|rules|prompts)\b", "INSTRUCTION_OVERRIDE", "CRITICAL", 0.98),
    (r"\byou\s+are\s+now\s+(?:an?\s+)?(?:unfiltered|jailbroken|dan|developer\s+mode)\b", "JAILBREAK_ATTEMPT", "CRITICAL", 0.99),
    (r"\b(?:reveal|show|print|display)\s+(?:your\s+)?(?:system\s+prompt|initial\s+instructions)\b", "PROMPT_EXFILTRATION", "HIGH", 0.92),
    (r"\bexecute\s+(?:base64|hex|encoded)\s+command\b", "PAYLOAD_OBFUSCATION", "HIGH", 0.88),
    (r"\[system\]\s*:\s*override", "SYSTEM_HEADER_SPOOFING", "CRITICAL", 0.95)
]

def scan_for_injection(text: str) -> List[ThreatDetection]:
    threats: List[ThreatDetection] = []
    text_lower = text.lower()
    
    for pattern, t_type, severity, conf in INJECTION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            threats.append(ThreatDetection(
                threat_type=t_type,
                severity=severity,
                matched_pattern=match.group(0),
                confidence=conf
            ))
            
    return threats
