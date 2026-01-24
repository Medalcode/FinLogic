import os, sys
import unittest

# allow importing module from src when running tests from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import aggregate_ohlc


class TestOHLC(unittest.TestCase):

    def test_aggregate_basic(self):
        rows = [
            {'ts': 100, 'price': 10},
            {'ts': 120, 'price': 12},
            {'ts': 150, 'price': 9},
            {'ts': 220, 'price': 11},
            {'ts': 260, 'price': 13},
        ]
        # interval 120 seconds -> buckets: [0..119], [120..239], [240..359]
        res = aggregate_ohlc(rows, 120)
        # expect 3 buckets
        self.assertEqual(len(res), 3)
        # first bucket: open 10, high 10, low 10, close 10
        self.assertEqual(res[0]['open'], 10)
        # second bucket contains 120,150,220 -> open 12, high 12, low 9, close 11
        self.assertEqual(res[1]['open'], 12)
        self.assertEqual(res[1]['close'], 11)
        # third bucket contains 260 -> open 13, close 13
        self.assertEqual(res[2]['open'], 13)
        self.assertEqual(res[2]['close'], 13)


if __name__ == '__main__':
    unittest.main()
