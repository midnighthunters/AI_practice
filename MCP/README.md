# 🔌 Model Context Protocol (MCP) Mastery Suite

A comprehensive, production-grade guide and interactive studio for the **Model Context Protocol (MCP)**, the open standard designed by Anthropic for connecting AI assistants to external tools, databases, and context resources.

---

## 🌟 What is the Model Context Protocol (MCP)?

As generative AI applications evolved from basic conversational chatbots into autonomous multi-tool agents, engineering teams faced a massive fragmentation problem:
- Every SaaS provider, database, and tool created its own proprietary API wrapper or plugin system.
- Connecting an LLM to a local database, Git repository, or Kubernetes cluster required writing custom glue code for every platform.

**MCP solves this by introducing a universal, standardized JSON-RPC 2.0 protocol** between:
1. **MCP Hosts**: The client applications where users interact with AI (e.g., Claude Desktop, Antigravity IDE, Cursor).
2. **MCP Servers**: Lightweight services that expose data and actions to the host.
3. **LLMs**: The reasoning engines that choose which MCP tools to invoke.

```
┌─────────────────────────────────────────────────────────────┐
│                          MCP HOST                           │
│  (Antigravity / Claude Desktop / Cursor / Custom Agent)     │
│                                                             │
│       ┌───────────────┐              ┌────────────────┐     │
│       │  User Prompt  │ ──► [LLM] ──►│   Tool Call    │     │
│       └───────────────┘              └───────┬────────┘     │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                                 JSON-RPC 2.0  │ (stdio or SSE)
                                               ▼
┌─────────────────────────────────────────────────────────────┐
│                         MCP SERVER                          │
│                                                             │
│  ┌────────────────────┐ ┌─────────────────┐ ┌────────────┐  │
│  │     RESOURCES      │ │      TOOLS      │ │  PROMPTS   │  │
│  │   (Read-only URI   │ │  (Executable    │ │(Reusable   │  │
│  │   data streams)    │ │   functions)    │ │ recipes)   │  │
│  └────────────────────┘ └─────────────────┘ └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 The 3 Core Primitives of MCP

| Primitive | Nature | Typical Verb | Example Use Case |
| :--- | :--- | :--- | :--- |
| **Resources** | Passive (Read-Only) | `GET` | Attaching file contents, SQL schemas, real-time CPU/GPU metrics (`system://telemetry/cluster`). |
| **Tools** | Active (Execution) | `POST` | Running SQL queries, calculating compound interest, deploying containers, triggering webhooks. |
| **Prompts** | Recipes (Templates) | `EXPAND` | Pre-engineered prompt recipes (e.g. `code_review_security`, `root_cause_analysis`) with parameters. |

---

## 📡 Transports: `stdio` vs `SSE`

MCP supports two standard communication transports:
1. **`stdio` (Standard Input / Output)**:
   - Host spawns the MCP server as a local child process.
   - Messages are serialized as single-line JSON strings over stdin/stdout.
   - **Fastest and most secure** for local tools, file access, and desktop workflows.
2. **`SSE` (Server-Sent Events) over HTTP**:
   - Ideal for remote cloud servers or microservices.
   - Client opens an SSE connection for server-to-client streaming, and sends client-to-server requests via HTTP POST.

---

## 🏃 Standalone Runnable Tutorials

This module includes 5 progressive, executable Python scripts:

```bash
cd MCP

# 1. Core Framing: JSON-RPC 2.0 handshake & ping
python 01_protocol_framing.py

# 2. Resource Provider: Listing & streaming URI resources
python 02_resource_provider.py

# 3. Tool Registry: Registering tools with JSON Schema validation
python 03_tool_registry.py

# 4. Prompt Templates: Parameterized prompt workflows
python 04_prompt_templates.py

# 5. Autonomous Agent: Full loop discovering tools and calling Gemini LLM
python 05_full_mcp_client_agent.py
```

---

## 🖥️ Interactive MCP Web Studio

Test all protocol handshakes, tools, resources, and agent execution visually in your browser:

```bash
cd MCP
python app.py
# Opens at: http://127.0.0.1:5003
```

Features:
- **🤝 Handshake Inspector**: Step through `initialize` and capability negotiation.
- **🔧 Tool Runner**: Live form generation based on the tool's JSON schema.
- **📂 Resource Browser**: Read live metrics and document streams.
- **📜 Prompt Expander**: Parameterize and render prompt recipes.
- **🤖 Autonomous Agent**: Ask natural language questions and watch the agent select and invoke MCP tools.

---

## 🧪 Running Automated Tests

```bash
python MCP/test_mcp.py
```
