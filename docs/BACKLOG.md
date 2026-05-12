# Backlog Técnico de FinLogic (Plan 90 Días)

Este documento transforma el Roadmap Estratégico Q1 en un plan de ejecución táctico.

## 📅 Mes 1: Estabilización y Simplificación (Infraestructura)

**Meta:** Eliminar Kafka, unificar servicios y asegurar el flujo de datos E2E.

### Epic 1.1: Decommission de Streaming Infra

_Reducir la complejidad operativa y el consumo de recursos._

- **[TASK-1.1.1] Eliminar Kafka y Zookeeper de Docker Compose**
  - _Descripción:_ Remover servicios `kafka`, `zookeeper`, `ingest-producer` y `ingest-consumer` del `docker-compose.yml`. Eliminar código fuente relacionado en `platform/data-ingest`.
  - _Criterios de Aceptación:_ `docker-compose up` levanta solo `cashflow` y `etl-runner` (o unificado) sin errores. El consumo de RAM baja drásticamente.
  - _Esfuerzo:_ 1 día.

### Epic 1.2: Nueva API de Ingesta (Batch-over-HTTP)

_Reemplazar el canal de Kafka con un endpoint HTTP robusto._

- **[TASK-1.2.1] Crear Endpoint `POST /ingest` en Servicio Cashflow**
  - _Descripción:_ Endpoint que acepta una lista de `MarketQuote` (JSON), valida esquema básico (Pydantic) y escribe (append) a un archivo local rotativo `data/raw/incoming_YYYYMMDD_HH.ndjson`.
  - _Dependencias:_ TASK-1.1.1
  - _Criterios de Aceptación:_ `curl -X POST` con 100 precios escribe correctamente en disco. Respuesta 200 OK.
  - _Esfuerzo:_ 2 días.

- **[TASK-1.2.2] Implementar Bloqueo de Archivos / Atomicidad en Escritura**
  - _Descripción:_ Asegurar que múltiples requests concurrentes no corrompan el archivo NDJSON. Usar un lock simple o escribir a archivos temporales y renombrar.
  - _Dependencias:_ TASK-1.2.1
  - _Criterios de Aceptación:_ Test de carga concurrente (50 hilos) no pierde ni corrompe líneas JSON.
  - _Esfuerzo:_ 2 días.

### Epic 1.3: Reparación del Pipeline ETL

_Corregir la lógica rota de "Create Table as Select"._

- **[TASK-1.3.1] Migrar ETL a Inserción Incremental (Idempotente)**
  - _Descripción:_ Modificar `load_to_duckdb.py`. En lugar de `CREATE TABLE AS`, usar `INSERT INTO ... SELECT ... WHERE NOT EXISTS` (deduplicación básica por `symbol` + `ts`). Leer de los archivos generados por la API.
  - _Dependencias:_ TASK-1.2.1
  - _Criterios de Aceptación:_ Ejecutar el ETL 3 veces seguidas no duplica datos. Datos nuevos aparecen, datos viejos se mantienen.
  - _Esfuerzo:_ 2 días.

- **[TASK-1.3.2] Unificar Servicios en Monolito Modular**
  - _Descripción:_ Integrar el runner de ETL dentro del mismo contenedor/proceso que la API (usando `APScheduler` o similar) para simplificar despliegue, o mantenerlo como sidecar ligero compartiendo volumen.
  - _Criterios de Aceptación:_ Un solo `Dockerfile` principal o dos muy ligeros. Volumen `data/` compartido correctamente.
  - _Esfuerzo:_ 2 días.

---

## 📅 Mes 2: Integridad del Dominio (Calidad de Datos)

**Meta:** Confianza matemática absoluta. "Garbage In" está prohibido.

### Epic 2.1: Tipado Fuerte y Validación Financiera

_Asegurar precisión numérica y lógica de negocio._

- **[TASK-2.1.1] Implementar Decimal en Modelos Pydantic y DuckDB**
  - _Descripción:_ Reemplazar `float` por `Decimal` en todos los DTOs de entrada y en el esquema de tabla DDL de DuckDB.
  - _Criterios de Aceptación:_ Operaciones de suma de precios no muestran errores de punto flotante (`0.1+0.2=0.3`).
  - _Esfuerzo:_ 2 días.

- **[TASK-2.1.2] Validadores de "Sanity Check" en Ingesta**
  - _Descripción:_ Pydantic Validators para: `price > 0`, `timestamp <= now() + 1min` (tolerancia clock skew), `symbol` no vacío.
  - _Dependencias:_ TASK-1.2.1
  - _Criterios de Aceptación:_ Payload con precio negativo recibe `422 Unprocessable Entity`. Payload válido pasa.
  - _Esfuerzo:_ 1 día.

### Epic 2.2: Catálogo Maestro de Instrumentos

_Integridad Referencial._

- **[TASK-2.2.1] Crear Tabla Maestra `instruments` y Seed Data**
  - _Descripción:_ Tabla en DuckDB/Memoria con `symbol`, `currency`, `type`. Cargar CSV inicial con símbolos permitidos (ej. whitelist).
  - _Criterios de Aceptación:_ La tabla existe y tiene datos de prueba.
  - _Esfuerzo:_ 1 día.

- **[TASK-2.2.2] Enforce Foreign Key Lógico en Ingesta**
  - _Descripción:_ El endpoint `/ingest` rechaza (o marca como warning) símbolos que no están en la tabla `instruments`.
  - _Dependencias:_ TASK-2.2.1
  - _Criterios de Aceptación:_ Ingestar "FAKECOIN" (no existente) devuelve error/warning.
  - _Esfuerzo:_ 2 días.

### Epic 2.3: Gestión de Errores (Dead Letter Queue)

_Evitar pérdida de datos silenciosa._

- **[TASK-2.3.1] Implementar "Bad Rows" Dump**
  - _Descripción:_ Si el ETL falla al procesar una fila (ej. error de parseo, validación estricta), mover esa fila a `data/rejected/YYYYMMDD_error.json` en lugar de crashear.
  - _Criterios de Aceptación:_ Script ETL no se detiene por 1 línea corrupta. La línea corrupta aparece en la carpeta de rechazos.
  - _Esfuerzo:_ 2 días.

---

## 📅 Mes 3: Performance y Analítica (Valor)

**Meta:** Velocidad de consulta y capacidades de reporte.

### Epic 3.1: Optimización de Almacenamiento

_Transición a formatos columnares eficientes._

- **[TASK-3.1.1] Migración a Parquet (Tiering)**
  - _Descripción:_ Job nocturno que toma los NDJSON del día anterior, los convierte a un solo archivo Parquet comprimido (Snappy/Zstd) particionado por fecha.
  - _Criterios de Aceptación:_ Carpeta `data/warehouse` contiene archivos `.parquet`. Tamaño en disco reduce ~60%.
  - _Esfuerzo:_ 3 días.

- **[TASK-3.1.2] Routing de Lectura Transparente**
  - _Descripción:_ Ajustar las queries de lectura para que lean transparentemente de `read_parquet(['history/*.parquet', 'current/*.ndjson'])` (Unión de histórico + reciente).
  - _Dependencias:_ TASK-3.1.1
  - _Criterios de Aceptación:_ Endpoint `/prices` devuelve datos de ayer (parquet) y de hace 5 min (json) ordenados correctamente.
  - _Esfuerzo:_ 3 días.

### Epic 3.2: Agregaciones Materializadas (OHLC)

_Acelerar gráficos y reportes._

- **[TASK-3.2.1] Vista Materializada de Velas (Candles)**
  - _Descripción:_ Tabla `market_candles_1h` en DuckDB actualizada por el ETL. Pre-calcula Open, High, Low, Close.
  - _Criterios de Aceptación:_ Query a tabla agregada es < 50ms vs Query raw > 500ms.
  - _Esfuerzo:_ 3 días.

### Epic 3.3: Observabilidad Básica

_Visibilidad operativa._

- **[TASK-3.3.1] Endpoint de Estado `/health/etl`**
  - _Descripción:_ JSON que devuelve: Última ejecución exitosa, Filas procesadas hoy, Errores hoy, Tamaño de DB.
  - _Criterios de Aceptación:_ `curl /health/etl` devuelve estado real del sistema.
  - _Esfuerzo:_ 1 día.
