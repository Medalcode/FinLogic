# FinLogic

FinLogic — MVP de una plataforma financiera para ingest, ETL y análisis.

Estructura principal:

- `services/cashflow/`: API financiera (FastAPI) con calculadoras y endpoints analíticos.
- `platform/data-ingest/`: productor y consumidor Kafka para ingest de mercado.
- `platform/etl/`: scripts ETL (NDJSON → CSV → DuckDB) y runner periódico.
- `data/raw/` y `data/warehouse/`: datos de entrada y warehouse DuckDB.
- `docs/`: arquitectura y bitácora.

Arranque rápido (desarrollo local):

1. Construir y levantar la pila (Docker Compose):

	- `docker-compose up -d --build`

2. Verificar que `cashflow` esté disponible:

	- `curl -H "X-API-Key: dev-key" http://localhost:8001/prices`

3. ETL: el `etl-runner` en Docker Compose ejecuta la conversión a DuckDB periódicamente.

Tests:

- Ejecutar tests unitarios: `python3 -m unittest discover services/cashflow/tests`

Siguientes pasos (pendiente):

- Completar CI para dependencias pesadas (duckdb/pandas).
- Mejorar observabilidad y seguridad antes de producción.

Ver `docs/BITACORA.md` para el registro de trabajo y próximos pasos.
# FinLogic