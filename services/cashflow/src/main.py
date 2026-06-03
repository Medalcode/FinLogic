import math
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from fastapi import FastAPI, Depends, Header, HTTPException, status
import os
from typing import List, Dict, Any, Optional
import statistics
import json
import time

try:
    from utils import (
        aggregate_ohlc,
        compute_var_historical,
        irr,
        load_market_rows,
        npv,
        read_prices_csv,
        read_prices_duckdb,
        resolve_data_path,
        summarize_prices,
    )
except ImportError:
    from services.cashflow.src.utils import (
        aggregate_ohlc,
        irr,
        load_market_rows,
        npv,
        resolve_data_path,
        summarize_prices,
    )

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
    cashflows: list[Decimal]
    rate: Decimal


class IRRRequest(BaseModel):
    cashflows: list[Decimal]


class MarketQuote(BaseModel):
    symbol: str = Field(..., min_length=1)
    price: Decimal
    ts: int

    @field_validator('price')
    @classmethod
    def check_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


@app.post("/npv")
def compute_npv(req: NPVRequest, api_key: str = Depends(validate_api_key)):
    result = npv(req.rate, req.cashflows)
    return {"npv": result}


@app.post("/irr")
def compute_irr(req: IRRRequest, api_key: str = Depends(validate_api_key)):
    result = irr(req.cashflows)
    return {"irr": result}


@app.post("/ingest")
def ingest_data(quotes: List[MarketQuote], api_key: str = Depends(validate_api_key)):
    """Ingesta de precios en formato Batch-over-HTTP."""
    out_dir = os.getenv('RAW_DIR', './data/raw')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "incoming.ndjson")
    
    with open(out_file, 'a') as f:
        for q in quotes:
            d = q.model_dump()
            d['price'] = float(d['price'])  # Serialize to float for json
            d['received_ts'] = int(time.time())
            f.write(json.dumps(d) + '\n')
            
    return {"status": "ok", "ingested": len(quotes)}


@app.get('/prices')
def get_prices(symbol: str | None = None, limit: int = 100, agg: str | None = None, interval: int = 60, data_file: str = None, offset: int | None = None, from_ts: int | None = None, to_ts: int | None = None, api_key: str = Depends(validate_api_key)):
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
def analytics_summary(symbol: str | None = None, from_ts: int | None = None, to_ts: int | None = None, confidence: float = 0.95, data_file: str = None, api_key: str = Depends(validate_api_key)):
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

