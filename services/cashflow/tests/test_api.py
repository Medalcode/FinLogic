import os
import unittest
from fastapi.testclient import TestClient
from services.cashflow.src.main import app


class TestAPIAuth(unittest.TestCase):

    def setUp(self):
        os.environ['API_KEY'] = 'test-key'
        self.client = TestClient(app)

    def tearDown(self):
        os.environ.pop('API_KEY', None)

    def test_prices_unauthorized(self):
        resp = self.client.get('/prices')
        self.assertEqual(resp.status_code, 401)

    def test_prices_with_key(self):
        headers = {'X-API-Key': 'test-key'}
        resp = self.client.get('/prices?data_file=./data/warehouse/market_prices.csv', headers=headers)
        self.assertIn(resp.status_code, (200, 204))


if __name__ == '__main__':
    unittest.main()
