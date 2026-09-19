"""
JPMorgan Chase LLM Suite - SEC 10-K & Financial Statement Intelligence Engine
Pydantic v2 Schemas for Document Intelligence & Tabular Financial Reconciliation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FinancialTable(BaseModel):
    title: str = Field(..., description="Name of financial statement (e.g., Consolidated Balance Sheet)")
    headers: List[str] = Field(..., description="Column headers (e.g., ['Line Item', '2023 ($M)', '2022 ($M)'])")
    rows: List[List[str]] = Field(..., description="Row data with numerical line items")
    footnotes: Optional[List[str]] = Field(default=[], description="Footnotes associated with this statement")

class FilingIngestRequest(BaseModel):
    ticker: str = Field(..., example="JPM", description="Company stock ticker")
    fiscal_year: int = Field(..., example=2023, description="Fiscal year")
    filing_type: str = Field(..., example="10-K", description="SEC Filing Type (10-K, 10-Q, 8-K)")
    tables: List[FinancialTable] = Field(..., description="Parsed financial statement tables")
    raw_text: Optional[str] = Field(None, description="Accompanying MD&A raw text")

class FilingIngestResponse(BaseModel):
    filing_id: str
    ticker: str
    fiscal_year: int
    tables_indexed: int
    line_items_indexed: int
    status: str

class FilingQueryRequest(BaseModel):
    filing_id: Optional[str] = Field("JPM_2023_10K", description="Filing identifier")
    question: str = Field(..., example="What was the Net Income and Total Assets for JPMC in 2023?", description="Financial query")
    enforce_grounding: bool = Field(True, description="Strictly verify numbers exist in source tables before returning")

class GroundedCitation(BaseModel):
    line_item: str
    reported_value: str
    table_name: str
    column: str
    verified_in_source: bool

class FilingQueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[GroundedCitation]
    grounding_confidence: float = Field(..., description="Percentage of extracted numbers verified in source tables (0.0 to 1.0)")
    numerical_hallucinations_detected: int

class ReconciliationCheck(BaseModel):
    equation_name: str
    lhs_name: str
    lhs_value: float
    rhs_name: str
    rhs_value: float
    difference: float
    is_balanced: bool
    status: str

class ReconciliationResponse(BaseModel):
    filing_id: str
    reconciliation_checks: List[ReconciliationCheck]
    all_balanced: bool
    summary: str
