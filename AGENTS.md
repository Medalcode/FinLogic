# FinLogic — Agent Guide

## Commands
```bash
make test                                   # run all 13 tests
make run-cashflow                           # start cashflow API on :8001
python -m unittest discover -v              # same as make test

# Docker:
docker-compose up --build                   # starts cashflow API + ETL runner

# Per-service:
pip install -r services/cashflow/requirements.txt
uvicorn services.cashflow.src.main:app --reload --port 8001
```

## Critical Quirks

- **Multi-service monorepo** with two Docker services:
  - `services/cashflow/` = **FastAPI** financial API (NPV, IRR, prices, analytics). Main entry point: `services/cashflow/src/main.py`.
  - `platform/etl/` = **Batch ETL engine** (reads NDJSON → writes DuckDB/CSV). Runs as a standalone script (`python engine.py`), not an API.
  - **Code in the wrong service will break** — ETL logic in `platform/etl/`, API logic in `services/cashflow/`. Don't cross boundaries.
- **DuckDB is the analytical database** — not PostgreSQL. The warehouse runs on DuckDB files (`*.duckdb`). There is no traditional DBMS to connect to.
- **No `.env.example`** — env vars are documented in `docker-compose.yml` and `services/cashflow/README.md`. Key vars: `API_KEY=dev-key`, `USE_DUCKDB=1`, `DATA_FILE=/data/warehouse/market.duckdb`.
- **Auth**: API requires `X-API-Key` header matching the `API_KEY` env var (default `dev-key`). Also accepts `Authorization: Bearer <key>`.
- **Tests** are consolidated in `services/cashflow/tests/` (13 tests total: 5 API + 8 unit). `make test` runs from repo root. Must install `services/cashflow/requirements.txt` first.
- **`docs/gemini-context.md`** (124 lines) is the primary context document for AI agents — more detailed than `README.md`. Read it after `AGENTS.md` for the full picture.
