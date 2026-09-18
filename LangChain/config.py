"""
Configuration & Model Initializers for LangChain Examples
=========================================================
Configures Google Gemini API connectivity, model parameters, and factory
helpers for both LLM generation and vector embeddings.
"""

import os
import sys
import warnings

# Ensure Windows consoles cleanly output UTF-8 without charmap errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Suppress harmless LangChain / Google AFC warning notices in terminal
warnings.filterwarnings("ignore", message=".*Direct use of automatic function calling.*")
warnings.filterwarnings("ignore", category=UserWarning)

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# The user-provided Google Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# Model identifiers supported on this API key
PRIMARY_MODEL = "gemini-3.6-flash"
FAST_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "models/gemini-embedding-001"

def get_llm(model: str = PRIMARY_MODEL, temperature: float = 0.2, max_retries: int = 3):
    """
    Returns a configured ChatGoogleGenerativeAI instance.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        max_retries=max_retries
    )

def get_embeddings(model: str = EMBEDDING_MODEL):
    """
    Returns a configured GoogleGenerativeAIEmbeddings instance.
    Produces 3072-dimensional semantic embeddings.
    """
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model=model,
        google_api_key=GEMINI_API_KEY
    )

def extract_text(content) -> str:
    """
    Safely normalizes LangChain/Gemini message content into a clean string.
    Handles strings, lists of content dicts [{'type': 'text', 'text': '...'}], etc.
    """
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
        return "".join(parts).strip()
    return str(content).strip()
