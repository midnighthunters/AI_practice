"""
================================================================================
EXAMPLE 04: Conversational Memory & Multi-Turn State
================================================================================
LLM APIs are fundamentally stateless: they remember nothing across requests.
Learn how LangChain manages multi-turn conversation memory:
1. `ChatMessageHistory`: In-memory storage for conversational turns.
2. `MessagesPlaceholder`: Dynamic placeholder in prompt templates for history.
3. `RunnableWithMessageHistory`: Associating distinct chat histories per session.
4. Demonstrating multi-turn context retention across successive queries.
================================================================================
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm, extract_text

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser


def demo_conversational_memory():
    print("\n" + "=" * 60)
    print("DEMO: Multi-Turn Memory with RunnableWithMessageHistory")
    print("=" * 60)

    llm = get_llm(temperature=0.2)
    parser = StrOutputParser()

    # Step 1: Define prompt template with MessagesPlaceholder for 'history'
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an intelligent virtual tutor. Answer the student's questions with high clarity and helpfulness."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    base_chain = prompt | llm | parser

    # Step 2: Global dictionary mapping session IDs to distinct conversation histories
    session_store = {}

    def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in session_store:
            session_store[session_id] = InMemoryChatMessageHistory()
        return session_store[session_id]

    # Step 3: Wrap base chain with RunnableWithMessageHistory
    conversational_chain = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    # Let's simulate a conversation across Session "Alice" and Session "Bob"
    print("\n--- Session 1: User 'Alice' ---")

    # Turn 1: Alice shares her background
    q1 = "Hello! My name is Alice, and I am learning Python to build data science pipelines for genomics."
    print(f"\n[Alice Turn 1]: {q1}")
    res1 = conversational_chain.invoke({"input": q1}, config={"configurable": {"session_id": "alice_session"}})
    print(f"[Assistant]: {res1}")

    # Turn 2: Alice asks a question that relies on context from Turn 1
    q2 = "What are the top 3 libraries I should install for my specific focus?"
    print(f"\n[Alice Turn 2]: {q2}")
    res2 = conversational_chain.invoke({"input": q2}, config={"configurable": {"session_id": "alice_session"}})
    print(f"[Assistant]: {res2}")

    # Turn 3: Alice asks for her name without stating it
    q3 = "Do you remember my name and what I am studying?"
    print(f"\n[Alice Turn 3]: {q3}")
    res3 = conversational_chain.invoke({"input": q3}, config={"configurable": {"session_id": "alice_session"}})
    print(f"[Assistant]: {res3}")

    # Verify session isolation: Bob starts his own session
    print("\n--- Session 2: User 'Bob' (Session Isolation) ---")
    q_bob = "What is my name?"
    print(f"\n[Bob Turn 1]: {q_bob}")
    res_bob = conversational_chain.invoke({"input": q_bob}, config={"configurable": {"session_id": "bob_session"}})
    print(f"[Assistant]: {res_bob}")

    # Inspect the stored history directly
    print("\n" + "=" * 60)
    print("INSPECTING STORED CHAT MESSAGES FOR ALICE:")
    print("=" * 60)
    alice_history = session_store["alice_session"]
    for i, msg in enumerate(alice_history.messages):
        role = "👤 USER" if msg.type == "human" else "🤖 AI"
        print(f"[{i + 1}] {role}: {extract_text(msg.content)[:80]}...")


if __name__ == "__main__":
    print("\n🚀 Starting Example 04: Conversational Memory")
    demo_conversational_memory()
    print("\n✅ Example 04 completed successfully!\n")
