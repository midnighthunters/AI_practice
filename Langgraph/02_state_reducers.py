"""
================================================================================
02_state_reducers.py - State Reducers & Parallel Branches
================================================================================

CONCEPT:
--------
In Example 01, each node completely replaced/overwrote the state keys.
What if you want to:
1. Accumulate an ongoing audit log of messages without losing previous ones?
2. Run TWO nodes in parallel (forking) and combine their outputs safely?

Enter **Reducers**!
By wrapping a field in `typing.Annotated`, you define a reducer function that
governs how incoming updates are merged into existing state.

Example:
  Annotated[list[str], operator.add]
  - When Node A returns: {"audit_log": ["Item 1"]}
  - And Node B returns:  {"audit_log": ["Item 2"]}
  - LangGraph applies `operator.add(existing, new)`, yielding `["Item 1", "Item 2"]`.

GRAPH TOPOLOGY (Fork & Join):
-----------------------------
             (START)
             ┌──┴──┐
             ▼     ▼   (Runs concurrently!)
    [sentiment]   [security_audit]
             └──┬──┘
                ▼
        [consolidate_report]
                │
                ▼
              (END)

RUN THIS FILE:
--------------
  python Langgraph/02_state_reducers.py
================================================================================
"""

import operator
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from gemini_client import call_gemini


# ------------------------------------------------------------------------------
# 1. STATE SCHEMA WITH REDUCERS
# ------------------------------------------------------------------------------
class AuditState(TypedDict):
    input_text: str
    sentiment_findings: str
    security_findings: str
    final_verdict: str
    # 'audit_trail' uses operator.add: any node returning a list will APPEND,
    # never overwriting previous steps!
    audit_trail: Annotated[List[str], operator.add]


# ------------------------------------------------------------------------------
# 2. NODES (TWO RUN IN PARALLEL)
# ------------------------------------------------------------------------------
def sentiment_node(state: AuditState) -> dict:
    """Evaluates tone and sentiment."""
    print("  [Parallel Branch A] Running Sentiment Analyzer...")
    prompt = (
        f"Classify the sentiment and urgency of this text in 1 concise line:\n"
        f"\"{state['input_text']}\""
    )
    res = call_gemini(prompt)
    findings = res["text"]

    # Returning audit_trail as a list will be appended via operator.add
    return {
        "sentiment_findings": findings,
        "audit_trail": ["[Audit] Sentiment analysis complete."]
    }


def security_node(state: AuditState) -> dict:
    """Evaluates security, PII, and compliance risk."""
    print("  [Parallel Branch B] Running Security & PII Scanner...")
    prompt = (
        f"Scan this text for security, credentials, PII, or confidential risk in 1 concise line:\n"
        f"\"{state['input_text']}\""
    )
    res = call_gemini(prompt)
    findings = res["text"]

    return {
        "security_findings": findings,
        "audit_trail": ["[Audit] Security scan complete."]
    }


def consolidate_node(state: AuditState) -> dict:
    """Join node: Waits for both branches to complete, then consolidates."""
    print("  [Join Node] Consolidating parallel findings into Final Verdict...")
    prompt = (
        f"Input Message: {state['input_text']}\n"
        f"Sentiment Analysis: {state['sentiment_findings']}\n"
        f"Security Analysis: {state['security_findings']}\n\n"
        f"Write an overall safety clearance verdict in 2 bullet points."
    )
    res = call_gemini(prompt)
    verdict = res["text"]

    return {
        "final_verdict": verdict,
        "audit_trail": ["[Audit] Final consolidation and verdict published."]
    }


# ------------------------------------------------------------------------------
# 3. BUILD FORK-AND-JOIN GRAPH
# ------------------------------------------------------------------------------
def build_reducer_graph():
    builder = StateGraph(AuditState)

    # Register Nodes
    builder.add_node("sentiment_analyzer", sentiment_node)
    builder.add_node("security_scanner", security_node)
    builder.add_node("consolidate_report", consolidate_node)

    # Fork: START splits into both branches
    builder.add_edge(START, "sentiment_analyzer")
    builder.add_edge(START, "security_scanner")

    # Join: Both branches converge on consolidate_report
    builder.add_edge("sentiment_analyzer", "consolidate_report")
    builder.add_edge("security_scanner", "consolidate_report")

    # Exit: consolidate_report -> END
    builder.add_edge("consolidate_report", END)

    return builder.compile()


def run_example(text: str = None):
    sample = text or (
        "URGENT: Database server db-prod-02 has 99.8% disk utilization! "
        "Credentials admin:Quantum$2026! are in the /var/log/credentials.txt file. "
        "Need someone to clear space immediately."
    )

    print("\n" + "=" * 60)
    print("LANGGRAPH 02: STATE REDUCERS & PARALLEL BRANCHES")
    print("=" * 60)
    print(f"Incoming Text:\n{sample}\n")

    app = build_reducer_graph()

    initial_state: AuditState = {
        "input_text": sample,
        "sentiment_findings": "",
        "security_findings": "",
        "final_verdict": "",
        "audit_trail": ["[Audit] Pipeline initialized."]
    }

    print("Executing Graph (Watch branches run and audit_trail accumulate):")
    final_output = app.invoke(initial_state)

    print("\n" + "-" * 60)
    print("PARALLEL BRANCH FINDINGS:")
    print("-" * 60)
    print(f"Sentiment Analysis:\n{final_output['sentiment_findings']}\n")
    print(f"Security Scanner:\n{final_output['security_findings']}\n")
    print(f"Final Verdict:\n{final_output['final_verdict']}\n")

    print("-" * 60)
    print("ACCUMULATED AUDIT TRAIL (via Annotated[list, operator.add]):")
    print("-" * 60)
    for entry in final_output["audit_trail"]:
        print(f"  • {entry}")
    print("=" * 60 + "\n")
    return final_output


if __name__ == "__main__":
    run_example()
