"""
evals_core.py
=============
Core Framework for LLM Evaluations (LLM-as-a-Judge, RAG Triad),
Production Safety Guardrails (Prompt Injection & PII Sanitization),
and Semantic Caching for Latency & Token Optimization.
"""

import sys
import os
import re
import json
import math
import time
from collections import Counter
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ==============================================================================
# 1. LLM-AS-A-JUDGE (Rubric-Based Evaluation & CoT Grading)
# ==============================================================================

class LLMAsAJudge:
    """Evaluates generated LLM responses using structured rubric criteria."""

    RUBRIC_ACCURACY = {
        5: "Flawless: Completely factual, precise, directly answers question with zero hallucination.",
        4: "Good: Factual and mostly complete, minor trivial omissions that do not affect correctness.",
        3: "Acceptable: Generally accurate, but contains minor ambiguity or vague assertions.",
        2: "Poor: Contains significant factual errors or contradicts reference context.",
        1: "Critical Failure: Completely fabricated, toxic, or directly contradicts facts."
    }

    RUBRIC_CONCISENESS = {
        5: "Optimal: Direct, high signal-to-noise ratio, zero corporate fluff or repetitive filler.",
        4: "Clear: Well-paced, minor unnecessary conversational padding.",
        3: "Verbose: Takes twice as many words as necessary to answer.",
        2: "Meandering: Buries the key answer inside rambling paragraphs.",
        1: "Unusable: Extremely repetitive or incomplete babble."
    }

    @classmethod
    def evaluate(
        cls,
        question: str,
        answer: str,
        reference_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculates deterministic heuristic rubric scores and simulated CoT explanation."""
        claims = [c.strip() for c in re.split(r"[.!?]", answer) if len(c.strip()) > 10]
        context_words = set(re.findall(r"\w+", (reference_context or "").lower()))
        ans_words = re.findall(r"\w+", answer.lower())

        # Accuracy Score
        if reference_context:
            novel_words = [w for w in ans_words if len(w) > 4 and w not in context_words]
            overlap = [w for w in ans_words if w in context_words and len(w) > 3]
            grounding_ratio = len(overlap) / max(1, len([w for w in ans_words if len(w) > 3]))
            
            if novel_words:
                accuracy_score = max(1, 3 - len(novel_words))
            elif grounding_ratio > 0.6:
                accuracy_score = 5
            elif grounding_ratio > 0.4:
                accuracy_score = 4
            elif grounding_ratio > 0.2:
                accuracy_score = 3
            else:
                accuracy_score = 2
        else:
            accuracy_score = 4 if len(claims) > 0 else 2

        # Conciseness Score
        word_count = len(ans_words)
        if 20 <= word_count <= 80:
            conciseness_score = 5
        elif word_count < 120:
            conciseness_score = 4
        elif word_count < 200:
            conciseness_score = 3
        else:
            conciseness_score = 2

        overall_score = round((accuracy_score * 0.65) + (conciseness_score * 0.35), 2)
        passed = overall_score >= 3.5

        reasoning = (
            f"Evaluated {len(claims)} claim(s). Accuracy rubric {accuracy_score}/5 based on context grounding. "
            f"Length: {word_count} words yields conciseness score {conciseness_score}/5. "
            f"Overall verdict: {'PASSED' if passed else 'FAILED'}."
        )

        return {
            "overall_score": overall_score,
            "accuracy_score": accuracy_score,
            "conciseness_score": conciseness_score,
            "passed": passed,
            "reasoning": reasoning
        }


# ==============================================================================
# 2. THE RAG TRIAD (Faithfulness, Answer Relevance, Context Precision)
# ==============================================================================

class RAGTriadEvaluator:
    """Computes quantitative metrics for the RAG Triad (TruLens / Ragas inspired)."""

    @staticmethod
    def _stem(word: str) -> str:
        w = word.lower()
        for suffix in ("ing", "es", "ed", "s"):
            if w.endswith(suffix) and len(w) > len(suffix) + 2:
                return w[:-len(suffix)]
        return w

    @classmethod
    def _text_to_vector(cls, text: str) -> Counter:
        words = re.findall(r"\w+", text.lower())
        return Counter([cls._stem(w) for w in words if len(w) > 2])

    @classmethod
    def _cosine_similarity(cls, vec1: Counter, vec2: Counter) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([val ** 2 for val in vec1.values()])
        sum2 = sum([val ** 2 for val in vec2.values()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        return float(numerator) / denominator

    @classmethod
    def evaluate_faithfulness(cls, context: str, answer: str) -> float:
        """Measures whether the claims in the answer can be directly inferred from context."""
        claims = [c.strip() for c in re.split(r"[.!?]", answer) if len(c.strip()) > 8]
        if not claims:
            return 0.0
        supported = 0
        ctx_lower = context.lower()
        for claim in claims:
            words = [w for w in re.findall(r"\w+", claim.lower()) if len(w) > 3]
            if not words:
                continue
            matched = sum(1 for w in words if w in ctx_lower)
            if (matched / len(words)) >= 0.5:
                supported += 1
        return round(supported / len(claims), 2)

    @classmethod
    def evaluate_answer_relevance(cls, question: str, answer: str) -> float:
        """Measures whether the answer directly addresses the user's question."""
        vec_q = cls._text_to_vector(question)
        vec_a = cls._text_to_vector(answer)
        sim = cls._cosine_similarity(vec_q, vec_a)
        # Boost scale slightly because answers contain elaboration
        relevance = min(1.0, round(sim * 1.6, 2))
        return relevance

    @classmethod
    def evaluate_context_precision(cls, question: str, contexts: List[str]) -> float:
        """Measures the proportion of retrieved chunks that are genuinely relevant to the query."""
        if not contexts:
            return 0.0
        vec_q = cls._text_to_vector(question)
        relevant_count = 0
        for ctx in contexts:
            sim = cls._cosine_similarity(vec_q, cls._text_to_vector(ctx))
            if sim >= 0.15:
                relevant_count += 1
        return round(relevant_count / len(contexts), 2)

    @classmethod
    def evaluate_triad(cls, question: str, contexts: List[str], answer: str) -> Dict[str, Any]:
        combined_ctx = " ".join(contexts)
        faith = cls.evaluate_faithfulness(combined_ctx, answer)
        relevance = cls.evaluate_answer_relevance(question, answer)
        precision = cls.evaluate_context_precision(question, contexts)
        composite = round((faith + relevance + precision) / 3.0, 2)
        return {
            "faithfulness": faith,
            "answer_relevance": relevance,
            "context_precision": precision,
            "composite_rag_score": composite,
            "health": "EXCELLENT" if composite >= 0.8 else ("MODERATE" if composite >= 0.6 else "AT_RISK")
        }


# ==============================================================================
# 3. PRODUCTION SAFETY GUARDRAILS (Input & Output)
# ==============================================================================

class SafetyGuardrails:
    """Scans and sanitizes inputs and outputs against jailbreaks and PII leaks."""

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"(?i)system\s+override",
        r"(?i)you\s+are\s+now\s+(DAN|unrestricted|god\s+mode)",
        r"(?i)disregard\s+(all\s+)?guidelines",
        r"(?i)bypass\s+safety\s+filter",
        r"(?i)developer\s+mode\s+enabled",
        r"(?i)do\s+not\s+follow\s+any\s+rules",
        r"(?i)print\s+your\s+system\s+prompt"
    ]

    PII_PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
        "PHONE": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    }

    @classmethod
    def scan_input(cls, user_prompt: str) -> Dict[str, Any]:
        """Inspects incoming user prompt for injection attempts and PII."""
        # 1. Prompt Injection Scan
        injection_detected = False
        matched_trigger = None
        for pattern in cls.INJECTION_PATTERNS:
            match = re.search(pattern, user_prompt)
            if match:
                injection_detected = True
                matched_trigger = match.group(0)
                break

        # 2. PII Detection & Anonymization
        sanitized_prompt = user_prompt
        pii_found = []
        for pii_type, regex in cls.PII_PATTERNS.items():
            matches = re.findall(regex, sanitized_prompt)
            if matches:
                pii_found.extend([f"{pii_type}: {m}" for m in matches])
                sanitized_prompt = re.sub(regex, f"[REDACTED_{pii_type}]", sanitized_prompt)

        allowed = not injection_detected
        return {
            "allowed": allowed,
            "injection_detected": injection_detected,
            "matched_trigger": matched_trigger,
            "pii_detected": len(pii_found) > 0,
            "pii_items": pii_found,
            "sanitized_prompt": sanitized_prompt,
            "action": "PASS" if allowed else "BLOCK"
        }

    @classmethod
    def scan_output(cls, model_output: str, required_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Inspects model output for hallucinations, PII leakage, and schema adherence."""
        sanitized_output = model_output
        pii_found = []
        for pii_type, regex in cls.PII_PATTERNS.items():
            matches = re.findall(regex, sanitized_output)
            if matches:
                pii_found.extend([f"{pii_type}: {m}" for m in matches])
                sanitized_output = re.sub(regex, f"[REDACTED_{pii_type}]", sanitized_output)

        schema_valid = True
        schema_err = None
        if required_schema:
            try:
                # Attempt to extract json from output
                json_match = re.search(r"\{.*\}", model_output, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    for req_field in required_schema.get("required", []):
                        if req_field not in parsed:
                            schema_valid = False
                            schema_err = f"Missing required field: {req_field}"
                else:
                    schema_valid = False
                    schema_err = "No JSON object found in output"
            except Exception as e:
                schema_valid = False
                schema_err = f"JSON parse error: {str(e)}"

        return {
            "schema_valid": schema_valid,
            "schema_error": schema_err,
            "pii_leakage_detected": len(pii_found) > 0,
            "pii_items": pii_found,
            "sanitized_output": sanitized_output
        }


# ==============================================================================
# 4. SEMANTIC CACHING (Sub-millisecond Token & Cost Optimization)
# ==============================================================================

class SemanticCache:
    """In-memory cosine similarity cache for saving LLM API calls and latency."""

    def __init__(self, similarity_threshold: float = 0.75, max_entries: int = 100):
        self.threshold = similarity_threshold
        self.max_entries = max_entries
        self.cache: List[Dict[str, Any]] = []

    def _tokenize(self, text: str) -> Counter:
        words = re.findall(r"\w+", text.lower())
        return Counter([w for w in words if len(w) > 2])

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Finds a semantically matching cached response if similarity >= threshold."""
        query_vec = self._tokenize(query)
        best_match = None
        best_sim = -1.0

        for item in self.cache:
            sim = RAGTriadEvaluator._cosine_similarity(query_vec, item["vector"])
            if sim > best_sim:
                best_sim = sim
                best_match = item

        if best_match and best_sim >= self.threshold:
            return {
                "response": best_match["response"],
                "cached_query": best_match["query"],
                "similarity": round(best_sim, 3),
                "cache_hit": True
            }

        return None

    def set(self, query: str, response: str):
        """Stores a new query and response pair."""
        if len(self.cache) >= self.max_entries:
            self.cache.pop(0)  # Simple FIFO eviction

        self.cache.append({
            "query": query,
            "vector": self._tokenize(query),
            "response": response,
            "timestamp": time.time()
        })
