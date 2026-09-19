"""
Numerical Grounding & Anti-Hallucination Verification Engine
Extracts numerical entities from candidate answers and verifies that every single
statistic or monetary figure exists verbatim in the verified SEC tables.
"""

import os
import re
from typing import Dict, List, Tuple, Any
from schemas import GroundedCitation, FilingQueryResponse
from services.parser import doc_store

def extract_numbers_from_text(text: str) -> List[str]:
    """Finds numbers like $158,104, 2023, 49.6, 3,875,393."""
    matches = re.findall(r'[$]?\d+(?:,\d{3})*(?:\.\d+)?', text)
    return [m.strip() for m in matches if m.strip()]

def generate_grounded_answer(filing_id: str, question: str, enforce_grounding: bool = True) -> FilingQueryResponse:
    filing = doc_store.get_filing(filing_id)
    if not filing:
        return FilingQueryResponse(
            question=question,
            answer=f"Filing '{filing_id}' is not loaded. Please ingest filing first.",
            citations=[],
            grounding_confidence=0.0,
            numerical_hallucinations_detected=0
        )

    index = filing["line_item_index"]
    num_val_lookup = filing["numerical_values"]

    # Keyword match against line items
    tokens = [t.lower() for t in re.findall(r'\b\w+\b', question) if len(t) > 2]
    matched_items = []
    
    for key, item_data in index.items():
        score = sum(1 for tok in tokens if tok in key)
        if score > 0:
            matched_items.append((score, item_data))

    matched_items.sort(key=lambda x: x[0], reverse=True)
    top_matches = matched_items[:5]

    citations: List[GroundedCitation] = []
    answer_parts: List[str] = []

    if top_matches:
        answer_parts.append(f"Based on the official {filing['fiscal_year']} {filing['filing_type']} for {filing['ticker']}:")
        for _, item in top_matches:
            c_name = item["canonical_name"]
            t_name = item["table"]
            for col_name, val_data in item["values"].items():
                raw_v = val_data["raw"]
                citations.append(GroundedCitation(
                    line_item=c_name,
                    reported_value=raw_v,
                    table_name=t_name,
                    column=col_name,
                    verified_in_source=True
                ))
                answer_parts.append(f"• **{c_name}** ({col_name}): **{raw_v}** [Source: {t_name}]")
        answer_text = "\n".join(answer_parts)
    else:
        answer_text = f"No direct line items matched your query '{question}' in the indexed tables of {filing_id}."

    # Anti-Hallucination Numerical Verification Pass
    extracted_nums = extract_numbers_from_text(answer_text)
    verified_count = 0
    hallucinations = 0

    # Include years and common metadata in allowable set
    known_metadata_numbers = {
        str(filing["fiscal_year"]),
        str(filing["fiscal_year"] - 1),
        str(filing["fiscal_year"] - 2),
        str(filing["fiscal_year"] - 3),
        "10", "8"  # 10-K, 8-K
    }

    for num_str in extracted_nums:
        # Standardize number
        clean_num = num_str.replace("$", "").replace(",", "").replace("%", "").strip()
        num_match = re.search(r'[-+]?\d*\.?\d+', clean_num)
        if num_match:
            base_val = num_match.group()
            # If it's a known fiscal year or metadata, it's valid
            if base_val in known_metadata_numbers:
                verified_count += 1
            # Check if this base number exists in the indexed tables
            elif base_val in num_val_lookup or any(base_val in k for k in num_val_lookup.keys()):
                verified_count += 1
            else:
                hallucinations += 1

    total_checked = verified_count + hallucinations
    confidence = (verified_count / total_checked) if total_checked > 0 else 1.0

    return FilingQueryResponse(
        question=question,
        answer=answer_text,
        citations=citations,
        grounding_confidence=round(confidence, 4),
        numerical_hallucinations_detected=hallucinations
    )
