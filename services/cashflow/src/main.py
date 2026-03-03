from fastapi import FastAPI, Depends, Header, HTTPException, status
from pydantic import BaseModel
import os
from typing import List, Dict, Any, Optional
import statistics
import math

try:
    from utils import aggregate_ohlc, read_prices_csv, npv, irr, read_prices_duckdb, compute_var_historical
except ImportError:
    from services.cashflow.src.utils import aggregate_ohlc, read_prices_csv, npv, irr, read_prices_duckdb, compute_var_historical

app = FastAPI(title="Cashflow Service")


def validate_api_key(x_api_key: str = Header(None), authorization: str = Header(None)) -> str:
    """Validar API key a través de header `X-API-Key` o `Authorization: Bearer <key>`.
    Lee la clave esperada dinámicamente desde la variable de entorno `API_KEY`.
    """
    expected = os.getenv('API_KEY', 'dev-key')
    key = None
    if x_api_key:
        key = x_api_key
    elif authorization and authorization.lower().startswith('bearer'):
        parts = authorization.split()
        if len(parts) == 2:
            key = parts[1]

    if not key or key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or missing API key')
    return key


class NPVRequest(BaseModel):
    cashflows: list[float]
    rate: float


class IRRRequest(BaseModel):
    cashflows: list[float]


@app.post("/npv")
def compute_npv(req: NPVRequest, api_key: str = Depends(validate_api_key)):
    result = npv(req.rate, req.cashflows)
    return {"npv": result}


@app.post("/irr")
def compute_irr(req: IRRRequest, api_key: str = Depends(validate_api_key)):
    result = irr(req.cashflows)
    return {"irr": result}


@app.get('/prices')
def get_prices(symbol: Optional[str] = None, limit: int = 100, agg: Optional[str] = None, interval: int = 60, data_file: str = None, offset: Optional[int] = None, from_ts: Optional[int] = None, to_ts: Optional[int] = None, api_key: str = Depends(validate_api_key)):
    """Devuelve las últimas `limit` observaciones del CSV (filtrado por `symbol` si se indica).

    `data_file` puede pasar por query para tests; por defecto usa `DATA_FILE` env var o
    `./data/warehouse/market_prices.csv`.
    """
    default_path = os.getenv('DATA_FILE', './data/warehouse/market_prices.csv')
    path = data_file or default_path
    # if path points to a DuckDB file, read from it
    if path.endswith('.duckdb') or os.getenv('USE_DUCKDB') == '1':
        # DuckDB reader currently supports symbol + limit; we load extra and then post-filter
        rows = read_prices_duckdb(path, symbol=symbol, limit=max(limit, 1000))
        # apply from_ts/to_ts filters in-memory
        if from_ts is not None:
            rows = [r for r in rows if 'ts' in r and r['ts'] >= from_ts]
        if to_ts is not None:
            rows = [r for r in rows if 'ts' in r and r['ts'] <= to_ts]
        # default behavior: return last `limit` rows
        if offset is None:
            rows = rows[-limit:]
        else:
            rows = rows[offset: offset + limit]
    else:
        rows = read_prices_csv(path, symbol=symbol, limit=limit, offset=offset, from_ts=from_ts, to_ts=to_ts)

    if agg == 'ohlc':
        agg_rows = aggregate_ohlc(rows, interval)
        return {"count": len(agg_rows), "rows": agg_rows}
    # support aggregation
    agg = None
    try:
        from fastapi import Request
    except Exception:
        Request = None

    # try to get query param `agg`/`interval` via environment fallback (FastAPI passes query params directly)
    # but function params can't directly accept `agg` so read from request via dependency if present.
    # Simpler: parse from query string available through os.environ override `AGG`/`AGG_INTERVAL` for tests.
    agg = os.getenv('AGG', None)
    interval = int(os.getenv('AGG_INTERVAL', '60'))

    # If FastAPI provided query params (in typical usage, these are function args), allow them by checking a specially passed `data_file` format.
    # To keep this endpoint simple and testable, also accept agg and interval via query-like `data_file` suffix, e.g. data.csv||agg=ohlc&interval=60
    if data_file and '||' in data_file:
        path_part, qs = data_file.split('||', 1)
        path = path_part
        for kv in qs.split('&'):
            if '=' in kv:
                k, v = kv.split('=', 1)
                if k == 'agg':
                    agg = v
                if k == 'interval':
                    try:
                        interval = int(v)
                    except Exception:
                        pass
        rows = read_prices_csv(path, symbol=symbol, limit=limit)

    if agg == 'ohlc':
        agg_rows = aggregate_ohlc(rows, interval)
        return {"count": len(agg_rows), "rows": agg_rows}

    return {"count": len(rows), "rows": rows}



@app.get('/analytics/summary')
def analytics_summary(symbol: Optional[str] = None, from_ts: Optional[int] = None, to_ts: Optional[int] = None, confidence: float = 0.95, data_file: str = None, api_key: str = Depends(validate_api_key)):
    """Devuelve resumen estadístico y VaR histórico para `symbol` en el rango dado.

    Usa DuckDB si `data_file` apunta a `.duckdb`, sino CSV.
    """
    default_path = os.getenv('DATA_FILE', './data/warehouse/market_prices.csv')
    path = data_file or default_path
    # obtener filas (precio) en orden asc
    if path.endswith('.duckdb') or os.getenv('USE_DUCKDB') == '1':
        rows = read_prices_duckdb(path, symbol=symbol, limit=1000000)
    else:
        rows = read_prices_csv(path, symbol=symbol, limit=1000000, offset=0, from_ts=from_ts, to_ts=to_ts)
    if from_ts is not None:
        rows = [r for r in rows if 'ts' in r and r['ts'] >= from_ts]
    if to_ts is not None:
        rows = [r for r in rows if 'ts' in r and r['ts'] <= to_ts]
    prices = [float(r['price']) for r in rows if 'price' in r and r['price'] is not None]
    if not prices:
        return {'count': 0, 'summary': {}, 'var': 0.0}
    summary = {}
    summary['count'] = len(prices)
    summary['min'] = min(prices)
    summary['max'] = max(prices)
    summary['mean'] = statistics.mean(prices)
    summary['stdev'] = statistics.pstdev(prices) if len(prices) > 1 else 0.0
    var = compute_var_historical(prices, confidence=confidence)
    return {'count': len(prices), 'summary': summary, 'var': var}

