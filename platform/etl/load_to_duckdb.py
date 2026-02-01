
import os
import json
import time
import duckdb
import glob

# Configuración
RAW_DIR = os.getenv('RAW_DIR', '/data/raw')
DB_FILE = os.getenv('DB_FILE', '/data/warehouse/market.duckdb')
TABLE_NAME = 'market_prices'
ETL_INTERVAL = int(os.getenv('ETL_INTERVAL', '15'))

def get_duckdb_connection():
    return duckdb.connect(DB_FILE)

def ensure_table_exists(con):
    """Crea la tabla si no existe con esquema explícito"""
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            symbol VARCHAR,
            price DECIMAL(18, 6),
            ts BIGINT,
            ingest_ts BIGINT,
            source VARCHAR
        )
    """)
    # Crear índice para evitar duplicados en queries rápidas (opcional)
    # DuckDB no tiene PRIMARY KEY enforcement estricto en inserts masivos como Postgres,
    # pero podemos gestionar deduplicación en lectura o inserción.

def run_etl():
    print(f"[{time.ctime()}] Iniciando ETL Batch...")
    
    # 1. Buscar archivos NDJSON nuevos
    # En un sistema real, moveríamos los procesados a /processed.
    # Aquí, para simplicidad, leemos todo y usamos deduplicación lógica.
    files = glob.glob(os.path.join(RAW_DIR, '*.ndjson'))
    
    if not files:
        print("No hay archivos para procesar.")
        return

    con = get_duckdb_connection()
    ensure_table_exists(con)
    
    try:
        # 2. Leer archivos Raw directamente hacia una tabla temporal
        # read_json_auto infiere tipos, pero forzamos cast si es necesario luego
        # Usamos union_by_name para seguridad si cambian columnas
        files_str = "', '".join(files)
        query = f"SELECT * FROM read_json_auto(['{files_str}'], union_by_name=true)"
        
        # 3. Insertar solo lo nuevo (Deduplicación simple basada en symbol+ts)
        # Estrategia: Insertar todo en staging, luego merge.
        # Simplificación MVP: Insertar WHERE NOT EXISTS.
        
        insert_query = f"""
            INSERT INTO {TABLE_NAME} 
            SELECT 
                symbol, 
                CAST(price AS DECIMAL(18,6)), 
                ts, 
                COALESCE(received_ts, ts) as ingest_ts,
                'api_ingest' as source
            FROM read_json_auto(['{files_str}'])
            WHERE (symbol, ts) NOT IN (SELECT symbol, ts FROM {TABLE_NAME})
        """
        
        con.execute(insert_query)
        
        # Contar filas
        count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        print(f"ETL Exitoso. Total filas en warehouse: {count}")
        
    except Exception as e:
        print(f"Error crítico en ETL: {e}")
    finally:
        con.close()

if __name__ == '__main__':
    print("ETL Runner Iniciado (Modo Filesystem)")
    while True:
        run_etl()
        time.sleep(ETL_INTERVAL)
