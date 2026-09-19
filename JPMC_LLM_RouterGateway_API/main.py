"""
JPMorgan Chase LLM Suite - Enterprise Token Economizer & Semantic Router Gateway
FastAPI Microservice (Port: 8005)

Features:
- Sub-10ms Semantic Vector Caching (Cosine Similarity)
- Dynamic Tiered Routing (Tier 1 Fast/Internal vs Tier 2 Frontier/Reasoning)
- Multi-Tenant Departmental Cost Attribution & Token Quotas (CIB, AWM, Risk)
- OpenAI-compatible /v1/chat/completions Reverse Proxy Interface
"""

import sys
import time
import uuid
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatMessage,
    UsageMetrics,
    CacheStats,
    DepartmentBudget
)
from services.semantic_cache import semantic_cache
from services.model_router import determine_routing, simulate_model_inference
from services.budget_tracker import budget_tracker

app = FastAPI(
    title="JPMC LLM Router Gateway API - Enterprise Token Economizer",
    description=(
        "Enterprise reverse-proxy and model routing gateway for JPMorgan Chase's LLM Suite. "
        "Slashes token costs and latency via sub-10ms semantic caching, tiered model routing, and departmental budgeting."
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
        "service": "JPMC_LLM_RouterGateway_API",
        "description": "Enterprise Token Economizer & Semantic Router Gateway",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "cache_stats": "/api/v1/gateway/cache-stats",
            "budget_allocation": "/api/v1/gateway/budget-allocation"
        }
    }

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "HEALTHY",
        "service": "JPMC_LLM_RouterGateway_API",
        "cached_entries": len(semantic_cache.entries),
        "total_requests_processed": semantic_cache.total_requests
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse, tags=["LLM Proxy"])
async def chat_completions(request: ChatCompletionRequest):
    start_time = time.perf_counter()
    prompt = request.messages[-1].content if request.messages else ""

    cached_ans = None
    cached_model = None
    sim_score = 0.0

    # 1. Check Semantic Cache if not bypassed
    if not request.bypass_cache:
        cached_ans, cached_model, sim_score = semantic_cache.lookup(prompt)

    if cached_ans:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        p_tokens = len(prompt) // 4
        c_tokens = len(cached_ans) // 4
        return ChatCompletionResponse(
            id=f"chatcmpl-cache-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model_routed_to=cached_model or "JPMC-Semantic-Cache",
            tier="CACHE_HIT",
            latency_ms=round(elapsed_ms, 2),
            choices=[ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=cached_ans),
                finish_reason="stop"
            )],
            usage=UsageMetrics(
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_tokens=p_tokens + c_tokens,
                estimated_cost_usd=0.0 # 0 API cost on cache hit
            ),
            cached=True
        )

    # 2. Dynamic Model Tier Routing
    model_name, tier = determine_routing(prompt)
    answer_text = simulate_model_inference(prompt, model_name, tier)

    # 3. Store in semantic cache for future reuse
    semantic_cache.store(prompt, answer_text, model_name)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    p_tokens = max(1, len(prompt) // 4)
    c_tokens = max(1, len(answer_text) // 4)
    total_tokens = p_tokens + c_tokens

    # Tiered pricing estimation
    cost_per_k = 0.002 if tier == "TIER_1_INTERNAL" else 0.015
    cost_usd = (total_tokens / 1000.0) * cost_per_k

    # Record departmental usage
    budget_tracker.record_usage(request.department, total_tokens, cost_usd)

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(time.time()),
        model_routed_to=model_name,
        tier=tier,
        latency_ms=round(elapsed_ms, 2),
        choices=[ChatChoice(
            index=0,
            message=ChatMessage(role="assistant", content=answer_text),
            finish_reason="stop"
        )],
        usage=UsageMetrics(
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=round(cost_usd, 6)
        ),
        cached=False
    )

@app.get("/api/v1/gateway/cache-stats", response_model=CacheStats, tags=["Governance & Economics"])
async def get_cache_stats():
    return semantic_cache.get_stats()

@app.get("/api/v1/gateway/budget-allocation", response_model=List[DepartmentBudget], tags=["Governance & Economics"])
async def get_budget_allocation():
    return budget_tracker.get_all_budgets()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=False)
