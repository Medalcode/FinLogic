# Arquitectura Lean — FinLogic

## Filosofía: Ingesta Ligera, Análisis Columnar
FinLogic rechaza la sobreingeniería de sistemas distribuidos pesados para casos de uso que pueden resolverse con **OLAP embebido**.

### Componentes Core
1. **Compute Layer (FastAPI)**: 
   - Localización: `services/cashflow/`
   - Función: Expone lógica de VAN/TIR y analíticas estadísticas.
   - Estado: Stateless, escalable horizontalmente.

2. **Storage Layer (DuckDB + Parquet)**:
   - Localización: `data/warehouse/`
   - Tecnología: DuckDB para consultas SQL analíticas ultrarrápidas directas sobre archivos.
   - Ventaja: Cero coste operacional, rendimiento similar a ClickHouse en local.

3. **ETL Motor (Unified Engine)**:
   - Localización: `platform/etl/engine.py`
   - Función: Motor paramétrico unificado para carga de datos (Bronze -> Silver/Gold).
   - Sustituye: Antiguos scripts fragmentados de carga CSV/DuckDB.

### Flujo de Datos
`Raw (NDJSON/CSV)` --[engine.py]--> `Warehouse (DuckDB)` <--[FastAPI]--> `Consumidor Final`

### Estrategia de Testing (Lean)
- **Unitarios**: Validación de lógica financiera en `utils.py`.
- **Integración**: Smoke tests de endpoints contra una instancia temporal de DuckDB.

---
*Documento actualizado por el Arquitecto Senior tras la consolidación de 2026.*
