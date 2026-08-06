# Minimal local Airflow pattern for this ingestion

Type: research
Status: resolved

## Question

What is a minimal, reproducible local Airflow setup suitable for this Zoomcamp project’s CCR ingestion into Postgres/pgvector?

## Answer

**Carried forward** from the pre-cut research ticket ([archive](../archive/future-scope/issues/02-airflow-local-compose.md)).

Use the official Airflow 3.3.0 `docker-compose.yaml` (CeleryExecutor) as the reproducible local baseline; keep Airflow metadata Postgres separate from app Postgres/pgvector; mount or bake project Python and call it via `@task`/`PythonOperator` + `PostgresHook`. Optional LocalExecutor trim drops Redis/worker for laptop RAM. Auth default: `airflow`/`airflow` at `http://localhost:8080` (demo-only).

Findings (live path): [`research/airflow-local-compose.md`](../../../research/airflow-local-compose.md)

**CCR-only note:** DAGs target CCR PDF fetch/extract + compliance-table load—not ASR/WQP/GPCD pipelines.
