# Arquitectura (borrador)

Resumen de alto nivel para la aplicación financiera escalable.

- API Gateway: `REST/GraphQL` para exponer endpoints públicos.
- Microservicios por dominio: `cashflow`, `pricing`, `risk`, `portfolio`, `users`, `compliance`.
- Servicios de cálculo: stateless para cálculos rápidos; batch para Monte Carlo y backtests.
- Ingesta: Kafka para feeds de mercado; almacén raw en S3.
- Data Platform: ETL hacia warehouse columnar (ClickHouse/BigQuery/Snowflake).
- ML: Feature store, MLflow, model serving.
- Seguridad: OIDC/OAuth2, OPA para políticas, cifrado y auditoría inmutable.

Roadmap inicial:
- Semana 1: `cashflow` API (VAN/TIR), pruebas unitarias y scaffold del repo.
- Semana 2: ETL básico y dashboard de KPIs.
- Semana 3: Risk (VaR, Monte Carlo) y batch processing.
- Semana 4: Pricing de derivados y XAI para modelos.
