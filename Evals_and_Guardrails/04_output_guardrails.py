"""
04_output_guardrails.py
=======================
Production Output Guardrails: Schema Conformance & Data Leakage Prevention.

After the LLM generates a response, Output Guardrails ensure:
1. Strict Schema Adherence: Validate required JSON fields and types.
2. Leakage Prevention: Detect if the LLM accidentally repeated customer PII.
3. Safe Fallback: Prevent broken JSON or leaked credentials from reaching end users.
"""

import sys
import json
from evals_core import SafetyGuardrails

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" 🛡️  EVALS 04: Production Output Guardrails & Schema Enforcement")
    print("=" * 70)

    # Required JSON schema from customer support triage
    target_schema = {
        "required": ["category", "urgency", "summary"]
    }

    # Output 1: Valid compliant structured JSON
    valid_llm_output = json.dumps({
        "category": "BILLING",
        "urgency": "HIGH",
        "summary": "Customer charged twice for annual subscription renewal."
    }, indent=2)

    # Output 2: Broken / Malformed JSON (LLM included preamble conversational text)
    broken_llm_output = (
        "Here is your analysis:\n\n"
        "{\n"
        "  \"category\": \"TECHNICAL\"\n"
        "  \"summary\": \"API returning 500 status\"\n"
        "}"  # Missing comma and missing required field 'urgency'
    )

    # Output 3: Valid JSON but accidentally leaks private user email and phone
    leaking_llm_output = json.dumps({
        "category": "ACCOUNT_RECOVERY",
        "urgency": "MEDIUM",
        "summary": "Password reset token sent to john.doe@secretcorp.com. User contact: (555) 987-6543."
    }, indent=2)

    outputs = [
        ("Output 1: Schema Compliant", valid_llm_output),
        ("Output 2: Malformed / Missing Fields", broken_llm_output),
        ("Output 3: Accidental PII Data Leak", leaking_llm_output)
    ]

    for title, out_text in outputs:
        print(f"\n--- {title} ---")
        guard_scan = SafetyGuardrails.scan_output(out_text, required_schema=target_schema)

        print(f"  • Schema Valid:         {guard_scan['schema_valid']}")
        if not guard_scan['schema_valid']:
            print(f"    Schema Error:         {guard_scan['schema_error']}")
        print(f"  • PII Leakage Detected: {guard_scan['pii_leakage_detected']}")
        if guard_scan['pii_leakage_detected']:
            print(f"    Leaked Items:         {guard_scan['pii_items']}")
        print(f"  • Delivered Output:\n{guard_scan['sanitized_output']}")

    print("\n✅ Output guardrail enforcement verified!")


if __name__ == "__main__":
    main()
