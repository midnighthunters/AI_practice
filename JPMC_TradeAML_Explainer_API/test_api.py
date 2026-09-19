"""
Automated Test Suite for JPMC Trade AML Explainer API
Verifies typology detection, regulatory SAR narrative formatting, and evidence lineage.
"""

import sys
import os

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
        assert len(data["active_rules"]) >= 3
        print("✓ test_health passed (Active rules:", data["active_rules"], ")")

        # 2. Demo endpoint
        res = client.get("/api/v1/aml/demo")
        assert res.status_code == 200
        d_data = res.json()
        assert d_data["sar_filing_id"].startswith("SAR-FCA-")
        assert len(d_data["narrative_sections"]) == 5
        section_names = [s["section_name"] for s in d_data["narrative_sections"]]
        assert "PART_1_WHO" in section_names
        assert "PART_5_WHY" in section_names
        assert len(d_data["evidence_lineage"]) == 3
        print("✓ test_demo_endpoint passed (SAR Sections:", len(section_names), ")")

        # 3. Alert Triage with structuring violation
        payload = {
            "alert_id": "ALERT-TEST-100",
            "subject_entity": "Sterling Logistics UK",
            "risk_score": 92.0,
            "transactions": [
                {
                    "transaction_id": "TX-1",
                    "timestamp": "2023-11-05T10:00:00Z",
                    "originating_account": "GB82WEST12345698765432",
                    "originator_name": "Sterling Logistics UK",
                    "destination_account": "CH9300762011623852957",
                    "destination_country": "CH",
                    "amount": 9900.0,
                    "currency": "GBP"
                },
                {
                    "transaction_id": "TX-2",
                    "timestamp": "2023-11-05T11:00:00Z",
                    "originating_account": "GB82WEST12345698765432",
                    "originator_name": "Sterling Logistics UK",
                    "destination_account": "CH9300762011623852957",
                    "destination_country": "CH",
                    "amount": 9950.0,
                    "currency": "GBP"
                }
            ]
        }
        res = client.post("/api/v1/aml/triage-alert", json=payload)
        assert res.status_code == 200
        t_data = res.json()
        assert t_data["triage_status"] == "ESCALATE_TO_SAR"
        assert any(v["rule_code"] == "AML-R101-STRUCTURING" for v in t_data["typology_violations"])
        print("✓ test_triage_alert passed (Status: ESCALATE_TO_SAR, Structuring detected)")

if __name__ == "__main__":
    run_all_tests()
    print("\nAll JPMC_TradeAML_Explainer_API tests PASSED successfully!")
