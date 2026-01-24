import sys, os
import unittest
# Hacer import local del paquete `cashflow` cuando se ejecutan tests desde la raíz del repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from cashflow.core import fv, pv, npv, irr


class TestCoreFinancials(unittest.TestCase):

    def test_fv_pv(self):
        self.assertAlmostEqual(fv(100, 0.1, 2), 121)
        self.assertAlmostEqual(pv(121, 0.1, 2), 100)

    def test_npv(self):
        cf = [-100, 60, 60]
        val = npv(0.1, cf)
        self.assertAlmostEqual(val, 4.132231405, places=6)

    def test_irr(self):
        cf = [-100, 60, 60]
        r = irr(cf)
        # validar que la tasa encontrada anula el NPV
        self.assertAlmostEqual(npv(r, cf), 0.0, places=6)


if __name__ == '__main__':
    unittest.main()
