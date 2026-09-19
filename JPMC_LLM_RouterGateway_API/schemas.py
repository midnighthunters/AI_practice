"""
JPMorgan Chase LLM Suite - Enterprise Token Economizer & Semantic Router Gateway
Pydantic v2 Schemas for Reverse Proxy Routing, Semantic Caching, and Token Quotas.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., example="user", description="system, user, or assistant")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Chat conversation turns")
    department: str = Field("CIB_Research", description="Department code (CIB_Research, AWM_Wealth, Risk_Compliance)")
    user_id: str = Field("trader_5510", description="Corporate Active Directory ID")
    temperature: Optional[float] = Field(0.2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(512, description="Maximum tokens to generate")
    bypass_cache: Optional[bool] = Field(False, description="Force fresh model invocation")

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class UsageMetrics(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model_routed_to: str
    tier: str = Field(..., description="CACHE_HIT, TIER_1_INTERNAL, TIER_2_FRONTIER")
    latency_ms: float
    choices: List[ChatChoice]
    usage: UsageMetrics
    cached: bool

class CacheStats(BaseModel):
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_ratio_pct: float
    total_tokens_saved: int
    total_usd_saved: float
    avg_cache_latency_ms: float

class DepartmentBudget(BaseModel):
    department: str
    monthly_budget_usd: float
    spent_usd: float
    tokens_consumed: int
    budget_utilized_pct: float
    status: str
