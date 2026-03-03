import os
import sys
import unittest
import tempfile
from fastapi.testclient import TestClient

# Permitir importar el módulo desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import app, validate_api_key

class TestAPI(unittest.TestCase):
    def setUp(self):
        os.environ['API_KEY'] = 'test-key'
        self.client = TestClient(app)

    def tearDown(self):
        os.environ.pop('API_KEY', None)

    def test_auth_unauthorized(self):
        resp = self.client.get('/prices')
        self.assertEqual(resp.status_code, 401)

    def test_auth_success_x_api_key(self):
        headers = {'X-API-Key': 'test-key'}
        # Verificamos que al menos no de 401 si enviamos la llave correcta
        resp = self.client.get('/prices', headers=headers)
        self.assertNotEqual(resp.status_code, 401)

    def test_auth_success_bearer(self):
        headers = {'Authorization': 'Bearer test-key'}
        resp = self.client.get('/prices', headers=headers)
        self.assertNotEqual(resp.status_code, 401)

    def test_npv_endpoint(self):
        headers = {'X-API-Key': 'test-key'}
        payload = {"cashflows": [-100, 60, 60], "rate": 0.1}
        resp = self.client.post("/npv", json=payload, headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertAlmostEqual(resp.json()["npv"], 4.1322314, places=5)

    def test_irr_endpoint(self):
        headers = {'X-API-Key': 'test-key'}
        payload = {"cashflows": [-100, 60, 60]}
        resp = self.client.post("/irr", json=payload, headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("irr", resp.json())

if __name__ == '__main__':
    unittest.main()
