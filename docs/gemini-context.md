# FinLogic: contexto de desarrollo para Gemini

Este documento resume lo necesario para que un asistente de IA entienda el proyecto, proponga cambios seguros y valide impacto sin perder tiempo re-descubriendo el repo.

## 1) Qué es FinLogic

FinLogic es una plataforma ligera de datos y analítica financiera. Su objetivo es unir ingesta de precios de mercado, almacenamiento analítico con DuckDB y una API FastAPI para cálculos financieros y analítica básica.

No está pensada para HFT, ejecución de órdenes ni contabilidad de doble entrada. El diseño favorece un stack simple, local y auditable.

## 2) Arquitectura actual

Flujo principal:

Raw NDJSON o CSV -> ETL -> Warehouse DuckDB/CSV -> API FastAPI -> consumidor final

Componentes principales:

- API de negocio: [services/cashflow/src/main.py](../services/cashflow/src/main.py)
- Lógica financiera y lectura de datos: [services/cashflow/src/utils.py](../services/cashflow/src/utils.py)
- ETL unificado: [platform/etl/engine.py](../platform/etl/engine.py)
- Despliegue local: [docker-compose.yml](../docker-compose.yml)
- Pruebas: [services/cashflow/tests/test_api.py](../services/cashflow/tests/test_api.py) y [services/cashflow/tests/test_logic.py](../services/cashflow/tests/test_logic.py)

## 3) Qué hace cada módulo

### API FastAPI

- Expone `POST /npv` para valor presente neto.
- Expone `POST /irr` para tasa interna de retorno.
- Expone `GET /prices` para consultar series de precios desde CSV o DuckDB.
- Expone `GET /analytics/summary` para estadística descriptiva y VaR histórico.
- Requiere API key por `X-API-Key` o `Authorization: Bearer <key>`.

### utils.py

- Implementa `fv`, `pv`, `npv`, `irr`.
- Implementa lectura de CSV y DuckDB.
- Implementa agregación OHLC.
- Implementa VaR histórico.

### ETL engine

- Lee NDJSON desde `data/raw`.
- Puede escribir a CSV o sincronizar una tabla DuckDB.
- Usa deduplicación básica por `symbol` + `ts`.
- Corre como loop periódico por `ETL_INTERVAL`.

## 4) Estado del producto

Estado actual descrito en la documentación: alpha / MVP refactorizado a modelo lean.

Roadmap corto actual:

- Soporte explícito multi-moneda.
- Observabilidad con Grafana y Prometheus.

Backlog técnico relevante:

- Eliminar infraestructura vieja y unificar servicios.
- Mejorar la ingesta por HTTP.
- Endurecer validación de datos y manejo de filas malas.
- Migrar más lecturas a DuckDB y luego Parquet.

## 5) Datos y almacenamiento

- Directorio raw: `data/raw/`
- Warehouse: `data/warehouse/`
- Archivo DuckDB principal: `data/warehouse/market.duckdb`
- CSV de warehouse: `data/warehouse/market_prices.csv`
- Fuente raw inicial: `data/raw/market_prices.ndjson`

La idea de diseño es no destruir crudo, conservar trazabilidad y usar DuckDB como warehouse embebido.

## 6) Despliegue local

Docker Compose levanta dos servicios:

- `cashflow`: API FastAPI en `8001`
- `etl-runner`: proceso batch del ETL

Variables importantes:

- `API_KEY`: clave de autenticación de la API
- `DATA_FILE`: ruta local de datos; puede apuntar a CSV o `.duckdb`
- `USE_DUCKDB=1`: fuerza lectura desde DuckDB
- `RAW_DIR`, `DB_FILE`: rutas usadas por el ETL

Comandos relevantes del repo:

- Tests: `python -m unittest discover -v`
- API local: `uvicorn services.cashflow.src.main:app --reload --port 8001`
- ETL local: `python platform/etl/engine.py`
- Docker: `docker-compose up --build`

## 7) Qué validan las pruebas actuales

- Autenticación API con `X-API-Key` y Bearer token.
- Cálculo de NPV e IRR.
- Lectura de CSV con filtros por símbolo, rango de tiempo y paginación.
- Agregación OHLC.
- VaR histórico.

## 8) Puntos frágiles o importantes para cambios

- `main.py` mezcla lectura CSV y DuckDB con lógica de fallback y filtros manuales; cambios en `/prices` deben probar ambas rutas.
- `read_prices_duckdb` asume una tabla `market_prices` en DuckDB.
- `irr` usa bisección y puede fallar si no hay cambio de signo.
- El ETL hace inserción incremental con deduplicación básica, pero el diseño todavía es sensible a concurrencia y atomicidad.
- El proyecto tiene documentación estratégica más ambiciosa que la implementación actual; no asumir que todo lo descrito ya está hecho.

## 9) Cómo debe ayudar Gemini

Cuando Gemini revise o cambie este repo, conviene darle estas reglas:

- Mantener cambios pequeños y alineados con el enfoque lean.
- Preferir correcciones en `services/cashflow/src/utils.py` antes de duplicar lógica en la API.
- Validar siempre con tests unitarios después de tocar cálculo financiero o filtros de datos.
- Si cambia el ETL, comprobar impacto sobre DuckDB y sobre los fixtures de pruebas.
- No introducir infraestructura extra si el objetivo puede resolverse con DuckDB, FastAPI y archivos locales.

## 10) Resumen corto para pegar en otro chat

FinLogic es una plataforma financiera lean basada en FastAPI + DuckDB + ETL local. La API vive en `services/cashflow/src/main.py`, la lógica financiera en `services/cashflow/src/utils.py` y el ETL unificado en `platform/etl/engine.py`. La autenticación usa API key, los datos viven en `data/raw` y `data/warehouse`, y las pruebas cubren auth, NPV, IRR, filtros CSV, OHLC y VaR. Prioridades actuales: robustecer ingesta, mejorar ETL, endurecer validación de datos y ampliar observabilidad.