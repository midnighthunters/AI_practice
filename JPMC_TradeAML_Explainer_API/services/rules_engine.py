"""
Deterministic AML & Trade Surveillance Rules Engine
Identifies known financial crime typologies: Structuring (Smurfing), Velocity Bursts,
and High-Risk Jurisdiction Hops without black-box hallucination.
"""

from typing import List, Tuple
from schemas import TransactionRecord, TypologyViolation

# High-risk / Offshore jurisdictions (FATF monitor list sample)
HIGH_RISK_JURISDICTIONS = {"CY", "PA", "KY", "VG", "SC", "VU"}

def evaluate_aml_rules(transactions: List[TransactionRecord]) -> List[TypologyViolation]:
    violations: List[TypologyViolation] = []

    # 1. Structuring (Smurfing) Check: Amounts just below the £10k/€10k/$10k reporting threshold (e.g., 9000 to 9999)
    structuring_txs = [
        tx.transaction_id for tx in transactions
        if 9000.0 <= tx.amount < 10000.0
    ]
    if len(structuring_txs) >= 2:
        violations.append(TypologyViolation(
            rule_code="AML-R101-STRUCTURING",
            typology_name="Structuring / Smurfing",
            severity="CRITICAL",
            description=f"Identified {len(structuring_txs)} transactions just below the mandatory regulatory reporting threshold of 10,000, indicating deliberate evasion of reporting controls.",
            flagged_transaction_ids=structuring_txs
        ))

    # 2. Velocity Burst Check: 3 or more transactions within the alert batch
    if len(transactions) >= 3:
        violations.append(TypologyViolation(
            rule_code="AML-R204-VELOCITY-SPIKE",
            typology_name="Rapid Velocity Layering",
            severity="HIGH",
            description=f"High-frequency burst of {len(transactions)} consecutive fund transfers within a compressed operational window.",
            flagged_transaction_ids=[tx.transaction_id for tx in transactions]
        ))

    # 3. High-Risk Jurisdiction Routing Check
    high_risk_txs = [
        tx.transaction_id for tx in transactions
        if tx.destination_country.upper() in HIGH_RISK_JURISDICTIONS
    ]
    if high_risk_txs:
        violations.append(TypologyViolation(
            rule_code="AML-R305-OFFSHORE-HOP",
            typology_name="High-Risk Jurisdiction Routing",
            severity="HIGH",
            description=f"Funds routed to offshore FATF monitored jurisdiction(s): {len(high_risk_txs)} transactions flagged.",
            flagged_transaction_ids=high_risk_txs
        ))

    return violations
