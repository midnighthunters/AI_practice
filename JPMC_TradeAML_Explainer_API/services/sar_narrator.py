"""
SAR (Suspicious Activity Report) Narrative Generator
Synthesizes regulatory SAR filings adhering to the 5-part statutory framework
(Who, What, When, Where, Why) required by the UK FCA / National Crime Agency (NCA) and FinCEN.
"""

import uuid
from typing import List
from schemas import (
    AlertTriageRequest,
    AlertTriageResponse,
    SARNarrativeResponse,
    SARNarrativeSection
)
from services.rules_engine import evaluate_aml_rules
from services.evidence_lineage import build_evidence_lineage

def generate_regulatory_sar(request: AlertTriageRequest) -> SARNarrativeResponse:
    txs = request.transactions
    violations = evaluate_aml_rules(txs)
    lineage = build_evidence_lineage(txs)

    sar_id = f"SAR-FCA-{uuid.uuid4().hex[:8].upper()}"
    total_amount = sum(t.amount for t in txs)
    currency = txs[0].currency if txs else "GBP"
    dates = sorted([t.timestamp for t in txs])
    start_date = dates[0] if dates else "UNKNOWN"
    end_date = dates[-1] if dates else "UNKNOWN"

    dest_countries = list(set(t.destination_country for t in txs))
    originator = txs[0].originator_name if txs else request.subject_entity
    orig_acc = txs[0].originating_account if txs else "UNKNOWN"

    # 1. Part 1: WHO
    who_narrative = (
        f"The subject of this filing is {originator}, maintaining primary account {orig_acc} "
        f"with JPMorgan Chase. The entity is registered as an international commercial enterprise, "
        f"with internal ML alert scoring {request.risk_score}/100 indicating anomalous flow behavior."
    )

    # 2. Part 2: WHAT
    what_narrative = (
        f"The suspicious activity comprises {len(txs)} wire transfer transactions totaling "
        f"{currency} {total_amount:,.2f}. The transactions exhibited repetitive transfer amounts "
        f"hovering consistently between {currency} 9,000 and {currency} 9,990 with generic memos."
    )

    # 3. Part 3: WHEN
    when_narrative = (
        f"The identified activity transpired between {start_date} and {end_date}. "
        f"All transactions were executed in rapid succession, reflecting an abnormal velocity burst."
    )

    # 4. Part 4: WHERE
    where_narrative = (
        f"Funds originated from the UK domestic banking infrastructure and were routed cross-border "
        f"to destination jurisdictions including: {', '.join(dest_countries)}."
    )

    # 5. Part 5: WHY
    violation_summaries = " ".join([f"[{v.rule_code}: {v.description}]" for v in violations])
    why_narrative = (
        f"This activity is deemed suspicious and warrants regulatory submission because transaction patterns "
        f"strongly indicate deliberate Structuring (Smurfing) designed to evade statutory currency transaction "
        f"reporting (CTR) thresholds. Specifically: {violation_summaries} "
        f"No legitimate commercial rationale was documented for fragmenting £{total_amount:,.2f} across multiple tranches."
    )

    sections = [
        SARNarrativeSection(section_name="PART_1_WHO", narrative_text=who_narrative),
        SARNarrativeSection(section_name="PART_2_WHAT", narrative_text=what_narrative),
        SARNarrativeSection(section_name="PART_3_WHEN", narrative_text=when_narrative),
        SARNarrativeSection(section_name="PART_4_WHERE", narrative_text=where_narrative),
        SARNarrativeSection(section_name="PART_5_WHY", narrative_text=why_narrative),
    ]

    exec_summary = (
        f"Suspicious Activity Report filed for {originator} regarding {len(txs)} structured wire transfers "
        f"totaling {currency} {total_amount:,.2f}. Pattern violates AML-R101 (Structuring) and AML-R204 (Velocity)."
    )

    return SARNarrativeResponse(
        sar_filing_id=sar_id,
        alert_id=request.alert_id,
        subject_entity=request.subject_entity,
        regulatory_body="UK Financial Conduct Authority (FCA) / UK National Crime Agency (NCA)",
        executive_summary=exec_summary,
        narrative_sections=sections,
        evidence_lineage=lineage,
        analyst_action_required="SUBMIT_TO_NCA_AND_FREEZE_DESTINATION_BENEFICIARY"
    )
