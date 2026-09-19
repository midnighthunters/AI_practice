"""
Automated Test Suite for JPMC DocIntel API
Verifies tabular parsing, numerical grounding, and accounting identity reconciliation.
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi.testclient import TestClient
from main import app

def run_all_tests():
    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "HEALTHY"
        assert "JPM_2023_10K" in data["indexed_filings"]
        print("✓ test_health passed (Indexed:", data["indexed_filings"], ")")

        # 2. Query financials
        payload = {
            "filing_id": "JPM_2023_10K",
            "question": "What is the Net Income and Total Net Revenue?",
            "enforce_grounding": True
        }
        res = client.post("/api/v1/filings/query", json=payload)
        assert res.status_code == 200
        q_data = res.json()
        assert len(q_data["citations"]) > 0
        assert q_data["grounding_confidence"] > 0.8
        assert q_data["numerical_hallucinations_detected"] == 0
        print("✓ test_query_financials passed (Citations:", len(q_data["citations"]), ")")

        # 3. Reconcile balance sheet
        res = client.post("/api/v1/filings/reconcile?filing_id=JPM_2023_10K")
        assert res.status_code == 200
        r_data = res.json()
        assert r_data["all_balanced"] is True
        assert len(r_data["reconciliation_checks"]) >= 2
        bs_check = next(c for c in r_data["reconciliation_checks"] if "Balance Sheet" in c["equation_name"])
        assert bs_check["status"] == "PASSED"
        assert bs_check["is_balanced"] is True
        print("✓ test_reconcile_balance_sheet passed (All balanced:", r_data["all_balanced"], ")")

        # 4. Ingest custom filing
        custom_filing = {
            "ticker": "MS",
            "fiscal_year": 2023,
            "filing_type": "10-K",
            "tables": [
                {
                    "title": "Consolidated Statement of Financial Condition",
                    "headers": ["Line Item", "2023 ($M)"],
                    "rows": [
                        ["Total Assets", "$1,180,000"],
                        ["Total Liabilities", "$1,085,000"],
                        ["Total Equity", "$95,000"]
                    ]
                }
            ],
            "raw_text": "Morgan Stanley 2023 10-K filing."
        }
        res = client.post("/api/v1/filings/ingest", json=custom_filing)
        assert res.status_code == 200
        i_data = res.json()
        assert i_data["filing_id"] == "MS_2023_10-K"
        assert i_data["tables_indexed"] == 1
        assert i_data["line_items_indexed"] == 3
        print("✓ test_ingest_custom_filing passed")

if __name__ == "__main__":
    run_all_tests()
    print("\nAll JPMC_DocIntel_API tests PASSED successfully!")
