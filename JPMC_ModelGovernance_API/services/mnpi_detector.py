"""
Material Non-Public Information (MNPI) & Insider Trading Detector
Enforces strict information barriers (Chinese walls) across JPMC LLM Suite.
Prevents unannounced M&A rumors, confidential board deliberations, and earnings leaks from touching LLMs.
"""

import re
from typing import List, Tuple
from schemas import ThreatDetection

# Known project codenames, confidential deal terms, and insider phrasing
MNPI_PATTERNS = [
    (r"\bproject\s+[a-z0-9_]+\b", "M&A_DEAL_CODENAME", "CRITICAL", 0.95),
    (r"\bunannounced\s+(?:merger|acquisition|takeover|dividend|earnings|restructuring)\b", "UNANNOUNCED_CORPORATE_ACTION", "CRITICAL", 0.98),
    (r"\b(?:pre-release|whisper)\s+(?:numbers?|earnings|eps|revenue)\b", "EARNINGS_LEAK", "HIGH", 0.90),
    (r"\bboard\s+(?:deliberation|confidential\s+vote|resolution\s+draft)\b", "BOARD_CONFIDENTIALITY", "CRITICAL", 0.92),
    (r"\bmaterial\s+non[- ]public\s+information\b", "MNPI_EXPLICIT_REFERENCE", "HIGH", 0.85),
    (r"\binsider\s+(?:trading|information|tip)\b", "INSIDER_TRADING_FLAG", "CRITICAL", 0.95),
    (r"\bconfidential\s+(?:pitchbook|term\s+sheet|syndicate\s+book)\b", "CONFIDENTIAL_BANKING_DOC", "MEDIUM", 0.80)
]

def scan_for_mnpi(text: str) -> List[ThreatDetection]:
    threats: List[ThreatDetection] = []
    text_lower = text.lower()
    
    for pattern, t_type, severity, conf in MNPI_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            threats.append(ThreatDetection(
                threat_type=t_type,
                severity=severity,
                matched_pattern=match.group(0),
                confidence=conf
            ))
            
    return threats
