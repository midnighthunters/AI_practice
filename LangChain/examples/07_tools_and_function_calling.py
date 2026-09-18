"""
================================================================================
EXAMPLE 07: Tools & Function Calling (Tool Binding)
================================================================================
LLMs cannot do math reliably or fetch live database records on their own.
Learn how LangChain equips models with executable Tools:
1. The `@tool` decorator: Creating typed tools with docstrings.
2. Inspecting the JSON Schema LangChain generates for Gemini.
3. Tool Binding: `llm.bind_tools([tool1, tool2])`.
4. Inspecting `tool_calls` emitted by the model.
5. Invoking the tool and returning the execution output.
================================================================================
"""

import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm, extract_text

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage


# 1. Define custom tools using the @tool decorator
@tool
def calculate_compound_interest(principal: float, annual_rate: float, years: int) -> float:
    """
    Calculates the final compound interest amount: A = P * (1 + r)^t.
    Use this whenever interest or compounding returns need to be calculated.
    """
    total = principal * ((1 + annual_rate) ** years)
    return round(total, 2)


@tool
def check_flight_status(flight_number: str) -> str:
    """
    Fetches real-time status, terminal, and gate for a commercial airline flight.
    """
    # Simulated live database lookup
    mock_db = {
        "BA-249": {"status": "On Time", "departure": "14:30 GMT", "gate": "B22", "terminal": "5"},
        "DL-104": {"status": "Delayed (45 mins)", "departure": "16:15 EST", "gate": "A8", "terminal": "2"},
        "LH-441": {"status": "Boarding Now", "departure": "11:05 CET", "gate": "G14", "terminal": "1"}
    }
    flight_key = flight_number.upper().strip()
    if flight_key in mock_db:
        info = mock_db[flight_key]
        return f"Flight {flight_key}: Status is {info['status']}, departing at {info['departure']} from Terminal {info['terminal']}, Gate {info['gate']}."
    return f"Flight {flight_key} not found in current daily schedule."


def demo_tool_inspection():
    print("\n" + "=" * 60)
    print("PART 1: Inspecting Auto-Generated Tool Schemas")
    print("=" * 60)

    # LangChain automatically analyzes Python type hints and docstrings
    # to construct the OpenAPI/JSON schema that Gemini understands
    tools = [calculate_compound_interest, check_flight_status]
    for t in tools:
        print(f"\nTool Name: {t.name}")
        print(f"Description: {t.description}")
        print("Schema Arguments:")
        print(json.dumps(t.args, indent=2))


def demo_tool_calling_flow():
    print("\n" + "=" * 60)
    print("PART 2: Model Tool Binding & Invocation Cycle")
    print("=" * 60)

    llm = get_llm(temperature=0.0)
    tools = [calculate_compound_interest, check_flight_status]
    tools_map = {t.name: t for t in tools}

    # Bind tools to the model
    llm_with_tools = llm.bind_tools(tools)

    user_query = "What is the current flight status for BA-249, and if I invest $5,000 at 7% annual interest for 10 years, what will it be worth?"
    print(f"[User Query]:\n'{user_query}'\n")

    messages = [HumanMessage(content=user_query)]

    print("[Sending query to Gemini with tools bound...]")
    ai_response = llm_with_tools.invoke(messages)

    print(f"\n[Model Decided To Call {len(ai_response.tool_calls)} Tools]:")
    for i, call in enumerate(ai_response.tool_calls, 1):
        print(f" Tool Call #{i}:")
        print(f"   Function: {call['name']}")
        print(f"   Arguments: {call['args']}")
        print(f"   Call ID: {call['id']}")

    # Append the AI's decision (which contains tool_calls) to the message trail
    messages.append(ai_response)

    # Execute each selected tool and create ToolMessages
    print("\n[Executing Tools Locally in Python...]")
    for call in ai_response.tool_calls:
        tool_func = tools_map[call["name"]]
        tool_result = tool_func.invoke(call["args"])
        print(f"  Ran `{call['name']}` -> Result: {tool_result}")

        # Send tool execution result back with matching tool_call_id
        messages.append(ToolMessage(
            content=str(tool_result),
            tool_call_id=call["id"]
        ))

    print("\n[Sending Tool Results back to Gemini for Final Answer Synthesis...]")
    final_response = llm_with_tools.invoke(messages)
    print(f"\n[Final Synthesized Answer]:\n{extract_text(final_response.content)}")


if __name__ == "__main__":
    print("\n🚀 Starting Example 07: Tools & Function Calling")
    demo_tool_inspection()
    demo_tool_calling_flow()
    print("\n✅ Example 07 completed successfully!\n")
