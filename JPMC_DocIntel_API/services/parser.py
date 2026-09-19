"""
Financial Statement Table & Footnote Parser
Normalizes monetary quantities, handles parenthetical negative numbers (e.g., (1,234) -> -1234.0),
and builds an in-memory numerical index for deterministic verification.
"""

import re
from typing import Dict, List, Tuple, Any, Optional

def clean_monetary_value(raw: str) -> Optional[float]:
    """Converts strings like '$3,875,393', '(4,500)', '12.5%' into standardized floats."""
    if not raw or not isinstance(raw, str):
        return None
    val = raw.strip().replace("$", "").replace(",", "")
    if val.startswith("(") and val.endswith(")"):
        val = "-" + val[1:-1]
    if val.endswith("%"):
        val = val[:-1]
    try:
        return float(val)
    except ValueError:
        return None

class FinancialDocumentStore:
    """In-memory financial filing store indexed for exact numerical retrieval."""
    def __init__(self):
        self.filings: Dict[str, Dict[str, Any]] = {}

    def index_filing(self, filing_id: str, ticker: str, fiscal_year: int, tables: List[Dict[str, Any]], raw_text: Optional[str] = None, filing_type: str = "10-K"):
        line_item_index: Dict[str, Dict[str, Any]] = {}
        numerical_values: Dict[str, List[Tuple[str, str]]] = {} # number_str -> list of (line_item, table_name)

        for table in tables:
            t_name = table.get("title", "Untitled Table")
            headers = table.get("headers", [])
            rows = table.get("rows", [])

            for row in rows:
                if not row or len(row) < 2:
                    continue
                item_name = row[0].strip()
                norm_key = item_name.lower()
                
                row_dict = {}
                for col_idx, col_val in enumerate(row[1:], start=1):
                    col_header = headers[col_idx] if col_idx < len(headers) else f"Col_{col_idx}"
                    cleaned_val = clean_monetary_value(col_val)
                    row_dict[col_header] = {
                        "raw": col_val,
                        "numeric": cleaned_val
                    }
                    if cleaned_val is not None:
                        clean_num_str = str(int(cleaned_val)) if cleaned_val.is_integer() else str(cleaned_val)
                        if clean_num_str not in numerical_values:
                            numerical_values[clean_num_str] = []
                        numerical_values[clean_num_str].append((item_name, t_name))

                line_item_index[norm_key] = {
                    "canonical_name": item_name,
                    "table": t_name,
                    "values": row_dict
                }

        self.filings[filing_id] = {
            "filing_id": filing_id,
            "ticker": ticker,
            "fiscal_year": fiscal_year,
            "filing_type": filing_type,
            "tables": tables,
            "line_item_index": line_item_index,
            "numerical_values": numerical_values,
            "raw_text": raw_text or ""
        }
        return len(tables), len(line_item_index)

    def get_filing(self, filing_id: str) -> Optional[Dict[str, Any]]:
        return self.filings.get(filing_id)

# Global document store instance
doc_store = FinancialDocumentStore()
