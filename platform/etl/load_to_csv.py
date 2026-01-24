"""ETL ligero: lee NDJSON de `data/raw/market_prices.ndjson` y lo persiste en CSV.
Salida: `data/warehouse/market_prices.csv`.
No requiere dependencias externas.
"""
import os
import json
import csv

RAW_FILE = os.getenv('RAW_FILE', './data/raw/market_prices.ndjson')
OUT_FILE = os.getenv('OUT_FILE', './data/warehouse/market_prices.csv')

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)


def read_ndjson(path):
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


def write_csv(rows, out_file):
    if not rows:
        print('No rows to write')
        return 0
    # obtener columnas unificadas
    cols = sorted({k for r in rows for k in r.keys()})
    with open(out_file, 'w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return len(rows)


if __name__ == '__main__':
    rows = read_ndjson(RAW_FILE)
    count = write_csv(rows, OUT_FILE)
    print(f'Wrote {count} rows to {OUT_FILE}')
