# 🧠 Interactive RAG Explainer App (Retrieval-Augmented Generation)

An interactive web application designed to demonstrate the fundamentals of **RAG (Retrieval-Augmented Generation)** using the **Google Gemini API**.

---

## 🌟 What is RAG?

Large Language Models (LLMs) like Gemini are trained on massive public web datasets, but they **do not know**:
1. Your company's private, confidential, or internal documents.
2. Real-time or recent updates past their knowledge cutoff date.
3. Proprietary technical specs, customer policies, or passwords.

When asked about proprietary facts, pure LLMs will either say *"I don't know"* or worse, **hallucinate** plausible-sounding false answers.

### The 3 Pillars of RAG:
```
                      [ Private Knowledge Base ]
                                 │
                                 ▼ (1. RETRIEVE)
User Question ──► [ Similarity Search / Vector Matching ]
                                 │
                                 ▼ Top-K Chunks
                      [ Prompt Augmentation ] (2. AUGMENT)
                                 │
                                 ▼ Augmented Prompt + Grounding Rules
                         [ Gemini LLM ] (3. GENERATE)
                                 │
                                 ▼
                     Factual Answer with Citations
```

1. **R (Retrieval)**: When the user asks a question, the retrieval engine searches your private knowledge base and scores each document chunk using TF-IDF / Cosine similarity to pick the most relevant chunks.
2. **A (Augmentation)**: The app builds an augmented prompt that packages the retrieved facts with strict grounding instructions: *"Answer ONLY using the provided context."*
3. **G (Generation)**: The augmented prompt is sent to Google Gemini, which synthesizes a precise, factual answer citing the source document.

---

## 🚀 How to Run the App

1. **Install requirements** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application**:
   ```bash
   python app.py
   ```

3. **Open in your browser**:
   Navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🎮 Interactive Features

- **Side-by-Side Arena**: Directly compare Gemini's response **Without RAG** vs. **With RAG** on the exact same question.
- **Visual Pipeline Indicator**: Watch the 4 stages animate: *Query ➔ Retrieval ➔ Augmentation ➔ Generation*.
- **Retrieval Inspector (Tab 1)**: See every document evaluated, its similarity score percentage, matched keywords, and whether it was selected or discarded.
- **Prompt Inspector (Tab 2)**: View the exact prompt string injected with private context that was sent to Gemini.
- **Knowledge Base Manager (Tab 3)**: Add your own custom confidential facts or documents on the fly and test them immediately!
- **1-Click Pre-configured Queries**:
  - *Project NovaStar Specs & Launch Plan*
  - *Office Wi-Fi password & Wellness Stipend*
  - *45-Day Customer Refund Policy*
  - *CEO Arthur Pendelton's allergy and dessert*
  - *Project Chimera Database Architecture*

---

## 📂 Project Structure

- `app.py`: Flask backend providing REST endpoints for queries and knowledge base management.
- `rag_engine.py`: Core RAG algorithm implementing TF-IDF cosine similarity search, prompt augmentation, and Gemini API calls.
- `sample_docs.json`: Seed knowledge base with fictional facts.
- `static/index.html`: Modern Single-Page Application with Tailwind CSS and FontAwesome.
- `static/app.js`: Interactive client handling live queries, animations, and knowledge base CRUD.
- `static/style.css`: Custom animations, card styling, and glowing effects.
- `test_app.py`: Integration test suite verifying retrieval accuracy and Gemini responses.
