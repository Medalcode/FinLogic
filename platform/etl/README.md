ETL skeleton: carga NDJSON de `data/raw/market_prices.ndjson` a DuckDB.

Run:

```bash
pip install -r platform/etl/requirements.txt
python platform/etl/load_to_duckdb.py
```

Salida: `data/warehouse/market.duckdb` contiene la tabla `market_prices`.
