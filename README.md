# FinLogic

**Plataforma Lean para Análisis y Calidad de Datos Financieros**

---

FinLogic is a Lean Financial Data Quality and Analytics Platform designed to ingest, validate, transform and analyze financial datasets with a focus on data integrity, reproducibility and operational simplicity.

## 🎯 El Problema

Los analistas financieros y equipos Quant consumen datos provenientes de múltiples fuentes, pero gran parte de su tiempo se pierde validando, limpiando y transformando información cruda antes de poder realizar análisis reales. 

FinLogic busca reducir ese esfuerzo mediante una plataforma ligera y tolerante a fallos que permita:
- Ingestar datos financieros masivos.
- Validar la calidad en tiempo real y rechazar anomalías (Data Quality Engine).
- Almacenar información analítica sin costos operacionales (DuckDB-Native).
- Calcular métricas financieras (VAN, TIR, VaR).
- Exponer resultados mediante APIs claras.

## 👥 ¿Para quién es esto?

- **Equipos Quant / Data Scientists**: Que necesitan ingestar datos de mercado sucios, obtener métricas de calidad y tener un backend robusto para sus modelos.
- **Fintechs en etapa MVP**: Que requieren persistencia histórica, control de anomalías y cálculos básicos desde el día 1.
- **Arquitectos de Software**: Buscando un blueprint de referencia para sistemas de Data Quality y Finanzas.

## ✅ Scope del Producto

### Lo que SÍ hace

- **Motor de Calidad (Ingesta)**: Endpoint `/ingest` tolerante a fallos. Valida la integridad, clasifica anomalías (ej. precios negativos, símbolos faltantes) y genera reportes de "Quality Score".
- **Warehousing Analítico**: Almacenamiento eficiente columnar (**DuckDB**) para consultas rápidas sobre series de tiempo directas en el sistema de archivos.
- **Motor Financiero**: endpoints API optimizados para cálculos vectorizados (Valor Presente, Tasa Interna de Retorno, Volatilidad/VaR).
- **Auditabilidad y Resiliencia**: Los datos crudos se conservan, y los corruptos van a una Dead Letter Queue (DLQ).

### Lo que NO hace

- **High Frequency Trading (HFT)**: No está diseñado para latencias de microsegundos.
- **Ejecución de Órdenes**: No conecta con brokers para emitir compra/venta real.
- **Contabilidad Ledger**: No es un ERP ni lleva libros contables de doble entrada.

## 🏗 Arquitectura "Lean"

El sistema sigue una filosofía de **"Ingesta Ligera, Análisis Pesado"**:

1.  **Ingest Layer**: Puntos de entrada para datos de mercado (Market Quotes).
2.  **Storage Layer (DuckDB)**: El corazón del sistema. Un warehouse embebido OLAP que permite queries SQL complejas sobre archivos locales (parquet/ndjson/csv) con rendimiento extremo.
3.  **Compute Layer (FastAPI)**: Servicio que expone capacidades analíticas. Realiza cálculos financieros sobre los datos del warehouse bajo demanda, delegando la carga pesada al motor columnar de DuckDB.

---

## 📍 Estado Actual y Roadmap

**Estado**: `Alpha / MVP - Refactorizado a Modelo Lean`. La infraestructura está consolidada para minimizar la fragmentación y maximizar la reutilización de código.

**Roadmap Corto Plazo:**
- [x] Core Banking Logic consolidado (VAN, TIR).
- [x] Motor ETL unificado y paramétrico.
- [x] Persistencia nativa en DuckDB.
- [ ] Soporte Multi-moneda explícito.
- [ ] Dashboard de Observabilidad (Grafana + Prometheus).

---

## 🚀 Quickstart (Entorno Local)

### 1. Activar entorno virtual (Windows)
```powershell
& .venv\Scripts\Activate.ps1
```

### 2. Ejecutar tests consolidados
```powershell
python -m unittest discover -v services/cashflow/tests
```

### 3. Levantar con Docker Compose
```powershell
docker-compose up --build
```

---

## 📂 Cambios Recientes (Hito de Consolidación 2026)

Se ha realizado una refactorización profunda para reducir la fragmentación del código:

- **Consolidación de Agentes**: Reemplazo de roles fragmentados por un **Agente Generalista** unificado en `docs/agents.md`.
- **Super-Skills**: Fusión de múltiples habilidades técnicas en 3 Super-Skills paramétricas (`DataLifecycle`, `BusinessIntelligence`, `SystemReliability`) detalladas en `docs/skills.md`.
- **Motor ETL Unificado**: Fusión de `load_to_csv`, `load_to_duckdb` y `etl_runner` en un único `platform/etl/engine.py`.
- **Core Analytics**: Movida toda la lógica de `cashflow/core.py` y analíticas de `main.py` hacia `utils.py` para una API más limpia.
- **Test Lean**: Reducción de 6 archivos de prueba dispersos a 2 archivos temáticos robustos.

### Actualización Técnica (Mayo 2026)

- **Refactor de lectura de mercado**: `services/cashflow/src/main.py` ahora delega carga, filtros y resumen en helpers reutilizables de `services/cashflow/src/utils.py`.
- **Hardening de modo DuckDB**: si `USE_DUCKDB=1`, `DATA_FILE` debe terminar en `.duckdb`; en caso contrario, la API responde `HTTP 400` con detalle explícito.
- **Cobertura ampliada**: se agregaron pruebas para ruta DuckDB (`offset`, rango temporal y validación de configuración forzada), además de test de contrato API para error `400`.
- **Validación final**: suite `services/cashflow/tests` en verde con 13 tests.

### Actualización Técnica (Junio 2026)

- **Precisión Numérica**: Reemplazo global de `float` por `Decimal` en el Core y la API para garantizar exactitud matemática en las operaciones de VAN e TIR.
- **Paginación Maximizada**: Pushdown nativo del parámetro `OFFSET` directamente a las consultas de DuckDB (`read_prices_duckdb`), mitigando problemas de memoria con datasets masivos.
- **Endpoint de Ingesta (Batch-over-HTTP)**: Nuevo endpoint `POST /ingest` protegido y con validación Pydantic que permite inyectar `MarketQuote` y almacenarlo en `data/raw/incoming.ndjson`.
- **Resiliencia ETL (DLQ)**: El motor `engine.py` ahora implementa una Dead Letter Queue volcando cualquier registro corrupto a `data/rejected/error.ndjson` en lugar de ignorarlo silenciosamente.
- **Validación final**: Suite de pruebas extendida (`test_api.py`, `test_logic.py`) en verde con 15 tests en 0.3s.

---
**Contacto**: Solicita próximas tareas a implementar o priorización para que las ejecute.
