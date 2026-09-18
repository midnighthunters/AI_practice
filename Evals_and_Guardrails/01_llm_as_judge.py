"""
01_llm_as_judge.py
==================
LLM-as-a-Judge: Automated Rubric-Based Scoring & Chain-of-Thought Grading.

Concepts:
- Using an LLM (or deterministic evaluation rubrics) to grade generated model responses.
- Separating evaluation into multiple orthagonal dimensions:
  1. Factual Accuracy (grounding against reference facts)
  2. Conciseness & Precision (signal-to-noise ratio)
- Automated pass/fail decision gates for CI/CD deployment pipelines.
"""

import sys
import json
from evals_core import LLMAsAJudge

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" ⚖️  EVALS 01: LLM-as-a-Judge Rubric-Based Evaluation")
    print("=" * 70)

    # Reference Ground Truth
    question = "When is Project NovaStar scheduled to launch and what is its frequency band?"
    reference_context = (
        "Project NovaStar is QuantumNova's flagship satellite system. "
        "Launch date: November 24, 2026 aboard the Falcon Heavy. "
        "Frequency band: Ka-band (26.5-40 GHz). Total budget: $420 million USD."
    )

    # Candidate 1: High Quality Response
    good_answer = (
        "Project NovaStar is scheduled to launch on November 24, 2026 on a Falcon Heavy rocket. "
        "It will operate on the Ka-band frequency (26.5 to 40 GHz)."
    )

    # Candidate 2: Hallucinated / Inaccurate Response
    hallucinated_answer = (
        "Project NovaStar will launch in early 2029 using an Ariane 6 rocket. "
        "Its frequency operates primarily on the legacy X-band spectrum."
    )

    # Candidate 3: Extremely Verbose Response
    verbose_answer = (
        "In regards to the exciting and multifaceted endeavor known as Project NovaStar, "
        "which has captured the interest of numerous aerospace engineers and stakeholders alike, "
        "it is indeed scheduled to lift off on November 24, 2026 aboard Falcon Heavy. Furthermore, "
        "delving into its electromagnetic transmission characteristics, it relies upon Ka-band frequencies. "
        "This project represents a truly momentous technological milestone in global satellite telecommunications."
    )

    candidates = [
        ("Candidate 1 (Factual & Concise)", good_answer),
        ("Candidate 2 (Hallucinated / Incorrect)", hallucinated_answer),
        ("Candidate 3 (Overly Verbose)", verbose_answer)
    ]

    for title, ans in candidates:
        print(f"\nEvaluating {title}:")
        print(f"Answer text: \"{ans[:75]}...\"")
        result = LLMAsAJudge.evaluate(question, ans, reference_context)
        print(f"  • Overall Score: {result['overall_score']} / 5.0 (Passed: {result['passed']})")
        print(f"  • Accuracy Rubric: {result['accuracy_score']} / 5")
        print(f"  • Conciseness Rubric: {result['conciseness_score']} / 5")
        print(f"  • Reason: {result['reasoning']}")

    print("\n✅ LLM-as-a-Judge rubric scoring complete!")


if __name__ == "__main__":
    main()
