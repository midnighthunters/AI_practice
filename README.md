# 🚀 AI Engineering Practice & Flagship Enterprise Suite

Welcome to the AI Engineering learning & production workspace. This repository features **AegisOps**—an enterprise-grade autonomous multi-agent incident commander platform—alongside seven in-depth learning & mastery modules powered by modern AI engineering standards:

```
takeaway/
├── AegisOps/                    # 🛡️ FLAGSHIP: Autonomous Multi-Agent SRE & Incident Commander (Port 5006)
│   ├── app.py                   # Mission Control Dashboard & Live HTML5 Canvas Topology
│   ├── orchestrator.py          # 5-Agent Swarm Orchestrator (Triage, RCA, Sec, Remediation, PostMortem)
│   ├── graph_topology.py        # GraphRAG Microservice Topology & Blast Radius Engine
│   └── README.md                # Architecture Deep Dive & Resume Talking Points
│
├── 🏛️ JPMC LLM Suite (London)   # 🏦 5 Enterprise FastAPI Microservices for Tier-1 Banking
│   ├── JPMC_DocIntel_API/       # SEC 10-K & Financial Statement Grounding Engine (Port 8001)
│   ├── JPMC_ModelGovernance_API/# SR 11-7 AI Safety, MNPI & Regulatory Audit Gateway (Port 8002)
│   ├── JPMC_MarketSynthesizer_API/# Multi-Agent Earnings & Consensus Synthesis Swarm (Port 8003)
│   ├── JPMC_TradeAML_Explainer_API/# Automated SAR & Trade Anomaly Narrator (Port 8004)
│   └── JPMC_LLM_RouterGateway_API/# Enterprise Token Economizer & Semantic Router (Port 8005)
│
├── RAG/                         # 🧠 Interactive RAG Explainer & Grounding Architecture (Port 5000)
├── LangChain/                   # 🦜🔗 LangChain Interactive Mastery Suite (Port 5001)
├── Langgraph/                   # 🕸️ LangGraph Multi-Agent Studio & Stateful Graphs (Port 5002)
├── MCP/                         # 🔌 Model Context Protocol (MCP) Suite (Port 5003)
├── Evals_and_Guardrails/        # 🛡️ Production Evals, Safety & Semantic Cache (Port 5004)
├── GraphRAG/                    # 🕸️ Knowledge Graphs & Multi-Hop Reasoning (Port 5005)
└── n8n/                         # ⚡ Production AI Workflow Automation (Port 5678)
```

---

## 🏛️ JPMorgan Chase LLM Suite - 5 Enterprise FastAPI Microservices

Built specifically for the **Senior Associate - Generative AI / LLM Suite** role at **JPMorgan Chase (London)**. Each service is fully independent, compliant with tier-1 banking regulations (Federal Reserve SR 11-7, UK FCA/PRA, FinCEN), and includes automated test suites and interactive Swagger OpenAPI documentation (`/docs`).

| Microservice | Port | Target JPMC Unit | Key Capabilities |
| :--- | :--- | :--- | :--- |
| [**JPMC_DocIntel_API**](file:///c:/Users/azureuser/Desktop/takeaway/JPMC_DocIntel_API) | `8001` | Corporate & Investment Bank (CIB) | SEC 10-K tabular & footnote RAG, verbatim numerical anti-hallucination verification, GAAP accounting reconciliation ($Assets = Liabilities + Equity$). |
| [**JPMC_ModelGovernance_API**](file:///c:/Users/azureuser/Desktop/takeaway/JPMC_ModelGovernance_API) | `8002` | Model Risk Governance (MRGO) & Compliance | Material Non-Public Information (**MNPI**) scrubber, banking PII pseudonymization (IBAN, UK NINO, SWIFT), prompt injection firewall, Federal Reserve **SR 11-7** compliance scorecard with SHA-256 cryptographic audit lineage. |
| [**JPMC_MarketSynthesizer_API**](file:///c:/Users/azureuser/Desktop/takeaway/JPMC_MarketSynthesizer_API) | `8003` | Global Markets & Equity Research | 3-Agent Swarm (`EarningsAuditorAgent`, `GuidanceSentimentAgent`, `ExecutiveBriefingAgent`) benchmarking reported figures vs Wall Street consensus and generating institutional briefing memos in sub-second time. |
| [**JPMC_TradeAML_Explainer_API**](file:///c:/Users/azureuser/Desktop/takeaway/JPMC_TradeAML_Explainer_API) | `8004` | Financial Crimes & AML Surveillance | Deterministic AML typology engine (Structuring / Smurfing, Velocity Bursts, Offshore Hops) + statutory **5-part regulatory SAR narrative generator** (Who, What, When, Where, Why) with transaction hash lineage. |
| [**JPMC_LLM_RouterGateway_API**](file:///c:/Users/azureuser/Desktop/takeaway/JPMC_LLM_RouterGateway_API) | `8005` | Core LLM Suite Platform Engineering | Sub-10ms in-memory semantic vector cache ($\text{sim} \ge 0.88$), dynamic tiered routing (Tier 1 Fast/Internal vs Tier 2 Frontier/Reasoning 70B), multi-tenant departmental token quota governance (CIB, AWM, Risk). |

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

---

## 💼 JPMorgan Chase (London) - Senior Associate Interview Pitch Guide

When presenting this portfolio to Executive Directors (EDs) and hiring managers for the **LLM Suite Senior Associate** opening at JPMorgan Chase (London), present the overarching architectural thesis:

> *"JPMorgan's internal LLM Suite serves 140,000+ employees across Corporate & Investment Banking (CIB), Asset & Wealth Management (AWM), Markets, and Risk. Deploying foundation models into a tier-1 global bank requires solving three non-negotiable enterprise constraints:
> 
> 1. **Zero Tolerance for Numerical Hallucination**: In equity research and financial reporting, a miscalculated basis point or missed footnote in a 10-K filing has severe regulatory and financial consequences. I built **`JPMC_DocIntel_API`** with coordinate-level tabular indexing and post-generation numerical anti-hallucination verification.
> 2. **Model Risk Management & Market Abuse Defense**: Under Federal Reserve **SR 11-7** and UK **FCA/PRA** governance, models cannot be black boxes, and Material Non-Public Information (**MNPI**) cannot leak outside information barriers. I built **`JPMC_ModelGovernance_API`** to scrub MNPI deal codenames, pseudonymize UK banking PII, and generate SHA-256 cryptographic audit scorecards.
> 3. **High-Throughput Token Economics at Scale**: Serving 140k users on frontier models causes massive GPU/API costs and rate limit exhaustion. I engineered **`JPMC_LLM_RouterGateway_API`** with a sub-10ms in-memory semantic cache and adaptive tiered model router that slashes API expenditure by 35%."*

### How to Run All 5 JPMC Services Locally

```bash
# 1. SEC 10-K Document Intelligence (Port 8001)
uvicorn JPMC_DocIntel_API.main:app --host 0.0.0.0 --port 8001

# 2. SR 11-7 Model Governance & MNPI Gateway (Port 8002)
uvicorn JPMC_ModelGovernance_API.main:app --host 0.0.0.0 --port 8002

# 3. Multi-Agent Market Synthesizer (Port 8003)
uvicorn JPMC_MarketSynthesizer_API.main:app --host 0.0.0.0 --port 8003

# 4. Automated SAR & AML Explainer (Port 8004)
uvicorn JPMC_TradeAML_Explainer_API.main:app --host 0.0.0.0 --port 8004

# 5. Enterprise LLM Router & Semantic Cache (Port 8005)
uvicorn JPMC_LLM_RouterGateway_API.main:app --host 0.0.0.0 --port 8005
```
Each service features interactive OpenAPI documentation at `http://127.0.0.1:<PORT>/docs`.
