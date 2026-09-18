"""
================================================================================
EXAMPLE 01: Chat Models & Prompt Templates
================================================================================
Learn the fundamentals of LangChain:
1. How LangChain abstracts LLMs into unified ChatModel interfaces.
2. Using typed messages: SystemMessage (instructions) & HumanMessage (input).
3. Creating reusable prompt templates with `ChatPromptTemplate`.
4. Streaming responses token-by-token in real time.
================================================================================
"""

import sys
import os
import time

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm, extract_text

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate


def demo_direct_messages():
    print("\n" + "=" * 60)
    print("PART 1: Direct Invocation with Typed Messages")
    print("=" * 60)

    llm = get_llm(temperature=0.3)

    # In LangChain, conversations are structured into standard message types:
    # - SystemMessage: Tells the model WHO it is and HOW it should behave.
    # - HumanMessage: The prompt or question from the end user.
    # - AIMessage: The assistant's response (used in memory/history).
    messages = [
        SystemMessage(content="You are a witty, concise tech professor who explains complex concepts in 2 sentences with an emoji."),
        HumanMessage(content="What is LangChain and why do developers use it?")
    ]

    print("\n[Input Messages]:")
    for msg in messages:
        print(f" - {msg.type.upper()}: {msg.content}")

    print("\n[Calling Gemini via LangChain...]")
    response = llm.invoke(messages)
    clean_text = extract_text(response.content)

    print(f"\n[Gemini Response]:\n{clean_text}")


def demo_chat_prompt_template():
    print("\n" + "=" * 60)
    print("PART 2: ChatPromptTemplate (Parameterized Prompts)")
    print("=" * 60)

    llm = get_llm(temperature=0.2)

    # Instead of hardcoding text or doing f-string manual formatting,
    # LangChain provides ChatPromptTemplate for reusability, safety, and validation.
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert software architect. Provide 3 core pros and 1 con of using {technology} for {use_case}. Format as concise bullet points."),
        ("human", "Analyze {technology} for {use_case}.")
    ])

    print(f"\n[Template Input Variables]: {template.input_variables}")

    # Format the prompt with concrete parameters
    variables = {
        "technology": "LangChain",
        "use_case": "enterprise document question-answering"
    }
    print(f"[Parameters]: {variables}")

    formatted_messages = template.format_messages(**variables)
    print(f"\n[Rendered System Prompt]: {formatted_messages[0].content}")
    print(f"[Rendered Human Prompt]: {formatted_messages[1].content}")

    print("\n[Invoking LLM with formatted template...]")
    response = llm.invoke(formatted_messages)
    print(f"\n[Gemini Response]:\n{extract_text(response.content)}")


def demo_streaming():
    print("\n" + "=" * 60)
    print("PART 3: Streaming Tokens in Real Time")
    print("=" * 60)

    llm = get_llm(temperature=0.7)
    prompt = "Explain in 3 short bullet points what makes LLM agents different from standard chatbots."

    print(f"\n[Prompt]: {prompt}\n")
    print("[Live Stream Output]: ", end="", flush=True)

    # Streaming allows outputting tokens as soon as the model generates them
    try:
        for chunk in llm.stream(prompt):
            chunk_text = extract_text(chunk.content)
            print(chunk_text, end="", flush=True)
            time.sleep(0.02)
        print("\n")
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print("\n[Notice]: Gemini free-tier rate limit (20 req/min) reached. Wait a few seconds between requests.")
        else:
            print(f"\n[Stream Error]: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Example 01: Chat Models & Prompts")
    demo_direct_messages()
    demo_chat_prompt_template()
    demo_streaming()
    print("\n✅ Example 01 completed successfully!\n")
