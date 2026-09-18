# 🚀 AI Engineering Practice & Flagship Enterprise Suite

Welcome to the AI Engineering learning & production workspace. This repository features **AegisOps**—an enterprise-grade autonomous multi-agent incident commander platform—alongside seven in-depth learning & mastery modules powered by modern AI engineering standards:

```
takeaway/
├── AegisOps/               # 🛡️ FLAGSHIP: Autonomous Multi-Agent SRE & Incident Commander (Port 5006)
│   ├── app.py              # Mission Control Dashboard & Live HTML5 Canvas Topology
│   ├── orchestrator.py     # 5-Agent Swarm Orchestrator (Triage, RCA, Sec, Remediation, PostMortem)
│   ├── graph_topology.py   # GraphRAG Microservice Topology & Blast Radius Engine
│   ├── mcp_sre_server.py   # Model Context Protocol (MCP) SRE Tooling & Telemetry
│   ├── guardrails_engine.py# Threat Defense Firewall, PII Masking & Semantic Cache
│   ├── test_aegisops.py    # Automated Chaos & Reliability Test Suite
│   └── README.md           # Architecture Deep Dive & Resume Talking Points
│
├── RAG/                    # 🧠 Interactive RAG Explainer & Grounding Architecture (Port 5000)
│   ├── app.py              # Flask Web App
│   ├── rag_engine.py       # Core TF-IDF, HyDE & Grounding Audit Engine
│   └── README.md           # RAG Architecture Deep Dive
│
├── LangChain/              # 🦜🔗 LangChain Interactive Mastery Suite (Port 5001)
│   ├── app.py              # Flask Web App
│   ├── examples/           # 8 Standalone Runnable Python Tutorials
│   └── README.md           # LangChain Concepts & LCEL Guide
│
├── Langgraph/              # 🕸️ LangGraph Multi-Agent Studio & Stateful Graphs (Port 5002)
│   ├── app.py              # Visual Graph Studio
│   ├── 01-09 examples      # State reducers, loops, HITL & supervisor patterns
│   └── README.md           # LangGraph StateGraph Deep Dive
│
├── MCP/                    # 🔌 Model Context Protocol (MCP) Suite (Port 5003)
│   ├── app.py              # Interactive MCP Web Inspector & Agent Studio
│   ├── 01-05 tutorials     # Framing, Resources, Tools, Prompts, Client Agent
│   ├── mcp_core.py         # Unified In-Memory MCP Server (JSON-RPC 2.0)
│   └── README.md           # MCP Architecture & Specification Guide
│
├── Evals_and_Guardrails/   # 🛡️ Production Evals, Safety & Semantic Cache (Port 5004)
│   ├── app.py              # Interactive Eval & Guardrail Playground
│   ├── 01-05 tutorials     # LLM Judge, RAG Triad, In/Out Guardrails, Cache
│   ├── evals_core.py       # Quality Rubrics, TruLens Triad, Firewall & Cache
│   └── README.md           # Production AI Reliability & Safety Guide
│
├── GraphRAG/               # 🕸️ Knowledge Graphs & Multi-Hop Reasoning (Port 5005)
│   ├── app.py              # Canvas Visual Graph Explorer & Hybrid Query Engine
│   ├── 01-04 tutorials     # NER & Triplet Extraction, Graph Builder, Traversal
│   ├── graph_core.py       # Directed Knowledge Graph & BFS Multi-Hop Traversal
│   └── README.md           # GraphRAG vs Vector RAG Architecture Guide
│
└── n8n/                    # ⚡ Production AI Workflow Automation (Port 5678)
    ├── docker-compose.yml  # Real n8n Self-Hosting Setup
    ├── simulator/          # Standalone Python-based n8n Web Simulator
    └── README.md           # n8n Comprehensive Engineering Guide
```

---

## 🧭 How to Explore Each Module

### 0. 🛡️ AegisOps Flagship Mission Control (`AegisOps/` - Port 5006)
**Autonomous Multi-Agent SRE & Incident Commander Platform:**
- **5 Autonomous Agents**: Triage, Forensic RCA, Security Auditor, Remediation Engineer, and Post-Mortem Scribe.
- **GraphRAG Topology**: Microservice dependency graph with real-time 3-hop cascading blast radius analysis.
- **Model Context Protocol (MCP)**: Live telemetry streaming and automated container/database remediation tools.
- **Human-in-the-Loop Gateway**: Safe interactive authorization terminal before running production repairs.

```bash
cd AegisOps
python app.py
# Opens at: http://127.0.0.1:5006
```

### 1. 🧠 The RAG Explainer (`RAG/` - Port 5000)
Understand the low-level mechanics of Retrieval-Augmented Generation:
- How similarity search retrieves private chunks.
- How prompts are augmented with grounding rules.
- How Naive RAG compares with Advanced RAG (HyDE query expansion, Cross-Encoder re-ranking, and Self-RAG grounding audits).

```bash
cd RAG
python app.py
# Opens at: http://127.0.0.1:5000
```

### 2. 🦜🔗 The LangChain Mastery Suite (`LangChain/` - Port 5001)
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

### 3. 🕸️ The LangGraph Studio (`Langgraph/` - Port 5002)
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

### 4. 🔌 The Model Context Protocol Studio (`MCP/` - Port 5003)
Master Anthropic's universal open standard for connecting AI assistants to tools & data:
- **JSON-RPC 2.0 Framing**: Protocol initialization handshake and capabilities negotiation.
- **Resources**: Passive read-only context streaming (`system://telemetry`, `docs://architecture`).
- **Tools**: Action execution with standard JSON Schema input validation.
- **Prompts**: Parameterized reusable prompt templates.
- **Autonomous Client Agent**: Full loop connecting to MCP servers, discovering tools, and solving user queries.

```bash
cd MCP
python app.py
# Opens at: http://127.0.0.1:5003
```

### 5. 🛡️ Evaluations & Guardrails Studio (`Evals_and_Guardrails/` - Port 5004)
Deploy reliable, safe, and performant AI systems in production:
- **LLM-as-a-Judge**: Multi-criteria rubric scoring (Accuracy, Conciseness) with Chain-of-Thought explanations.
- **The RAG Triad**: Measuring Faithfulness, Answer Relevance, and Context Precision.
- **Production Guardrails**: Prompt injection detection, jailbreak classification, and PII masking.
- **Semantic Caching**: Sub-millisecond vector similarity caching to reduce API costs to $0.00.

```bash
cd Evals_and_Guardrails
python app.py
# Opens at: http://127.0.0.1:5004
```

### 6. 🕸️ GraphRAG & Multi-Hop Reasoning (`GraphRAG/` - Port 5005)
Bridge the gap where standard vector search fails at global synthesis:
- **NER & Triplet Extraction**: Extracting `(Subject) ──[Predicate]──► (Object)` relations from raw text.
- **Directed Knowledge Graph**: In-memory adjacency lists, node types, and degree centrality.
- **Multi-Hop Traversal**: Shortest path finding and $N$-hop neighborhood expansion.
- **Hybrid Retrieval**: Combining dense document chunks with relational graph triplets.

```bash
cd GraphRAG
python app.py
# Opens at: http://127.0.0.1:5005
```

### 7. ⚡ n8n Workflow Automation (`n8n/` - Port 5678)
Build visual, low-code AI workflows and production pipelines:
- **Visual AI Pipelines**: Connect webhooks, databases, and Gemini AI visually.
- **Offline Simulator**: Test n8n workflows locally without Docker via the Python simulator.
- **Production Workflows**: Pre-configured workflows for triage, RAG, and agentic tool-use.

```bash
cd n8n
python simulator/server.py
# Opens at: http://127.0.0.1:5678
```
