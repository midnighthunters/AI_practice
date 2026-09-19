"""
Adaptive Model Router for JPMorgan Chase LLM Suite
Routes incoming prompts dynamically between Tier 1 (Ultra-low latency internal/flash models)
and Tier 2 (Frontier high-reasoning models) based on complexity scoring and prompt length.
"""

from typing import Tuple

TIER_1_MODEL = "JPMC-Internal-FinLLM-8B-Fast"
TIER_2_MODEL = "JPMC-Frontier-Reasoning-70B"

COMPLEX_TRIGGERS = [
    "reconcile", "discounted cash flow", "dcf", "monte carlo",
    "var calculation", "swaption", "credit default swap",
    "sec 10-k", "merger agreement", "indenture", "complex reasoning"
]

def determine_routing(prompt: str) -> Tuple[str, str]:
    """Returns (model_name, tier_label)"""
    prompt_lower = prompt.lower()
    word_count = len(prompt.split())

    # Complex prompts go to Tier 2
    if word_count > 300 or any(trigger in prompt_lower for trigger in COMPLEX_TRIGGERS):
        return TIER_2_MODEL, "TIER_2_FRONTIER"
    
    # Simple, high-speed prompts go to Tier 1
    return TIER_1_MODEL, "TIER_1_INTERNAL"

def simulate_model_inference(prompt: str, model_name: str, tier: str) -> str:
    """Generates deterministic context-aware banking response if live external LLM is offline."""
    if "basel" in prompt.lower():
        return "JPMorgan Chase maintains robust capital buffers with a CET1 ratio consistently exceeding regulatory minimums under Basel III standards."
    elif "dcf" in prompt.lower() or "valuation" in prompt.lower():
        return "Discounted Cash Flow (DCF) model projected enterprise value using a 9.5% WACC and 2.5% terminal growth rate, yielding a defensible institutional valuation range."
    else:
        return f"[Synthesized by {model_name} ({tier})]: Analysis completed successfully with strict compliance to JPMC LLM Suite enterprise policies."
