# Skills: Catálogo y Playbooks

## Propósito
Catálogo de skills (roles operativos y técnicos) y playbooks prácticos para ejecutar y mantener FinLogic en producción.

## Roles / Skills

- **ETL Operator**
  - Responsabilidades: ejecutar y supervisar pipelines ETL, comprobar integridad de datos, coordinar backups y migraciones del warehouse.
  - Herramientas: Python, DuckDB, Cron/Kubernetes CronJob, S3 (backups), Redis (locks opcional).
  - Playbook corto:
    1. Ver logs del job ETL: `kubectl logs job/etl-...` o revisar container logs en Compose.
    2. Forzar re-run: crear `Job` en k8s con la imagen del ETL y comprobar `kubectl logs`.
    3. Comprobar tabla: usar DuckDB CLI o conectar con `duckdb` para validar filas y deduplicación.

- **API Maintainer (Backend Engineer)**
  - Responsabilidades: mantener endpoints, asegurar rendimiento, instrumentar métricas y manejar releases.
  - Herramientas: FastAPI, uvicorn, Prometheus client, Docker, Kubernetes.
  - Playbook corto:
    1. Ver salud: `curl http://<service>/health`.
    2. Revisar errores: `kubectl logs deployment/cashflow`.
    3. Actualizar dependencias y ejecutar tests: `python -m unittest discover -v`.

- **Data Engineer**
  - Responsabilidades: modelado y calidad de datos, migraciones de esquema, optimizaciones de consulta para análisis.
  - Herramientas: DuckDB, SQL, Python, migration snapshots.
  - Playbook corto:
    1. Exportar subset para pruebas: `duckdb -c "COPY (SELECT ...) TO 'subset.csv' (HEADER)"`.
    2. Planificar migración a DB gestionada si se requiere concurrencia/HA.

- **DevOps / Platform**
  - Responsabilidades: CI/CD, despliegue en Kubernetes, provisioning de observabilidad y secretos (Vault).
  - Herramientas: kubectl, Helm, Vault, Prometheus, Grafana, GitHub Actions.
  - Playbook corto:
    1. Ver estado cluster: `kubectl get nodes,pods,svc`.
    2. Aplicar manifiestos: `kubectl apply -f k8s/`.
    3. Revisión de alertas en Grafana/Prometheus y ejecutar rollback si es necesario.

## Playbooks operativos (por skill)

- ETL Operator: diagnóstico de fallo ETL
  - Comprobar logs del job
  - Verificar existencia de archivos en `data/raw`
  - Ejecutar script ETL localmente con `python platform/etl/load_to_duckdb.py --dry-run`

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
4. Revisión rápida de `services/cashflow/src/main.py` y `platform/etl/load_to_duckdb.py`.

## Contactos y propiedad
- Mantener en el README del equipo la lista de propietarios por componente (ETL / API / Platform).
