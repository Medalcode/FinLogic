import os
import csv
import math
import statistics
from typing import List, Dict, Any, Optional


def resolve_data_path(data_file: Optional[str]) -> str:
    return data_file or os.getenv('DATA_FILE', './data/warehouse/market_prices.csv')


def uses_duckdb(path: str) -> bool:
    return path.endswith('.duckdb') or os.getenv('USE_DUCKDB') == '1'


def filter_rows(
    rows: List[Dict[str, Any]],
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
) -> List[Dict[str, Any]]:
    if from_ts is not None:
        rows = [r for r in rows if 'ts' in r and r['ts'] >= from_ts]
    if to_ts is not None:
        rows = [r for r in rows if 'ts' in r and r['ts'] <= to_ts]
    return rows


def load_market_rows(
    path: str,
    symbol: Optional[str] = None,
    limit: int = 100,
    offset: Optional[int] = None,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
) -> List[Dict[str, Any]]:
    if uses_duckdb(path):
        if not path.endswith('.duckdb'):
            raise ValueError(
                f"Invalid DATA_FILE for DuckDB mode: '{path}'. "
                "When USE_DUCKDB=1, DATA_FILE must end with '.duckdb'."
            )
        rows = read_prices_duckdb(path, symbol=symbol, limit=max(limit, 1000))
        rows = filter_rows(rows, from_ts=from_ts, to_ts=to_ts)
        if offset is None:
            return rows[-limit:]
        return rows[offset: offset + limit]

    return read_prices_csv(
        path,
        symbol=symbol,
        limit=limit,
        offset=offset,
        from_ts=from_ts,
        to_ts=to_ts,
    )


def summarize_prices(prices: List[float], confidence: float) -> Dict[str, Any]:
    if not prices:
        return {}
    return {
        'count': len(prices),
        'min': min(prices),
        'max': max(prices),
        'mean': statistics.mean(prices),
        'stdev': statistics.pstdev(prices) if len(prices) > 1 else 0.0,
        'var': compute_var_historical(prices, confidence=confidence),
    }


def read_prices_csv(path: str, symbol: Optional[str] = None, limit: int = 100, offset: Optional[int] = None, from_ts: Optional[int] = None, to_ts: Optional[int] = None) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, 'r') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            try:
                if 'price' in r and r['price'] != '':
                    r['price'] = float(r['price'])
                if 'ts' in r and r['ts'] != '':
                    r['ts'] = int(r['ts'])
            except Exception:
                pass
            if symbol and r.get('symbol') != symbol:
                continue
            if from_ts is not None and ('ts' not in r or r['ts'] < from_ts):
                continue
            if to_ts is not None and ('ts' not in r or r['ts'] > to_ts):
                continue
            rows.append(r)
    # sort ascending by ts
    rows = sorted(rows, key=lambda x: x.get('ts', 0))
    # pagination: if offset is None, return last `limit` rows for backward compatibility
    if offset is None:
        return rows[-limit:]
    else:
        return rows[offset: offset + limit]


def aggregate_ohlc(rows: List[Dict[str, Any]], interval_seconds: int) -> List[Dict[str, Any]]:
    if not rows:
        return []
    # ensure rows sorted by ts ascending
    sorted_rows = sorted([r for r in rows if 'ts' in r and 'price' in r], key=lambda x: int(x['ts']))
    buckets = {}
    order = []
    for r in sorted_rows:
        ts = int(r['ts'])
        price = float(r['price'])
        bucket = ts - (ts % interval_seconds)
        if bucket not in buckets:
            buckets[bucket] = {'open': price, 'high': price, 'low': price, 'close': price, 'count': 1}
            order.append(bucket)
        else:
            b = buckets[bucket]
            b['high'] = max(b['high'], price)
            b['low'] = min(b['low'], price)
            b['close'] = price
            b['count'] += 1
    result = []
    for b in sorted(order):
        item = buckets[b]
        result.append({'bucket_ts': b, 'open': item['open'], 'high': item['high'], 'low': item['low'], 'close': item['close'], 'count': item['count']})
    return result


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
    """Tasa interna de retorno por bisección."""
    def f(r: float) -> float:
        return npv(r, cashflows)

    low = -0.999999
    high = 10.0
    fl = f(low)
    fh = f(high)

    if fl * fh > 0:
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


def read_prices_duckdb(path: str, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Leer últimas `limit` filas desde una DuckDB `path` (tabla `market_prices`)."""
    try:
        import duckdb
    except Exception:
        return []
    try:
        base = 'SELECT * FROM market_prices'
        clauses = []
        if symbol:
            clauses.append(f"symbol = '{symbol}'")
        order = f" ORDER BY ts DESC LIMIT {int(limit)}"
        where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
        sql = base + where + order
        con = duckdb.connect(path)
        df = con.execute(sql).df()
        con.close()
        records = df.to_dict(orient='records')
        for r in records:
            if 'price' in r and r['price'] is not None:
                r['price'] = float(r['price'])
            if 'ts' in r and r['ts'] is not None:
                r['ts'] = int(r['ts'])
        return list(reversed(records))
    except Exception:
        return []


def compute_var_historical(prices: List[float], confidence: float = 0.95) -> float:
    """Compute historical VaR at `confidence` given a list of prices.
    VaR is returned as a positive fraction (e.g., 0.02 = 2%).
    """
    if not prices or len(prices) < 2:
        return 0.0
    returns = []
    for i in range(1, len(prices)):
        prev = prices[i - 1]
        cur = prices[i]
        if prev == 0: continue
        returns.append((cur - prev) / prev)
    if not returns: return 0.0
    returns_sorted = sorted(returns)
    q = (1.0 - float(confidence))
    idx = int(math.floor(q * len(returns_sorted)))
    idx = max(0, min(idx, len(returns_sorted) - 1))
    var_value = -returns_sorted[idx]
    return max(0.0, var_value)
