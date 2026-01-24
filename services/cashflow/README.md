Cashflow service (MVP)

Endpoints:
- POST /npv  -> calcula NPV. Body: {"cashflows": [...], "rate": 0.1}
- POST /irr  -> calcula IRR. Body: {"cashflows": [...]} 

Run locally (install deps):

```bash
pip install -r services/cashflow/requirements.txt
uvicorn services.cashflow.src.main:app --reload --port 8001
```

Examples:

- Obtener últimas 10 observaciones (desde CSV local):

```bash
curl 'http://localhost:8001/prices?limit=10'
```

- Filtrar por símbolo:

```bash
curl 'http://localhost:8001/prices?symbol=USDCLP&limit=50'
```

Autenticación:

Por simplicidad el servicio soporta autenticación por API key. Establece la variable de entorno `API_KEY` y envía la clave en el header `X-API-Key` o como `Authorization: Bearer <key>`.

Ejemplo:

```bash
export API_KEY=mi-clave-secreta
curl -H "X-API-Key: mi-clave-secreta" 'http://localhost:8001/prices?limit=10'
```
