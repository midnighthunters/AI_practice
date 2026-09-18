"""
================================================================================
05_tool_calling_agent.py - ReAct (Reason + Act) Agent Loop from Scratch
================================================================================

CONCEPT:
--------
In standard LLM chains, the model cannot execute Python code or fetch live
system metrics. It can only talk.

In LangGraph, an **Agent** is simply a cyclic graph with two main nodes:
1. **Agent Node (Reason)**: The LLM receives the message history, determines if
   it needs external tools, and either calls a tool OR outputs a final answer.
2. **Tool Execution Node (Act)**: Executes the tool function (e.g. calculator,
   cluster telemetry lookup), packages the result into the state, and
   loops BACK to the Agent Node!

GRAPH TOPOLOGY (ReAct Loop):
----------------------------
         (START)
            │
            ▼
     ┌──► [agent_reason] ◄────────┐
     │          │                 │
     │          ▼ (Conditional)   │
     │    Needs Tool Call?        │
     │    ├── YES ──► [run_tool] ─┘
     └───┼─── NO
         │
         ▼
       (END)

RUN THIS FILE:
--------------
  python Langgraph/05_tool_calling_agent.py
================================================================================
"""

import operator
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from gemini_client import call_gemini_json


# ------------------------------------------------------------------------------
# 1. TOOL DEFINITIONS
# ------------------------------------------------------------------------------
def tool_calculator(expression: str) -> str:
    """Safely evaluates basic arithmetic expressions."""
    try:
        # Whitelist safe characters only
        allowed = set("0123456789+-*/(). %")
        if not all(c in allowed for c in expression):
            return "Error: Unsupported characters in calculation."
        result = eval(expression, {"__builtins__": {}})
        return f"Calculation Result: {result}"
    except Exception as e:
        return f"Calculation Error: {str(e)}"


def tool_cluster_telemetry(cluster_name: str) -> str:
    """Mock telemetry tool looking up cluster status."""
    cluster = cluster_name.lower().strip()
    telemetry_db = {
        "zurich-alpha": "Zurich Cluster: 12 nodes online, CPU: 42%, Memory: 68%, Status: HEALTHY",
        "singapore-beta": "Singapore Cluster: 8 nodes online, CPU: 89%, Memory: 94%, Status: WARNING_HIGH_LOAD",
        "tokyo-gamma": "Tokyo Cluster: 4 nodes online, CPU: 12%, Memory: 21%, Status: IDLE"
    }
    for key, val in telemetry_db.items():
        if key in cluster or cluster in key:
            return val
    return f"Cluster '{cluster_name}' not found. Known clusters: zurich-alpha, singapore-beta, tokyo-gamma."


TOOLS = {
    "calculator": tool_calculator,
    "cluster_telemetry": tool_cluster_telemetry
}

TOOLS_DESCRIPTION = """
Available Tools:
1. 'calculator': Evaluates math expressions. Input: {"expression": "14 * 25"}
2. 'cluster_telemetry': Queries live health of server clusters. Input: {"cluster_name": "singapore-beta"}
"""


# ------------------------------------------------------------------------------
# 2. STATE SCHEMA
# ------------------------------------------------------------------------------
class ReActState(TypedDict):
    input_query: str
    messages: Annotated[List[Dict[str, str]], operator.add]
    next_tool: str            # Name of tool to execute or "none"
    tool_args: Dict[str, Any]
    final_answer: str
    step_count: int


# ------------------------------------------------------------------------------
# 3. AGENT REASONING NODE
# ------------------------------------------------------------------------------
def agent_reason_node(state: ReActState) -> dict:
    """Agent evaluates conversation history and decides next action or final answer."""
    step = state.get("step_count", 0) + 1
    print(f"\n  [Agent Reason] Step #{step}: Evaluating next action...")

    history_str = "\n".join([f"- {m['role']}: {m['content']}" for m in state.get("messages", [])])

    prompt = (
        f"You are an autonomous ReAct AI agent equipped with tools.\n"
        f"{TOOLS_DESCRIPTION}\n\n"
        f"Original User Query: \"{state['input_query']}\"\n\n"
        f"Execution History:\n{history_str or 'No actions taken yet.'}\n\n"
        f"Instructions:\n"
        f"1. If you need more information to answer the user query, specify which tool to call and the args.\n"
        f"2. If you already have sufficient info (or no tools are needed), provide the final_answer and set tool to 'none'.\n\n"
        f"Return JSON format:\n"
        f"{{\n"
        f"  \"thought\": \"Reasoning step\",\n"
        f"  \"action\": \"tool_name\" | \"none\",\n"
        f"  \"tool_args\": {{ \"expression\": \"...\" }} or {{ \"cluster_name\": \"...\" }},\n"
        f"  \"final_answer\": \"Complete final response if action is none\"\n"
        f"}}"
    )

    res = call_gemini_json(prompt)
    parsed = res.get("parsed") or {}

    action = parsed.get("action", "none").lower()
    tool_args = parsed.get("tool_args", {})
    thought = parsed.get("thought", "")
    final_ans = parsed.get("final_answer", "")

    print(f"  [Agent Thought]: {thought}")
    if action in TOOLS:
        print(f"  [Action Planned]: Call tool '{action}' with args {tool_args}")
    else:
        print(f"  [Action Planned]: Finished. Ready with final answer.")

    new_messages = [{
        "role": "agent",
        "content": f"Thought: {thought} | Action: {action} with {tool_args}"
    }]

    return {
        "messages": new_messages,
        "next_tool": action,
        "tool_args": tool_args,
        "final_answer": final_ans,
        "step_count": step
    }


# ------------------------------------------------------------------------------
# 4. TOOL EXECUTION NODE
# ------------------------------------------------------------------------------
def execute_tool_node(state: ReActState) -> dict:
    """Executes the chosen tool and appends observation to state."""
    tool_name = state["next_tool"]
    args = state["tool_args"]
    print(f"  [Tool Execution] Running '{tool_name}'...")

    if tool_name == "calculator":
        result = tool_calculator(args.get("expression", "0"))
    elif tool_name == "cluster_telemetry":
        result = tool_cluster_telemetry(args.get("cluster_name", ""))
    else:
        result = f"Error: Tool '{tool_name}' unknown."

    print(f"  [Tool Output]: {result}")

    new_messages = [{
        "role": "tool_observation",
        "content": f"Output of {tool_name}: {result}"
    }]

    return {
        "messages": new_messages,
        "next_tool": "none"  # Reset for next loop
    }


# ------------------------------------------------------------------------------
# 5. CONDITIONAL ROUTER (Decides: Continue ReAct loop or Finish?)
# ------------------------------------------------------------------------------
def should_continue(state: ReActState) -> Literal["execute_tool", "finish"]:
    tool_name = state.get("next_tool", "none")
    step = state.get("step_count", 0)

    # Safety guard against infinite loops
    if step >= 5:
        print("  [Router Guard] Max steps reached. Forcing finish.")
        return "finish"

    if tool_name in TOOLS:
        return "execute_tool"
    return "finish"


# ------------------------------------------------------------------------------
# 6. BUILD REACT GRAPH
# ------------------------------------------------------------------------------
def build_react_graph():
    builder = StateGraph(ReActState)

    builder.add_node("agent_reason", agent_reason_node)
    builder.add_node("run_tool", execute_tool_node)

    builder.add_edge(START, "agent_reason")

    # Conditional branch: agent_reason -> (run_tool OR END)
    builder.add_conditional_edges(
        "agent_reason",
        should_continue,
        {
            "execute_tool": "run_tool",
            "finish": END
        }
    )

    # Loop back: after running tool, go back to agent_reason to think again!
    builder.add_edge("run_tool", "agent_reason")

    return builder.compile()


def run_example(query: str = None):
    sample_query = query or (
        "Check the telemetry of the singapore-beta cluster, and if its CPU utilization is over 80%, "
        "calculate how many new servers we need to add if each server reduces load by 15% to get below 60%?"
    )

    print("\n" + "=" * 65)
    print("LANGGRAPH 05: REACT TOOL-CALLING AGENT LOOP")
    print("=" * 65)
    print(f"User Request:\n\"{sample_query}\"")

    app = build_react_graph()

    initial_state: ReActState = {
        "input_query": sample_query,
        "messages": [{"role": "user", "content": sample_query}],
        "next_tool": "none",
        "tool_args": {},
        "final_answer": "",
        "step_count": 0
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 65)
    print(f"AGENT RESOLVED QUERY IN {final_state['step_count']} REASONING STEPS!")
    print("=" * 65)
    print(f"Final Agent Answer:\n{final_state['final_answer']}\n")

    print("-" * 65)
    print("COMPLETE MESSAGE & TOOL LOG:")
    print("-" * 65)
    for m in final_state["messages"]:
        print(f"[{m['role'].upper()}]: {m['content']}")
    print("=" * 65 + "\n")
    return final_state


if __name__ == "__main__":
    run_example()
