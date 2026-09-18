"""
gemini_client.py
================
Unified Google Gemini API Client for LangGraph examples.
Configured with the user's API key and robust fallback mechanisms.
"""

import os
import json
import time
import re
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "")

# Primary fast model and reasoning model
DEFAULT_FAST_MODEL = "gemini-flash-lite-latest"
DEFAULT_REASONING_MODEL = "gemini-flash-latest"


def call_gemini(
    prompt: str,
    system_instruction: Optional[str] = None,
    model: str = DEFAULT_FAST_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    timeout: int = 20,
    retries: int = 2
) -> Dict[str, Any]:
    """
    Direct, low-latency REST call to Google Gemini generateContent API.
    Returns:
        dict: {
            "success": bool,
            "text": str,
            "model": str,
            "latency_ms": int,
            "error": Optional[str]
        }
    """
    start_time = time.time()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": API_KEY
    }

    contents = []
    if system_instruction:
        contents.append({
            "role": "user",
            "parts": [{"text": f"[System Instructions]: {system_instruction}"}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood. I will strictly follow these instructions."}]
        })

    contents.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }

    last_error = ""
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            latency_ms = int((time.time() - start_time) * 1000)

            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    return {
                        "success": True,
                        "text": text,
                        "model": model,
                        "latency_ms": latency_ms,
                        "error": None
                    }
            elif resp.status_code == 429:
                sleep_sec = 1.5 * (attempt + 1)
                time.sleep(sleep_sec)
                last_error = f"Rate limited (429): {resp.text[:120]}"
                continue
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"
        except requests.exceptions.Timeout:
            last_error = f"Request timed out ({timeout}s)"
        except Exception as e:
            last_error = str(e)

    # Automatic fallback to ultra-fast lite model if another model was attempted
    if model != DEFAULT_FAST_MODEL:
        return call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            model=DEFAULT_FAST_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=15,
            retries=1
        )

    latency_ms = int((time.time() - start_time) * 1000)
    return {
        "success": False,
        "text": f"Error calling Gemini: {last_error}",
        "model": model,
        "latency_ms": latency_ms,
        "error": last_error
    }


def call_gemini_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    model: str = DEFAULT_FAST_MODEL,
    retries: int = 2
) -> Dict[str, Any]:
    """
    Call Gemini and parse the response strictly as a JSON object or array.
    Automatically strips markdown code fence wrappers (```json ... ```).
    """
    formatting_prompt = (
        f"{prompt}\n\n"
        "CRITICAL: Respond ONLY with valid JSON (no explanation, no markdown wrappers, no backticks)."
    )
    result = call_gemini(
        prompt=formatting_prompt,
        system_instruction=system_instruction,
        model=model,
        temperature=0.1,
        retries=retries
    )

    if not result["success"]:
        return {"parsed": None, "raw": result["text"], "error": result["error"]}

    raw_text = result["text"].strip()
    # Strip ```json ... ``` if model added it
    cleaned_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r"\s*```$", "", cleaned_text, flags=re.MULTILINE).strip()

    try:
        parsed_data = json.loads(cleaned_text)
        return {"parsed": parsed_data, "raw": raw_text, "error": None}
    except Exception as e:
        # Fallback regex extraction of first {...} or [...] block
        match = re.search(r"(\{.*\}|\[.*\])", cleaned_text, re.DOTALL)
        if match:
            try:
                parsed_data = json.loads(match.group(1))
                return {"parsed": parsed_data, "raw": raw_text, "error": None}
            except Exception:
                pass
        return {"parsed": None, "raw": raw_text, "error": f"JSON parse error: {str(e)}"}


if __name__ == "__main__":
    print("Testing gemini_client.py...")
    res = call_gemini("Say 'LangGraph is ready!' in 5 words.")
    print("Direct Gemini response:", res)
    json_res = call_gemini_json("Return a JSON object with key 'status'='active' and 'tools'=['retriever', 'search']")
    print("JSON Gemini response:", json_res)
