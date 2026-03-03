FROM python:3.10-slim

WORKDIR /app

# Copiar el motor consolidado y las dependencias
COPY engine.py /app/engine.py
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

VOLUME ["/data"]

# El motor detectará el modo (CSV/DuckDB) vía env-vars en docker-compose.yml
CMD ["python", "/app/engine.py"]
