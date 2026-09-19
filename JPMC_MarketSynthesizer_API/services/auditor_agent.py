"""
Auditor Agent: Quantitative Earnings Auditor
Compares reported financial metrics against Wall Street consensus estimates,
computing variances and classification (BEAT, IN_LINE, MISS).
"""

from typing import List, Tuple
from schemas import ConsensusMetric, MetricAuditResult, AgentStepLog
import time

def run_auditor_agent(consensus_list: List[ConsensusMetric]) -> Tuple[List[MetricAuditResult], AgentStepLog]:
    start_time = time.perf_counter()
    audit_results: List[MetricAuditResult] = []
    findings: List[str] = []

    for item in consensus_list:
        rep = item.reported_value
        con = item.consensus_estimate
        diff = rep - con
        pct = (diff / con * 100) if con != 0 else 0.0

        if pct >= 1.0:
            outcome = "BEAT"
            findings.append(f"{item.metric_name} beat consensus by {round(pct, 2)}% ({item.unit}{round(rep, 2)} vs {item.unit}{round(con, 2)})")
        elif pct <= -1.0:
            outcome = "MISS"
            findings.append(f"{item.metric_name} missed consensus by {abs(round(pct, 2))}% ({item.unit}{round(rep, 2)} vs {item.unit}{round(con, 2)})")
        else:
            outcome = "IN_LINE"
            findings.append(f"{item.metric_name} met expectations in-line ({item.unit}{round(rep, 2)})")

        audit_results.append(MetricAuditResult(
            metric_name=item.metric_name,
            reported=round(rep, 2),
            consensus=round(con, 2),
            variance=round(diff, 2),
            variance_pct=round(pct, 2),
            outcome=outcome
        ))

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    log = AgentStepLog(
        agent_name="EarningsAuditorAgent",
        role="Quantitative Consensus Benchmarker",
        execution_time_ms=round(elapsed_ms, 2),
        status="COMPLETED",
        key_findings=findings
    )

    return audit_results, log
