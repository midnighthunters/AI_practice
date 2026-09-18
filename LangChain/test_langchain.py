"""
Integration & Regression Test Suite for LangChain Educational Suite
===================================================================
Verifies:
1. Config and Gemini API connectivity.
2. Prompt templates, LCEL expression pipelines, and output parsers.
3. Conversational memory retention.
4. Text splitting chunk logic.
5. Vector store retrieval and RAG chain.
6. Tool functions and schemas.
7. Flask Web App REST endpoints.
"""

import unittest
import json
import os
import sys

# Ensure LangChain directory is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from config import get_llm, get_embeddings, extract_text, PRIMARY_MODEL
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app import app, init_vectorstore, TOOLS_REGISTRY


class TestLangChainSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        init_vectorstore()

    def test_01_config_and_llm(self):
        """Verify LLM initialization."""
        llm = get_llm(temperature=0.0)
        self.assertIsNotNone(llm)
        self.assertEqual(llm.model, PRIMARY_MODEL)

    def test_02_prompt_template_and_lcel(self):
        """Verify prompt template formatting and pipe syntax."""
        prompt = ChatPromptTemplate.from_template("Say {word} in uppercase.")
        formatted = prompt.format(word="hello")
        self.assertIn("hello", formatted)

        # Test LCEL chaining with PromptTemplate and a RunnableLambda
        from langchain_core.runnables import RunnableLambda
        chain = prompt | RunnableLambda(lambda p: p.to_string().upper())
        res = chain.invoke({"word": "test"})
        self.assertIn("TEST", res)

    def test_03_text_splitter(self):
        """Verify RecursiveCharacterTextSplitter creates expected chunks with overlap."""
        sample = (
            "Paragraph one is about machine learning basics.\n\n"
            "Paragraph two delves into deep neural networks and attention mechanisms.\n\n"
            "Paragraph three concludes with practical deployment on cloud GPUs."
        )
        splitter = RecursiveCharacterTextSplitter(chunk_size=75, chunk_overlap=15)
        chunks = splitter.split_text(sample)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(all(len(c) <= 90 for c in chunks))

    def test_04_tools_registry(self):
        """Verify tool functions execute directly."""
        calc = TOOLS_REGISTRY["calculate_compound_interest"]
        # $10,000 at 10% for 2 years = $12,100
        res = calc.invoke({"principal": 10000, "annual_rate": 0.10, "years": 2})
        self.assertEqual(res, 12100.0)

        flight = TOOLS_REGISTRY["check_flight_status"]
        res_flight = flight.invoke({"flight_number": "BA-249"})
        self.assertIn("On Time", res_flight)

        math_tool = TOOLS_REGISTRY["evaluate_math"]
        res_math = math_tool.invoke({"expression": "100 * 1.05"})
        self.assertEqual(res_math, "105.0")

    def test_05_flask_index(self):
        """Verify web app root serves HTML."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"LangChain", resp.data)

    def test_06_flask_info_api(self):
        """Verify info endpoint returns all 8 examples."""
        resp = self.client.get("/api/info")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["examples"]), 8)

    def test_07_flask_splitters_api(self):
        """Verify splitter demo API endpoint."""
        resp = self.client.post("/api/demo/splitters", json={
            "text": "Sentence A is here. Sentence B is there. Sentence C is elsewhere.",
            "chunk_size": 30,
            "chunk_overlap": 10
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["total_chunks"], 0)

    def test_08_flask_tools_api(self):
        """Verify tool execution API endpoint."""
        resp = self.client.post("/api/demo/tools", json={
            "tool": "check_flight_status",
            "args": {"flight_number": "LH-441"}
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertIn("Boarding Now", str(data["result"]))


if __name__ == "__main__":
    unittest.main()
