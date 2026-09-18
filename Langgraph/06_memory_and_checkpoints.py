"""
================================================================================
06_memory_and_checkpoints.py - Persistence & Checkpointing (MemorySaver)
================================================================================

CONCEPT:
--------
Standard LLM scripts are stateless: once a function finishes, the memory vanishes.

LangGraph provides built-in, production-grade **Persistence & Checkpointing**:
1. **Checkpointer**: Automatically snapshots the graph's State at every super-step
   (e.g., `MemorySaver`, `SqliteSaver`, `PostgresSaver`).
2. **Thread ID**: A session identifier (`thread_id`) passed via the config dictionary:
   `{"configurable": {"thread_id": "session-42"}}`
   LangGraph restores the exact previous state for that thread on the next call!
3. **Thread Isolation**: Different users or conversations maintain distinct,
   completely isolated states simultaneously.
4. **Time Travel (State History)**:
   `app.get_state_history(config)` enables you to replay, inspect, and rewind
   to any previous state snapshot in time.

GRAPH TOPOLOGY:
---------------
  (START)
     │
     ▼
[chat_node] ──► Reads full history from persistent state, calls Gemini
     │
     ▼
   (END)
  [Checkpointer saves state snapshot to MemorySaver for thread_id]

RUN THIS FILE:
--------------
  python Langgraph/06_memory_and_checkpoints.py
================================================================================
"""

import operator
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from gemini_client import call_gemini


# ------------------------------------------------------------------------------
# 1. STATE SCHEMA
# ------------------------------------------------------------------------------
class ConversationState(TypedDict):
    # 'messages' accumulates history across turns via operator.add
    messages: Annotated[List[Dict[str, str]], operator.add]
    user_name: str
    user_role: str
    turn_count: int


# ------------------------------------------------------------------------------
# 2. CHAT NODE
# ------------------------------------------------------------------------------
def chat_node(state: ConversationState) -> dict:
    turn = state.get("turn_count", 0) + 1
    recent_user_msg = state["messages"][-1]["content"]
    print(f"  [Chat Node] Processing turn #{turn}: '{recent_user_msg}'...")

    # Build context from previous conversation turns in state
    history_lines = []
    for msg in state["messages"][:-1]:
        history_lines.append(f"{msg['role'].capitalize()}: {msg['content']}")

    history_context = "\n".join(history_lines) if history_lines else "No previous history."

    prompt = (
        f"You are a helpful persistent conversational assistant.\n"
        f"Conversation History:\n{history_context}\n\n"
        f"Latest User Message: \"{recent_user_msg}\"\n\n"
        f"Respond helpfully and naturally in 1-2 sentences."
    )

    res = call_gemini(prompt)
    assistant_reply = res["text"]

    # Extract user profile if mentioned
    user_name = state.get("user_name", "")
    user_role = state.get("user_role", "")

    return {
        "messages": [{"role": "assistant", "content": assistant_reply}],
        "turn_count": turn
    }


# ------------------------------------------------------------------------------
# 3. BUILD GRAPH WITH MEMORY SAVER CHECKPOINTER
# ------------------------------------------------------------------------------
def build_memory_graph():
    builder = StateGraph(ConversationState)
    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    # In-memory checkpointer for demonstration (persists state across invokes)
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


def run_example():
    app = build_memory_graph()

    print("\n" + "=" * 65)
    print("LANGGRAPH 06: MULTI-TURN PERSISTENCE & CHECKPOINTING")
    print("=" * 65)

    # SESSION 1: Alice (thread_id: "thread-alice-101")
    config_alice = {"configurable": {"thread_id": "thread-alice-101"}}

    print("\n--- TURN 1 (Alice): Introducing herself ---")
    turn1_input = {
        "messages": [{"role": "user", "content": "Hi! My name is Dr. Alice Chen, Lead Cryptographer at QuantumNova."}],
        "user_name": "Dr. Alice Chen",
        "user_role": "Lead Cryptographer",
        "turn_count": 0
    }
    app.invoke(turn1_input, config=config_alice)
    current_alice_state = app.get_state(config_alice)
    print(f"Alice's Assistant: {current_alice_state.values['messages'][-1]['content']}")

    print("\n--- TURN 2 (Alice): Follow-up question (Testing Memory Recall) ---")
    turn2_input = {
        "messages": [{"role": "user", "content": "What is my job title and where do I work?"}]
    }
    app.invoke(turn2_input, config=config_alice)
    current_alice_state = app.get_state(config_alice)
    print(f"Alice's Assistant: {current_alice_state.values['messages'][-1]['content']}")

    # SESSION 2: Bob (thread_id: "thread-bob-202") -> Complete isolation test!
    config_bob = {"configurable": {"thread_id": "thread-bob-202"}}
    print("\n--- SESSION 2 (Bob): Completely different thread ---")
    bob_input = {
        "messages": [{"role": "user", "content": "Hello, do you know who I am?"}],
        "turn_count": 0
    }
    app.invoke(bob_input, config=config_bob)
    current_bob_state = app.get_state(config_bob)
    print(f"Bob's Assistant: {current_bob_state.values['messages'][-1]['content']}")

    # TIME TRAVEL / STATE HISTORY INSPECTOR
    print("\n" + "-" * 65)
    print("INSPECTING STATE CHECKPOINT HISTORY FOR ALICE (Time Travel):")
    print("-" * 65)
    history = list(app.get_state_history(config_alice))
    print(f"Total saved checkpoints for Alice's thread: {len(history)}")
    for i, snapshot in enumerate(history):
        checkpoint_id = snapshot.config["configurable"]["checkpoint_id"]
        msg_count = len(snapshot.values.get("messages", []))
        print(f"  [{i+1}] Checkpoint ID: {checkpoint_id[:8]}... | Messages stored: {msg_count}")

    print("=" * 65 + "\n")
    return current_alice_state.values


if __name__ == "__main__":
    run_example()
