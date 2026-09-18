"""
================================================================================
EXAMPLE 08: Autonomous AI Agents (ReAct & Tool Calling Loop)
================================================================================
An Agent combines an LLM with a loop: it reasons about what steps to take,
selects tools dynamically, executes actions, observes results, and iterates
autonomously until it solves complex, multi-step problems.
Learn:
1. Constructing an autonomous agent loop.
2. Handling multi-step reasoning across multiple independent tools.
3. Tracing Agent Thoughts, Actions, Observations, and Final Answers.
================================================================================
"""

import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm, extract_text

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


# --- Agent Tools ---

@tool
def get_stock_price(ticker: str) -> str:
    """
    Looks up the latest simulated stock price and market status for a company ticker symbol.
    """
    prices = {
        "NVDA": {"price": 128.50, "currency": "USD", "change": "+3.4%"},
        "AAPL": {"price": 224.20, "currency": "USD", "change": "-0.8%"},
        "GOOGL": {"price": 178.90, "currency": "USD", "change": "+1.2%"},
        "TSLA": {"price": 245.00, "currency": "USD", "change": "+5.1%"}
    }
    symbol = ticker.upper().strip()
    if symbol in prices:
        item = prices[symbol]
        return json.dumps({"ticker": symbol, "current_price": item["price"], "currency": item["currency"], "change": item["change"]})
    return json.dumps({"error": f"Ticker symbol '{symbol}' not found in stock feed."})


@tool
def evaluate_math_expression(expression: str) -> str:
    """
    Safely calculates a mathematical arithmetic expression (e.g. '15 * 128.50 * 1.085').
    Always use this tool for arithmetic calculations to ensure 100% precision.
    """
    # Clean expression allowing only digits and basic arithmetic operators
    cleaned = "".join(c for c in expression if c in "0123456789+-*/.() ")
    try:
        result = eval(cleaned, {"__builtins__": None}, {})
        return str(round(result, 4))
    except Exception as e:
        return f"Math calculation error: {e}"


@tool
def query_company_directory(employee_name: str) -> str:
    """
    Searches internal corporate directory for an employee's title, department, and office location.
    """
    directory = {
        "dr. evelyn vasquez": {"role": "Chief Cryptographer", "department": "Quantum R&D", "building": "Building D - Room 402"},
        "arthur pendelton": {"role": "Chief Executive Officer", "department": "Executive Office", "building": "Penthouse Suite"},
        "lorenzo moretti": {"role": "Executive Chef", "department": "Culinary Services", "building": "Cafeteria Level 3"}
    }
    name_key = employee_name.lower().strip()
    if name_key in directory:
        return json.dumps(directory[name_key])
    return json.dumps({"status": "Employee not found in directory."})


def run_autonomous_agent(query: str, max_iterations: int = 5):
    """
    Executes an autonomous agent loop:
    Loop:
      1. Model receives messages (History + System Prompt + Tools).
      2. If Model returns text without tool calls -> We are done! Return answer.
      3. If Model returns tool calls:
         a. Execute each tool.
         b. Append tool results to messages.
         c. Loop back to step 1.
    """
    print("\n" + "=" * 70)
    print(f"AGENT GOAL: {query}")
    print("=" * 70)

    llm = get_llm(temperature=0.0)
    tools = [get_stock_price, evaluate_math_expression, query_company_directory]
    tool_map = {t.name: t for t in tools}

    llm_with_tools = llm.bind_tools(tools)

    system_instruction = (
        "You are an autonomous executive research agent equipped with specific tools.\n"
        "Break down user questions into logical steps. Call appropriate tools when you need facts or exact calculations.\n"
        "When all necessary facts are gathered, synthesize a comprehensive, clear final answer."
    )

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=query)
    ]

    iteration = 1
    while iteration <= max_iterations:
        print(f"\n🧠 [Iteration {iteration} - Agent Reasoning...]")
        ai_response = llm_with_tools.invoke(messages)
        messages.append(ai_response)

        # Check if the agent wants to invoke tools
        if not ai_response.tool_calls:
            print("\n🎯 [Agent Decision: Task Complete! Synthesizing Final Answer]")
            final_text = extract_text(ai_response.content)
            print(f"\n{final_text}")
            return final_text

        print(f"🛠️ [Agent decided to invoke {len(ai_response.tool_calls)} tool(s)]:")
        for call in ai_response.tool_calls:
            tool_name = call["name"]
            tool_args = call["args"]
            print(f"   ▶ ACTION: Calling `{tool_name}` with args: {tool_args}")

            tool_fn = tool_map.get(tool_name)
            if tool_fn:
                output = tool_fn.invoke(tool_args)
            else:
                output = f"Error: Unknown tool '{tool_name}'"

            print(f"   👁️ OBSERVATION: {output}")

            messages.append(ToolMessage(
                content=str(output),
                tool_call_id=call["id"]
            ))

        iteration += 1

    print("⚠️ Agent reached maximum iterations without terminating.")
    return "Reached maximum iteration limit."


if __name__ == "__main__":
    print("\n🚀 Starting Example 08: Autonomous AI Agents")

    # Multi-step query: Requires (1) Looking up NVDA stock price, (2) Calculating total cost with tax
    multi_step_query = (
        "I want to purchase 15 shares of NVDA. "
        "Find the current stock price, and then calculate the total purchase cost "
        "assuming an additional 6.5% brokerage processing fee."
    )
    run_autonomous_agent(multi_step_query)

    print("\n" + "#" * 70)

    # Second query: Employee Directory lookup
    second_query = "Where is Dr. Evelyn Vasquez located, and what is her exact title?"
    run_autonomous_agent(second_query)

    print("\n✅ Example 08 completed successfully!\n")
