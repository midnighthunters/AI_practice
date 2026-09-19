"""
Banking PII & Financial Entity Sanitizer
Sanitizes UK National Insurance Numbers (NINO), IBANs, SWIFT BICs, UK Sort Codes,
and credit cards with reversible pseudonymization tokens (e.g. [REDACTED_IBAN_1]).
"""

import re
import uuid
from typing import Dict, List, Tuple
from schemas import SanitizeResponse

# Financial regex patterns
PATTERNS = {
    "IBAN": r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b",
    "SWIFT_BIC": r"\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b",
    "UK_NINO": r"\b[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]\s?[0-9]{2}\s?[0-9]{2}\s?[0-9]{2}\s?[A-D]\b",
    "UK_SORT_CODE": r"\b\d{2}-\d{2}-\d{2}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
}

# In-memory mapping vault
pseudonym_vault: Dict[str, Dict[str, str]] = {}

def sanitize_banking_payload(text: str, anonymize_mnpi: bool = True, anonymize_banking_pii: bool = True) -> SanitizeResponse:
    mapping_id = str(uuid.uuid4())
    token_map: Dict[str, str] = {}
    entities_masked: List[Dict[str, str]] = []
    sanitized = text

    if anonymize_banking_pii:
        for p_name, regex in PATTERNS.items():
            matches = list(re.finditer(regex, sanitized, re.IGNORECASE))
            for idx, match in enumerate(matches, start=1):
                val = match.group(0)
                # Avoid masking standard English words matching SWIFT loosely
                if p_name == "SWIFT_BIC" and (len(val) < 8 or not any(c in val for c in ["CHAS", "JPMC", "MIDL", "BARC", "HSBC"])):
                    continue
                token = f"[MASKED_{p_name}_{idx}]"
                token_map[token] = val
                sanitized = sanitized.replace(val, token)
                entities_masked.append({
                    "entity_type": p_name,
                    "original_value": val[:4] + "****" if len(val) > 4 else "****",
                    "replacement_token": token
                })

    if anonymize_mnpi:
        # Mask project names like "Project Falcon" -> "[RESTRICTED_PROJECT_CODENAME]"
        project_matches = re.finditer(r"\bproject\s+([a-z0-9_]+)\b", sanitized, re.IGNORECASE)
        for idx, match in enumerate(project_matches, start=1):
            val = match.group(0)
            token = f"[RESTRICTED_M&A_CODENAME_{idx}]"
            token_map[token] = val
            sanitized = sanitized.replace(val, token)
            entities_masked.append({
                "entity_type": "MNPI_PROJECT_CODENAME",
                "original_value": val,
                "replacement_token": token
            })

    pseudonym_vault[mapping_id] = token_map

    return SanitizeResponse(
        sanitized_text=sanitized,
        redactions_count=len(entities_masked),
        entities_masked=entities_masked,
        token_mapping_id=mapping_id
    )
