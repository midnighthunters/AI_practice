"""
JPMorgan Chase LLM Suite - SEC 10-K & Financial Statement Intelligence Engine
FastAPI Microservice (Port: 8001)

Features:
- Structured Tabular & Footnote RAG
- Verbatim Numerical Anti-Hallucination Grounding
- Accounting Identity Reconciliation (Assets = Liabilities + Equity)
"""

import os
import json
import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    FilingIngestRequest,
    FilingIngestResponse,
    FilingQueryRequest,
    FilingQueryResponse,
    ReconciliationResponse
)
from services.parser import doc_store
from services.reconciler import reconcile_filing
from services.llm_grounding import generate_grounded_answer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload sample JPMC 2023 10-K on startup
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_jpmc_10k.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            t_count, item_count = doc_store.index_filing(
                filing_id="JPM_2023_10K",
                ticker=data.get("ticker", "JPM"),
                fiscal_year=data.get("fiscal_year", 2023),
                tables=data.get("tables", []),
                raw_text=data.get("raw_text", ""),
                filing_type=data.get("filing_type", "10-K")
            )
            print(f"[Startup] Preloaded JPM_2023_10K: {t_count} tables, {item_count} unique financial metrics.")
    yield

app = FastAPI(
    title="JPMC DocIntel API - SEC 10-K & Tabular Financial Engine",
    description=(
        "Enterprise document intelligence microservice built for JPMorgan Chase's LLM Suite. "
        "Extracts, grounds, and reconciles financial statements with zero numerical hallucination."
    ),
    version="1.0.0",
    lifespan=lifespan
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
        "service": "JPMC_DocIntel_API",
        "description": "JPMorgan Chase LLM Suite - SEC 10-K & Financial Statement Intelligence Engine",
        "version": "1.0.0",
        "docs_url": "/docs",
        "preloaded_filing": "JPM_2023_10K"
    }

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "HEALTHY",
        "service": "JPMC_DocIntel_API",
        "indexed_filings": list(doc_store.filings.keys())
    }

@app.post("/api/v1/filings/ingest", response_model=FilingIngestResponse, tags=["Document Intelligence"])
async def ingest_filing(request: FilingIngestRequest):
    filing_id = f"{request.ticker.upper()}_{request.fiscal_year}_{request.filing_type.upper()}"
    tables_dict = [t.model_dump() for t in request.tables]
    t_count, item_count = doc_store.index_filing(
        filing_id=filing_id,
        ticker=request.ticker.upper(),
        fiscal_year=request.fiscal_year,
        tables=tables_dict,
        raw_text=request.raw_text,
        filing_type=request.filing_type
    )
    return FilingIngestResponse(
        filing_id=filing_id,
        ticker=request.ticker.upper(),
        fiscal_year=request.fiscal_year,
        tables_indexed=t_count,
        line_items_indexed=item_count,
        status="INDEXED_SUCCESSFULLY"
    )

@app.post("/api/v1/filings/query", response_model=FilingQueryResponse, tags=["Document Intelligence"])
async def query_filing(request: FilingQueryRequest):
    f_id = request.filing_id or "JPM_2023_10K"
    response = generate_grounded_answer(
        filing_id=f_id,
        question=request.question,
        enforce_grounding=request.enforce_grounding
    )
    return response

@app.post("/api/v1/filings/reconcile", response_model=ReconciliationResponse, tags=["Financial Reconciliation"])
async def reconcile(filing_id: str = Query("JPM_2023_10K", description="Filing identifier to reconcile")):
    return reconcile_filing(filing_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
