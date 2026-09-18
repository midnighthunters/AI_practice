"""
================================================================================
04_cyclical_agent_loop.py - Cycles & Self-Correction Loops (Drafter-Critic)
================================================================================

CONCEPT:
--------
Why do we need LangGraph instead of classic linear chains or DAGs (Airflow, LCEL)?
Because true autonomous intelligence requires **CYCLES** (Loops)!

A linear chain can only generate once:
  Prompt ──► Output (Hope it's right!)

A LangGraph cycle creates a self-healing feedback loop:
  1. Drafter generates initial version.
  2. Critic analyzes version against strict criteria and assigns a score (1-10).
  3. If score >= 8: Approved! Move to END.
  4. If score < 8: Loop BACK to Drafter with specific critique instructions!

GRAPH TOPOLOGY (The Cycle):
---------------------------
         (START)
            │
            ▼
     ┌──► [drafter] ◄───────────────┐
     │      │                       │ (Loop back if score < 8)
     │      ▼                       │
     │   [critic]                   │
     │      │                       │
     │      ▼ (Conditional Edge)    │
     │   Score >= 8 ?               │
     │   ├── NO (needs revision) ───┘
     └───┼── YES (meets standard) ──┐
                                    ▼
                                  (END)

RUN THIS FILE:
--------------
  python Langgraph/04_cyclical_agent_loop.py
================================================================================
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from gemini_client import call_gemini, call_gemini_json


# ------------------------------------------------------------------------------
# 1. STATE SCHEMA
# ------------------------------------------------------------------------------
class DrafterCriticState(TypedDict):
    topic: str
    target_criteria: str
    current_draft: str
    critique: str
    quality_score: int
    iteration_count: int
    max_iterations: int
    history: list[dict]


# ------------------------------------------------------------------------------
# 2. DRAFTER NODE (Generates / Refines)
# ------------------------------------------------------------------------------
def drafter_node(state: DrafterCriticState) -> dict:
    """Drafts or revises the text based on accumulated critique."""
    iteration = state.get("iteration_count", 0) + 1
    print(f"\n  [Drafter Node] Iteration #{iteration}: Drafting content...")

    if not state.get("current_draft"):
        # Initial draft: intentionally rough/brief to let the critic trigger a revision cycle
        prompt = (
            f"You are writing a preliminary, rough draft announcement.\n"
            f"Topic: {state['topic']}\n"
            f"Write a brief 1-2 sentence rough placeholder draft without looking at the fine details."
        )
    else:
        # Revision based on critic's feedback!
        prompt = (
            f"You are revising your previous draft based on reviewer critique.\n"
            f"Topic: {state['topic']}\n"
            f"Target Criteria: {state['target_criteria']}\n\n"
            f"Previous Draft:\n{state['current_draft']}\n\n"
            f"Reviewer Critique & Missing Requirements:\n{state['critique']}\n\n"
            f"Rewrite the draft addressing ALL the reviewer's points cleanly."
        )

    res = call_gemini(prompt)
    draft_text = res["text"]

    return {
        "current_draft": draft_text,
        "iteration_count": iteration
    }


# ------------------------------------------------------------------------------
# 3. CRITIC NODE (Evaluates Quality & Assigns Score)
# ------------------------------------------------------------------------------
def critic_node(state: DrafterCriticState) -> dict:
    """Evaluates the draft against strict rubric and outputs JSON score & critique."""
    print(f"  [Critic Node] Reviewing Draft #{state['iteration_count']} against criteria...")
    prompt = (
        f"You are a strict editorial quality reviewer.\n"
        f"Target Criteria:\n{state['target_criteria']}\n\n"
        f"Draft to Review:\n\"\"\"{state['current_draft']}\"\"\"\n\n"
        f"Evaluate the draft:\n"
        f"1. Check if all target criteria are fulfilled.\n"
        f"2. Give a score from 1 to 10 (10 = perfect, >=8 = pass, <8 = revision needed).\n"
        f"3. Provide specific, actionable critique for improvements if score < 8.\n\n"
        f"Return JSON format:\n"
        f"{{\"score\": 7, \"approved\": false, \"critique\": \"Specific feedback here.\"}}"
    )
    res = call_gemini_json(prompt)
    parsed = res.get("parsed") or {}

    score = int(parsed.get("score", 5))
    critique = parsed.get("critique", "Please improve clarity and fulfill all requirements.")

    print(f"  [Critic Assessment] Score: {score}/10 | Critique: {critique[:90]}...")

    history_entry = {
        "iteration": state["iteration_count"],
        "draft": state["current_draft"],
        "score": score,
        "critique": critique
    }

    return {
        "quality_score": score,
        "critique": critique,
        "history": state.get("history", []) + [history_entry]
    }


# ------------------------------------------------------------------------------
# 4. CONDITIONAL ROUTER (Decides: Loop back or Finish?)
# ------------------------------------------------------------------------------
def evaluate_loop_condition(state: DrafterCriticState) -> Literal["revise", "finish"]:
    """
    Evaluates whether the draft passes quality standards or needs another cycle.
    Includes a recursion guard (max_iterations) to prevent infinite loops.
    """
    score = state.get("quality_score", 0)
    iterations = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 3)

    if score >= 8:
        print(f"  [Decision] Score {score}/10 meets standard (>=8)! Moving to END.")
        return "finish"

    if iterations >= max_iter:
        print(f"  [Decision] Max iterations reached ({iterations}/{max_iter}). Finalizing to prevent infinite loop.")
        return "finish"

    print(f"  [Decision] Score {score}/10 is below threshold (<8). LOOPING BACK to Drafter!")
    return "revise"


# ------------------------------------------------------------------------------
# 5. BUILD CYCLICAL GRAPH
# ------------------------------------------------------------------------------
def build_cyclical_graph():
    builder = StateGraph(DrafterCriticState)

    # Register Nodes
    builder.add_node("drafter", drafter_node)
    builder.add_node("critic", critic_node)

    # Fixed edge: START -> drafter
    builder.add_edge(START, "drafter")

    # Fixed edge: drafter -> critic
    builder.add_edge("drafter", "critic")

    # CYCLICAL CONDITIONAL EDGE:
    # critic -> evaluate_loop_condition:
    #   "revise" -> loops back to "drafter"
    #   "finish" -> exits to END
    builder.add_conditional_edges(
        "critic",
        evaluate_loop_condition,
        {
            "revise": "drafter",
            "finish": END
        }
    )

    return builder.compile()


def run_example():
    topic = "Announcing QuantumNova's SOC-2 Type II Compliance Certification"
    # Intentionally strict criteria so initial draft will receive critique!
    criteria = (
        "1. Must explicitly mention third-party auditor 'Deloitte & Touche'.\n"
        "2. Must specify coverage over both Cloud Vault and API Infrastructure.\n"
        "3. Must include a clear customer Call to Action to download the report from the Trust Center.\n"
        "4. Tone must be professional, reassuring, and concise (under 80 words)."
    )

    print("\n" + "=" * 65)
    print("LANGGRAPH 04: CYCLICAL AGENT LOOP (DRAFTER-CRITIC)")
    print("=" * 65)
    print(f"Topic: {topic}")
    print(f"Target Criteria:\n{criteria}\n")

    app = build_cyclical_graph()

    initial_state: DrafterCriticState = {
        "topic": topic,
        "target_criteria": criteria,
        "current_draft": "",
        "critique": "",
        "quality_score": 0,
        "iteration_count": 0,
        "max_iterations": 3,
        "history": []
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 65)
    print(f"CYCLE COMPLETED IN {final_state['iteration_count']} ITERATIONS!")
    print(f"FINAL QUALITY SCORE: {final_state['quality_score']}/10")
    print("=" * 65)
    print(f"Final Approved Text:\n{final_state['current_draft']}\n")

    print("-" * 65)
    print("CYCLE ITERATION BREAKDOWN:")
    print("-" * 65)
    for step in final_state["history"]:
        print(f"Iteration #{step['iteration']} - Score: {step['score']}/10")
        print(f"  Critique: {step['critique']}")
        print(f"  Draft: {step['draft'][:100]}...\n")
    print("=" * 65 + "\n")
    return final_state


if __name__ == "__main__":
    run_example()
