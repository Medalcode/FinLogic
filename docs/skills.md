# Skills: Catálogo y Playbooks

## Propósito
Catálogo de skills (roles operativos y técnicos) y playbooks prácticos para ejecutar y mantener FinLogic en producción.

## Super-Skills (Paramétricas)

- **DataLifecycle [Super-Skill]**
  - **Fusión**: ETL Operator + Data Engineer logic.
  - **Parámetros**: `operation` (ingest, extract, clean, migrate), `format` (duckdb, csv, ndjson, parquet).
  - **Herramientas**: Python, DuckDB, SQL, S3, Parquet.
  - **Uso**: Unifica la carga desde `data/raw`, deduplicación en Warehouse y exportaciones para análisis.
  
- **BusinessIntelligence [Super-Skill]**
  - **Fusión**: API Maintainer (Analytics) + Core Financial.
  - **Parámetros**: `calc_type` (financial_math, statistical_agg, risk_modeling), `engine` (core_py, duckdb_sql).
  - **Herramientas**: FastAPI, core.py, statistics, VaR modules.
  - **Uso**: Centraliza el cálculo de NPV, IRR, retornos históricos y métricas de riesgo desde una única interfaz lógica.

- **SystemReliability [Super-Skill]**
  - **Fusión**: DevOps / Platform + API Maintainer (Ops).
  - **Parámetros**: `scope` (infrastructure, observability, security), `action` (deploy, rotate, monitor).
  - **Herramientas**: Kubectl, Helm, Vault, Prometheus, Grafana.
  - **Uso**: Automatiza el ciclo CI/CD, despliegue en K8s, rotación de secretos y observabilidad de salud operativa.

## Playbooks operativos (por Super-Skill)

- DataLifecycle: diagnóstico de fallo en Warehouse
  - Comprobar logs del job
  - Verificar existencia de archivos en `data/raw`
  - Ejecutar script ETL localmente con `python platform/etl/engine.py --dry-run`

- API Maintainer: alto latency
  - Revisar métricas de latencia en Prometheus/Grafana
  - Escalar el `Deployment` o aumentar `replicas`
  - Revisar queries que leen DuckDB; considerar cache en memoria o read replica (DB gestionada)

- DevOps: rotación de secretos
  - Subir nuevo secreto a Vault
  - Actualizar SecretProvider y forzar rolling update: `kubectl rollout restart deployment/cashflow`

## Automatización y tareas frecuentes
- Integración continua: tests unitarios + lint + build de imagen + smoke tests.
- Deploy: pipeline de staging/production con revisiones manuales y rollbacks automáticos en fallo de health checks.

## Observability tasks
- Añadir métricas custom:
  - `requests_total`, `request_latency_seconds`, `etl_last_run_timestamp`, `etl_processed_records`.
- Alerts recomendadas:
  - `expr: rate(api_requests_total[5m]) > some_threshold` — tráfico anómalo
  - `expr: increase(etl_errors_total[1h]) > 0` — ETL fallando

## Security tasks
- Revisión semanal de dependencias (`pip-audit` o `safety`).
- Escaneo de imágenes Docker para vulnerabilidades antes de push.

## Testing & validation tasks
- Unit tests: `python -m unittest discover -v`.
- Integration smoke: levantar staging mínimo (ETL → warehouse → API) y validar `/health`, `/metrics` y `GET /prices`.

## Scaling tasks
- Para datasets grandes o alta concurrencia:
  - Migrar DuckDB → Postgres/ClickHouse.
  - Implementar read replicas y caches.
  - Offload heavy analytics to dedicated analytics cluster.

## Onboarding checklist (nuevo miembro)
1. Clonar repo y revisar `README.md`.
2. Correr tests: `python -m unittest discover -v`.
3. Levantar ambiente local con `docker-compose up --build`.
4. Revisión rápida de `services/cashflow/src/main.py` y `platform/etl/engine.py`.

## Contactos y propiedad
- Mantener en el README del equipo la lista de propietarios por componente (ETL / API / Platform).
