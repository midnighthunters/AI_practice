"""
Synthesis Agent: Institutional Equity Research Note Synthesizer
Synthesizes quantitative variance audits and qualitative executive guidance
into an actionable institutional briefing memo with rating and risks.
"""

import time
from typing import List, Tuple
from schemas import (
    MetricAuditResult,
    GuidanceStatement,
    InstitutionalResearchBrief,
    AgentStepLog
)

def run_synthesis_agent(
    ticker: str,
    quarter: str,
    audit_results: List[MetricAuditResult],
    guidance_statements: List[GuidanceStatement]
) -> Tuple[InstitutionalResearchBrief, AgentStepLog]:
    start_time = time.perf_counter()

    beats = sum(1 for m in audit_results if m.outcome == "BEAT")
    misses = sum(1 for m in audit_results if m.outcome == "MISS")
    bullish_guidance = sum(1 for g in guidance_statements if g.sentiment == "BULLISH")
    cautious_guidance = sum(1 for g in guidance_statements if g.sentiment == "CAUTIOUS")

    # Stance logic
    if beats >= misses and bullish_guidance >= cautious_guidance:
        stance = "OVERWEIGHT"
        headline = f"{ticker} {quarter}: High-Quality Beat Powered by Resilient Net Margins & Strong Balance Sheet"
    elif misses > beats and cautious_guidance > bullish_guidance:
        stance = "UNDERWEIGHT"
        headline = f"{ticker} {quarter}: Soft Top-Line & Elevated Provisioning Signal Margin Headwinds"
    else:
        stance = "NEUTRAL"
        headline = f"{ticker} {quarter}: Balanced Earnings Profile with Mixed Forward Guidance"

    catalysts = [
        f"Operating leverage supported by {beats} metrics outperforming consensus.",
        "Disciplined expense control and accretive capital deployment into digital platforms.",
        "Market share gains in core institutional investment banking and wealth advisory."
    ]

    risks = [
        "Unfavorable deposit repricing and flattening yield curve compression.",
        "Potential credit normalization across commercial real estate portfolios.",
        "Heightened regulatory capital requirements under Basel III Endgame."
    ]

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    log = AgentStepLog(
        agent_name="ExecutiveBriefingAgent",
        role="Institutional Memo Synthesizer",
        execution_time_ms=round(elapsed_ms, 2),
        status="COMPLETED",
        key_findings=[
            f"Assigned {stance} rating based on {beats} beats and {bullish_guidance} bullish guidance items.",
            "Formulated 3 institutional catalysts and 3 key macro risk vectors."
        ]
    )

    brief = InstitutionalResearchBrief(
        ticker=ticker,
        quarter=quarter,
        headline=headline,
        investment_stance=stance,
        audited_metrics=audit_results,
        forward_guidance=guidance_statements,
        key_catalysts=catalysts,
        downside_risks=risks,
        agent_audit_trail=[]  # Populated by orchestrator
    )

    return brief, log
