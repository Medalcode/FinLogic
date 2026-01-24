import os, sys, tempfile, json
import unittest

# allow importing module from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import compute_var_historical


class TestAnalytics(unittest.TestCase):

    def test_var_basic(self):
        prices = [100, 98, 97, 99, 95]
        # compute returns: -0.02, -0.0102, 0.0206, -0.0404
        # sorted = [-0.0404, -0.02, -0.0102, 0.0206]
        # at confidence 0.95, q=0.05 -> idx= floor(0.05*4)=0 -> VaR = -(-0.0404)=0.0404
        v = compute_var_historical(prices, confidence=0.95)
        self.assertAlmostEqual(v, 0.0404, places=3)


if __name__ == '__main__':
    unittest.main()
