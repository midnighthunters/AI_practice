# ⚡ The Ultimate Guide to n8n & Google Gemini AI Automation

Welcome to the **n8n** guide! Having mastered RAG (Retrieval-Augmented Generation) in code, you are now ready to see how modern AI engineering teams build, deploy, and scale production AI pipelines using **n8n**.

---

## 📑 Table of Contents
1. [What is n8n?](#-what-is-n8n)
2. [The Core Mental Model of n8n](#-the-core-mental-model-of-n8n)
3. [Mapping Your cURL Request to n8n's HTTP Request Node](#-mapping-your-curl-request-to-n8ns-http-request-node)
4. [Anatomy of Essential Nodes](#-anatomy-of-essential-nodes)
5. [Advanced AI in n8n (LangChain Ecosystem)](#-advanced-ai-in-n8n-langchain-ecosystem)
6. [Bridging RAG: Python Code vs. n8n Visual Workflow](#-bridging-rag-python-code-vs-n8n-visual-workflow)
7. [The 4 Production Workflows Included Here](#-the-4-production-workflows-included-here)
8. [Interactive Simulator & Real-World Testing](#-interactive-simulator--real-world-testing)
9. [How to Run Real n8n Locally](#-how-to-run-real-n8n-locally)

---

## 🌟 What is n8n?

**n8n** (*nodemation*) is a fair-code, self-hostable workflow automation and orchestration platform. While tools like Zapier or Make are built for simple non-technical "If This Then That" triggers, n8n is built for **engineers and AI practitioners**.

| Feature | Zapier / Make | Raw Code (Python/Node) | n8n |
| :--- | :--- | :--- | :--- |
| **Hosting** | Proprietary SaaS only | Your own servers / AWS | **Self-hostable (Docker) or Cloud** |
| **Privacy & Data Control** | Third-party cloud | 100% private | **100% private on your own VPC** |
| **Complex Logic** | Clunky branching | Infinite flexibility | **Visual graph + inline JS/Python code** |
| **Debugging** | Black-box execution | Print statements / IDE | **Step-through visual inspector with live JSON diffs** |
| **Native AI/LangChain** | Basic single-prompt bots | High maintenance glue code | **Full visual LangChain: Agents, Tools, Memory, RAG** |
| **Cost** | Expensive per-task pricing | Compute costs | **Free open-source / fair-code** |

---

## 🧠 The Core Mental Model of n8n

To understand n8n, you only need to grasp 3 fundamental concepts:

### 1. The Canonical Data Structure: Item Arrays
In n8n, **all data passing between nodes is always an array of JavaScript objects**, where each item has a `json` key (and optionally a `binary` key for files/images):

```json
[
  {
    "json": {
      "query": "Explain how AI works in a few words",
      "userId": "user_492",
      "timestamp": "2026-09-10T08:00:00Z"
    }
  }
]
```
If a node receives an array of 5 items, it will automatically execute 5 times (once for each item) unless configured otherwise.

### 2. Expression Syntax (`{{ }}`)
Nodes can dynamically reference data from previous nodes using double curly braces:
- Current item's field: `{{ $json.query }}`
- Data from a specific preceding node: `{{ $('Webhook Trigger').item.json.body.message }}`
- JavaScript logic inside expressions: `{{ $json.query.trim().toLowerCase() }}`
- Environment variables: `{{ $env.GEMINI_API_KEY }}`

### 3. Node Execution Graph
Execution moves from left to right along connection lines:
```
[Trigger Node] ──► [Data Prep / Code Node] ──► [HTTP / AI Node] ──► [Output Node]
```

---

## 🔌 Mapping Your cURL Request to n8n's HTTP Request Node

You provided this exact cURL command for Google Gemini:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: YOUR_GEMINI_API_KEY' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
```

In n8n, you implement this directly using the **HTTP Request Node**. Here is the exact parameter mapping:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       n8n HTTP REQUEST NODE CONFIGURATION                   │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ Method                │ POST                                                │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ URL                   │ https://generativelanguage.googleapis.com/v1beta/   │
│                       │ models/gemini-flash-latest:generateContent          │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Authentication        │ None (or Generic Credential Type)                   │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Send Headers          │ TRUE                                                │
│ ├─ Content-Type       │ application/json                                    │
│ └─ X-goog-api-key     │ YOUR_GEMINI_API_KEY (or $env.GEMINI_API_KEY)        │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Send Body             │ TRUE                                                │
│ Body Content Type     │ JSON                                                │
│ Specify Body          │ Using JSON                                          │
│ JSON Body             │ {                                                   │
│                       │   "contents": [                                     │
│                       │     {                                               │
│                       │       "parts": [                                    │
│                       │         {                                           │
│                       │           "text": "={{ $json.query }}"              │
│                       │         }                                           │
│                       │       ]                                             │
│                       │     }                                               │
│                       │   ]                                                 │
│                       │ }                                                   │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

Notice how `"Explain how AI works in a few words"` is replaced with `={{ $json.query }}`. This turns your static cURL command into a **dynamic API automation pipeline**!

---

## 🧩 Anatomy of Essential Nodes

### 1. The Trigger Node (The Workflow Starter)
Every workflow begins with a trigger. Common triggers:
- **Webhook**: Exposes a public or private URL (`https://your-n8n/webhook/my-api`). When another service sends a POST request, the workflow runs.
- **Schedule (Cron)**: Runs at recurring intervals (e.g. every morning at 9 AM, or every 5 minutes).
- **Chat Trigger**: Provides an interactive, embedded chat UI widget for conversational AI bots.

### 2. The Code Node (Custom JS & Python)
When you need custom data manipulation, you don't need external microservices—write JavaScript or Python directly inside n8n:

```javascript
// JavaScript Code Node example: Extract Gemini's generated answer text
const candidate = $input.first().json.candidates[0];
const answerText = candidate.content.parts[0].text;

return [
  {
    json: {
      success: true,
      answer: answerText,
      model: "gemini-flash-latest",
      generatedAt: new Date().toISOString()
    }
  }
];
```

### 3. The Control Flow Nodes
- **If Node**: Branch your workflow based on a boolean condition (e.g., `if ($json.sentiment === 'ANGRY')`).
- **Switch Node**: Route items to multiple pathways based on categories (e.g., Billing, Bug, Feature Request).
- **Split In Batches (Loop)**: Process a list of 1,000 documents in batches of 10 to respect Gemini rate limits.
- **Merge Node**: Recombine outputs from parallel branches.

---

## 🤖 Advanced AI in n8n (LangChain Ecosystem)

n8n has native first-class integration with LangChain. Instead of writing complex agentic loops in code, you connect visual building blocks:

```
                      ┌───────────────────────────┐
                      │    Chat / Webhook Trigger │
                      └─────────────┬─────────────┘
                                    │
                                    ▼
                      ┌───────────────────────────┐
                      │       AI Agent Node       │
                      │  (Reasoning & ReAct Loop) │
                      └──────┬─────────────┬──────┘
                             │             │
              ┌──────────────┘             └──────────────┐
              ▼                                           ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│ Google Gemini Chat Model  │               │      Attached Tools       │
│  (gemini-flash-latest)    │               │  - Weather API            │
│  API Key: AQ.Ab8RN6...    │               │  - PostgreSQL Query       │
└───────────────────────────┘               │  - Calculator             │
                                            └───────────────────────────┘
```

### Key AI Sub-nodes:
1. **Google Gemini Chat Model Node**: Provides the intelligence core, temperature settings, and safety filters.
2. **AI Agent Node**: Uses Gemini to determine which tools to invoke, analyzes their return values, and loops until the task is solved.
3. **Memory Nodes (Window Buffer / Redis)**: Automatically tracks multi-turn chat history for each user session.
4. **Tool Nodes**: Lets Gemini call custom HTTP APIs, execute Python scripts, or query SQL databases.

---

## 🔄 Bridging RAG: Python Code vs. n8n Visual Workflow

Earlier, you learned how RAG works in Python (`takeaway/rag_engine.py`):
1. Load documents (`sample_docs.json`).
2. Calculate TF-IDF token overlap & Cosine Similarity.
3. Augment prompt with `[Document X]: Excerpt...`.
4. Send augmented prompt to Gemini API.

Here is how that exact same RAG pipeline translates into n8n:

### Side-by-Side Comparison

```
┌────────────────────────────────────────┬────────────────────────────────────────┐
│        Python RAG (rag_engine.py)      │              n8n Visual RAG            │
├────────────────────────────────────────┼────────────────────────────────────────┤
│ 1. docs = json.load(sample_docs.json)  │ 1. Read JSON / Google Drive Node       │
│ 2. tokenize(doc) & compute_tfidf()     │ 2. Text Splitter / Chunker Node        │
│ 3. cosine_similarity(query_vec, doc)   │ 3. Gemini Embeddings + Vector Store    │
│ 4. prompt = f"{instruction}\n{context}"│ 4. Vector Store Retriever Tool         │
│ 5. requests.post(gemini_url, json=...) │ 5. Gemini Flash Model Node             │
│ 6. return resp.json()                  │ 6. Respond to Webhook Node             │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

### Visual n8n RAG Workflow Architecture
```
[User Question Webhook]
          │
          ▼
[Vector Store Retriever] ◄── [Vector Store: In-Memory / Pinecone / Supabase]
(Finds Top-K Chunks)                 ▲
          │                          │ (Ingestion Pipeline: Embeddings)
          ▼                          │
[Augment Prompt Node] ────────► [Gemini Flash Model]
(Injects Grounding Facts)     (Generates Cited Answer)
                                     │
                                     ▼
                           [Webhook Response JSON]
```

**Why build RAG in n8n?**
- **Zero boilerplate**: No need to write vector chunking, math similarity, or retry loops manually.
- **Dynamic knowledge updates**: When an employee drops a new PDF into Google Drive or Notion, an n8n trigger automatically parses, embeds, and updates the vector database in real-time.
- **Plug-and-play models**: Switch from `gemini-flash-latest` to `gemini-1.5-pro` with a single dropdown selection.

---

## 📦 The 4 Production Workflows Included Here

In the `takeaway/n8n/workflows/` directory, you have 4 production-grade JSON files ready to import directly into any n8n instance:

### 1. `01_gemini_http_request.json`
- **Purpose**: Direct replica of your exact cURL command, dynamicized with incoming webhook queries.
- **Key Nodes**:
  - `Webhook`: Accepts `POST /webhook/gemini-ask` with `{"query": "..."}`.
  - `Prepare Payload`: Wraps the query into Gemini's `{"contents": [{"parts": [{"text": ...}]}]}` format.
  - `HTTP Request (Gemini API)`: Sends the request to `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent` using your configured `GEMINI_API_KEY`.
  - `Format Output`: Cleans up the candidate response and returns JSON.

### 2. `02_smart_customer_triage.json`
- **Purpose**: Automated customer ticket analyzer & router.
- **Workflow**:
  - Incoming ticket webhook ➔ Gemini Flash with structured system prompt ➔ Outputs clean JSON schema:
    ```json
    {
      "category": "BILLING | TECHNICAL | COMPLAINT",
      "urgency": "HIGH | MEDIUM | LOW",
      "sentiment": "POSITIVE | NEUTRAL | ANGRY",
      "summary": "One sentence summary"
    }
    ```
  - `Switch Node`: If urgency is `HIGH`, immediately sends an urgent notification; if `LOW`, routes to backlog.

### 3. `03_n8n_rag_pipeline.json`
- **Purpose**: Complete enterprise RAG pipeline matching the QuantumNova knowledge base from your RAG app.
- **Workflow**:
  - Incoming query ➔ Vector Retriever (matches Project NovaStar specs, WiFi passwords, Refund policy) ➔ Prompt Augmenter ➔ Gemini Flash ➔ Returns answer with source citations.

### 4. `04_gemini_ai_agent_tools.json`
- **Purpose**: Autonomous Agent utilizing Gemini Flash as its cognitive engine with tool-calling capabilities.
- **Workflow**:
  - Chat Trigger ➔ AI Agent Node ➔ Attached Tools:
    - *Calculator Tool*: Math calculations.
    - *Customer Database Tool*: Mock SQL lookup for customer order status.
    - *Knowledge Base Search Tool*: Proprietary documentation lookup.

---

## 💻 Interactive Simulator & Real-World Testing

You don't even need to launch Docker right now to see this in action! We have built a dedicated **n8n Interactive Simulator** inside `n8n/simulator/`.

### Running the Simulator:
```bash
python n8n/simulator/server.py
```
Then open your browser at:
```
http://127.0.0.1:5050
```

### What you can do in the simulator:
1. **Interactive Workflow Canvas**: Visually see nodes connected with flow paths.
2. **Execute Live Workflows**: Choose between:
   - *Direct Gemini cURL Automation*
   - *Automated RAG Knowledge Base*
   - *Ticket Sentiment & Triage*
   - *AI Agent Tool Invocation*
3. **Real Gemini API Calls**: Uses your actual API key to call Google Gemini live!
4. **Node-by-Node Inspector**: Click any node to see its exact **Input Items**, **Parameters/Headers**, and **Output Items**, exactly as you would in n8n's UI!

---

## 🐳 How to Run Real n8n Locally

If you want to run the full official n8n application on your machine:

### Option A: Using Docker Compose (Recommended)
We have included a pre-configured `docker-compose.yml` in this folder:
```bash
cd n8n
docker compose up -d
```
Then open:
```
http://localhost:5678
```

### Option B: Using Node / npx (Zero Docker Required)
Since Node.js is installed on your system:
```bash
npx n8n
```
Once n8n opens:
1. Click **Add Workflow** ➔ **Import from File...**
2. Select any `.json` file from `takeaway/n8n/workflows/` (e.g., `01_gemini_http_request.json`).
3. Click **Test Step** or **Execute Workflow** to run!

---

## 🎯 Summary Checklist

- [x] Master n8n guide created (`n8n/README.md`).
- [x] cURL request mapped 1-to-1 to n8n HTTP Request node.
- [x] Gemini API key configured (`GEMINI_API_KEY` via .env or environment).
- [x] Model set to `gemini-flash-latest`.
- [x] 4 Production n8n workflow JSONs generated in `n8n/workflows/`.
- [x] Interactive n8n Simulator included in `n8n/simulator/`.
- [x] Docker compose file provided for instant self-hosting.
