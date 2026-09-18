"""
================================================================================
EXAMPLE 03: LCEL (LangChain Expression Language) Deep Dive
================================================================================
LCEL is the foundational composability standard in modern LangChain:
1. The Pipe Operator (`|`): Clean Unix-style declarative pipelines.
2. `RunnableSequence`: Passing outputs sequentially across chains.
3. `RunnableParallel`: Executing multiple branches concurrently on the same input.
4. `RunnableLambda`: Integrating custom pure Python functions into chains seamlessly.
================================================================================
"""

import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_llm

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda


def demo_sequential_pipeline():
    print("\n" + "=" * 60)
    print("PART 1: Sequential Chain (Output of Chain 1 -> Input of Chain 2)")
    print("=" * 60)

    llm = get_llm(temperature=0.7)
    parser = StrOutputParser()

    # Step 1: Generate a catchy startup business idea based on an industry
    prompt_idea = ChatPromptTemplate.from_template(
        "Generate a creative, one-sentence startup product idea in the {industry} space. Only return the idea."
    )
    chain_idea = prompt_idea | llm | parser

    # Step 2: Take that product idea and generate a punchy 3-word marketing tagline
    prompt_tagline = ChatPromptTemplate.from_template(
        "Here is a startup product idea:\n'{product_idea}'\nCreate a memorable 3-word marketing slogan or tagline for it. Output only the 3 words."
    )
    chain_tagline = prompt_tagline | llm | parser

    # Combine into a composite pipeline using dictionary mapping
    overall_pipeline = (
        {"product_idea": chain_idea}
        | RunnablePassthrough.assign(tagline=chain_tagline)
    )

    industry = "sustainable urban agriculture"
    print(f"[Industry Input]: {industry}")
    print("\n[Executing Sequential Pipeline...]")
    t0 = time.time()
    result = overall_pipeline.invoke({"industry": industry})
    elapsed = time.time() - t0

    print(f"\n[Generated Idea]: {result['product_idea']}")
    print(f"[Generated Tagline]: {result['tagline']}")
    print(f"[Elapsed Time]: {elapsed:.2f}s")


def demo_parallel_execution():
    print("\n" + "=" * 60)
    print("PART 2: RunnableParallel (Concurrent Branching)")
    print("=" * 60)

    llm = get_llm(temperature=0.2)
    parser = StrOutputParser()

    # Branch A: Summarizer
    summary_prompt = ChatPromptTemplate.from_template("Summarize in 1 concise sentence:\n{text}")
    summary_chain = summary_prompt | llm | parser

    # Branch B: Tone & Sentiment Analyzer
    tone_prompt = ChatPromptTemplate.from_template("Determine the emotional tone and sentiment of this text in 2-3 words:\n{text}")
    tone_chain = tone_prompt | llm | parser

    # Branch C: Target Audience Extractor
    audience_prompt = ChatPromptTemplate.from_template("Identify who the primary target audience is for this message in 3-5 words:\n{text}")
    audience_chain = audience_prompt | llm | parser

    # Combine all 3 chains into a parallel runnable
    parallel_analysis = RunnableParallel(
        summary=summary_chain,
        tone=tone_chain,
        audience=audience_chain,
        original_length=RunnableLambda(lambda x: len(x["text"]))
    )

    sample_article = (
        "We are thrilled to announce the launch of our zero-emission commercial drone delivery fleet. "
        "Beginning this November, enterprise clients can deliver temperature-sensitive pharmaceuticals "
        "across remote regional healthcare facilities in under 30 minutes, reducing cold-chain spoilage by 94%."
    )

    print(f"[Input Text]:\n'{sample_article}'\n")
    print("[Executing 3 chains concurrently with RunnableParallel...]")
    t0 = time.time()
    results = parallel_analysis.invoke({"text": sample_article})
    elapsed = time.time() - t0

    print("\n[Parallel Analysis Results]:")
    print(f" - Summary: {results['summary']}")
    print(f" - Tone: {results['tone']}")
    print(f" - Audience: {results['audience']}")
    print(f" - Original Character Count: {results['original_length']}")
    print(f"[Total Elapsed Time]: {elapsed:.2f}s (Ran branches concurrently)")


def demo_custom_python_lambda():
    print("\n" + "=" * 60)
    print("PART 3: RunnableLambda (Injecting Pure Python Logic into LCEL)")
    print("=" * 60)

    llm = get_llm(temperature=0.0)
    parser = StrOutputParser()

    # Custom Python preprocessing function
    def sanitize_input(data: dict) -> dict:
        raw_code = data.get("code", "")
        clean_code = raw_code.strip()
        return {"code": clean_code, "line_count": len(clean_code.splitlines())}

    # Custom Python postprocessing function
    def format_banner(text: str) -> str:
        return f"*** CODE REVIEW REPORT ***\n{text}\n*** END REPORT ***"

    prompt = ChatPromptTemplate.from_template(
        "Analyze this Python snippet ({line_count} lines). Suggest 1 optimization:\n```python\n{code}\n```"
    )

    # LCEL pipeline mixing Python functions and LLMs
    chain = (
        RunnableLambda(sanitize_input)
        | prompt
        | llm
        | parser
        | RunnableLambda(format_banner)
    )

    snippet = """
    def find_duplicates(numbers):
        duplicates = []
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                if numbers[i] == numbers[j] and numbers[i] not in duplicates:
                    duplicates.append(numbers[i])
        return duplicates
    """

    print("[Input Python Snippet (O(n^2) duplicate finder)]")
    result = chain.invoke({"code": snippet})
    print(f"\n{result}")


if __name__ == "__main__":
    print("\n🚀 Starting Example 03: LCEL Expression Language")
    demo_sequential_pipeline()
    demo_parallel_execution()
    demo_custom_python_lambda()
    print("\n✅ Example 03 completed successfully!\n")
