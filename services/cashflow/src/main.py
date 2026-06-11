import math
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ValidationError

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
def ingest_data(quotes: List[Dict[str, Any]], api_key: str = Depends(validate_api_key)):
    """Motor de Calidad Financiera: Ingesta, validación y segregación de anomalías."""
    out_dir = os.getenv('RAW_DIR', './data/raw')
    rej_dir = os.path.join(os.path.dirname(out_dir), 'rejected')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(rej_dir, exist_ok=True)
    
    out_file = os.path.join(out_dir, "incoming.ndjson")
    err_file = os.path.join(rej_dir, "error.ndjson")
    
    valid_count = 0
    rejected_count = 0
    anomalies = set()
    
    with open(out_file, 'a') as f_out, open(err_file, 'a') as f_err:
        for q in quotes:
            try:
                valid_quote = MarketQuote.model_validate(q)
                d = valid_quote.model_dump()
                d['price'] = float(d['price'])  # Serialize to float for json
                d['received_ts'] = int(time.time())
                f_out.write(json.dumps(d) + '\n')
                valid_count += 1
            except ValidationError as e:
                rejected_count += 1
                error_reasons = []
                for err in e.errors():
                    if err.get('type') == 'value_error' and 'greater than 0' in err.get('msg', ''):
                        error_reasons.append('negative_price')
                    elif err.get('type') == 'missing':
                        error_reasons.append(f"missing_{err.get('loc')[0]}")
                    else:
                        error_reasons.append(err.get('type'))
                
                anomalies.update(error_reasons)
                rej_record = {
                    "raw_data": q,
                    "errors": error_reasons,
                    "rejected_ts": int(time.time())
                }
                f_err.write(json.dumps(rej_record) + '\n')
            except Exception as e:
                rejected_count += 1
                anomalies.add("unknown_error")
                rej_record = {"raw_data": q, "errors": ["unknown_error"], "rejected_ts": int(time.time())}
                f_err.write(json.dumps(rej_record) + '\n')
                
    total = len(quotes)
    quality_score = (valid_count / total * 100) if total > 0 else 0.0
    
    return {
        "records_received": total,
        "valid": valid_count,
        "rejected": rejected_count,
        "quality_score": round(quality_score, 2),
        "anomalies": list(anomalies)
    }


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

