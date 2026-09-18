import unittest
import json
from app import app, engine

class TestRAGApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'RAG Explainer', resp.data)

    def test_get_documents(self):
        resp = self.client.get('/api/documents')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['count'], 5)

    def test_retrieve_only(self):
        resp = self.client.post('/api/retrieve-only', 
                                json={'query': 'What is the wifi password?', 'top_k': 2})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['documents']), len(engine.documents))
        # Verify Office Policies document is ranked #1
        top_doc = data['documents'][0]
        self.assertIn('Office Policies', top_doc['title'])
        self.assertIn('Wi-Fi', top_doc['content'])
        self.assertTrue(top_doc['selected'])

    def test_query_api(self):
        resp = self.client.post('/api/query',
                                json={'query': 'What is the launch date for Project NovaStar?', 'top_k': 1, 'model': 'gemini-flash-lite-latest'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        res_data = data['data']
        self.assertIn('without_rag', res_data)
        self.assertIn('with_rag', res_data)
        self.assertIn('retrieval', res_data)
        self.assertIn('augmentation', res_data)
        # Verify RAG answer contains November 24, 2026
        rag_text = res_data['with_rag']['response']
        print('Test RAG Response:', rag_text)
        self.assertTrue('2026' in rag_text or 'NovaStar' in rag_text)

    def test_advanced_rag_api(self):
        resp = self.client.post('/api/query',
                                json={'query': 'What is the refund policy credit percentage?', 'top_k': 2, 'mode': 'advanced', 'model': 'gemini-flash-lite-latest'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        res_data = data['data']
        self.assertEqual(res_data['mode'], 'advanced')
        self.assertIn('advanced_features', res_data)
        adv = res_data['advanced_features']
        self.assertIn('hyde', adv)
        self.assertIn('grounding_audit', adv)
        self.assertIn('context_arrangement', adv)
        # Check audit
        self.assertGreaterEqual(adv['grounding_audit']['grounding_score_pct'], 0)

if __name__ == '__main__':
    unittest.main()
