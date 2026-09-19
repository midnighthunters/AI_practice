"""
JPMorgan Chase LLM Suite - Model Risk Governance (MRGO) & SR 11-7 Audit Gateway
FastAPI Microservice (Port: 8002)

Features:
- Material Non-Public Information (MNPI) Scrubber
- Banking PII (IBAN, UK NINO, SWIFT BIC) Sanitizer
- Prompt Injection & Jailbreak Firewall
- Federal Reserve SR 11-7 Model Risk Scorecard & SHA-256 Audit Trail
"""

import sys
import time
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from schemas import (
    InspectPromptRequest,
    InspectPromptResponse,
    SanitizeRequest,
    SanitizeResponse,
    SR11_7_ScorecardRequest,
    SR11_7_ScorecardResponse,
    AuditLogEntry
)
from services.mnpi_detector import scan_for_mnpi
from services.injection_firewall import scan_for_injection
from services.pii_sanitizer import sanitize_banking_payload
from services.sr11_7_auditor import generate_sr11_7_scorecard, audit_ledger

app = FastAPI(
    title="JPMC Model Governance API - SR 11-7 & Regulatory Safety Gateway",
    description=(
        "Enterprise regulatory governance microservice for JPMorgan Chase's LLM Suite. "
        "Enforces Federal Reserve SR 11-7 compliance, UK FCA/PRA standards, and MNPI/PII sanitization."
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["System"])
async def root():
    return {
        "service": "JPMC_ModelGovernance_API",
        "description": "Model Risk Governance & SR 11-7 Audit Gateway",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "HEALTHY",
        "service": "JPMC_ModelGovernance_API",
        "active_rules": ["MNPI_FILTER", "BANKING_PII_FILTER", "INJECTION_FIREWALL", "SR11_7_AUDITOR"],
        "audit_entries_count": len(audit_ledger)
    }

@app.post("/api/v1/governance/inspect", response_model=InspectPromptResponse, tags=["Threat Inspection"])
async def inspect_prompt(request: InspectPromptRequest):
    mnpi_threats = scan_for_mnpi(request.prompt)
    injection_threats = scan_for_injection(request.prompt)
    all_threats = mnpi_threats + injection_threats

    is_safe = len(all_threats) == 0
    mnpi_flagged = len(mnpi_threats) > 0
    injection_flagged = len(injection_threats) > 0

    if not is_safe:
        risk_level = "CRITICAL" if any(t.severity == "CRITICAL" for t in all_threats) else "HIGH"
        rec_action = "REJECT" if risk_level == "CRITICAL" else "QUARANTINE"
    else:
        risk_level = "LOW"
        rec_action = "ALLOW"

    return InspectPromptResponse(
        is_safe=is_safe,
        risk_level=risk_level,
        threats_detected=all_threats,
        mnpi_flagged=mnpi_flagged,
        injection_flagged=injection_flagged,
        recommended_action=rec_action
    )

@app.post("/api/v1/governance/sanitize", response_model=SanitizeResponse, tags=["PII & MNPI Sanitization"])
async def sanitize_payload(request: SanitizeRequest):
    return sanitize_banking_payload(
        text=request.text,
        anonymize_mnpi=request.anonymize_mnpi,
        anonymize_banking_pii=request.anonymize_banking_pii
    )

@app.post("/api/v1/governance/scorecard", response_model=SR11_7_ScorecardResponse, tags=["SR 11-7 Model Risk"])
async def get_sr11_7_scorecard(request: SR11_7_ScorecardRequest):
    return generate_sr11_7_scorecard(
        model_name=request.model_name,
        intended_use_case=request.intended_use_case,
        sample_queries=request.sample_queries
    )

@app.get("/api/v1/governance/audit-trail", response_model=List[AuditLogEntry], tags=["Compliance Audit"])
async def get_audit_trail():
    return audit_ledger

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
