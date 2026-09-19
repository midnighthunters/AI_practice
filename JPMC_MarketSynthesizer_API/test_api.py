"""
Automated Test Suite for JPMC Market Synthesizer API
Verifies multi-agent earnings auditing, guidance sentiment extraction, and institutional memo generation.
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
        assert len(data["active_agents"]) == 3
        print("✓ test_health passed (Agents:", data["active_agents"], ")")

        # 2. Demo endpoint
        res = client.get("/api/v1/market/demo")
        assert res.status_code == 200
        d_data = res.json()
        assert d_data["ticker"] == "JPM"
        assert d_data["investment_stance"] in ["OVERWEIGHT", "NEUTRAL"]
        assert len(d_data["audited_metrics"]) == 3
        assert len(d_data["agent_audit_trail"]) == 3
        print("✓ test_demo_endpoint passed (Stance:", d_data["investment_stance"], ")")

        # 3. Custom Earnings Analysis
        custom_payload = {
            "ticker": "MS",
            "quarter": "Q4 2023",
            "transcript_text": "We expect institutional equities trading to accelerate in 2024. We anticipate solid wealth management inflows.",
            "consensus": [
                {
                    "metric_name": "EPS",
                    "reported_value": 1.13,
                    "consensus_estimate": 1.05,
                    "unit": "$"
                },
                {
                    "metric_name": "Revenue ($B)",
                    "reported_value": 12.9,
                    "consensus_estimate": 12.7,
                    "unit": "$B"
                }
            ]
        }
        res = client.post("/api/v1/market/analyze-earnings", json=custom_payload)
        assert res.status_code == 200
        c_data = res.json()
        assert c_data["ticker"] == "MS"
        assert c_data["investment_stance"] == "OVERWEIGHT"
        assert all(m["outcome"] == "BEAT" for m in c_data["audited_metrics"])
        assert len(c_data["agent_audit_trail"]) == 3
        print("✓ test_custom_earnings_analysis passed (All metrics BEAT)")

if __name__ == "__main__":
    run_all_tests()
    print("\nAll JPMC_MarketSynthesizer_API tests PASSED successfully!")
