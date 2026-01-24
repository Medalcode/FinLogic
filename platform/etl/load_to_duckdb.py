"""ETL simple: lee NDJSON de `data/raw/market_prices.ndjson` y lo persiste en DuckDB.
Genera `data/warehouse/market.duckdb` con tabla `market_prices`.
"""
import os
import json
from typing import List

import pandas as pd
import duckdb

RAW_FILE = os.getenv('RAW_FILE', './data/raw/market_prices.ndjson')
DB_FILE = os.getenv('DB_FILE', './data/warehouse/market.duckdb')
TABLE = os.getenv('TABLE', 'market_prices')

os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)


def read_ndjson(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_to_duckdb(raw_file: str = RAW_FILE, db_file: str = DB_FILE, table: str = TABLE) -> int:
    rows = read_ndjson(raw_file)
    if not rows:
        print('No rows to load')
        return 0
    df = pd.DataFrame(rows)
    con = duckdb.connect(db_file)
    con.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df")
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    con.close()
    print(f'Loaded {count} rows into {db_file}::{table}')
    return count


if __name__ == '__main__':
    load_to_duckdb()
