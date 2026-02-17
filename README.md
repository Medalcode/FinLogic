# FinLogic

**The Lightweight Financial Data & Analytics Platform.**

---

FinLogic es una plataforma de ingeniería de datos financieros diseñada para eliminar la fricción entre la ingestión de datos de mercado y el análisis cuantitativo. Permite a los equipos centrarse en modelar y valorar activos sin perder tiempo construyendo tuberías de datos frágiles.

## 🎯 El Problema

En la mayoría de los proyectos financieros, el 80% del tiempo se pierde en "plomería": conectar APIs, parsear JSONs, luchar con bases de datos relacionales lentas para series temporales y limpiar datos sucios. Solo el 20% se dedica a lo que genera valor: **el análisis financiero**.

FinLogic invierte esta ecuación ofreciendo una arquitectura de caja blanca lista para usar (Ingest → Warehouse → Compute).

## 👥 ¿Para quién es esto?

- **Equipos Quant / Data Scientists**: Que necesitan un backend robusto para sus modelos sin configurar infra compleja.
- **Fintechs en etapa MVP**: Que requieren persistencia histórica y cálculos basicos (NPV, IRR, VaR) desde el día 1.
- **Arquitectos de Software**: Buscando un blueprint de referencia para sistemas financieros modernos no-HFT.

## ✅ Scope del Producto

### Lo que SÍ hace

- **Ingesta de Datos**: Acepta flujos de precios de mercado y los normaliza.
- **Warehousing Analítico**: Almacenamiento eficiente columnar (DuckDB) para consultas rápidas sobre series de tiempo.
- **Motor Financiero**: endpoints API optimizados para cálculos vectorizados (Valor Presente, Tasa Interna de Retorno, Volatilidad/VaR).
- **Auditabilidad**: Los datos crudos nunca se destruyen (Bronze Layer).

### Lo que NO hace

- **High Frequency Trading (HFT)**: No está diseñado para latencias de microsegundos.
- **Ejecución de Órdenes**: No conecta con brokers para emitir compra/venta real.
- **Contabilidad Ledger**: No es un ERP ni lleva libros contables de doble entrada.

## 🏗 Arquitectura de Alto Nivel

El sistema sigue una arquitectura de **"Ingesta Ligera, Análisis Pesado"**:

1.  **Ingest Layer**: Puntos de entrada para datos de mercado (Market Quotes).
2.  **Storage Layer (DuckDB)**: El corazón del sistema. Un warehouse embebido OLAP que permite queries SQL complejas sobre archivos locales (parquet/ndjson) sin el coste operativo de un data warehouse distribuido.
3.  **Compute Layer (FastAPI)**: Servicio que expone capacidades analíticas. Realiza cálculos financieros sobre los datos del warehouse bajo demanda.

_Dominio Conceptual_:

- **Instrument**: La entidad maestra (ej. `USDCLP`).
- **MarketQuote**: El hecho inmutable (ej. precio en `t`).
- **CashFlow**: La proyección financiera a valorar.

## 💡 Casos de Uso Reales

1.  **Valuador de Portafolios**: Un servicio externo envía flujos de caja futuros; FinLogic consulta las tasas de mercado actuales y devuelve el Valor Presente Neto (NPV) instantáneo.
2.  **Backtesting de Estrategias**: Un analista descarga la historia completa de precios de un activo vía SQL para probar una media móvil en local.
3.  **Risk Dashboard**: Monitorización diaria del Value at Risk (VaR) de una posición en moneda extranjera.

## 📍 Estado Actual y Roadmap

**Estado**: `Alpha / MVP`. La infraestructura core está operativa, la transición de Kafka a una ingestión directa HTTP está en evaluación para simplificar el despliegue.

**Roadmap Corto Plazo:**

- [x] Core Banking Logic (NPV, IRR).
- [x] Persistencia en DuckDB.
- [ ] API de Ingesta HTTP Directa (reemplazo de complejidad Kafka).
- [ ] Soporte Multi-moneda explícito.
- [ ] Autenticación Granular.

---

### Quickstart (Dev)

```bash
# 1. Levantar servicios
docker-compose up -d --build

# 2. Verificar API
curl http://localhost:8001/prices

# 3. Test de carga
python -m unittest discover services/cashflow/tests
```

---

## Cambios recientes en el repositorio

Hechos durante la mejora hacia un proyecto más profesional y observable:

- Se añadieron documentación operativa en `docs/agent.md` y `docs/skills.md`.
- Se instrumentó la API con métricas Prometheus y se expuso `/metrics`.
- Se extrajeron utilidades (`read_prices_csv`, `aggregate_ohlc`) a `services/cashflow/src/utils.py` para mejorar separación de responsabilidades.
- Ajustes en `services/cashflow/src/main.py` para usar la instrumentación y las utilidades refactorizadas.
- Tests unitarios actualizados y verificados: `python -m unittest discover -v services/cashflow/tests` → OK.

## Instrucciones rápidas (entorno local)

1. Activar entorno virtual (Windows PowerShell):

```powershell
& .venv\Scripts\Activate.ps1
```

2. Instalar dependencias (si no están instaladas):

```powershell
python -m pip install -r services/cashflow/requirements.txt
```

3. Ejecutar tests:

```powershell
python -m unittest discover -v services/cashflow/tests
```

4. Levantar en dev con Docker Compose:

```powershell
docker-compose up --build
```

---

Si quieres, puedo además crear los manifiestos iniciales de Kubernetes en `k8s/` y configurar ejemplos de dashboards de Prometheus/Grafana.

