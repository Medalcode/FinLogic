"""ETL runner: ejecuta periódicamente `load_to_csv.py` para procesar `data/raw`.
Intervalo configurable vía env `ETL_INTERVAL` en segundos.
"""
import os
import time
import subprocess

INTERVAL = int(os.getenv('ETL_INTERVAL', '30'))
SCRIPT = os.getenv('ETL_SCRIPT', '/app/load_to_csv.py')

print(f"ETL runner starting: interval={INTERVAL}s, script={SCRIPT}")

while True:
    try:
        print('Running ETL...')
        res = subprocess.run(['python', SCRIPT], capture_output=True, text=True)
        print('ETL stdout:\n', res.stdout)
        if res.stderr:
            print('ETL stderr:\n', res.stderr)
    except Exception as e:
        print('ETL runner error:', e)
    time.sleep(INTERVAL)
