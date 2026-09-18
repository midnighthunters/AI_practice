"""
================================================================================
07_human_in_the_loop.py - Human-in-the-Loop (HITL) Interrupts & Approval
================================================================================

CONCEPT:
--------
In autonomous systems, certain actions are irreversible and dangerous:
- Wire transfers / financial debits
- Production database drops or migrations
- Sending mass emails or deleting accounts

LangGraph solves this with **Breakpoints / Interrupts**:
`app = builder.compile(checkpointer=memory, interrupt_before=["sensitive_node"])`

When execution reaches a sensitive node:
1. LangGraph **halts execution** and saves the exact state to the checkpointer.
2. The outer system or human inspects `app.get_state(config)`.
3. The human reviews the proposed parameters and issues an approval or rejection.
4. The system resumes execution cleanly by calling `app.invoke(None, config)`.

GRAPH TOPOLOGY:
---------------
  (START)
     │
     ▼
[draft_transaction] ──► Prepares transfer payload using Gemini reasoning
     │
    ⏸️ [INTERRUPT BEFORE] ──► Halts! Waits for human approval signal
     │
     ▼
[execute_transfer]  ──► Executes wire transfer ONLY if approved
     │
     ▼
   (END)

RUN THIS FILE:
--------------
  python Langgraph/07_human_in_the_loop.py
================================================================================
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from gemini_client import call_gemini_json


# ------------------------------------------------------------------------------
# 1. STATE SCHEMA
# ------------------------------------------------------------------------------
class FinancialTransferState(TypedDict):
    request: str
    recipient: str
    amount_usd: float
    reason: str
    human_approval: str      # "PENDING", "APPROVED", "REJECTED"
    execution_status: str
    transaction_id: str


# ------------------------------------------------------------------------------
# 2. NODES
# ------------------------------------------------------------------------------
def draft_transaction_node(state: FinancialTransferState) -> dict:
    """Uses Gemini to parse and structure the proposed financial transfer."""
    print("  [Step 1: Drafter] Parsing transaction request with Gemini...")
    prompt = (
        f"Parse this financial transfer request into JSON:\n"
        f"\"{state['request']}\"\n\n"
        f"Return JSON format:\n"
        f"{{\n"
        f"  \"recipient\": \"Account or person\",\n"
        f"  \"amount_usd\": 50000.0,\n"
        f"  \"reason\": \"Summary of purpose\"\n"
        f"}}"
    )
    res = call_gemini_json(prompt)
    parsed = res.get("parsed") or {}

    recipient = parsed.get("recipient", "Unknown Vendor")
    amount = float(parsed.get("amount_usd", 0.0))
    reason = parsed.get("reason", "Internal Transfer")

    print(f"  [Drafter Output] Recipient: {recipient} | Amount: ${amount:,.2f} | Reason: {reason}")

    return {
        "recipient": recipient,
        "amount_usd": amount,
        "reason": reason,
        "human_approval": "PENDING",
        "execution_status": "WAITING_FOR_HUMAN_REVIEW"
    }


def execute_transfer_node(state: FinancialTransferState) -> dict:
    """CRITICAL NODE: Executes the transfer ONLY if human has approved."""
    print("  [Step 2: Execution Node] Checking approval authorization...")

    approval = state.get("human_approval", "PENDING")

    if approval == "APPROVED":
        tx_id = f"TX-NOVANET-{int(state['amount_usd'])}-OK"
        status = f"SUCCESS: Transferred ${state['amount_usd']:,.2f} to {state['recipient']} (TX: {tx_id})"
        print(f"  [EXECUTED]: {status}")
        return {
            "execution_status": status,
            "transaction_id": tx_id
        }
    else:
        status = f"ABORTED: Transfer of ${state['amount_usd']:,.2f} was {approval} by human reviewer."
        print(f"  [ABORTED]: {status}")
        return {
            "execution_status": status,
            "transaction_id": "NONE_ABORTED"
        }


# ------------------------------------------------------------------------------
# 3. BUILD GRAPH WITH INTERRUPT BREAKPOINT
# ------------------------------------------------------------------------------
def build_hitl_graph():
    builder = StateGraph(FinancialTransferState)

    builder.add_node("draft_transaction", draft_transaction_node)
    builder.add_node("execute_transfer", execute_transfer_node)

    builder.add_edge(START, "draft_transaction")
    builder.add_edge("draft_transaction", "execute_transfer")
    builder.add_edge("execute_transfer", END)

    # CRITICAL: Interrupt before 'execute_transfer' so execution halts!
    memory = MemorySaver()
    return builder.compile(
        checkpointer=memory,
        interrupt_before=["execute_transfer"]
    )


def run_example(simulated_approval: str = "APPROVED"):
    transfer_request = "Please wire transfer $75,000 to Apex Data Centers for Q3 server rack expansion."

    print("\n" + "=" * 65)
    print("LANGGRAPH 07: HUMAN-IN-THE-LOOP (HITL) APPROVAL WORKFLOW")
    print("=" * 65)
    print(f"Incoming Request:\n\"{transfer_request}\"\n")

    app = build_hitl_graph()
    config = {"configurable": {"thread_id": "transfer-thread-888"}}

    initial_state: FinancialTransferState = {
        "request": transfer_request,
        "recipient": "",
        "amount_usd": 0.0,
        "reason": "",
        "human_approval": "PENDING",
        "execution_status": "INITIALIZED",
        "transaction_id": ""
    }

    # PHASE 1: Launch graph. It will pause right before 'execute_transfer'!
    print("Phase 1: Starting autonomous workflow...")
    app.invoke(initial_state, config=config)

    # Inspect current state at the breakpoint
    state_at_breakpoint = app.get_state(config)
    print(f"\n[PAUSED] WORKFLOW HALTED AT BREAKPOINT!")
    print(f"   Next Pending Node: {state_at_breakpoint.next}")
    print(f"   Drafted Recipient: {state_at_breakpoint.values['recipient']}")
    print(f"   Drafted Amount:    ${state_at_breakpoint.values['amount_usd']:,.2f}")
    print(f"   Reason:            {state_at_breakpoint.values['reason']}")
    print(f"   Current Status:    {state_at_breakpoint.values['execution_status']}")

    # PHASE 2: Human reviews the pending action and supplies approval decision
    print(f"\nPhase 2: Human Reviewer evaluates transaction...")
    print(f"   Decision applied: {simulated_approval}")

    # Update state with the human's decision before resuming!
    app.update_state(
        config,
        {"human_approval": simulated_approval},
        as_node="draft_transaction"
    )

    # PHASE 3: Resume execution from the breakpoint
    print("\nPhase 3: Resuming execution with app.invoke(None, config)...")
    app.invoke(None, config=config)

    final_state = app.get_state(config)
    print("\n" + "=" * 65)
    print("FINAL WORKFLOW OUTCOME:")
    print("=" * 65)
    print(f"Final Status:    {final_state.values['execution_status']}")
    print(f"Transaction ID:  {final_state.values['transaction_id']}")
    print("=" * 65 + "\n")
    return final_state.values


if __name__ == "__main__":
    run_example()
