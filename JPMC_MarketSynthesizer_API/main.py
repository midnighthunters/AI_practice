"""
JPMorgan Chase LLM Suite - Multi-Agent Earnings & Market Consensus Engine
FastAPI Microservice (Port: 8003)

Features:
- Quantitative Earnings Auditor Agent (Beat/Miss calculation)
- Qualitative Guidance Sentiment Agent (CFO forward outlook analysis)
- Executive Briefing Memo Synthesizer (Institutional rating & risk analysis)
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
    EarningsAnalysisRequest,
    InstitutionalResearchBrief
)
from services.orchestrator import orchestrate_market_synthesis

app = FastAPI(
    title="JPMC Market Synthesizer API - Multi-Agent Earnings Engine",
    description=(
        "Multi-agent institutional equity research microservice built for JPMorgan Chase's LLM Suite. "
        "Orchestrates a 3-agent swarm (Auditor, Guidance Extractor, Synthesis) to evaluate corporate earnings in seconds."
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
        "service": "JPMC_MarketSynthesizer_API",
        "description": "Multi-Agent Earnings & Consensus Synthesis Engine",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "HEALTHY",
        "service": "JPMC_MarketSynthesizer_API",
        "active_agents": ["EarningsAuditorAgent", "GuidanceSentimentAgent", "ExecutiveBriefingAgent"]
    }

@app.post("/api/v1/market/analyze-earnings", response_model=InstitutionalResearchBrief, tags=["Market Synthesis"])
async def analyze_earnings(request: EarningsAnalysisRequest):
    return orchestrate_market_synthesis(request)

@app.get("/api/v1/market/demo", response_model=InstitutionalResearchBrief, tags=["Market Synthesis"])
async def run_sample_demo():
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_earnings_transcript.json")
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="Sample earnings file not found.")
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    req = EarningsAnalysisRequest(**data)
    return orchestrate_market_synthesis(req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False)
