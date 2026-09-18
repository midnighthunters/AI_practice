# 🚀 AI Engineering Practice & Mastery Suite

Welcome to the AI Engineering learning workspace. This repository contains four comprehensive, interactive, production-ready modules powered by the **Google Gemini API**:

```
takeaway/
├── RAG/                    # 🧠 Interactive RAG Explainer & Grounding Architecture
│   ├── app.py              # Flask Web App (Port 5000)
│   ├── rag_engine.py       # Core TF-IDF, HyDE & Grounding Audit Engine
│   ├── sample_docs.json    # Private Knowledge Base
│   ├── static/             # Visual RAG Interface
│   └── README.md           # RAG Architecture Deep Dive
│
├── LangChain/              # 🦜🔗 LangChain Interactive Mastery Suite
│   ├── app.py              # Flask Web App (Port 5001)
│   ├── config.py           # Gemini API & LCEL Model Factories
│   ├── examples/           # Standalone Runnable Python Tutorials
│   ├── static/             # Interactive Mastery Dashboard
│   ├── test_langchain.py   # Test Suite
│   └── README.md           # LangChain Concepts & LCEL Guide
│
├── Langgraph/              # 🕸️ LangGraph Multi-Agent Studio & Stateful Graphs
│   ├── app.py              # Visual Graph Studio (Port 5002)
│   ├── gemini_client.py    # Structured Gemini Client
│   ├── 01-09 examples      # State reducers, loops, HITL & supervisor patterns
│   ├── static/             # Graph Visualizer Web Interface
│   ├── test_langgraph.py   # LangGraph Test Suite
│   └── README.md           # LangGraph StateGraph Deep Dive
│
└── n8n/                    # ⚡ Production AI Workflow Automation
    ├── docker-compose.yml  # Real n8n Self-Hosting Setup
    ├── simulator/          # Standalone Python-based n8n Web Simulator (Port 5678)
    ├── workflows/          # Production n8n JSON Workflows (cURL, RAG, Triage, Agent)
    ├── test_n8n_integration.py # Workflow Integration Test Suite
    └── README.md           # n8n Comprehensive Engineering Guide
```

---

## 🧭 How to Explore Each Module

### 1. 🧠 The RAG Explainer (`RAG/`)
Understand the low-level mechanics of Retrieval-Augmented Generation:
- How similarity search retrieves private chunks.
- How prompts are augmented with grounding rules.
- How Naive RAG compares with Advanced RAG (HyDE query expansion, Cross-Encoder re-ranking, and Self-RAG grounding audits).

```bash
cd RAG
python app.py
# Opens at: http://127.0.0.1:5000
```

### 2. 🦜🔗 The LangChain Mastery Suite (`LangChain/`)
Understand how enterprise AI applications are engineered with LangChain and LCEL:
- **Models & Prompts**: `ChatGoogleGenerativeAI`, `ChatPromptTemplate`, streaming.
- **Output Parsers**: Extracting clean strings, JSON dictionaries, and typed Pydantic models.
- **LCEL Expression Language**: The `|` pipe operator, `RunnableSequence`, and `RunnableParallel`.
- **Conversational Memory**: Managing multi-turn state per session.
- **Text Splitters**: Chunking documents with overlap.
- **LangChain RAG**: 5-line RAG with `InMemoryVectorStore` and `GoogleGenerativeAIEmbeddings`.
- **Tools & Function Calling**: Binding Python functions to Gemini.
- **Autonomous Agents**: ReAct loops reasoning across multiple tools dynamically.

```bash
cd LangChain
python app.py
# Opens at: http://127.0.0.1:5001
```

### 3. 🕸️ The LangGraph Studio (`Langgraph/`)
Master stateful, cyclical multi-agent graphs:
- **Cyclic Agent Loops**: ReAct loops with retry logic and error correction.
- **State Reducers**: TypedDict state with custom operator reducers.
- **Conditional Routing**: Dynamic path decision trees.
- **Human-in-the-Loop (HITL)**: Safe breakpoints and interruption approval before tool execution.
- **Multi-Agent Supervisor**: Orchestrator-worker patterns.

```bash
cd Langgraph
python app.py
# Opens at: http://127.0.0.1:5002
```

### 4. ⚡ n8n Workflow Automation (`n8n/`)
Build visual, low-code AI workflows and production pipelines:
- **Visual AI Pipelines**: Connect webhooks, databases, and Gemini AI visually.
- **Offline Simulator**: Test n8n workflows locally without Docker via the Python simulator.
- **Production Workflows**: Pre-configured workflows for triage, RAG, and agentic tool-use.

```bash
cd n8n
python simulator/server.py
# Opens at: http://127.0.0.1:5678
```
