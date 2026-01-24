import os, sys, tempfile
import unittest

# allow importing main from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import read_prices_csv


class TestFilters(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile('w+', delete=False)
        self.path = self.tmp.name
        # write header and some rows
        self.tmp.write('price,symbol,ts\n')
        self.tmp.write('10,USD,100\n')
        self.tmp.write('12,USD,120\n')
        self.tmp.write('9,USD,150\n')
        self.tmp.write('11,USD,220\n')
        self.tmp.write('13,USD,260\n')
        self.tmp.flush()

    def tearDown(self):
        try:
            os.unlink(self.path)
        except Exception:
            pass

    def test_from_to_filter(self):
        rows = read_prices_csv(self.path, symbol='USD', limit=10, offset=None, from_ts=120, to_ts=220)
        # should include ts 120,150,220
        tss = [r['ts'] for r in rows]
        self.assertEqual(tss, [120, 150, 220])

    def test_pagination_offset(self):
        # offset 1, limit 2 -> should return ts 120,150
        rows = read_prices_csv(self.path, symbol='USD', limit=2, offset=1)
        tss = [r['ts'] for r in rows]
        self.assertEqual(tss, [120, 150])


if __name__ == '__main__':
    unittest.main()
