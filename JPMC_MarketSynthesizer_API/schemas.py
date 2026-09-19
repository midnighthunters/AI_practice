"""
JPMorgan Chase LLM Suite - Multi-Agent Earnings & Market Consensus Engine
Pydantic v2 Schemas for Multi-Agent Market Synthesis.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConsensusMetric(BaseModel):
    metric_name: str = Field(..., example="EPS", description="Metric name (e.g., EPS, Net Revenue)")
    reported_value: float = Field(..., example=3.97, description="Actual reported figure")
    consensus_estimate: float = Field(..., example=3.65, description="Wall Street consensus consensus estimate")
    unit: str = Field("$", description="Unit of measurement ($, %, $M, $B)")

class EarningsAnalysisRequest(BaseModel):
    ticker: str = Field(..., example="JPM", description="Company ticker")
    quarter: str = Field("Q4 2023", description="Fiscal quarter")
    transcript_text: str = Field(..., description="Earnings call transcript or press release text")
    consensus: List[ConsensusMetric] = Field(..., description="Wall Street consensus metrics")

class MetricAuditResult(BaseModel):
    metric_name: str
    reported: float
    consensus: float
    variance: float
    variance_pct: float
    outcome: str = Field(..., description="BEAT, IN_LINE, MISS")

class GuidanceStatement(BaseModel):
    category: str = Field(..., description="REVENUE, EXPENSE, CAPEX, NII")
    statement: str
    sentiment: str = Field(..., description="BULLISH, NEUTRAL, CAUTIOUS")
    confidence: float

class AgentStepLog(BaseModel):
    agent_name: str
    role: str
    execution_time_ms: float
    status: str
    key_findings: List[str]

class InstitutionalResearchBrief(BaseModel):
    ticker: str
    quarter: str
    headline: str
    investment_stance: str = Field(..., description="OVERWEIGHT, NEUTRAL, UNDERWEIGHT")
    audited_metrics: List[MetricAuditResult]
    forward_guidance: List[GuidanceStatement]
    key_catalysts: List[str]
    downside_risks: List[str]
    agent_audit_trail: List[AgentStepLog]
