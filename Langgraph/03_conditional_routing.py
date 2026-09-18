"""
================================================================================
03_conditional_routing.py - Dynamic Branching & Conditional Edges
================================================================================

CONCEPT:
--------
In linear pipelines, every piece of data passes through the exact same steps.
In real-world applications, different user queries require completely different
expert logic:
- A billing question should go to billing specialists.
- A technical error code should go to engineering diagnostics.
- A casual hello should go to standard conversational models.

LangGraph solves this with **Conditional Edges**:
`builder.add_conditional_edges(source_node, routing_function, path_map)`

1. `source_node`: The node whose output determines the next step (e.g. classifier).
2. `routing_function`: A function that inspects the State and returns a string key.
3. `path_map`: A dict mapping return keys to target nodes:
   {"tech": "handle_tech", "billing": "handle_billing", "casual": "handle_casual"}

GRAPH TOPOLOGY:
---------------
                    (START)
                       │
                       ▼
              [classify_intent]
                       │
             ┌─────────┼─────────┐
             ▼ (tech)  ▼ (bill)  ▼ (casual)
       [handle_tech] [handle_bill] [handle_casual]
             └─────────┬─────────┘
                       ▼
                     (END)

RUN THIS FILE:
--------------
  python Langgraph/03_conditional_routing.py
================================================================================
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from gemini_client import call_gemini_json, call_gemini


# ------------------------------------------------------------------------------
# 1. STATE SCHEMA
# ------------------------------------------------------------------------------
class RouterState(TypedDict):
    query: str
    intent: str               # "technical", "billing", or "casual"
    confidence: float
    response: str
    route_taken: str


# ------------------------------------------------------------------------------
# 2. CLASSIFIER NODE (Determines Route)
# ------------------------------------------------------------------------------
def classify_node(state: RouterState) -> dict:
    """Uses Gemini to classify query intent into one of 3 categories."""
    print(f"  [Router] Classifying user intent for: '{state['query']}'...")
    prompt = (
        f"Classify the following user message into exactly ONE category:\n"
        f"- 'technical': Programming, errors, bugs, API keys, architecture, system crashes.\n"
        f"- 'billing': Invoices, refunds, subscriptions, pricing, payment methods.\n"
        f"- 'casual': Greetings, chit-chat, identity questions, polite banter.\n\n"
        f"Message: \"{state['query']}\"\n\n"
        f"Return JSON format: {{\"category\": \"technical\" | \"billing\" | \"casual\", \"confidence\": 0.95}}"
    )
    res = call_gemini_json(prompt)
    parsed = res.get("parsed") or {}

    category = parsed.get("category", "casual").lower()
    if category not in ["technical", "billing", "casual"]:
        category = "casual"

    confidence = parsed.get("confidence", 0.9)
    print(f"  [Router Decision] Detected category: '{category}' (Confidence: {confidence})")

    return {
        "intent": category,
        "confidence": confidence
    }


# ------------------------------------------------------------------------------
# 3. SPECIALIZED HANDLER NODES
# ------------------------------------------------------------------------------
def tech_handler(state: RouterState) -> dict:
    """Specialized node for Technical & Code queries."""
    print("  [Handler: Tech] Executing technical diagnostics with Gemini...")
    prompt = (
        f"You are a Senior Systems Architect.\n"
        f"User technical issue: {state['query']}\n"
        f"Provide a crisp 2-step diagnostic guide with code snippet if helpful."
    )
    res = call_gemini(prompt)
    return {
        "response": res["text"],
        "route_taken": "Technical Support Specialist"
    }


def billing_handler(state: RouterState) -> dict:
    """Specialized node for Billing & Subscription queries."""
    print("  [Handler: Billing] Executing financial & subscription policy...")
    prompt = (
        f"You are a QuantumNova Billing Concierge.\n"
        f"User query: {state['query']}\n"
        f"Explain our 45-day refund guarantee and payment policies in 2 friendly sentences."
    )
    res = call_gemini(prompt)
    return {
        "response": res["text"],
        "route_taken": "Billing & Accounts Department"
    }


def casual_handler(state: RouterState) -> dict:
    """Specialized node for General & Casual queries."""
    print("  [Handler: Casual] Generating friendly conversational reply...")
    prompt = (
        f"You are a friendly AI companion. Respond warmly in 1-2 sentences to:\n"
        f"\"{state['query']}\""
    )
    res = call_gemini(prompt)
    return {
        "response": res["text"],
        "route_taken": "General Assistant"
    }


# ------------------------------------------------------------------------------
# 4. ROUTING LOGIC FUNCTION
# ------------------------------------------------------------------------------
def route_by_intent(state: RouterState) -> Literal["tech_path", "billing_path", "casual_path"]:
    """
    This function inspects the state returned by classify_node and returns
    the routing key corresponding to the desired path.
    """
    intent = state.get("intent", "casual")
    if intent == "technical":
        return "tech_path"
    elif intent == "billing":
        return "billing_path"
    return "casual_path"


# ------------------------------------------------------------------------------
# 5. BUILD CONDITIONAL GRAPH
# ------------------------------------------------------------------------------
def build_routing_graph():
    builder = StateGraph(RouterState)

    # Register Nodes
    builder.add_node("classify_intent", classify_node)
    builder.add_node("handle_tech", tech_handler)
    builder.add_node("handle_billing", billing_handler)
    builder.add_node("handle_casual", casual_handler)

    # Start -> Classifier
    builder.add_edge(START, "classify_intent")

    # Dynamic Conditional Edge:
    # After classify_intent, call route_by_intent to determine which handler executes!
    builder.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "tech_path": "handle_tech",
            "billing_path": "handle_billing",
            "casual_path": "handle_casual"
        }
    )

    # All handlers transition to END
    builder.add_edge("handle_tech", END)
    builder.add_edge("handle_billing", END)
    builder.add_edge("handle_casual", END)

    return builder.compile()


def run_example(query: str = None):
    test_queries = [
        "How do I fix a NullPointerException in my Java Redis cache cluster?",
        "I was charged twice on my credit card invoice for the Enterprise tier.",
        "Good morning! How are you feeling today?"
    ]

    app = build_routing_graph()

    print("\n" + "=" * 65)
    print("LANGGRAPH 03: DYNAMIC CONDITIONAL ROUTING")
    print("=" * 65)

    queries_to_run = [query] if query else test_queries

    for q in queries_to_run:
        print(f"\nIncoming User Query: \"{q}\"")
        initial_state: RouterState = {
            "query": q,
            "intent": "",
            "confidence": 0.0,
            "response": "",
            "route_taken": ""
        }
        out = app.invoke(initial_state)
        print(f" -> Selected Route: {out['route_taken']} (Intent: {out['intent']})")
        print(f" -> Generated Response:\n{out['response']}\n" + "-" * 40)

    print("=" * 65 + "\n")
    return out


if __name__ == "__main__":
    run_example()
