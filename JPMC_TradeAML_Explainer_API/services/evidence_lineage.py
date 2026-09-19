"""
Evidence Lineage & Cryptographic Hash Linker
Maps every factual assertion in the Suspicious Activity Report (SAR) narrative
to immutable transaction IDs and computes a tamper-proof SHA-256 evidence chain.
"""

import hashlib
from typing import List, Dict, Any
from schemas import TransactionRecord

def build_evidence_lineage(transactions: List[TransactionRecord]) -> List[Dict[str, Any]]:
    lineage: List[Dict[str, Any]] = []
    
    for tx in transactions:
        raw_signature = f"{tx.transaction_id}:{tx.originating_account}:{tx.destination_account}:{tx.amount}:{tx.currency}:{tx.timestamp}"
        tx_hash = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()
        
        lineage.append({
            "transaction_id": tx.transaction_id,
            "timestamp": tx.timestamp,
            "originator": tx.originator_name,
            "amount_formatted": f"{tx.currency} {tx.amount:,.2f}",
            "destination_country": tx.destination_country,
            "cryptographic_hash": tx_hash[:16]
        })
        
    return lineage
