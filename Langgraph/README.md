# 🕸️ LangGraph Interactive Masterclass & Agent Studio

A comprehensive, hands-on educational suite designed to explain **LangGraph** from first principles to advanced autonomous multi-agent systems using the **Google Gemini API**.

---

## 💡 Why LangGraph? The Paradigm Shift

In basic LLM development and standard RAG, code runs as a **one-way linear chain**:

```
[User Query] ──► [Retrieve Chunks] ──► [Prompt Template] ──► [LLM Generation]
```

### The Fundamental Flaw of Linear Chains:
- **No Self-Correction**: If the LLM generates flawed code or hallucinates, a linear chain cannot go back and fix it.
- **No Loops or Retries**: Real agents need to try an action, observe the error, critique the result, and iterate until it succeeds.
- **Stateless Execution**: Complex multi-turn sessions lose track of historical checkpoints and branch forks.
- **No Safe Human Gateways**: Dangerous actions (financial transfers, database updates) execute without pausing for human verification.

### Enter LangGraph: Stateful, Cyclical Multi-Agent Graphs
LangGraph models agent workflows as **StateGraphs**:
1. **Cyclic Execution**: Nodes can loop back onto themselves or earlier nodes until goals are met.
2. **First-Class State Management**: Centralized, schema-defined state with fine-grained reducers (`operator.add`).
3. **Built-in Persistence**: Every step is checkpointed under a `thread_id`, enabling time-travel debugging and session isolation.
4. **Human-in-the-Loop (HITL)**: Native breakpoints (`interrupt_before`) that halt execution for human approval before critical operations.
5. **Multi-Agent Coordination**: Supervisor-worker topologies orchestrating specialized sub-agents.

---

## 🗺️ The LangGraph Architecture & Building Blocks

```
                      LANGGRAPH MENTAL MODEL
                      
        ┌─────────────────────────────────────────────────┐
        │                 SHARED STATE                    │
        │  TypedDict: { messages, findings, step_count }  │
        └───────────────────────┬─────────────────────────┘
                                │
        ┌───────────────────────┴─────────────────────────┐
        ▼                                                 ▼
   [ START ]                                         [  END  ]
        │                                                 ▲
        ▼                                                 │
  ┌───────────┐       Normal Edge                   ┌───────────┐
  │  Node A   │ ──────────────────────────────────► │  Node B   │
  └─────┬─────┘                                     └─────▲─────┘
        │                                                 │
        │          Conditional Edge (Router)              │
        └─────────────────┬───────────────────────────────┘
                          │
                Route Decision Function
                 ├── "loop" ──► Loops back to Node A
                 └── "pass" ──► Proceeds to Node B
```

### The 4 Core Primitives:
1. **State**: A shared Python `TypedDict` or Pydantic class defining all data flowing through the graph.
2. **Nodes**: Plain Python functions `def my_node(state: State) -> dict:` that do work and return partial updates.
3. **Edges**:
   - `START`: The entry point.
   - `END`: The terminal completion point.
   - `add_edge(node_a, node_b)`: Deterministic fixed transition.
   - `add_conditional_edges(node_a, router_fn, path_map)`: Dynamic branching based on state.
4. **Checkpointer (`MemorySaver`)**: Automatically saves state snapshots at every step for persistence and rewind capabilities.

---

## 📚 The 9 Progressive Examples

Every concept is implemented in an independent, executable Python script:

| File | Concept | What It Demonstrates |
| :--- | :--- | :--- |
| [`01_basic_graph.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/01_basic_graph.py) | **Foundations** | State schema, nodes, `START` ➔ `END`, graph compilation, streaming. |
| [`02_state_reducers.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/02_state_reducers.py) | **Reducers & Parallelism** | `Annotated[list, operator.add]` for append vs overwrite; parallel fork & join. |
| [`03_conditional_routing.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/03_conditional_routing.py) | **Dynamic Branching** | Intent classification with Gemini routing to Tech, Billing, or Casual handlers. |
| [`04_cyclical_agent_loop.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/04_cyclical_agent_loop.py) | **Cycles & Self-Correction** | Drafter-Critic loop. Re-drafts until quality score $\ge 8/10$ (with recursion guard). |
| [`05_tool_calling_agent.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/05_tool_calling_agent.py) | **ReAct Agent Loop** | Reason ➔ Act ➔ Observe cycle with calculator and cluster telemetry tools. |
| [`06_memory_and_checkpoints.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/06_memory_and_checkpoints.py) | **Persistence & History** | `MemorySaver`, session `thread_id`, cross-turn recall, and state history replay. |
| [`07_human_in_the_loop.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/07_human_in_the_loop.py) | **HITL Interrupts** | `interrupt_before=["execute_transfer"]`, inspect pending action, approve/reject. |
| [`08_corrective_rag.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/08_corrective_rag.py) | **Corrective RAG (CRAG)** | Evaluates retrieved docs; if irrelevant, rewrites query and searches fallback. |
| [`09_multi_agent_supervisor.py`](file:///c:/Users/azureuser/Desktop/takeaway/Langgraph/09_multi_agent_supervisor.py) | **Multi-Agent Supervisor** | Lead supervisor delegates subtasks to Researcher & Coder agents, combining deliverables. |

---

## 🏃 Quickstart: Running from the Terminal

You can run any script individually from your terminal:

```bash
# 1. Basic StateGraph
python Langgraph/01_basic_graph.py

# 2. State Reducers & Parallel Branches
python Langgraph/02_state_reducers.py

# 3. Dynamic Conditional Routing
python Langgraph/03_conditional_routing.py

# 4. Cyclical Agent Loop (Self-Correction)
python Langgraph/04_cyclical_agent_loop.py

# 5. ReAct Tool-Calling Agent Loop
python Langgraph/05_tool_calling_agent.py

# 6. Multi-Turn Memory & Checkpointing
python Langgraph/06_memory_and_checkpoints.py

# 7. Human-in-the-Loop Interrupts
python Langgraph/07_human_in_the_loop.py

# 8. Corrective RAG (Self-Reflective RAG)
python Langgraph/08_corrective_rag.py

# 9. Multi-Agent Supervisor Collaboration
python Langgraph/09_multi_agent_supervisor.py
```

---

## 🖥️ Interactive Web Studio (Port 5001)

An interactive visual dashboard is provided to inspect graphs, trigger live runs with Gemini, watch active nodes pulse, view state diffs, and test Human-in-the-Loop approval workflows.

### 1. Launch the Server:
```bash
python Langgraph/app.py
```

### 2. Open in Your Browser:
Navigate to:
```
http://127.0.0.1:5001
```

*(Note: Port 5001 is used so you can run both the RAG app on port 5000 and the LangGraph Studio on port 5001 simultaneously!)*

### Features in the Web Studio:
- **Interactive DAG Topologies**: Displays the exact node structure and edge labels for all 9 workflows.
- **Live Node Pulsing**: Highlights active nodes in real time as Gemini executes each step.
- **State & Reducer Inspector**: Switch between formatted breakdown and raw JSON state snapshots.
- **Interactive HITL Approval Modal**: In Module 7, the UI pauses at the breakpoint and provides 1-click **Approve** and **Reject** buttons to resume execution dynamically!
- **Customizable Inputs**: Modify queries, prompts, and criteria on the fly.

---

## 🌉 Connecting Your RAG Knowledge to LangGraph

In your previous RAG lessons, you mastered:
1. **Retrieval**: Vector / TF-IDF similarity search.
2. **Augmentation**: Injecting private facts into the prompt.
3. **Generation**: Generating answers grounded in retrieved documents.

### How LangGraph Supercharges RAG (Module 08: Corrective RAG):
```
                       [ User Query ]
                             │
                             ▼
                    [ Retrieve Documents ]
                             │
                             ▼
                    [ Grade Relevance ]  ◄── (Gemini Self-Reflection)
                             │
                ┌────────────┴────────────┐
                │ Relevant?               │ Irrelevant / Missing?
                ▼                         ▼
      [ Generate Answer ]        [ Rewrite Query & Fallback ]
                │                         │
                ▼                         ▼
             ( END ) ◄─────────── [ Generate Answer ]
```

When retrieved documents are insufficient or noisy, LangGraph detects this via an evaluation node, redirects to query transformation and fallback search, and only then generates the final grounded answer.

---

## 🧪 Automated Testing

To run the complete automated test suite across all 9 modules:

```bash
python -m unittest Langgraph/test_langgraph.py
```
