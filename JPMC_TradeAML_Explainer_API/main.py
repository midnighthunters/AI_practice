"""
JPMorgan Chase LLM Suite - Automated SAR & Trade Anomaly Narrator
FastAPI Microservice (Port: 8004)

Features:
- Deterministic Anti-Money Laundering (AML) Typology Engine
- FCA / FinCEN 5-Part Regulatory SAR Narrative Generator (Who, What, When, Where, Why)
- Cryptographic Transaction Evidence Lineage Tracking
"""

import os
import json
import sys
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from schemas import (
    AlertTriageRequest,
    AlertTriageResponse,
    SARNarrativeResponse
)
from services.rules_engine import evaluate_aml_rules
from services.sar_narrator import generate_regulatory_sar

app = FastAPI(
    title="JPMC Trade AML Explainer API - Regulatory SAR Narrator",
    description=(
        "Financial crime and AML surveillance microservice built for JPMorgan Chase's LLM Suite. "
        "Triages transaction alerts and drafts regulatory Suspicious Activity Reports (SARs) with immutable evidence lineage."
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
        "service": "JPMC_TradeAML_Explainer_API",
        "description": "Automated SAR & Trade Anomaly Narrator",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "HEALTHY",
        "service": "JPMC_TradeAML_Explainer_API",
        "active_rules": ["AML-R101-STRUCTURING", "AML-R204-VELOCITY", "AML-R305-OFFSHORE-HOP"]
    }

@app.post("/api/v1/aml/triage-alert", response_model=AlertTriageResponse, tags=["AML Surveillance"])
async def triage_alert(request: AlertTriageRequest):
    violations = evaluate_aml_rules(request.transactions)
    agg_amount = sum(t.amount for t in request.transactions)
    triage_status = "ESCALATE_TO_SAR" if len(violations) > 0 else "MONITOR"

    return AlertTriageResponse(
        alert_id=request.alert_id,
        subject_entity=request.subject_entity,
        triage_status=triage_status,
        typology_violations=violations,
        aggregate_amount_flagged=agg_amount,
        total_transactions_analyzed=len(request.transactions)
    )

@app.post("/api/v1/aml/generate-sar", response_model=SARNarrativeResponse, tags=["Regulatory SAR Filing"])
async def generate_sar(request: AlertTriageRequest):
    return generate_regulatory_sar(request)

@app.get("/api/v1/aml/demo", response_model=SARNarrativeResponse, tags=["Regulatory SAR Filing"])
async def run_aml_demo():
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_suspicious_transactions.json")
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="Sample suspicious transaction data not found.")
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    req = AlertTriageRequest(**data)
    return generate_regulatory_sar(req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=False)
