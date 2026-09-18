"""
================================================================================
EXAMPLE 06: Vector Stores & LCEL RAG Pipeline
================================================================================
See how LangChain transforms an entire Retrieval-Augmented Generation (RAG)
architecture into just a few declarative lines using LCEL:
1. `GoogleGenerativeAIEmbeddings`: Generating dense 3072-dimension vectors.
2. `InMemoryVectorStore`: Storing and indexing chunk embeddings.
3. Building an LCEL RAG Chain:
   `{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | parser`
4. Comparing Gemini's response with RAG vs. without RAG.
================================================================================
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm, get_embeddings, extract_text

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# Sample proprietary knowledge base (simulating internal corporate records)
PROPRIETARY_KNOWLEDGE_DOCS = [
    Document(
        page_content="Project Chronos is the codename for our next-generation quantum-resistant encryption suite. Lead architect Dr. Evelyn Vasquez scheduled the zero-knowledge audit for October 14, 2026. Internal repo is git@sec.internal:chronos-crypto.git.",
        metadata={"title": "Project Chronos Architecture", "author": "Evelyn Vasquez", "classification": "Confidential"}
    ),
    Document(
        page_content="All employees receive an annual remote-work workstation stipend of $1,850 payable in two equal installments. Expense claims must be submitted through Concur under code EXP-REMOTE-EQUIP.",
        metadata={"title": "Employee Benefits 2026", "author": "HR Operations", "classification": "Internal"}
    ),
    Document(
        page_content="The cafeteria on Level 3 serves artisan espresso roasted by Blue Mountain Coffee Co. Friday special is Sicilian cannoli prepared by Chef Lorenzo. Arthur's favorite dessert is strictly gluten-free strawberry gelato due to severe peanut and wheat allergies.",
        metadata={"title": "Headquarters Amenities", "author": "Facilities", "classification": "Public"}
    ),
    Document(
        page_content="Under the 2026 Enterprise Service Agreement, customer contract refunds are guaranteed at 100% full refund within 45 days of invoice date, after which a 15% administrative restocking deduction applies up to 90 days.",
        metadata={"title": "Enterprise Refund Terms", "author": "Legal", "classification": "Internal"}
    )
]


def format_docs(docs):
    """Formats retrieved Document objects into a clean, numbered context string with citations."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("title", "Unknown Source")
        formatted.append(f"[Source {i}: {source}]\n{doc.page_content}")
    return "\n\n".join(formatted)


def run_rag_demonstration():
    print("\n" + "=" * 60)
    print("STEP 1: Initializing Embeddings & In-Memory Vector Store")
    print("=" * 60)

    embeddings = get_embeddings()
    llm = get_llm(temperature=0.0)

    print("[Indexing proprietary documents into InMemoryVectorStore...]")
    vectorstore = InMemoryVectorStore.from_documents(
        documents=PROPRIETARY_KNOWLEDGE_DOCS,
        embedding=embeddings
    )
    print(f"✅ Indexed {len(PROPRIETARY_KNOWLEDGE_DOCS)} documents into semantic vector space.")

    # Convert the vector store into a LangChain Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    print("\n" + "=" * 60)
    print("STEP 2: Constructing the Modern LCEL RAG Chain")
    print("=" * 60)

    # In LangChain LCEL, the standard RAG chain pattern is:
    # 1. RunnablePassthrough allows the user's question to pass through unchanged.
    # 2. retriever | format_docs automatically fetches the top-k chunks and formats them.
    # 3. Both are injected into the prompt template.
    # 4. The formatted prompt flows into the LLM.
    # 5. StrOutputParser returns the finalized answer string.

    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant for internal corporate inquiries.\n"
            "Use ONLY the following retrieved context to answer the question.\n"
            "If the answer cannot be found in the context, say 'I cannot find that in the provided documents.'\n"
            "Cite the source document title when providing facts.\n\n"
            "Retrieved Context:\n{context}"
        )),
        ("human", "{question}")
    ])

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    # Test Query 1: Information contained in private documents
    test_queries = [
        "What is the remote-work equipment stipend amount, and what is the Concur code?",
        "When is the zero-knowledge audit for Project Chronos and who is leading it?",
        "What is Arthur's favorite dessert and why?"
    ]

    for q in test_queries:
        print("\n" + "-" * 60)
        print(f"QUESTION: {q}")
        print("-" * 60)

        try:
            # First: Ask Gemini WITHOUT RAG
            vanilla_prompt = f"Answer concisely: {q}"
            vanilla_ans = extract_text(llm.invoke(vanilla_prompt).content)
            print(f"\n❌ [Gemini WITHOUT RAG (Pure Knowledge Cutoff)]:\n{vanilla_ans}")

            # Second: Ask Gemini WITH LangChain RAG
            rag_ans = rag_chain.invoke(q)
            print(f"\n✅ [Gemini WITH LangChain RAG (Grounded in Private Facts)]:\n{rag_ans}")
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"\n[Rate Limit]: Free tier quota reached for this minute. Please wait 20s before next query.")
            else:
                print(f"\n[Query Error]: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Example 06: Vector Stores & LCEL RAG")
    run_rag_demonstration()
    print("\n✅ Example 06 completed successfully!\n")
