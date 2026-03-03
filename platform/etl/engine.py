"""ETL Engine: Motor consolidado de ingesta y transformación.
Fusiona la lógica de CSV, DuckDB y el Runner en una única interfaz paramétrica.
"""
import os
import json
import csv
import time
import glob
from typing import List, Dict, Any, Optional

# Configuración vía Variables de Entorno
RAW_DIR = os.getenv('RAW_DIR', './data/raw')
RAW_FILE = os.getenv('RAW_FILE', './data/raw/market_prices.ndjson')
OUT_FILE_CSV = os.getenv('OUT_FILE_CSV', './data/warehouse/market_prices.csv')
DB_FILE = os.getenv('DB_FILE', './data/warehouse/market.duckdb')
TABLE_NAME = os.getenv('TABLE_NAME', 'market_prices')
ETL_INTERVAL = int(os.getenv('ETL_INTERVAL', '15'))
ETL_MODE = os.getenv('ETL_MODE', 'duckdb')  # 'csv' o 'duckdb'

def read_ndjson(path: str) -> List[Dict[str, Any]]:
    """Lee archivos NDJSON desde un path específico."""
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows

def write_csv(rows: List[Dict[str, Any]], out_file: str) -> int:
    """Escribe filas en un archivo CSV."""
    if not rows:
        return 0
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    cols = sorted({k for r in rows for k in r.keys()})
    with open(out_file, 'w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)

def write_duckdb(con, table: str, files: List[str]) -> int:
    """Inserta datos en DuckDB con deduplicación básica."""
    files_str = "', '".join(files)
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            symbol VARCHAR, price DECIMAL(18, 6), ts BIGINT, ingest_ts BIGINT, source VARCHAR
        )
    """)
    insert_query = f"""
        INSERT INTO {table} 
        SELECT symbol, CAST(price AS DECIMAL(18,6)), ts, COALESCE(received_ts, ts) as ingest_ts, 'engine_v2' as source
        FROM read_json_auto(['{files_str}'])
        WHERE (symbol, ts) NOT IN (SELECT symbol, ts FROM {table})
    """
    con.execute(insert_query)
    return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

def run_step(mode: str = 'duckdb'):
    """Ejecuta un paso del ciclo ETL basado en el modo solicitado."""
    print(f"[{time.ctime()}] Ejecutando ETL (Modo: {mode})...")
    
    if mode == 'csv':
        rows = read_ndjson(RAW_FILE)
        count = write_csv(rows, OUT_FILE_CSV)
        print(f"CSV Update: {count} filas procesadas.")
        
    elif mode == 'duckdb':
        import duckdb
        files = glob.glob(os.path.join(RAW_DIR, '*.ndjson'))
        if not files:
            print("No hay archivos para procesar.")
            return
        con = duckdb.connect(DB_FILE)
        try:
            total = write_duckdb(con, TABLE_NAME, files)
            print(f"DuckDB Sync: {total} filas totales en Warehouse.")
        except Exception as e:
            print(f"Error en DuckDB: {e}")
        finally:
            con.close()

if __name__ == '__main__':
    print(f"ETL Engine Iniciado. Intervalo: {ETL_INTERVAL}s")
    while True:
        try:
            run_step(mode=ETL_MODE)
        except Exception as e:
            print(f"Error crítico en loop: {e}")
        time.sleep(ETL_INTERVAL)
