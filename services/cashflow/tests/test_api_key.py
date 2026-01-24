import os
import sys
import unittest
from fastapi import HTTPException

# allow importing package from src when running tests from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import main as app_main
from main import validate_api_key


class TestAPIKeyValidator(unittest.TestCase):

    def setUp(self):
        os.environ['API_KEY'] = 'unit-test-key'

    def tearDown(self):
        os.environ.pop('API_KEY', None)

    def test_validate_success_header(self):
        # simulate X-API-Key header
        key = validate_api_key(x_api_key='unit-test-key', authorization=None)
        self.assertEqual(key, 'unit-test-key')

    def test_validate_success_bearer(self):
        key = validate_api_key(x_api_key=None, authorization='Bearer unit-test-key')
        self.assertEqual(key, 'unit-test-key')

    def test_validate_missing(self):
        with self.assertRaises(HTTPException):
            validate_api_key(x_api_key=None, authorization=None)

    def test_validate_wrong(self):
        with self.assertRaises(HTTPException):
            validate_api_key(x_api_key='bad', authorization=None)


if __name__ == '__main__':
    unittest.main()
