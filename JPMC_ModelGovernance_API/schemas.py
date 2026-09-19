"""
JPMorgan Chase LLM Suite - Model Risk Governance (MRGO) & SR 11-7 Audit Gateway
Pydantic v2 Schemas for Regulatory Compliance, MNPI Scrubbing, and Audit Trails.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class InspectPromptRequest(BaseModel):
    prompt: str = Field(..., example="Draft an email regarding Project Falcon merger with Barclays before the public announcement.", description="Inbound prompt")
    user_id: str = Field("analyst_4091", description="JPMC Corporate Active Directory ID")
    department: str = Field("CIB_M&A", description="Department (e.g. CIB_M&A, Markets, Asset_Management)")

class ThreatDetection(BaseModel):
    threat_type: str = Field(..., description="Type of threat (e.g., MNPI_LEAK, PROMPT_INJECTION, JAILBREAK)")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    matched_pattern: str
    confidence: float

class InspectPromptResponse(BaseModel):
    is_safe: bool
    risk_level: str
    threats_detected: List[ThreatDetection]
    mnpi_flagged: bool
    injection_flagged: bool
    recommended_action: str = Field(..., description="ALLOW, QUARANTINE, REJECT")

class SanitizeRequest(BaseModel):
    text: str = Field(..., description="Text containing potential banking PII or MNPI")
    anonymize_mnpi: bool = True
    anonymize_banking_pii: bool = True

class SanitizeResponse(BaseModel):
    sanitized_text: str
    redactions_count: int
    entities_masked: List[Dict[str, str]]
    token_mapping_id: str

class SR11_7_ScorecardRequest(BaseModel):
    model_name: str = Field("JPMC-Internal-Llama3-70B", description="Model undergoing evaluation")
    intended_use_case: str = Field("CIB Equity Research Summarization", description="Business justification")
    sample_queries: List[str] = Field(default=[], description="Batch queries for validation")

class SR11_7_ScorecardResponse(BaseModel):
    audit_id: str
    model_name: str
    sr11_7_status: str = Field(..., description="APPROVED, CONDITIONAL, REJECTED")
    conceptual_soundness_score: float = Field(..., description="Scale 0.0 - 1.0 (SR 11-7 Pillar 1)")
    outcome_analysis_score: float = Field(..., description="Scale 0.0 - 1.0 (SR 11-7 Pillar 2)")
    ongoing_monitoring_score: float = Field(..., description="Scale 0.0 - 1.0 (SR 11-7 Pillar 3)")
    overall_compliance_rating: str
    cryptographic_lineage_hash: str
    compliance_notes: List[str]

class AuditLogEntry(BaseModel):
    timestamp: str
    event_id: str
    user_id: str
    department: str
    action: str
    risk_rating: str
    sha256_hash: str
