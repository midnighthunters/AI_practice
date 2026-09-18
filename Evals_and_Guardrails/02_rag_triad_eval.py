"""
02_rag_triad_eval.py
====================
The RAG Triad: Faithfulness, Answer Relevance, and Context Precision.

The RAG Triad is the industry standard framework (TruLens, Ragas) for
diagnosing RAG pipeline failures:
1. Context Precision: Did our retriever fetch the right chunks?
2. Faithfulness (Groundedness): Is the answer grounded strictly in retrieved context without hallucinations?
3. Answer Relevance: Does the generated answer actually address the user's question?
"""

import sys
import json
from evals_core import RAGTriadEvaluator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print(" 📐  EVALS 02: The RAG Triad (Faithfulness, Relevance, Precision)")
    print("=" * 70)

    question = "What is the Wi-Fi password and core working hours at QuantumNova headquarters?"

    retrieved_contexts = [
        "QuantumNova headquarters is located in Seattle, WA. The high-speed office Wi-Fi password is StellarNebula2026! and SSID is QuantumNova-Corp-5G.",
        "Core working hours for full-time employees are 10:00 AM to 4:00 PM Pacific Time. All staff receive a $1,500 annual wellness stipend.",
        "Unrelated chunk: The orbital satellite Project NovaStar is slated for launch in late November."
    ]

    # Scenario A: Healthy RAG generation (High faithfulness + high relevance)
    answer_a = (
        "The Wi-Fi password at headquarters is 'StellarNebula2026!' and core working hours are 10:00 AM to 4:00 PM Pacific Time."
    )

    # Scenario B: Hallucinated / Unfaithful generation (Context ignored)
    answer_b = (
        "The Wi-Fi password is 'Welcome2024' and working hours are 9:00 AM to 5:00 PM Eastern."
    )

    # Scenario C: Irrelevant generation (Factual from context, but ignores the question)
    answer_c = (
        "Project NovaStar is an orbital satellite system launching in late November with a Falcon Heavy rocket."
    )

    scenarios = [
        ("Scenario A: Grounded & Directly Relevant", answer_a),
        ("Scenario B: Hallucinated / Contradicts Context", answer_b),
        ("Scenario C: High Faithfulness, Low Answer Relevance", answer_c)
    ]

    for title, ans in scenarios:
        print(f"\n--- {title} ---")
        metrics = RAGTriadEvaluator.evaluate_triad(question, retrieved_contexts, ans)
        print(f"  • Faithfulness:      {metrics['faithfulness']}  (Answer grounded in retrieved chunks)")
        print(f"  • Answer Relevance:  {metrics['answer_relevance']}  (Direct response to user question)")
        print(f"  • Context Precision: {metrics['context_precision']}  (Fraction of useful chunks retrieved)")
        print(f"  • Composite Score:   {metrics['composite_rag_score']} / 1.0 -> Status: [{metrics['health']}]")

    print("\n✅ RAG Triad quantitative diagnosis complete!")


if __name__ == "__main__":
    main()
