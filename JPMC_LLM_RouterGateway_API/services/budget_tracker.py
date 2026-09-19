"""
Departmental Token Budget & Cost Attribution Manager
Tracks token quotas and USD spending across JPMorgan Chase business units
(CIB Research, AWM Wealth Management, Risk & Compliance).
"""

from typing import Dict, List
from schemas import DepartmentBudget

BUDGET_CONFIG = {
    "CIB_Research": {"monthly_budget": 50000.0, "spent": 14200.50, "tokens": 2840100},
    "AWM_Wealth": {"monthly_budget": 35000.0, "spent": 8120.00, "tokens": 1624000},
    "Risk_Compliance": {"monthly_budget": 20000.0, "spent": 3400.20, "tokens": 680040},
    "Commercial_Banking": {"monthly_budget": 25000.0, "spent": 5900.00, "tokens": 1180000}
}

class DepartmentBudgetTracker:
    def __init__(self):
        self.budgets = BUDGET_CONFIG.copy()

    def record_usage(self, department: str, tokens: int, cost_usd: float):
        if department not in self.budgets:
            self.budgets[department] = {"monthly_budget": 10000.0, "spent": 0.0, "tokens": 0}
        
        self.budgets[department]["spent"] += cost_usd
        self.budgets[department]["tokens"] += tokens

    def get_all_budgets(self) -> List[DepartmentBudget]:
        results: List[DepartmentBudget] = []
        for dept, data in self.budgets.items():
            spent = data["spent"]
            total = data["monthly_budget"]
            pct = (spent / total * 100) if total > 0 else 0.0
            status = "HEALTHY" if pct < 80.0 else ("WARNING" if pct < 100.0 else "EXCEEDED")

            results.append(DepartmentBudget(
                department=dept,
                monthly_budget_usd=total,
                spent_usd=round(spent, 2),
                tokens_consumed=data["tokens"],
                budget_utilized_pct=round(pct, 2),
                status=status
            ))
        return results

budget_tracker = DepartmentBudgetTracker()
