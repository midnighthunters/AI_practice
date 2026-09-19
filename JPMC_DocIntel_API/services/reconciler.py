"""
Deterministic Financial Reconciliation Engine
Verifies foundational accounting identities across extracted financial statements.
Under strict banking standards, any LLM output violating GAAP/IFRS identities is flagged immediately.
"""

from typing import Dict, List, Any
from schemas import ReconciliationCheck, ReconciliationResponse
from services.parser import doc_store

def reconcile_filing(filing_id: str) -> ReconciliationResponse:
    filing = doc_store.get_filing(filing_id)
    if not filing:
        return ReconciliationResponse(
            filing_id=filing_id,
            reconciliation_checks=[],
            all_balanced=False,
            summary=f"Filing {filing_id} not found in store."
        )

    index = filing["line_item_index"]
    checks: List[ReconciliationCheck] = []

    def find_val(search_keys: List[str]) -> float:
        for k in search_keys:
            norm = k.lower()
            for stored_key, data in index.items():
                if norm in stored_key:
                    # Pick the first available numeric value (usually most recent fiscal year)
                    for col, val_info in data["values"].items():
                        if val_info["numeric"] is not None:
                            return val_info["numeric"]
        return 0.0

    # 1. Balance Sheet Equation: Assets = Total Liabilities + Total Stockholders' Equity
    assets = find_val(["total assets"])
    liabilities = find_val(["total liabilities"])
    equity = find_val(["total stockholders' equity", "total equity", "stockholders' equity"])

    if assets > 0 and (liabilities > 0 or equity > 0):
        rhs_bs = liabilities + equity
        diff_bs = abs(assets - rhs_bs)
        # Allow small variance for rounding in millions ($1M)
        is_bs_balanced = diff_bs <= 1.0
        checks.append(ReconciliationCheck(
            equation_name="Balance Sheet Identity (Assets = Liabilities + Equity)",
            lhs_name="Total Assets",
            lhs_value=assets,
            rhs_name="Liabilities ($" + str(liabilities) + "M) + Equity ($" + str(equity) + "M)",
            rhs_value=rhs_bs,
            difference=round(diff_bs, 2),
            is_balanced=is_bs_balanced,
            status="PASSED" if is_bs_balanced else "DISCREPANCY DETECTED"
        ))

    # 2. Net Income Identity: Total Net Revenue - Noninterest Expense - Provision = Pretax Income
    rev = find_val(["total net revenue", "total net revenues", "net revenue"])
    exp = find_val(["total noninterest expense", "noninterest expense"])
    provision = find_val(["provision for credit losses"])
    pretax = find_val(["income before income tax expense", "income before taxes"])

    if rev > 0 and exp > 0 and pretax > 0:
        expected_pretax = rev - exp - provision
        diff_inc = abs(expected_pretax - pretax)
        is_inc_balanced = diff_inc <= 2.0
        checks.append(ReconciliationCheck(
            equation_name="Operating Identity (Revenue - Expenses - Provisions = Pretax Income)",
            lhs_name="Reported Pretax Income",
            lhs_value=pretax,
            rhs_name="Revenue - Noninterest Expense - Provisions",
            rhs_value=round(expected_pretax, 2),
            difference=round(diff_inc, 2),
            is_balanced=is_inc_balanced,
            status="PASSED" if is_inc_balanced else "DISCREPANCY DETECTED"
        ))

    all_balanced = all(c.is_balanced for c in checks) if checks else False
    summary = (
        f"All {len(checks)} accounting equations balanced successfully within rounding tolerance."
        if all_balanced else
        f"Reconciliation completed with {sum(1 for c in checks if not c.is_balanced)} discrepancies detected."
    )

    return ReconciliationResponse(
        filing_id=filing_id,
        reconciliation_checks=checks,
        all_balanced=all_balanced,
        summary=summary
    )
