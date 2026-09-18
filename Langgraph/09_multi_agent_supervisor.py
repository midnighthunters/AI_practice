"""
================================================================================
09_multi_agent_supervisor.py - Multi-Agent Collaboration (Supervisor Pattern)
================================================================================

CONCEPT:
--------
As LLM workflows grow in complexity, a single monolithic agent struggles.
Best practice is **Multi-Agent Systems**: breaking problems down across
specialized expert workers orchestrated by a **Supervisor Agent**.

The **Supervisor Pattern** in LangGraph:
1. A central **Supervisor** node inspects the overarching goal and current progress.
2. The Supervisor chooses the next worker:
   - `researcher`: Gathers domain specs and technical requirements.
   - `coder`: Writes production-grade Python code implementing the specs.
   - `FINISH`: When both tasks are fulfilled, exits to END.
3. Each worker completes its work, updates the shared state, and reports back
   to the Supervisor!

GRAPH TOPOLOGY (Supervisor Hub):
--------------------------------
                     (START)
                        │
                        ▼
           ┌───► [supervisor_node] ◄────┐
           │            │               │
           │      ┌─────┴─────┐         │
(Report    │      ▼           ▼         │ (Report
 back)     │ [researcher]  [coder]      │  back)
           │      │           │         │
           └──────┴─────┬─────┴─────────┘
                        │ (When done)
                        ▼
                      (END)

RUN THIS FILE:
--------------
  python Langgraph/09_multi_agent_supervisor.py
================================================================================
"""

import operator
from typing import TypedDict, Annotated, List, Literal
from langgraph.graph import StateGraph, START, END
from gemini_client import call_gemini, call_gemini_json


# ------------------------------------------------------------------------------
# 1. STATE SCHEMA
# ------------------------------------------------------------------------------
class MultiAgentState(TypedDict):
    task: str
    research_notes: str
    code_artifact: str
    final_deliverable: str
    next_worker: str          # "researcher", "coder", or "FINISH"
    step_count: int
    worker_log: Annotated[List[str], operator.add]


# ------------------------------------------------------------------------------
# 2. SUPERVISOR NODE (Orchestrator)
# ------------------------------------------------------------------------------
def supervisor_node(state: MultiAgentState) -> dict:
    step = state.get("step_count", 0) + 1
    print(f"\n  [Supervisor Hub] Step #{step}: Evaluating team progress...")

    has_research = bool(state.get("research_notes"))
    has_code = bool(state.get("code_artifact"))

    prompt = (
        f"You are the Lead Project Supervisor managing an AI team.\n"
        f"Goal: \"{state['task']}\"\n\n"
        f"Current Team State:\n"
        f"- Research Status: {'COMPLETED' if has_research else 'NOT YET STARTED'}\n"
        f"- Coding Status:   {'COMPLETED' if has_code else 'NOT YET STARTED'}\n\n"
        f"Available Workers:\n"
        f"1. 'researcher': Conducts technical research and gathers specifications.\n"
        f"2. 'coder': Writes Python code (requires research first).\n"
        f"3. 'FINISH': Both research and code are complete and task is solved.\n\n"
        f"Select the NEXT worker to assign. Return JSON:\n"
        f"{{\"next_worker\": \"researcher\" | \"coder\" | \"FINISH\", \"reasoning\": \"1 sentence\"}}"
    )

    res = call_gemini_json(prompt)
    parsed = res.get("parsed") or {}

    next_worker = parsed.get("next_worker", "FINISH")
    # Rule fallback logic to guarantee smooth multi-agent handoff
    if not has_research:
        next_worker = "researcher"
    elif not has_code:
        next_worker = "coder"
    else:
        next_worker = "FINISH"

    reasoning = parsed.get("reasoning", "Standard delegation flow.")
    print(f"  [Supervisor Decision]: Assign to -> '{next_worker}' (Reason: {reasoning})")

    return {
        "next_worker": next_worker,
        "step_count": step,
        "worker_log": [f"Supervisor delegated to {next_worker} at step #{step}"]
    }


# ------------------------------------------------------------------------------
# 3. SPECIALIZED WORKER NODES
# ------------------------------------------------------------------------------
def researcher_node(state: MultiAgentState) -> dict:
    """Specialized worker for domain research and specifications."""
    print("  [Worker: Researcher] Conducting technical research with Gemini...")
    prompt = (
        f"You are a Principal Research Engineer.\n"
        f"Task: {state['task']}\n\n"
        f"Provide 3 concise technical requirements & algorithmic specifications for this solution."
    )
    res = call_gemini(prompt)
    notes = res["text"]

    return {
        "research_notes": notes,
        "worker_log": ["Researcher published technical requirements."]
    }


def coder_node(state: MultiAgentState) -> dict:
    """Specialized worker for implementing code."""
    print("  [Worker: Coder] Writing Python implementation with Gemini...")
    prompt = (
        f"You are a Senior Python Developer.\n"
        f"Task: {state['task']}\n\n"
        f"Technical Specifications:\n{state.get('research_notes', 'Standard Python specs.')}\n\n"
        f"Write a clean, self-contained Python function with type hints and a 1-line docstring."
    )
    res = call_gemini(prompt)
    code = res["text"]

    return {
        "code_artifact": code,
        "worker_log": ["Coder generated Python implementation."]
    }


def synthesize_node(state: MultiAgentState) -> dict:
    """Final node synthesizing research and code into a cohesive deliverable."""
    print("  [Final Synthesizer] Compiling final project package...")
    deliverable = (
        f"### Research & Specifications:\n{state.get('research_notes', '')}\n\n"
        f"### Verified Code Solution:\n{state.get('code_artifact', '')}"
    )
    return {
        "final_deliverable": deliverable,
        "worker_log": ["Project package consolidated and published."]
    }


# ------------------------------------------------------------------------------
# 4. CONDITIONAL ROUTER (Supervisor Delegation)
# ------------------------------------------------------------------------------
def route_supervisor(state: MultiAgentState) -> Literal["researcher", "coder", "synthesize"]:
    worker = state.get("next_worker", "FINISH")
    if worker == "researcher":
        return "researcher"
    elif worker == "coder":
        return "coder"
    return "synthesize"


# ------------------------------------------------------------------------------
# 5. BUILD MULTI-AGENT GRAPH
# ------------------------------------------------------------------------------
def build_multi_agent_graph():
    builder = StateGraph(MultiAgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("coder", coder_node)
    builder.add_node("synthesize", synthesize_node)

    builder.add_edge(START, "supervisor")

    # Supervisor conditionally dispatches to researcher, coder, or synthesize
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "coder": "coder",
            "synthesize": "synthesize"
        }
    )

    # After workers finish, they hand control BACK to the supervisor!
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("coder", "supervisor")

    # Synthesizer is the terminal step -> END
    builder.add_edge("synthesize", END)

    return builder.compile()


def run_example():
    task = "Build a thread-safe token bucket rate limiter in Python for a REST API."

    print("\n" + "=" * 65)
    print("LANGGRAPH 09: MULTI-AGENT SUPERVISOR SYSTEM")
    print("=" * 65)
    print(f"Team Goal: \"{task}\"\n")

    app = build_multi_agent_graph()

    initial_state: MultiAgentState = {
        "task": task,
        "research_notes": "",
        "code_artifact": "",
        "final_deliverable": "",
        "next_worker": "supervisor",
        "step_count": 0,
        "worker_log": ["Team session initialized."]
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 65)
    print("MULTI-AGENT TEAM DELIVERABLE:")
    print("=" * 65)
    print(final_state["final_deliverable"])

    print("\n" + "-" * 65)
    print("TEAM HANDOFF & COORDINATION LOG:")
    print("-" * 65)
    for log in final_state["worker_log"]:
        print(f"  * {log}")
    print("=" * 65 + "\n")
    return final_state


if __name__ == "__main__":
    run_example()
