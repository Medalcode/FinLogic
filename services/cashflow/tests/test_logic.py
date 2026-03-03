import os
import sys
import unittest
import tempfile
import statistics

# Aseguramos la ruta del src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from utils import aggregate_ohlc, read_prices_csv, fv, pv, npv, irr, compute_var_historical

class TestLibrary(unittest.TestCase):

    def test_financial_math(self):
        """Prueba funciones financieras básicas: FV, PV, NPV, IRR."""
        self.assertAlmostEqual(fv(100, 0.1, 2), 121)
        self.assertAlmostEqual(pv(121, 0.1, 2), 100)
        
        cf = [-100, 60, 60]
        val_npv = npv(0.1, cf)
        self.assertAlmostEqual(val_npv, 4.1322314, places=5)
        
        val_irr = irr(cf)
        self.assertAlmostEqual(npv(val_irr, cf), 0.0, places=5)

    def test_ohlc_aggregation(self):
        """Prueba la agregación de ticks a velas OHLC."""
        rows = [
            {'ts': 100, 'price': 10},
            {'ts': 120, 'price': 12},
            {'ts': 150, 'price': 9},
            {'ts': 220, 'price': 11},
            {'ts': 260, 'price': 13},
        ]
        # Agrupados por intervalos de 120s
        res = aggregate_ohlc(rows, 120)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[1]['open'], 12)
        self.assertEqual(res[1]['low'], 9)
        self.assertEqual(res[1]['close'], 11)

    def test_var_historical(self):
        """Prueba el cálculo de VaR Histórico."""
        prices = [100, 98, 97, 99, 95]
        v = compute_var_historical(prices, confidence=0.95)
        self.assertAlmostEqual(v, 0.0404, places=3)

class TestDataFilters(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile('w+', delete=False)
        self.path = self.tmp.name
        self.tmp.write('price,symbol,ts\n')
        self.tmp.write('10,USD,100\n')
        self.tmp.write('12,USD,120\n')
        self.tmp.write('9,USD,150\n')
        self.tmp.write('11,USD,220\n')
        self.tmp.write('13,USD,260\n')
        self.tmp.flush()

    def tearDown(self):
        try: os.unlink(self.path)
        except: pass

    def test_csv_filters(self):
        """Prueba filtros de rango de tiempo y paginación en archivos CSV."""
        rows = read_prices_csv(self.path, symbol='USD', limit=10, from_ts=120, to_ts=220)
        tss = [r['ts'] for r in rows]
        self.assertEqual(tss, [120, 150, 220])
        
        rows_page = read_prices_csv(self.path, symbol='USD', limit=2, offset=1)
        tss_page = [r['ts'] for r in rows_page]
        self.assertEqual(tss_page, [120, 150])

if __name__ == '__main__':
    unittest.main()
