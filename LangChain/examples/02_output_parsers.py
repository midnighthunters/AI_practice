"""
================================================================================
EXAMPLE 02: Output Parsers (Structured & Reliable Data)
================================================================================
Learn how LangChain turns unpredictable, free-form LLM text into reliable,
strongly-typed data structures for backend code:
1. `StrOutputParser`: Simple string extraction.
2. `JsonOutputParser`: Direct Python dictionary extraction.
3. `PydanticOutputParser`: Enforcing strict schema validation using Pydantic.
================================================================================
"""

import sys
import os
from typing import List
from pydantic import BaseModel, Field

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser, PydanticOutputParser


def demo_string_output_parser():
    print("\n" + "=" * 60)
    print("PART 1: StrOutputParser (Clean Text Extraction)")
    print("=" * 60)

    llm = get_llm(temperature=0.0)

    # Without StrOutputParser, llm.invoke returns an AIMessage or complex object.
    # With StrOutputParser in the chain (prompt | llm | parser), the output is a pure str!
    prompt = ChatPromptTemplate.from_template("Give 3 punchy keywords for {subject}.")
    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({"subject": "Quantum Computing"})
    print(f"[Input Subject]: Quantum Computing")
    print(f"[Parsed Output (type={type(result).__name__})]:\n{result}")


def demo_json_output_parser():
    print("\n" + "=" * 60)
    print("PART 2: JsonOutputParser (Python Dict Extraction)")
    print("=" * 60)

    llm = get_llm(temperature=0.1)
    parser = JsonOutputParser()

    # JsonOutputParser generates schema instructions that guide the LLM to output valid JSON
    prompt = PromptTemplate(
        template="Analyze the following product review.\n{format_instructions}\nReview: {review}\n",
        input_variables=["review"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    print("\n[Automatically Injected Format Instructions]:")
    print(parser.get_format_instructions()[:180] + "...")

    chain = prompt | llm | parser

    sample_review = "I bought the UltraClean vacuum last week. It has incredible suction power and is very quiet, but the battery lasts only 20 minutes."
    result = chain.invoke({"review": sample_review})

    print(f"\n[Parsed Output Object (type={type(result).__name__})]:")
    print(result)
    print(f"[Accessing Fields Directly in Python]:")
    for key, value in result.items():
        print(f" - {key}: {value}")


# Define a strict Pydantic model
class BookRecommendation(BaseModel):
    title: str = Field(description="Title of the recommended book")
    author: str = Field(description="Author of the book")
    year_published: int = Field(description="Year first published")
    key_themes: List[str] = Field(description="List of 2-3 main themes covered")
    why_read: str = Field(description="One compelling sentence why this book is worth reading")


def demo_pydantic_output_parser():
    print("\n" + "=" * 60)
    print("PART 3: PydanticOutputParser (Type-Safe Validation)")
    print("=" * 60)

    llm = get_llm(temperature=0.1)
    parser = PydanticOutputParser(pydantic_object=BookRecommendation)

    prompt = PromptTemplate(
        template="Recommend a seminal book on the topic: {topic}.\n{format_instructions}\n",
        input_variables=["topic"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    topic = "Distributed Systems & Cloud Architecture"
    print(f"[Topic]: {topic}")
    print("[Querying Gemini and parsing into Pydantic model...]")

    try:
        book: BookRecommendation = chain.invoke({"topic": topic})
        print("\n✅ Successfully validated into BookRecommendation Pydantic Object:")
        print(f" - Title: {book.title}")
        print(f" - Author: {book.author}")
        print(f" - Year: {book.year_published}")
        print(f" - Themes: {', '.join(book.key_themes)}")
        print(f" - Pitch: {book.why_read}")
        print(f"\n[Raw Object Dump]: {book.model_dump()}")
    except Exception as e:
        print(f"Parsing error: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Example 02: Output Parsers")
    demo_string_output_parser()
    demo_json_output_parser()
    demo_pydantic_output_parser()
    print("\n✅ Example 02 completed successfully!\n")
