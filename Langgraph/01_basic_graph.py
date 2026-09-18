"""
================================================================================
01_basic_graph.py - The Hello World of LangGraph
================================================================================

CONCEPT:
--------
In traditional LangChain (LCEL) or simple Python scripts, execution is a 
one-way linear chain: A -> B -> C.

LangGraph introduces a much more powerful paradigm: a **StateGraph**.
A StateGraph consists of three primary building blocks:

1. **State**: A central shared data structure (usually a `TypedDict` or Pydantic model)
   that flows between nodes.
2. **Nodes**: Python functions that receive the current State, do work (e.g. call Gemini),
   and return a dictionary of state updates.
3. **Edges**: Connections that dictate which node runs next:
   - `START`: The entry point where execution begins.
   - `END`: The terminal point where the graph completes.
   - Fixed edges: Direct transition from Node A to Node B.

GRAPH TOPOLOGY:
---------------
  (START)
     │
     ▼
[analyze_input]  ──► Calls Gemini to extract key themes & sentiment
     │
     ▼
[generate_summary] ──► Calls Gemini to synthesize an executive summary
     │
     ▼
   (END)

RUN THIS FILE:
--------------
  python Langgraph/01_basic_graph.py
================================================================================
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from gemini_client import call_gemini


# ------------------------------------------------------------------------------
# 1. DEFINE STATE SCHEMA
# ------------------------------------------------------------------------------
# The State is the single source of truth passed across all nodes.
# By default in LangGraph, returning a key from a node OVERWRITES that key in State.
class PipelineState(TypedDict):
    input_text: str
    analysis: str
    summary: str
    step_history: list[str]


# ------------------------------------------------------------------------------
# 2. DEFINE GRAPH NODES
# ------------------------------------------------------------------------------
# A Node is simply a Python function that:
#   - Takes `state: PipelineState` as input
#   - Returns a partial dict of keys to update in State
def analyze_node(state: PipelineState) -> dict:
    """Node 1: Analyzes the raw input text using Gemini."""
    print("  [Node: analyze_input] Analyzing input text with Gemini...")
    prompt = (
        f"Analyze this text in 2 short bullet points (Main Theme and Sentiment):\n"
        f"\"\"\"{state['input_text']}\"\"\""
    )
    result = call_gemini(prompt)
    analysis = result["text"]
    
    # Return updates to merge into State
    return {
        "analysis": analysis,
        "step_history": state.get("step_history", []) + ["analyze_input completed"]
    }


def summary_node(state: PipelineState) -> dict:
    """Node 2: Generates a high-impact summary based on input & analysis."""
    print("  [Node: generate_summary] Synthesizing final summary with Gemini...")
    prompt = (
        f"Original text: {state['input_text']}\n"
        f"Analysis: {state['analysis']}\n\n"
        f"Write a 1-sentence executive takeaway for leadership."
    )
    result = call_gemini(prompt)
    summary = result["text"]

    return {
        "summary": summary,
        "step_history": state.get("step_history", []) + ["generate_summary completed"]
    }


# ------------------------------------------------------------------------------
# 3. CONSTRUCT & COMPILE THE GRAPH
# ------------------------------------------------------------------------------
def build_basic_graph():
    """Builds and compiles the StateGraph."""
    builder = StateGraph(PipelineState)

    # Add Nodes
    builder.add_node("analyze_input", analyze_node)
    builder.add_node("generate_summary", summary_node)

    # Add Edges
    # START -> analyze_input -> generate_summary -> END
    builder.add_edge(START, "analyze_input")
    builder.add_edge("analyze_input", "generate_summary")
    builder.add_edge("generate_summary", END)

    # Compile into a Runnable
    return builder.compile()


def run_example(text: str = None):
    sample_text = text or (
        "QuantumNova has launched its breakthrough optical quantum computing platform Q-Core. "
        "Initial enterprise benchmark tests show a 40x speedup in portfolio optimization over "
        "classical supercomputers, though cryogenic cooling costs currently remain high for small firms."
    )

    print("\n" + "=" * 60)
    print("LANGGRAPH 01: BASIC GRAPH EXECUTION")
    print("=" * 60)
    print(f"Input Text:\n{sample_text}\n")

    app = build_basic_graph()

    # We can stream intermediate node updates!
    initial_state: PipelineState = {
        "input_text": sample_text,
        "analysis": "",
        "summary": "",
        "step_history": []
    }

    print("Streaming Graph Execution:")
    final_state = None
    for event in app.stream(initial_state):
        # Event is a dict where key is the node name that just ran
        for node_name, state_update in event.items():
            print(f"\n[Event from '{node_name}']:")
            for key, val in state_update.items():
                if key != "step_history":
                    print(f"   {key}: {val}")
        final_state = event

    # Also demonstrate full invoke
    final_output = app.invoke(initial_state)
    print("\n" + "-" * 60)
    print("FINAL GRAPH STATE OUTPUT:")
    print("-" * 60)
    print(f"Analysis:\n{final_output['analysis']}\n")
    print(f"Executive Summary:\n{final_output['summary']}\n")
    print(f"Execution History:\n{final_output['step_history']}")
    print("=" * 60 + "\n")
    return final_output


if __name__ == "__main__":
    run_example()
