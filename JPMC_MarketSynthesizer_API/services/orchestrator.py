"""
Multi-Agent Orchestrator
Coordinates the execution pipeline across EarningsAuditorAgent,
GuidanceSentimentAgent, and ExecutiveBriefingAgent.
"""

from typing import List
from schemas import (
    EarningsAnalysisRequest,
    InstitutionalResearchBrief,
    AgentStepLog
)
from services.auditor_agent import run_auditor_agent
from services.guidance_agent import run_guidance_agent
from services.synthesis_agent import run_synthesis_agent

def orchestrate_market_synthesis(request: EarningsAnalysisRequest) -> InstitutionalResearchBrief:
    agent_logs: List[AgentStepLog] = []

    # Agent 1: Quantitative Auditor
    audit_results, log1 = run_auditor_agent(request.consensus)
    agent_logs.append(log1)

    # Agent 2: Qualitative Guidance & Tone Extractor
    guidance_stmts, log2 = run_guidance_agent(request.transcript_text)
    agent_logs.append(log2)

    # Agent 3: Executive Memo Synthesizer
    brief, log3 = run_synthesis_agent(
        ticker=request.ticker,
        quarter=request.quarter,
        audit_results=audit_results,
        guidance_statements=guidance_stmts
    )
    agent_logs.append(log3)

    brief.agent_audit_trail = agent_logs
    return brief
