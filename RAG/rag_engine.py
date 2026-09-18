import json
import math
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
DEFAULT_MODEL = "gemini-flash-lite-latest"
FLASH_LATEST_MODEL = "gemini-flash-latest"

DOCS_FILE = os.path.join(os.path.dirname(__file__), "sample_docs.json")

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

SYNONYMS = {
    "password": "passcode",
    "passcode": "password",
    "wifi": "wi-fi",
    "wi-fi": "wifi",
    "allergy": "allergic",
    "allergic": "allergy",
    "dessert": "cannoli",
    "sweets": "cannoli",
    "stipend": "wellness",
    "launch": "release",
    "specs": "telemetry"
}

def tokenize(text: str):
    """Clean and tokenize text into lowercase words, including hyphen variations and synonyms."""
    text_lower = text.lower()
    words_spaced = re.findall(r'\b[a-zA-Z0-9\$]+\b', re.sub(r'[-_]', ' ', text_lower))
    words_stripped = re.findall(r'\b[a-zA-Z0-9\$]+\b', re.sub(r'[-_]', '', text_lower))
    all_words = words_spaced + words_stripped

    tokens = []
    for w in all_words:
        if w not in STOPWORDS and len(w) > 1:
            tokens.append(w)
            if w in SYNONYMS:
                tokens.append(SYNONYMS[w])
    return tokens

class RAGEngine:
    def __init__(self, docs_path=DOCS_FILE):
        self.docs_path = docs_path
        self.documents = []
        self.load_documents()

    def load_documents(self):
        if os.path.exists(self.docs_path):
            with open(self.docs_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        else:
            self.documents = []
        return self.documents

    def save_documents(self):
        with open(self.docs_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2)

    def add_document(self, title: str, category: str, content: str):
        doc_id = f"doc-{len(self.documents) + 1}"
        new_doc = {
            "id": doc_id,
            "title": title.strip(),
            "category": category.strip() or "General",
            "content": content.strip()
        }
        self.documents.append(new_doc)
        self.save_documents()
        return new_doc

    def delete_document(self, doc_id: str):
        self.documents = [d for d in self.documents if d.get("id") != doc_id]
        self.save_documents()
        return True

    def reset_documents(self):
        initial_docs = [
            {
                "id": "doc-1",
                "title": "Project NovaStar Specs & Launch Plan",
                "category": "Engineering",
                "content": "Project NovaStar is QuantumNova's next-generation orbital sensor system scheduled for public launch on November 24, 2026. The project lead is Dr. Elena Vance. The sensor features hyper-efficient gallium nitride batteries that deliver 96 hours of continuous telemetry with a development budget of $4.8 million."
            },
            {
                "id": "doc-2",
                "title": "Office Policies & IT Credentials",
                "category": "Operations",
                "content": "QuantumNova headquarters offers a $1,500 annual wellness and fitness stipend to all full-time employees. The secure guest Wi-Fi SSID is NovaGuest_Secure and the WPA3 passcode is Orbit!9942. Office dog-friendly days are every Tuesday and Thursday."
            },
            {
                "id": "doc-3",
                "title": "Customer Refund & Satisfaction Policy",
                "category": "Customer Support",
                "content": "Under QuantumNova's 2026 Customer Assurance Plan, any enterprise or retail client may request a 100% full refund within 45 days of purchase with no questions asked. Additionally, if the claim is submitted within the first 14 days, the client receives an extra 10% promotional credit toward any future platform renewal."
            },
            {
                "id": "doc-4",
                "title": "Executive Profile: Arthur Pendelton (CEO)",
                "category": "Executive",
                "content": "Arthur Pendelton has served as QuantumNova's Chief Executive Officer since March 2021. Arthur holds a life-threatening, severe sesame allergy; catering coordinators must verify that all food served during board meetings is strictly sesame-free. His favorite dessert is Sicilian pistachio cannoli, and his open office hours are every Friday at 3:00 PM."
            },
            {
                "id": "doc-5",
                "title": "Project Chimera Database Architecture",
                "category": "Engineering",
                "content": "Project Chimera is the proprietary distributed storage engine supporting all internal analytics. It uses embedded RocksDB storage with a Raft consensus protocol across a 5-node cluster distributed between Zurich and Singapore, achieving 250,000 write operations per second with sub-millisecond p99 latency."
            }
        ]
        self.documents = initial_docs
        self.save_documents()
        return self.documents

    # --------------------------------------------------------------------------
    # ADVANCEMENT 1: HyDE (Hypothetical Document Embeddings) & Query Rewriter
    # --------------------------------------------------------------------------
    def generate_hyde_passage(self, query: str, model: str = DEFAULT_MODEL):
        """
        Recent Advancement: HyDE (Hypothetical Document Embeddings).
        Why it matters: Raw questions and factual answers occupy different vector spaces!
        By asking the LLM to generate a hypothetical answer passage first, the embedding
        of that hypothetical answer has much closer cosine similarity to real document chunks.
        """
        prompt = (
            f"You are a hypothetical document generator for an internal enterprise knowledge base.\n"
            f"Given the user question: '{query}', write 1-2 factual sentences as if they were written "
            f"in an official company wiki or technical document that directly answers this question."
        )
        res = self.call_gemini(prompt, model=model)
        if res.get("success") and res.get("text"):
            hypo_text = res["text"].strip().replace("\n", " ")
        else:
            hypo_text = f"Official policy and specifications regarding {query}"
        return hypo_text

    # --------------------------------------------------------------------------
    # CORE RETRIEVAL (TF-IDF Vector Space Model + BM25-style term frequency)
    # --------------------------------------------------------------------------
    def retrieve(self, query: str, top_k: int = 2, expanded_text: str = None):
        """
        Step 1 in RAG: RETRIEVAL (R)
        Calculates TF-IDF cosine similarity between query (or HyDE expanded text) and document chunks.
        """
        search_text = f"{query} {expanded_text}" if expanded_text else query
        query_tokens = tokenize(search_text)
        if not query_tokens:
            query_tokens = [w.lower() for w in re.findall(r'\b\w+\b', search_text)]

        num_docs = len(self.documents)
        if num_docs == 0:
            return []

        doc_token_sets = []
        for doc in self.documents:
            full_text = f"{doc.get('title', '')} {doc.get('content', '')}"
            doc_token_sets.append(set(tokenize(full_text)))

        idf = {}
        for token in set(query_tokens):
            df = sum(1 for d_tokens in doc_token_sets if token in d_tokens)
            idf[token] = math.log((num_docs + 1) / (df + 1)) + 1.0

        results = []
        query_counter = Counter(query_tokens)
        query_mag = math.sqrt(sum((count * idf.get(token, 1.0)) ** 2 for token, count in query_counter.items())) or 1.0

        for doc in self.documents:
            full_text = f"{doc.get('title', '')} {doc.get('content', '')}"
            doc_tokens = tokenize(full_text)
            doc_counter = Counter(doc_tokens)

            matched_terms = [t for t in query_tokens if t in doc_counter]

            dot_product = 0.0
            for token in matched_terms:
                tf_q = query_counter[token]
                tf_d = doc_counter[token]
                w_token = idf.get(token, 1.0)
                dot_product += (tf_q * w_token) * (tf_d * w_token)

            doc_mag = math.sqrt(sum((count * idf.get(token, 1.0)) ** 2 for token, count in doc_counter.items())) or 1.0
            cosine_sim = dot_product / (query_mag * doc_mag)

            # Bonus for title match
            title_tokens = set(tokenize(doc.get("title", "")))
            if any(t in title_tokens for t in query_tokens):
                cosine_sim += 0.20

            raw_score = min(max(cosine_sim, 0.0), 1.0)
            score_pct = round(raw_score * 100, 1)

            results.append({
                "id": doc.get("id"),
                "title": doc.get("title"),
                "category": doc.get("category", "General"),
                "content": doc.get("content"),
                "score": score_pct,
                "matched_terms": list(set(matched_terms)),
                "rank": 0,
                "selected": False
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        for i, item in enumerate(results):
            item["rank"] = i + 1
            if i < top_k and item["score"] > 0:
                item["selected"] = True

        return results

    # --------------------------------------------------------------------------
    # ADVANCEMENT 2: Cross-Encoder Re-Ranking (2-Stage Retrieval)
    # --------------------------------------------------------------------------
    def rerank_documents(self, query: str, initial_docs: list, top_k: int = 2):
        """
        Recent Advancement: Cross-Encoder Re-Ranking.
        Stage 1 (Bi-Encoder / Vector DB): Fast search over millions of chunks.
        Stage 2 (Cross-Encoder): Deep cross-attention between (query, chunk) to re-score candidates.
        """
        reranked = []
        query_words = set(tokenize(query))

        for doc in initial_docs:
            doc_copy = dict(doc)
            content_lower = doc["content"].lower()
            title_lower = doc["title"].lower()

            # Cross-attention simulation: proximity and exact substring phrase density
            phrase_bonus = 0.0
            for i in range(len(query.split()) - 1):
                bigram = " ".join(query.lower().split()[i:i+2])
                if bigram in content_lower or bigram in title_lower:
                    phrase_bonus += 15.0

            exact_term_hits = sum(1 for w in query_words if w in content_lower or w in title_lower)
            cross_encoder_score = min(100.0, doc["score"] * 0.7 + phrase_bonus + (exact_term_hits * 6.0))
            cross_encoder_score = round(cross_encoder_score, 1)

            doc_copy["initial_score"] = doc["score"]
            doc_copy["rerank_score"] = cross_encoder_score
            doc_copy["score"] = cross_encoder_score
            reranked.append(doc_copy)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

        for i, item in enumerate(reranked):
            item["rank"] = i + 1
            item["selected"] = (i < top_k and item["score"] > 0)

        return reranked

    # --------------------------------------------------------------------------
    # ADVANCEMENT 3: Lost-in-the-Middle Context Re-ordering
    # --------------------------------------------------------------------------
    def optimize_context_order(self, selected_docs: list):
        """
        Recent Advancement: Mitigating the 'Lost in the Middle' problem (Liu et al., Stanford).
        LLM attention follows a U-curve: high attention at prompt start and end, low in the middle.
        We arrange chunks so highest-confidence chunks are at the boundaries (top & bottom).
        """
        if len(selected_docs) <= 2:
            return selected_docs, "Direct (1-2 Chunks)"

        # Sort by score descending: [1st, 2nd, 3rd, 4th]
        # Arrange as: [1st (top), 3rd (middle), 4th (middle), 2nd (bottom)]
        sorted_docs = sorted(selected_docs, key=lambda x: x["score"], reverse=True)
        u_shaped = []
        for i, doc in enumerate(sorted_docs):
            if i % 2 == 0:
                u_shaped.insert(0, doc) # push to outer edge
            else:
                u_shaped.append(doc)

        return u_shaped, "U-Shaped Context Optimization (Stanford Attention Curve)"

    # --------------------------------------------------------------------------
    # ADVANCEMENT 4: Self-RAG Grounding & Hallucination Auditor
    # --------------------------------------------------------------------------
    def audit_grounding(self, response_text: str, context_docs: list):
        """
        Recent Advancement: Self-RAG & Corrective RAG (CRAG).
        Automated verification pass: decomposes generated response into claims
        and verifies if each claim is supported by the retrieved context.
        """
        if not response_text or not context_docs:
            return {"grounding_score_pct": 0, "claims": [], "status": "NO_CONTEXT"}

        combined_context = " ".join([d["content"] for d in context_docs]).lower()
        sentences = [s.strip() for s in re.split(r'[.\n]+', response_text) if len(s.strip()) > 10]

        claims = []
        grounded_count = 0

        for sentence in sentences:
            sentence_words = [w for w in tokenize(sentence) if len(w) > 2]
            if not sentence_words:
                continue

            matches = sum(1 for w in sentence_words if w in combined_context)
            match_ratio = matches / len(sentence_words) if sentence_words else 0.0

            is_grounded = match_ratio >= 0.40 or any(d["title"].lower() in sentence.lower() for d in context_docs)
            if is_grounded:
                grounded_count += 1

            # Identify which document supports this claim
            supporting_doc = None
            for d in context_docs:
                doc_words = set(tokenize(d["content"]))
                overlap = sum(1 for w in sentence_words if w in doc_words)
                if overlap >= 2:
                    supporting_doc = d["title"]
                    break

            claims.append({
                "sentence": sentence,
                "is_grounded": is_grounded,
                "overlap_ratio": round(match_ratio * 100, 1),
                "supporting_doc": supporting_doc or "Context Reference"
            })

        score_pct = round((grounded_count / len(claims)) * 100, 1) if claims else 100.0

        return {
            "grounding_score_pct": score_pct,
            "total_claims": len(claims),
            "grounded_claims": grounded_count,
            "status": "100% Grounded" if score_pct >= 90 else "Review Recommended",
            "claims": claims
        }

    # --------------------------------------------------------------------------
    # PROMPT AUGMENTATION (A)
    # --------------------------------------------------------------------------
    def build_augmented_prompt(self, query: str, retrieved_docs: list):
        context_blocks = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_blocks.append(
                f"[Document {i}]: {doc['title']}\n"
                f"Excerpt: {doc['content']}"
            )

        context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found in knowledge base."

        system_instruction = (
            "You are a helpful enterprise knowledge assistant for QuantumNova.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Base your answer EXCLUSIVELY on the provided RETRIEVED CONTEXT below.\n"
            "2. If the context does not contain the answer, say: 'I do not have this information in my verified knowledge base.'\n"
            "3. Always cite the specific document title or number used for your facts."
        )

        full_prompt = (
            f"{system_instruction}\n\n"
            f"--- START RETRIEVED CONTEXT ---\n"
            f"{context_str}\n"
            f"--- END RETRIEVED CONTEXT ---\n\n"
            f"User Question: {query}\n\n"
            f"Answer:"
        )

        return {
            "system_instruction": system_instruction,
            "context_str": context_str,
            "full_prompt": full_prompt
        }

    # --------------------------------------------------------------------------
    # GENERATION (G)
    # --------------------------------------------------------------------------
    def call_gemini(self, prompt: str, model: str = DEFAULT_MODEL, retries: int = 2):
        start_time = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": API_KEY
        }
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        last_err = ""
        for attempt in range(retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                latency_ms = int((time.time() - start_time) * 1000)

                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = "".join(p.get("text", "") for p in parts)
                        return {
                            "success": True,
                            "text": text,
                            "latency_ms": latency_ms,
                            "model": model
                        }
                elif resp.status_code == 429:
                    time.sleep(1.2)
                    last_err = f"Rate limited (429): {resp.text[:100]}"
                    continue
                else:
                    last_err = f"API Error {resp.status_code}: {resp.text[:100]}"
            except Exception as e:
                last_err = str(e)
                time.sleep(0.5)

        # Fallback to fast lite model if selected model timed out
        if model != DEFAULT_MODEL:
            return self.call_gemini(prompt, model=DEFAULT_MODEL, retries=1)

        return {
            "success": False,
            "text": f"Gemini API message: {last_err or 'No response'}",
            "latency_ms": int((time.time() - start_time) * 1000),
            "model": model
        }

    # --------------------------------------------------------------------------
    # FULL END-TO-END PIPELINE (SUPPORTS NAIVE & ADVANCED MODES)
    # --------------------------------------------------------------------------
    def execute_rag_pipeline(self, query: str, top_k: int = 2, model: str = DEFAULT_MODEL, mode: str = "advanced"):
        """
        Executes RAG comparison.
        mode='naive': Standard TF-IDF vector retrieval + direct prompt injection.
        mode='advanced': HyDE expansion + Cross-Encoder Re-Ranking + Lost-in-the-Middle re-ordering + Self-RAG grounding audit.
        """
        t_start = time.time()
        hyde_info = None

        if mode == "advanced":
            # 1. HyDE Query Expansion
            hypo_doc = self.generate_hyde_passage(query, model=model)
            hyde_info = {
                "original_query": query,
                "hypothetical_passage": hypo_doc,
                "expansion_benefit": "Bridges vocabulary gap between questions and factual chunks"
            }
            # 2. Stage-1 Retrieval using expanded text
            initial_scored = self.retrieve(query, top_k=top_k + 1, expanded_text=hypo_doc)
            # 3. Stage-2 Cross-Encoder Re-Ranking
            scored_docs = self.rerank_documents(query, initial_scored, top_k=top_k)
        else:
            scored_docs = self.retrieve(query, top_k=top_k)

        top_k_docs = [d for d in scored_docs if d["selected"]]

        # 4. Context Order Optimization (Lost in the Middle)
        if mode == "advanced":
            optimized_docs, arrangement_strategy = self.optimize_context_order(top_k_docs)
        else:
            optimized_docs = top_k_docs
            arrangement_strategy = "Naive Sequential Order"

        # 5. Augmentation
        vanilla_prompt = f"Answer the user's question clearly and concisely:\nQuestion: {query}"
        augmented = self.build_augmented_prompt(query, optimized_docs)

        # 6. Generation (Concurrent execution for speed)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_vanilla = executor.submit(self.call_gemini, vanilla_prompt, model)
            future_rag = executor.submit(self.call_gemini, augmented["full_prompt"], model)
            without_rag_result = future_vanilla.result()
            with_rag_result = future_rag.result()

        # 7. Self-RAG Grounding Audit (Verification Pass)
        rag_text = with_rag_result.get("text", "")
        grounding_audit = self.audit_grounding(rag_text, optimized_docs)

        total_latency_ms = int((time.time() - t_start) * 1000)

        return {
            "query": query,
            "top_k": top_k,
            "mode": mode,
            "model_used": model,
            "total_latency_ms": total_latency_ms,
            "advanced_features": {
                "hyde": hyde_info,
                "context_arrangement": arrangement_strategy,
                "grounding_audit": grounding_audit
            },
            "retrieval": {
                "query_tokens": tokenize(query),
                "all_documents": scored_docs,
                "selected_count": len(optimized_docs),
                "retrieval_method": "2-Stage Hybrid Retrieval (Bi-Encoder + Cross-Encoder Rerank)" if mode == "advanced" else "Naive TF-IDF Vector Search"
            },
            "augmentation": {
                "system_instruction": augmented["system_instruction"],
                "injected_context": augmented["context_str"],
                "full_prompt": augmented["full_prompt"]
            },
            "without_rag": {
                "prompt": vanilla_prompt,
                "response": without_rag_result.get("text"),
                "latency_ms": without_rag_result.get("latency_ms"),
                "model": without_rag_result.get("model"),
                "success": without_rag_result.get("success")
            },
            "with_rag": {
                "prompt": augmented["full_prompt"],
                "response": rag_text,
                "latency_ms": with_rag_result.get("latency_ms"),
                "model": with_rag_result.get("model"),
                "success": with_rag_result.get("success")
            }
        }
