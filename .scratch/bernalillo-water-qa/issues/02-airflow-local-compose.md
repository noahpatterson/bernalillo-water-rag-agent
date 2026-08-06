# Minimal local Airflow pattern for this ingestion

Type: research
Status: resolved

## Question

What is a minimal, reproducible local Airflow setup (preferably docker-compose–friendly) suitable for a Zoomcamp-style student project that schedules Python ingestion into Postgres—without enterprise bloat?

Cover: Official vs community compose approaches in current Airflow docs, minimum services required, how a simple DAG would call project Python to load into Postgres/pgvector, local auth defaults safe for demo, and gotchas that burn beginners (Apple Silicon, parallelism, mounting project code). Prefer primary Airflow documentation over blog posts.

## Answer

Use the official Airflow 3.3.0 `docker-compose.yaml` (CeleryExecutor) as the reproducible local baseline; keep Airflow metadata Postgres separate from app Postgres/pgvector; mount or bake project Python and call it via `@task`/`PythonOperator` + `PostgresHook`. Optional LocalExecutor trim drops Redis/worker for laptop RAM. Auth default: `airflow`/`airflow` at `http://localhost:8080` (demo-only).

Findings: [`research/airflow-local-compose.md`](../../../research/airflow-local-compose.md)
