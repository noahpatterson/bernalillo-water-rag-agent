# Minimal local Airflow for Python → Postgres/pgvector ingestion

**Ticket:** `.scratch/bernalillo-water-qa/issues/02-airflow-local-compose.md`  
**Airflow docs version consulted:** 3.3.0 (stable at research time)  
**Primary sources only** (official Apache Airflow / docker-stack docs and the shipped compose file).

## Verdict

For a Zoomcamp-style student project, start from the **official Airflow 3.3.0 `docker-compose.yaml`** (CeleryExecutor quick-start), then keep Airflow’s metadata Postgres separate from the app’s Postgres/pgvector service; mount project code via volumes + `PYTHONPATH` (or bake deps into a custom image), and call ingestion with `@task` / `PythonOperator`. Do **not** treat third-party “minimal Airflow” compose blogs as the source of truth—the community’s published local pattern is this compose file, labeled for learning/exploration only.

## Official vs community compose

| Approach | What it is | Fit for this project |
| --- | --- | --- |
| **Official compose** | Fetch `docker-compose.yaml` from Airflow docs; CeleryExecutor + Redis + Postgres metadata DB | **Recommended baseline**—reproducible, versioned with the docs, maintained by the project |
| **Trimmed LocalExecutor fork of that file** | Same images/dirs; set `AIRFLOW__CORE__EXECUTOR=LocalExecutor`; drop Redis + Celery worker (and often Flower) | Reasonable **RAM-saving customization** for a laptop; not a separate official file—you own the diffs |
| **Helm / K8s** | Official production path called out in the compose guide | Out of scope for local student demo |
| **Blog “3-service Airflow” recipes** | Secondary | Skip unless they merely restate the official file |

**Fetch command (pin the docs version you use):**

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.3.0/docker-compose.yaml'
```

Sources: [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html); shipped file comments warn local-dev only ([compose on `main`](https://github.com/apache/airflow/blob/main/airflow-core/docs/howto/docker-compose/docker-compose.yaml)).

## Services in the official compose (Airflow 3.3.0)

The quick-start runs **CeleryExecutor**. Documented / file services:

| Service | Role | Required for Celery quick-start? |
| --- | --- | --- |
| `postgres` | Airflow **metadata** DB (`airflow`/`airflow`, DB `airflow`) | Yes |
| `redis` | Celery broker | Yes (Celery) |
| `airflow-apiserver` | UI + API at `http://localhost:8080` (Airflow 3 replaces classic webserver) | Yes |
| `airflow-scheduler` | Schedules work | Yes |
| `airflow-dag-processor` | Parses DAG files (Airflow 3 split) | Yes |
| `airflow-worker` | Celery worker executes tasks | Yes (Celery) |
| `airflow-triggerer` | Deferrable tasks | Yes in official file; only needed if you use deferrable operators |
| `airflow-init` | DB migrate + create admin user | One-shot before `up` |
| `flower` | Celery monitor (`--profile flower`) | Optional |
| `airflow-cli` | Debug profile helper | Optional |

Sources: [Running Airflow in Docker — service list](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html); [3.3.0 compose YAML](https://airflow.apache.org/docs/apache-airflow/3.3.0/docker-compose.yaml) (`AIRFLOW__CORE__EXECUTOR: CeleryExecutor`).

### Minimum mental model for *this* ingestion project

Treat **two Postgres roles** as distinct:

1. **Airflow metadata** — the compose `postgres` service (do not store embeddings / domain tables here).
2. **App data** — a separate Postgres (+ pgvector) container or host DB that ingestion writes to.

Airflow’s default executor in core config is **LocalExecutor** (simplest local option); the **compose quick-start deliberately uses Celery** so students see a multi-component layout. For a low-RAM Mac, switching the official file to LocalExecutor and removing `redis` + `airflow-worker` (+ Flower) is a common simplification, but it is a **local edit**, not a second official download.

Sources: [Executor overview — LocalExecutor default](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/index.html); [LocalExecutor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/local.html).

### Prerequisites (from official guide)

- Docker CE; Docker Compose **v2.14.0+**
- **≥4 GB** RAM for Docker (ideally **8 GB** on macOS—default Docker Desktop memory is often too low and the API server may flap)
- Init: `mkdir -p ./dags ./logs ./plugins ./config`, then `docker compose up airflow-init`, then `docker compose up`

Source: [Before you begin / Initializing Environment](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

## How a simple DAG calls project Python → Postgres/pgvector

### 1. Get project code onto the workers’ Python path

Official compose mounts:

- `./dags` → `/opt/airflow/dags`
- `./logs`, `./config`, `./plugins` similarly

Airflow auto-adds **dags**, **config**, and **plugins** to `sys.path`. For ingestion modules living outside `dags/` (recommended: keep DAGs thin), either:

- mount the repo (e.g. `../src` or project root) into the container and set `PYTHONPATH`, or  
- install the project as a package in a **custom image** (`build: .` + Dockerfile extending `apache/airflow:3.3.0`).

Use a unique package name, `__init__.py` packages, and **absolute** imports (no relative imports in DAGs). Put shared non-DAG code behind `.airflowignore` if it lives under `dags/`.

Sources: [Modules Management](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html); compose volume block in [docker-compose.yaml](https://airflow.apache.org/docs/apache-airflow/3.3.0/docker-compose.yaml); [Using custom images](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#using-custom-images).

### 2. Prefer extending the image over `_PIP_ADDITIONAL_REQUIREMENTS`

For `psycopg`, `pgvector` client libs, embedding SDKs, etc.:

- Official guidance: comment `image:`, enable `build: .`, Dockerfile `FROM apache/airflow:3.3.0` + `pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt`.
- `_PIP_ADDITIONAL_REQUIREMENTS` is documented as **quick checks only** (slow starts; not for sustained use).

Sources: [Special case — requirements.txt](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#special-case-adding-dependencies-via-requirements-txt-file); [Entrypoint — installing additional requirements](https://airflow.apache.org/docs/docker-stack/entrypoint.html); [Building the image](https://airflow.apache.org/docs/docker-stack/build.html).

### 3. Wire a Postgres connection for the *app* DB

Use a Postgres connection (UI or env URI):

```text
AIRFLOW_CONN_APP_POSTGRES='postgresql://USER:PASSWORD@HOST:5432/DBNAME'
```

From Docker Compose, `HOST` is the **app** service name on the Compose network (not `localhost`). If the DB runs on the Mac host, use `host.docker.internal` and, on Linux, the documented `extra_hosts` pattern.

Sources: [PostgreSQL Connection](https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/connections/postgres.html); [Networking](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#networking).

### 4. Thin DAG + project callable

Airflow 3 docs recommend **`@task`** over classic `PythonOperator` when you do not need Jinja templating in arguments. Pattern:

```python
# dags/ingest_water.py  (illustrative — do not scaffold yet)
from datetime import datetime
from airflow.sdk import dag, task

@dag(schedule="@daily", start_date=datetime(2024, 1, 1), catchup=False)
def bernalillo_ingest():
    @task
    def load_to_pgvector():
        # Project code on PYTHONPATH — e.g. mount + import
        from my_project.ingest import run_ingestion
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id="app_postgres")
        conn = hook.get_conn()  # DB-API connection
        run_ingestion(conn)     # embeddings / COPY / SQL live in project module

    load_to_pgvector()

bernalillo_ingest()
```

Notes:

- Keep SQL/embedding logic in the **project package**; the DAG is scheduling glue.
- `PostgresHook` is the provider API for Python callables; for raw SQL tasks, provider docs point to `SQLExecuteQueryOperator` (PostgresOperator deprecated path).
- New DAGs are **paused at creation** in the official compose (`AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'`)—unpause in the UI.

Sources: [Operators — `@task` / PythonOperator](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html); [PostgresHook API](https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/_api/airflow/providers/postgres/hooks/postgres/index.html); [Postgres operators how-to](https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/operators.html); compose env in [docker-compose.yaml](https://airflow.apache.org/docs/apache-airflow/3.3.0/docker-compose.yaml).

## Local auth defaults (demo-safe, not production)

From official init / docs:

| Item | Default |
| --- | --- |
| UI URL | `http://localhost:8080` |
| Username | `airflow` (`_AIRFLOW_WWW_USER_USERNAME`) |
| Password | `airflow` (`_AIRFLOW_WWW_USER_PASSWORD`) |
| Auth manager (compose) | `FabAuthManager` |
| Example DAGs | `AIRFLOW__CORE__LOAD_EXAMPLES: 'true'` in the shipped YAML (noisy; set `'false'` for a clean student UI) |
| Compose security posture | Explicitly **not** production-safe |

Init creates the user via `_AIRFLOW_WWW_USER_CREATE=true` on `airflow-init`. REST API examples use username/password then JWT (`/auth/token`).

**Demo hygiene:** bind only to localhost (default port publish), keep `airflow`/`airflow` only on a personal machine, turn off examples, do not expose 8080 to the internet.

Sources: [Initialize the database / Accessing the web interface](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html); [Entrypoint — creating admin user](https://airflow.apache.org/docs/docker-stack/entrypoint.html); compose `airflow-init` env block.

## Beginner gotchas

### Apple Silicon / Docker Desktop Mac

- Official images are **multi-platform AMD64/ARM64**—pull `apache/airflow:3.3.0` on Apple Silicon without a special “M1 fork.”
- Allocate **≥4 GB** (prefer **8 GB**) Docker memory; official tip: default Mac allocation is often insufficient.
- On macOS/Windows, unset `AIRFLOW_UID` warning is ignorable; `.env` with `AIRFLOW_UID=50000` silences it. On Linux, set `AIRFLOW_UID=$(id -u)` so mounted `dags`/`logs` are not root-owned.

Sources: [docker-stack — multi-platform images](https://airflow.apache.org/docs/docker-stack/index.html); [Before you begin / Setting the right Airflow user](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

### Mounting project code

- Only `dags`/`logs`/`config`/`plugins` are mounted by default—**your `src/` package is invisible until you add a volume + `PYTHONPATH` or bake it into the image.**
- Avoid naming top-level packages `airflow`, `logging`, etc. (shadowing).
- Prefer custom image for Python deps; do not rely on `_PIP_ADDITIONAL_REQUIREMENTS` for the course project.

Sources: [Modules Management](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html); compose volumes; pip-additional warning in compose + entrypoint docs.

### Parallelism and resource burn

- **Celery compose** runs many long-lived containers (scheduler + dag-processor + worker + apiserver + triggerer + redis + postgres)—heavy on a student laptop.
- **LocalExecutor** `[core] parallelism` defaults to **32**; in containers that looks like the scheduler eating RAM and can OOM/restart. Lower parallelism for local demos. Unlimited parallelism (`0`) was **removed in Airflow 3.0**.
- macOS LocalExecutor uses **spawn** (not fork) multiprocessing start method.
- Compose init warns if Docker has **&lt;4 GB RAM** or **&lt;2 CPUs**.

Sources: [LocalExecutor — parallelism / spawn on macOS / OOM warning](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/local.html); compose `airflow-init` resource checks.

### Airflow 3 naming surprises (vs older Zoomcamp blogs)

- UI process is **`api-server`**, not `webserver`.
- Separate **`dag-processor`** service.
- Older tutorials that only start `webserver` + `scheduler` against SQLite do not match the current official compose.

Source: [Running Airflow in Docker — services](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

### Metadata DB vs app DB

Beginners often point ingestion at the compose `postgres` (`airflow` database). That DB is for Airflow internals. Use a **second** Postgres (with pgvector) for domain data.

## Recommended compose approach (this repo)

1. Download **Airflow 3.3.0** official `docker-compose.yaml`.
2. Set `.env`: `AIRFLOW_UID=50000` (Mac), optionally override admin password, set `AIRFLOW__CORE__LOAD_EXAMPLES=false` if you edit the file/env.
3. Extend image for project + provider deps (`psycopg`, etc.); mount repo package on `PYTHONPATH`.
4. Add **app** Postgres/pgvector as a sibling Compose service (or reuse an existing project Compose file on the same network); create `AIRFLOW_CONN_…` for it.
5. If Docker Desktop RAM is tight: switch executor to **LocalExecutor** and remove Redis + Celery worker before adding more project services.
6. Do **not** scaffold Airflow into the repo until implementation tickets ask for it.

## Key citations

1. https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html  
2. https://airflow.apache.org/docs/apache-airflow/3.3.0/docker-compose.yaml  
3. https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/index.html  
4. https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/local.html  
5. https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/modules_management.html  
6. https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html  
7. https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/connections/postgres.html  
8. https://airflow.apache.org/docs/docker-stack/index.html  
9. https://airflow.apache.org/docs/docker-stack/entrypoint.html  
10. https://airflow.apache.org/docs/docker-stack/build.html  
