FROM python:3.10-slim

WORKDIR /app

COPY load_to_csv.py /app/load_to_csv.py
COPY load_to_duckdb.py /app/load_to_duckdb.py
COPY etl_runner.py /app/etl_runner.py

RUN python -m pip install --no-cache-dir --upgrade pip
RUN python -m pip install --no-cache-dir duckdb pandas

VOLUME ["/data"]

CMD ["python", "/app/etl_runner.py"]
