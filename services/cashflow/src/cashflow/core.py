"""Funciones de cálculo financiero básicas: FV, PV, NPV y IRR.
Implementadas en Python puro para facilitar pruebas sin dependencias.
"""
from typing import List


def fv(pv: float, rate: float, n: int) -> float:
    """Valor futuro de un monto `pv` a tasa `rate` durante `n` periodos."""
    return pv * (1 + rate) ** n


def pv(fv_value: float, rate: float, n: int) -> float:
    """Valor presente de un monto futuro."""
    return fv_value / (1 + rate) ** n


def npv(rate: float, cashflows: List[float]) -> float:
    """Valor actual neto de una serie de `cashflows` con tasa `rate`.
    Se asume `cashflows[0]` en t=0.
    """
    return sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))


def irr(cashflows: List[float], tol: float = 1e-6, max_iter: int = 200) -> float:
    """Tasa interna de retorno por bisección.

    Busca r tal que NPV(r) = 0. Requiere que exista un cambio de signo en el rango de búsqueda.
    """
    def f(r: float) -> float:
        return npv(r, cashflows)

    low = -0.999999
    high = 10.0
    fl = f(low)
    fh = f(high)

    if fl * fh > 0:
        # intentar expandir el límite superior
        for _ in range(60):
            high *= 2
            fh = f(high)
            if fl * fh <= 0:
                break
        else:
            raise ValueError("No se encontró cambio de signo para calcular IRR")

    for _ in range(max_iter):
        mid = (low + high) / 2
        fm = f(mid)
        if abs(fm) < tol:
            return mid
        if fl * fm < 0:
            high = mid
            fh = fm
        else:
            low = mid
            fl = fm
    return (low + high) / 2
