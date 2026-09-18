"""
LangChain Interactive Educational Web Application
==================================================
Flask server powering an interactive web UI that demonstrates LangChain concepts:
- Prompts & Models (LCEL invocation)
- Output Parsers (Str, JSON, Pydantic)
- LCEL Chains (Sequential & Parallel)
- Conversational Memory (Session-based)
- Text Splitters & Chunking
- RAG Pipeline with Gemini Embeddings & VectorStore
- Tools & Function Calling
- Autonomous Agents with Step-by-Step Tracing
- Live Example Script Runner
"""

import os
import sys
import json
import time
import subprocess
from flask import Flask, jsonify, request, send_from_directory

# Ensure LangChain directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from config import get_llm, get_embeddings, extract_text, PRIMARY_MODEL, FAST_MODEL, EMBEDDING_MODEL

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List

app = Flask(__name__, static_folder="static", static_url_path="")

# --------------------------------------------------------------------------
# GLOBAL IN-MEMORY STORES
# --------------------------------------------------------------------------
SESSION_HISTORIES = {}
GLOBAL_VECTORSTORE = None

def init_vectorstore():
    global GLOBAL_VECTORSTORE
    if GLOBAL_VECTORSTORE is None:
        try:
            embeddings = get_embeddings()
            docs = [
                Document(
                    page_content="Project Chronos is the codename for our quantum-resistant encryption suite led by Dr. Evelyn Vasquez. Zero-knowledge audit scheduled for October 14, 2026.",
                    metadata={"title": "Project Chronos Architecture", "author": "Dr. Evelyn Vasquez"}
                ),
                Document(
                    page_content="Annual workstation stipend for remote employees is $1,850 payable in two equal installments via Concur code EXP-REMOTE-EQUIP.",
                    metadata={"title": "Workstation Stipend Policy", "author": "HR Department"}
                ),
                Document(
                    page_content="Under the 2026 Enterprise Service Agreement, customer refunds are guaranteed 100% within 45 days of invoice date, with a 15% restocking fee up to 90 days.",
                    metadata={"title": "Enterprise Refund Terms", "author": "Legal Department"}
                ),
                Document(
                    page_content="Arthur's favorite dessert is strictly gluten-free strawberry gelato due to severe peanut and wheat allergies. Chef Lorenzo prepares it on Fridays.",
                    metadata={"title": "Headquarters Amenities", "author": "Facilities & Dining"}
                )
            ]
            GLOBAL_VECTORSTORE = InMemoryVectorStore.from_documents(docs, embeddings)
        except Exception as e:
            print(f"Warning initializing vectorstore: {e}")

# --------------------------------------------------------------------------
# TOOLS DEFINITIONS
# --------------------------------------------------------------------------
@tool
def calculate_compound_interest(principal: float, annual_rate: float, years: int) -> float:
    """Calculates final compound interest amount: A = P * (1 + r)^t."""
    return round(principal * ((1 + annual_rate) ** years), 2)

@tool
def check_flight_status(flight_number: str) -> str:
    """Fetches real-time status and gate for a flight (e.g. BA-249, DL-104, LH-441)."""
    db = {
        "BA-249": {"status": "On Time", "departure": "14:30 GMT", "gate": "B22", "terminal": "5"},
        "DL-104": {"status": "Delayed (45 mins)", "departure": "16:15 EST", "gate": "A8", "terminal": "2"},
        "LH-441": {"status": "Boarding Now", "departure": "11:05 CET", "gate": "G14", "terminal": "1"}
    }
    key = flight_number.upper().strip()
    if key in db:
        f = db[key]
        return f"Flight {key}: {f['status']}, departing {f['departure']} from Terminal {f['terminal']}, Gate {f['gate']}."
    return f"Flight {key} not found in database."

@tool
def get_stock_price(ticker: str) -> str:
    """Looks up the latest simulated stock price for a company ticker (NVDA, AAPL, GOOGL, TSLA)."""
    prices = {
        "NVDA": 128.50, "AAPL": 224.20, "GOOGL": 178.90, "TSLA": 245.00
    }
    sym = ticker.upper().strip()
    if sym in prices:
        return json.dumps({"ticker": sym, "price": prices[sym], "currency": "USD"})
    return json.dumps({"error": f"Ticker '{sym}' not found."})

@tool
def evaluate_math(expression: str) -> str:
    """Safely calculates an arithmetic expression (e.g., '15 * 128.50 * 1.065')."""
    clean = "".join(c for c in expression if c in "0123456789+-*/.() ")
    try:
        return str(round(eval(clean, {"__builtins__": None}, {}), 4))
    except Exception as e:
        return f"Error: {e}"

TOOLS_REGISTRY = {
    "calculate_compound_interest": calculate_compound_interest,
    "check_flight_status": check_flight_status,
    "get_stock_price": get_stock_price,
    "evaluate_math": evaluate_math
}

# --------------------------------------------------------------------------
# ROUTES
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/info", methods=["GET"])
def get_info():
    return jsonify({
        "success": True,
        "primary_model": PRIMARY_MODEL,
        "fast_model": FAST_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "examples": [
            {"id": "01", "name": "01_chat_models_and_prompts.py", "title": "Models & Prompts"},
            {"id": "02", "name": "02_output_parsers.py", "title": "Output Parsers"},
            {"id": "03", "name": "03_lcel_expression_language.py", "title": "LCEL Expression Language"},
            {"id": "04", "name": "04_conversational_memory.py", "title": "Conversational Memory"},
            {"id": "05", "name": "05_text_splitters_and_chunking.py", "title": "Text Splitters"},
            {"id": "06", "name": "06_vectorstore_and_rag.py", "title": "Vector Stores & RAG"},
            {"id": "07", "name": "07_tools_and_function_calling.py", "title": "Tools & Function Calling"},
            {"id": "08", "name": "08_autonomous_agents.py", "title": "Autonomous Agents"}
        ]
    })

# 1. Models & Prompts
@app.route("/api/demo/prompt", methods=["POST"])
def demo_prompt():
    data = request.get_json() or {}
    system_text = data.get("system", "You are an expert technical teacher.")
    human_template = data.get("template", "Explain {topic} in {style} style.")
    variables = data.get("variables", {"topic": "LangChain LCEL", "style": "ELI5"})
    temp = float(data.get("temperature", 0.2))

    t0 = time.time()
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_text),
            ("human", human_template)
        ])
        llm = get_llm(temperature=temp)
        chain = prompt | llm | StrOutputParser()

        rendered_prompt = prompt.format_messages(**variables)
        result = chain.invoke(variables)
        latency = int((time.time() - t0) * 1000)

        return jsonify({
            "success": True,
            "rendered_messages": [{"role": m.type, "content": m.content} for m in rendered_prompt],
            "response": result,
            "latency_ms": latency
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 2. Output Parsers
class TechAnalysis(BaseModel):
    technology: str = Field(description="Name of tech")
    strengths: List[str] = Field(description="List of 2 strengths")
    primary_drawback: str = Field(description="1 key challenge")
    verdict: str = Field(description="One sentence verdict")

@app.route("/api/demo/parser", methods=["POST"])
def demo_parser():
    data = request.get_json() or {}
    parser_type = data.get("parser_type", "pydantic")
    topic = data.get("topic", "Vector Databases")

    t0 = time.time()
    try:
        llm = get_llm(temperature=0.0)
        if parser_type == "string":
            prompt = ChatPromptTemplate.from_template("Give 3 bullet point benefits of {topic}.")
            chain = prompt | llm | StrOutputParser()
            res = chain.invoke({"topic": topic})
            parsed_data = res
            raw_type = "str"
        elif parser_type == "json":
            parser = JsonOutputParser()
            prompt = PromptTemplate(
                template="Analyze {topic}.\n{format_instructions}\n",
                input_variables=["topic"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            chain = prompt | llm | parser
            parsed_data = chain.invoke({"topic": topic})
            raw_type = "dict (JSON)"
        else: # pydantic
            parser = PydanticOutputParser(pydantic_object=TechAnalysis)
            prompt = PromptTemplate(
                template="Analyze {topic}.\n{format_instructions}\n",
                input_variables=["topic"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            chain = prompt | llm | parser
            obj = chain.invoke({"topic": topic})
            parsed_data = obj.model_dump()
            raw_type = "Pydantic (TechAnalysis)"

        return jsonify({
            "success": True,
            "parser_type": parser_type,
            "parsed_type": raw_type,
            "data": parsed_data,
            "latency_ms": int((time.time() - t0) * 1000)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3. LCEL Chains (Sequential & Parallel)
@app.route("/api/demo/chains", methods=["POST"])
def demo_chains():
    data = request.get_json() or {}
    text = data.get("text", "Our AI robotics startup raised $12M to automate fruit harvesting in vertical farms.")
    mode = data.get("mode", "parallel")

    t0 = time.time()
    try:
        llm = get_llm(temperature=0.2)
        parser = StrOutputParser()

        if mode == "parallel":
            chain_summary = ChatPromptTemplate.from_template("Summarize in 1 short sentence:\n{text}") | llm | parser
            chain_sentiment = ChatPromptTemplate.from_template("Classify sentiment (Positive/Neutral/Negative) and tone in 3 words:\n{text}") | llm | parser
            chain_keywords = ChatPromptTemplate.from_template("Extract 3 comma-separated core technical keywords:\n{text}") | llm | parser

            parallel_chain = RunnableParallel(
                summary=chain_summary,
                sentiment=chain_sentiment,
                keywords=chain_keywords,
                char_count=RunnableLambda(lambda x: len(x["text"]))
            )
            result = parallel_chain.invoke({"text": text})
        else: # sequential
            prompt_critique = ChatPromptTemplate.from_template("Critique this business proposal in 2 bullet points:\n{text}") | llm | parser
            prompt_pitch = ChatPromptTemplate.from_template("Based on this critique:\n{critique}\nWrite a revised 1-sentence elevator pitch.") | llm | parser

            seq_chain = (
                {"text": RunnablePassthrough()}
                | RunnablePassthrough.assign(critique=prompt_critique)
                | RunnablePassthrough.assign(revised_pitch=prompt_pitch)
            )
            result = seq_chain.invoke(text)

        return jsonify({
            "success": True,
            "mode": mode,
            "result": result,
            "latency_ms": int((time.time() - t0) * 1000)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 4. Memory & Chat History
@app.route("/api/demo/memory", methods=["POST"])
def demo_memory():
    data = request.get_json() or {}
    session_id = data.get("session_id", "user_1")
    message = data.get("message", "Hello, my name is Alex and I specialize in Kubernetes.")
    reset = data.get("reset", False)

    if reset and session_id in SESSION_HISTORIES:
        SESSION_HISTORIES[session_id].clear()
        return jsonify({"success": True, "message": f"Session {session_id} reset.", "history": []})

    if session_id not in SESSION_HISTORIES:
        SESSION_HISTORIES[session_id] = InMemoryChatMessageHistory()

    history = SESSION_HISTORIES[session_id]
    t0 = time.time()
    try:
        llm = get_llm(temperature=0.2)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a friendly, helpful assistant. Maintain conversational context accurately."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        chain = RunnableWithMessageHistory(
            prompt | llm | StrOutputParser(),
            lambda s: SESSION_HISTORIES[s],
            input_messages_key="input",
            history_messages_key="history"
        )

        reply = chain.invoke({"input": message}, config={"configurable": {"session_id": session_id}})

        # Extract history list
        history_list = []
        for m in history.messages:
            history_list.append({"role": m.type, "text": extract_text(m.content)})

        return jsonify({
            "success": True,
            "session_id": session_id,
            "reply": reply,
            "history": history_list,
            "latency_ms": int((time.time() - t0) * 1000)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 5. Text Splitters
@app.route("/api/demo/splitters", methods=["POST"])
def demo_splitters():
    data = request.get_json() or {}
    text = data.get("text", "")
    chunk_size = int(data.get("chunk_size", 200))
    chunk_overlap = int(data.get("chunk_overlap", 40))

    if not text:
        text = (
            "LangChain is a framework for developing applications powered by language models. "
            "It enables applications that are context-aware and reason autonomously.\n\n"
            "The main value props of LangChain are: 1. Components (abstractions for working with LLMs), "
            "2. Off-the-shelf chains (structured assemblies of components for accomplishing specific tasks).\n\n"
            "Retrieval Augmented Generation (RAG) is one of the most popular patterns in LangChain, "
            "connecting private external documents into the prompt dynamically."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = splitter.split_text(text)
    chunk_data = []
    for i, c in enumerate(chunks):
        chunk_data.append({
            "index": i + 1,
            "chars": len(c),
            "text": c
        })

    return jsonify({
        "success": True,
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "chunks": chunk_data
    })

# 6. RAG Pipeline
@app.route("/api/demo/rag", methods=["POST"])
def demo_rag():
    init_vectorstore()
    data = request.get_json() or {}
    question = data.get("question", "What is the remote workstation stipend amount and code?")

    t0 = time.time()
    try:
        llm = get_llm(temperature=0.0)

        # 1. Non-RAG
        ans_vanilla = extract_text(llm.invoke(f"Answer concisely: {question}").content)

        # 2. RAG
        retriever = GLOBAL_VECTORSTORE.as_retriever(search_kwargs={"k": 2})
        retrieved_docs = retriever.invoke(question)

        context_str = "\n\n".join([f"[{d.metadata.get('title')}]: {d.page_content}" for d in retrieved_docs])

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer ONLY using the provided context. If unsure, say 'Not found'. Cite the source title.\nContext:\n{context}"),
            ("human", "{question}")
        ])

        rag_chain = rag_prompt | llm | StrOutputParser()
        ans_rag = rag_chain.invoke({"context": context_str, "question": question})

        return jsonify({
            "success": True,
            "question": question,
            "without_rag": ans_vanilla,
            "with_rag": ans_rag,
            "retrieved_docs": [{"title": d.metadata.get("title"), "content": d.page_content} for d in retrieved_docs],
            "latency_ms": int((time.time() - t0) * 1000)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 7. Tools
@app.route("/api/demo/tools", methods=["POST"])
def demo_tools():
    data = request.get_json() or {}
    tool_name = data.get("tool", "check_flight_status")
    args = data.get("args", {"flight_number": "BA-249"})

    if tool_name not in TOOLS_REGISTRY:
        return jsonify({"success": False, "error": f"Unknown tool {tool_name}"}), 400

    try:
        t_func = TOOLS_REGISTRY[tool_name]
        result = t_func.invoke(args)
        return jsonify({
            "success": True,
            "tool": tool_name,
            "args": args,
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 8. Autonomous Agent
@app.route("/api/demo/agent", methods=["POST"])
def demo_agent():
    data = request.get_json() or {}
    goal = data.get("goal", "Find the current stock price of NVDA, then calculate the total cost for 12 shares with 8% sales tax.")

    t0 = time.time()
    steps_log = []
    try:
        llm = get_llm(temperature=0.0)
        tools = [get_stock_price, evaluate_math, check_flight_status, calculate_compound_interest]
        tool_map = {t.name: t for t in tools}
        llm_with_tools = llm.bind_tools(tools)

        messages = [
            SystemMessage(content="You are an autonomous research and math agent. Use tools as needed to gather facts and calculate. Synthesize final answer when done."),
            HumanMessage(content=goal)
        ]

        final_answer = ""
        for step_idx in range(1, 6):
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            if not ai_msg.tool_calls:
                final_answer = extract_text(ai_msg.content)
                steps_log.append({
                    "step": step_idx,
                    "type": "finish",
                    "thought": "All information collected. Synthesizing final answer.",
                    "final_answer": final_answer
                })
                break

            step_calls = []
            for call in ai_msg.tool_calls:
                t_name = call["name"]
                t_args = call["args"]
                t_fn = tool_map.get(t_name)
                t_res = t_fn.invoke(t_args) if t_fn else "Error"

                messages.append(ToolMessage(content=str(t_res), tool_call_id=call["id"]))
                step_calls.append({
                    "tool": t_name,
                    "args": t_args,
                    "observation": str(t_res)
                })

            steps_log.append({
                "step": step_idx,
                "type": "action",
                "thought": f"Calling {len(step_calls)} tool(s) to gather data.",
                "actions": step_calls
            })

        return jsonify({
            "success": True,
            "goal": goal,
            "final_answer": final_answer or "Finished reasoning loop.",
            "steps": steps_log,
            "total_steps": len(steps_log),
            "latency_ms": int((time.time() - t0) * 1000)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 9. Script Runner
@app.route("/api/run-example/<filename>", methods=["POST"])
def run_example_script(filename):
    allowed_scripts = {
        "01": "01_chat_models_and_prompts.py",
        "02": "02_output_parsers.py",
        "03": "03_lcel_expression_language.py",
        "04": "04_conversational_memory.py",
        "05": "05_text_splitters_and_chunking.py",
        "06": "06_vectorstore_and_rag.py",
        "07": "07_tools_and_function_calling.py",
        "08": "08_autonomous_agents.py"
    }

    script_to_run = None
    for k, v in allowed_scripts.items():
        if filename in (k, v):
            script_to_run = v
            break

    if not script_to_run:
        return jsonify({"success": False, "error": "Invalid script name."}), 400

    script_path = os.path.join(BASE_DIR, "examples", script_to_run)
    if not os.path.exists(script_path):
        return jsonify({"success": False, "error": f"Script {script_to_run} not found."}), 404

    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "-u", script_path],
            capture_output=True,
            text=True,
            timeout=40,
            cwd=os.path.dirname(script_path)
        )
        latency = int((time.time() - t0) * 1000)
        output = proc.stdout + ("\nSTDERR:\n" + proc.stderr if proc.stderr else "")

        return jsonify({
            "success": proc.returncode == 0,
            "script": script_to_run,
            "returncode": proc.returncode,
            "output": output,
            "latency_ms": latency
        })
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Script execution timed out (40s limit)."}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/get-code/<filename>", methods=["GET"])
def get_example_code(filename):
    examples_dir = os.path.join(BASE_DIR, "examples")
    target = os.path.join(examples_dir, filename)
    if not os.path.exists(target) or not filename.endswith(".py"):
        return jsonify({"success": False, "error": "File not found"}), 404
    with open(target, "r", encoding="utf-8") as f:
        code = f.read()
    return jsonify({"success": True, "filename": filename, "code": code})


if __name__ == "__main__":
    init_vectorstore()
    port = int(os.environ.get("PORT", 5001))
    print(f"\n========================================================")
    print(f"🦜🔗 LangChain Interactive Explainer running at:")
    print(f"👉 http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
