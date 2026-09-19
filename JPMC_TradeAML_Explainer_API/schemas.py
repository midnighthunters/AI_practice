"""
JPMorgan Chase LLM Suite - Automated SAR & Trade Anomaly Narrator
Pydantic v2 Schemas for AML Alert Triage and Regulatory SAR Drafting.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TransactionRecord(BaseModel):
    transaction_id: str = Field(..., example="TX-90124", description="Unique transaction reference")
    timestamp: str = Field(..., example="2023-11-04T14:22:10Z")
    originating_account: str = Field(..., example="GB82WEST12345698765432")
    originator_name: str = Field(..., example="Apex Global Trading Ltd")
    destination_account: str = Field(..., example="CH9300762011623852957")
    destination_country: str = Field(..., example="CH")
    amount: float = Field(..., example=9850.0)
    currency: str = Field("GBP", description="Currency ISO code")
    narrative: Optional[str] = Field("Consulting advisory services fee", description="Transaction memo")

class AlertTriageRequest(BaseModel):
    alert_id: str = Field(..., example="AML-ALERT-2023-8812")
    subject_entity: str = Field(..., example="Apex Global Trading Ltd")
    risk_score: float = Field(..., example=84.5, description="Initial ML anomaly score (0-100)")
    transactions: List[TransactionRecord] = Field(..., description="Chronological series of flagged transactions")

class TypologyViolation(BaseModel):
    rule_code: str = Field(..., description="e.g., AML-R101-STRUCTURING, AML-R204-VELOCITY")
    typology_name: str = Field(..., description="e.g. Structuring (Smurfing), Sanctions Hop, Layering")
    severity: str = Field(..., description="CRITICAL, HIGH, MEDIUM")
    description: str
    flagged_transaction_ids: List[str]

class AlertTriageResponse(BaseModel):
    alert_id: str
    subject_entity: str
    triage_status: str = Field(..., description="ESCALATE_TO_SAR, MONITOR, DISMISS")
    typology_violations: List[TypologyViolation]
    aggregate_amount_flagged: float
    total_transactions_analyzed: int

class SARNarrativeSection(BaseModel):
    section_name: str = Field(..., description="PART_1_WHO, PART_2_WHAT, PART_3_WHEN, PART_4_WHERE, PART_5_WHY")
    narrative_text: str

class SARNarrativeResponse(BaseModel):
    sar_filing_id: str
    alert_id: str
    subject_entity: str
    regulatory_body: str = Field("UK Financial Conduct Authority (FCA) / FinCEN", description="Primary regulator")
    executive_summary: str
    narrative_sections: List[SARNarrativeSection]
    evidence_lineage: List[Dict[str, Any]]
    analyst_action_required: str
