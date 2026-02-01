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
