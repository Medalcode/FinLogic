from fastapi import FastAPI, Depends, Header, HTTPException, status
from pydantic import BaseModel
import os
from typing import List, Dict, Any, Optional
import statistics
import math

try:
    from utils import aggregate_ohlc, read_prices_csv, npv, irr, read_prices_duckdb, compute_var_historical, resolve_data_path, load_market_rows, summarize_prices
except ImportError:
    from services.cashflow.src.utils import aggregate_ohlc, read_prices_csv, npv, irr, read_prices_duckdb, compute_var_historical, resolve_data_path, load_market_rows, summarize_prices

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
    path = resolve_data_path(data_file)
    try:
        rows = load_market_rows(
            path,
            symbol=symbol,
            limit=limit,
            offset=offset,
            from_ts=from_ts,
            to_ts=to_ts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if agg == 'ohlc':
        agg_rows = aggregate_ohlc(rows, interval)
        return {"count": len(agg_rows), "rows": agg_rows}

    return {"count": len(rows), "rows": rows}



@app.get('/analytics/summary')
def analytics_summary(symbol: Optional[str] = None, from_ts: Optional[int] = None, to_ts: Optional[int] = None, confidence: float = 0.95, data_file: str = None, api_key: str = Depends(validate_api_key)):
    """Devuelve resumen estadístico y VaR histórico para `symbol` en el rango dado.

    Usa DuckDB si `data_file` apunta a `.duckdb`, sino CSV.
    """
    path = resolve_data_path(data_file)
    try:
        rows = load_market_rows(
            path,
            symbol=symbol,
            limit=1000000,
            offset=0,
            from_ts=from_ts,
            to_ts=to_ts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    prices = [float(r['price']) for r in rows if 'price' in r and r['price'] is not None]
    if not prices:
        return {'count': 0, 'summary': {}, 'var': 0.0}
    summary = summarize_prices(prices, confidence)
    var = summary.pop('var')
    return {'count': len(prices), 'summary': summary, 'var': var}

