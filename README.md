# FinLogic

**The Lightweight Financial Data & Analytics Platform.**

---

FinLogic es una plataforma de ingeniería de datos financieros diseñada para eliminar la fricción entre la ingestión de datos de mercado y el análisis cuantitativo. Permite a los equipos centrarse en modelar y valorar activos sin perder tiempo construyendo tuberías de datos frágiles mediante un enfoque **Lean** y basado en **DuckDB-Native**.

## 🎯 El Problema

En la mayoría de los proyectos financieros, el 80% del tiempo se pierde en "plomería": conectar APIs, parsear JSONs, luchar con infraestructuras pesadas y limpiar datos sucios. Solo el 20% se dedica a lo que genera valor: **el análisis financiero**.

FinLogic invierte esta ecuación ofreciendo una arquitectura de caja blanca lista para usar (Ingest → Warehouse → Compute) con cero coste operacional de base de datos.

## 👥 ¿Para quién es esto?

- **Equipos Quant / Data Scientists**: Que necesitan un backend robusto para sus modelos sin configurar infra compleja.
- **Fintechs en etapa MVP**: Que requieren persistencia histórica y cálculos básicos (NPV, IRR, VaR) desde el día 1.
- **Arquitectos de Software**: Buscando un blueprint de referencia para sistemas financieros modernos de alta eficiencia.

## ✅ Scope del Producto

### Lo que SÍ hace

- **Ingesta de Datos**: Acepta flujos de precios de mercado y los normaliza mediante un motor unificado.
- **Warehousing Analítico**: Almacenamiento eficiente columnar (**DuckDB**) para consultas rápidas sobre series de tiempo directas sobre el sistema de archivos.
- **Motor Financiero**: endpoints API optimizados para cálculos vectorizados (Valor Presente, Tasa Interna de Retorno, Volatilidad/VaR).
- **Auditabilidad**: Los datos crudos nunca se destruyen (Bronze Layer).

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

---
**Contacto**: Solicita próximas tareas a implementar o priorización para que las ejecute.
