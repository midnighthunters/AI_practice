# 🛡️ LLM Evaluations, Safety Guardrails & Semantic Caching

A comprehensive production-grade architecture and interactive studio for **LLM Evaluations (LLM-as-a-Judge, RAG Triad)**, **Safety Guardrails (Prompt Injections, PII Sanitization)**, and **Semantic Caching**.

---

## 💡 Why Evals & Guardrails are Mandatory for Production AI

Building a working GenAI demo takes an afternoon; making it **safe, verifiable, cost-effective, and reliable** in enterprise production is the real engineering challenge:
1. **Blind Deployments**: Without automated evaluation rubrics, subtle prompt updates or model changes degrade answer quality without warning.
2. **Hallucination Risk**: Unchecked RAG pipelines fabricate answers when retrieval fails.
3. **Security Vulnerabilities**: Malicious users bypass system prompts via prompt injections, extracting sensitive operational data or internal keys.
4. **Latency & Cost Spikes**: Re-querying expensive frontier LLMs for repetitive or paraphrased queries burns budgets and slows down applications.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION GATEWAY                                │
│                                                                             │
│  [User Query] ──► [INPUT GUARDRAILS] ──► [SEMANTIC CACHE]                   │
│                    (Injection / PII)      (Sub-ms Hit?)                     │
│                           │                      │                          │
│                           ▼ (Pass)               ├──► (HIT: Return 0.2ms)   │
│                   ┌───────────────┐              │                          │
│                   │  LLM / RAG    │◄─────────────┘ (MISS: Run Model)        │
│                   └───────┬───────┘                                         │
│                           ▼                                                 │
│                  [OUTPUT GUARDRAILS] ──► [EVALUATION SUITE] ──► [End User]  │
│                   (Schema / PII)         (Judge / Triad)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚖️ 1. LLM-as-a-Judge (Rubric-Based Quality Control)

Rather than relying on outdated n-gram metrics (BLEU, ROUGE) that fail to grasp semantic meaning, **LLM-as-a-Judge** evaluates model responses against multi-dimensional scoring rubrics:
- **Accuracy (1-5)**: Factual alignment, grounding in truth, absence of hallucinations.
- **Conciseness (1-5)**: Signal-to-noise ratio, zero filler or repetitive babble.
- **Chain-of-Thought (CoT)**: Step-by-step reasoning explaining why points were awarded or deducted.

---

## 📐 2. The RAG Triad (TruLens / Ragas Framework)

The RAG Triad decomposes retrieval-augmented generation into three distinct, measurable verification axes:

| Metric | Question Answered | Failure Mode Detected |
| :--- | :--- | :--- |
| **Context Precision** | Did retrieval return relevant chunks? | Bad chunking, low vector similarity, noisy embeddings. |
| **Faithfulness** | Is the answer grounded strictly in retrieved context? | Hallucinations, model injecting outside bias. |
| **Answer Relevance** | Does the answer directly address the user query? | Model drifting or answering the wrong question. |

---

## 🛡️ 3. Production Safety Guardrails

- **Input Guardrails**:
  - Catches prompt injection delimiters (`IGNORE PREVIOUS INSTRUCTIONS`, `SYSTEM OVERRIDE`).
  - Blocks roleplay bypasses (e.g., `DAN` mode).
  - Redacts sensitive PII (Social Security Numbers, Credit Cards, Emails, Phone Numbers) before requests touch the LLM.
- **Output Guardrails**:
  - Enforces strict JSON Schema compliance.
  - Verifies that model outputs do not regurgitate private customer PII.

---

## ⚡ 4. Semantic Caching

Standard key-value caches (Redis/Memcached) only match exact identical character strings. A **Semantic Cache**:
1. Encodes incoming queries into semantic token vectors.
2. Computes cosine similarity against previously cached queries.
3. If similarity exceeds the threshold (e.g. `0.75`), returns the cached answer in **< 1 millisecond** with **$0 token cost**.

---

## 🏃 Standalone Runnable Tutorials

```bash
cd Evals_and_Guardrails

# 1. Rubric-based LLM-as-a-Judge evaluation
python 01_llm_as_judge.py

# 2. Quantitative RAG Triad health calculation
python 02_rag_triad_eval.py

# 3. Input security scanning & PII anonymization
python 03_input_guardrails.py

# 4. Output schema validation & leakage prevention
python 04_output_guardrails.py

# 5. Semantic Cache latency & cost benchmark
python 05_semantic_cache.py
```

---

## 🖥️ Interactive Web Studio

```bash
cd Evals_and_Guardrails
python app.py
# Opens at: http://127.0.0.1:5004
```

Features:
- **⚖️ Judge Studio**: Test custom candidate responses against reference context and view rubric scoring.
- **📐 Triad Diagnostics**: Live visual progress bars for Faithfulness, Relevance, and Precision.
- **🛡️ Guardrail Tester**: Live firewall scanner for prompt injections and PII redactions.
- **⚡ Cache Telemetry**: Live latency and similarity comparisons for cold vs warm queries.

---

## 🧪 Running Automated Tests

```bash
python Evals_and_Guardrails/test_evals.py
```
