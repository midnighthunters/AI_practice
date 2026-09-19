"""
Automated Test Suite for JPMC LLM Router Gateway API
Verifies semantic caching, dynamic model tier routing, token economization, and budget tracking.
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
        print("✓ test_health passed")

        # 2. Semantic Cache Hit (Preloaded statutory CET1 query)
        cache_hit_payload = {
            "messages": [
                {"role": "user", "content": "What is the statutory CET1 capital ratio requirement under Basel III for JPMC?"}
            ],
            "department": "Risk_Compliance",
            "user_id": "risk_officer_1"
        }
        res = client.post("/v1/chat/completions", json=cache_hit_payload)
        assert res.status_code == 200
        c_data = res.json()
        assert c_data["cached"] is True
        assert c_data["tier"] == "CACHE_HIT"
        assert c_data["usage"]["estimated_cost_usd"] == 0.0
        assert "11.9%" in c_data["choices"][0]["message"]["content"]
        print("✓ test_semantic_cache_hit passed (Latency:", c_data["latency_ms"], "ms, Cost: $0.00)")

        # 3. Dynamic Model Routing - Tier 2 Frontier for Complex Valuation
        complex_payload = {
            "messages": [
                {"role": "user", "content": "Perform a complex discounted cash flow DCF valuation analysis on First Republic integration synergies."}
            ],
            "department": "CIB_Research",
            "user_id": "analyst_901"
        }
        res = client.post("/v1/chat/completions", json=complex_payload)
        assert res.status_code == 200
        r_data = res.json()
        assert r_data["tier"] == "TIER_2_FRONTIER"
        assert r_data["cached"] is False
        print("✓ test_tier_2_frontier_routing passed (Model:", r_data["model_routed_to"], ")")

        # 4. Dynamic Model Routing - Tier 1 Fast Internal for Standard Query
        simple_payload = {
            "messages": [
                {"role": "user", "content": "Format this list into bullet points."}
            ],
            "department": "AWM_Wealth",
            "user_id": "advisor_33"
        }
        res = client.post("/v1/chat/completions", json=simple_payload)
        assert res.status_code == 200
        s_data = res.json()
        assert s_data["tier"] == "TIER_1_INTERNAL"
        print("✓ test_tier_1_internal_routing passed (Model:", s_data["model_routed_to"], ")")

        # 5. Cache Stats
        res = client.get("/api/v1/gateway/cache-stats")
        assert res.status_code == 200
        stats = res.json()
        assert stats["cache_hits"] >= 1
        assert stats["total_requests"] >= 1
        print("✓ test_cache_stats passed (Hit ratio:", stats["hit_ratio_pct"], "%, Tokens saved:", stats["total_tokens_saved"], ")")

        # 6. Departmental Budget Status
        res = client.get("/api/v1/gateway/budget-allocation")
        assert res.status_code == 200
        budgets = res.json()
        assert len(budgets) >= 4
        dept_names = [b["department"] for b in budgets]
        assert "CIB_Research" in dept_names
        assert "AWM_Wealth" in dept_names
        print("✓ test_budget_allocation passed (Departments tracked:", len(budgets), ")")

if __name__ == "__main__":
    run_all_tests()
    print("\nAll JPMC_LLM_RouterGateway_API tests PASSED successfully!")
