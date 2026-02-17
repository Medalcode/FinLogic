# Agent: Arquitectura y Operaciones

## Propósito
Documento de referencia del "agent" para operar y evolucionar FinLogic como una aplicación escalable y profesional.

## Alcance
Describe componentes, flujo de datos, entry points, recomendaciones de despliegue (Kubernetes), observabilidad, seguridad y runbook operacional.

## Visión general (alto nivel)

Ingest → ETL → Warehouse → API

```
  +-------------+     +-----------+     +-------------+
  | Productor   | --> | ETL       | --> | Warehouse   |
  | (NDJSON)    |     | (batch)   |     | (DuckDB/DB) |
  +-------------+     +-----------+     +-------------+
                              |
                              v
                         +---------+
                         | API     |
                         | (cashflow)
                         +---------+
```

## Componentes y responsabilidades
- **ETL (batch)**: `platform/etl/load_to_duckdb.py` y `platform/etl/etl_runner.py` — ingesta desde `data/raw`, carga y deduplicación a `data/warehouse/market.duckdb`.
- **API**: `services/cashflow/src/main.py` — servicio HTTP (uvicorn/FastAPI) que expone cálculos financieros y endpoints analíticos.
- **Contenedores**: `services/cashflow/Dockerfile`, `platform/etl/Dockerfile`.
- **Orquestación local**: `docker-compose.yml` (desarrollo). Para producción, objetivo: Kubernetes.

## Entrypoints importantes
- `services/cashflow/src/main.py` — app HTTP y configuración mediante variables de entorno (`API_KEY`, `DATA_FILE`, `USE_DUCKDB`).
- `platform/etl/etl_runner.py` — runner programado simple para ejecutar la ETL.
- `platform/etl/load_to_duckdb.py` — lógica de carga y deduplicación.

## Configuración recomendada
- Migrar la configuración a un objeto de settings validado (por ejemplo `pydantic.BaseSettings`) centralizado.
- Variables críticas a exponer y documentar: `API_KEY`, `DATA_FILE`, `USE_DUCKDB`, `ETL_INTERVAL`, `ETL_LOCK_PATH`, `LOG_LEVEL`.
- No almacenar secretos en repositorios; usar `HashiCorp Vault` (sección Seguridad).

## Despliegue (objetivo: Kubernetes)
- Recomendación mínima para producción:
  - API: `Deployment` con `readinessProbe`/`livenessProbe`, `resources` y `HorizontalPodAutoscaler`.
  - ETL: `CronJob` (si es periódica) o `Job`/`Argo Workflow` para runs controlados y retry.
  - Almacenamiento: migrar a DB gestionada (Postgres/ClickHouse) si la concurrencia o dataset crecen; DuckDB es excelente para análisis embebido pero limitado en concurrencia y HA.

### Ejemplo de Deployment (simplificado)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cashflow
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cashflow
  template:
    metadata:
      labels:
        app: cashflow
    spec:
      containers:
      - name: cashflow
        image: finlogic/cashflow:latest
        ports:
        - containerPort: 8001
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 15
          periodSeconds: 20
```

## Observabilidad
- **Métricas**: instrumentar con `prometheus_client` y exponer `/metrics`.
- **Logs**: usar logs estructurados (JSON), `LOG_LEVEL` controlable por env.
- **Tracing**: recomendar OpenTelemetry para trazas distribuidas (etapas futuras).
- **Dashboards/alertas**: Prometheus + Grafana; reglas de alerta para errores 5xx, latencia alta y uso de recursos.

## Seguridad y secretos
- Uso recomendado: `HashiCorp Vault` con auth para Kubernetes o `external-secrets` para sincronizar secretos.
- TLS: terminación TLS en Ingress/LoadBalancer.
- Autenticación: rotación periódica de `API_KEY`; evaluar migración a OAuth2 si se amplía acceso.

## Datos y Backups
- Backups regulares de `data/warehouse/market.duckdb` y política de retención.
- Plan de migración a DB gestionada (Postgres/ClickHouse) para mayores requisitos de concurrencia y HA.

## Runbook básico
- Desarrollo local: `docker-compose up --build`.
- Despliegue k8s (dev): `kubectl apply -f k8s/` y `kubectl get pods`.
- Restaurar backup DuckDB: reemplazar archivo en storage y reiniciar pods que lo monten.
- Rotación de `API_KEY`: actualizar secreto en Vault y redeployar deployments consumidores.

## Testing y CI
- Mantener `python -m unittest discover -v` en CI.
- Añadir job de integración para verificar endpoints `/health` y `/metrics` tras despliegue en staging.

## Limitaciones y riesgos
- DuckDB no es una base transaccional distribuida; riesgo en concurrencia y backup/restore.
- ETL runner actual requiere locking/atomicidad para evitar condiciones de carrera.

## Roadmap inmediato
1. Añadir `pydantic` settings y validación de envs.
2. Instrumentar métricas básicas y exponer `/metrics`.
3. Convertir ETL runner a `CronJob` en k8s y añadir locking (ConfigMap/Lease o Redis).
4. Integrar Vault para gestión de secretos.

## Referencias rápidas
- `services/cashflow/src/main.py`
- `platform/etl/load_to_duckdb.py`
- `platform/etl/etl_runner.py`
