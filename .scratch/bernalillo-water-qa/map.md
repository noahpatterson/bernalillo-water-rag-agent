# Wayfinder map: Bernalillo County water Q&A

## Destination

A public, docker-composed Streamlit app that answers Bernalillo County water questions—priority themes Bear Canyon recharge, water-quality trends, and per-capita use (aquifer depth / quantity next)—via hybrid knowledge base + tools with citations; scores full LLM Zoomcamp project 2s plus hybrid search, reranking, and query rewriting; Airflow-automated ingestion into Postgres/pgvector; Grafana + user-feedback monitoring (≥5 charts); OpenAI for the runtime LLM. Built so the human learns by implementing retrieval, tools, prompts, and eval—not vibe-coded.

## Notes

- **Domain**: Bernalillo County, NM water; institutions in scope: ABCWUA, USGS, NMED, named sites (e.g. Bear Canyon recharge). See `CONTEXT.md`.
- **Course**: [LLM Zoomcamp project](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md). Separate repo; peer-reviewed.
- **Stack locks**: Streamlit UI; Postgres + pgvector; Airflow for ingestion (resume-relevant; expect extra teaching help); Grafana + feedback for monitoring; OpenAI API key (dev: cheaper/free-tier mini model; stronger model when cost allows—confirm exact API model IDs in a ticket).
- **Architecture**: Hybrid (B)—KB for narrative/methodology docs; tools for exact series/readings.
- **Learning mode (fatal)**: Agent may scaffold structure, tests, and review diffs. Human implements retrieval, tools, prompts, and eval loops. No whole-app generation dumps. Prefer explaining *why* before code.
- **Timeline**: ~4 intensive days.
- **Skills**: `/grilling`, `/domain-modeling`, `/research` for research tickets; `/prototype` only when a cheap artifact unblocks a decision.
- **Tracker**: local markdown under `.scratch/bernalillo-water-qa/`.
- **Git remote**: local only until the human asks to push (`noahpatterson/...`).

## Decisions so far

<!-- index — one line per closed ticket -->
- [Catalog public data sources for priority themes](.scratch/bernalillo-water-qa/issues/01-data-source-inventory.md) — CCR/NMED/WQP for quality; ABCWUA ASR PDFs+AIS for Bear Canyon; ABCWUA GPCD (~125 CY2024) for per-capita; USGS basin levels later

- [Minimal local Airflow pattern for this ingestion](issues/02-airflow-local-compose.md) — Official Airflow 3.3.0 docker-compose (Celery) baseline; separate app Postgres/pgvector; thin DAG → `@task` + PostgresHook ([findings](../../research/airflow-local-compose.md))

## Not yet specified

- Chunking and embedding choices once source formats are known
- Exact Grafana chart set (≥5) once metrics exist
- Aquifer-depth / quantity source selection (after priority themes land)
- Population denominator / year for per-capita (Census vs ABCWUA customer counts)
- Query-rewrite and rerank library choices
- Whether Airflow runs ingestion only or also eval/batch jobs
- Ground-truth construction method beyond golden questions (LLM-as-judge thresholds, etc.)

## Out of scope

- Cloud deployment (bonus only if time remains after full 2s)
- Statewide New Mexico water (outside county / ABCWUA footprint except as needed to interpret a county series)
- Using DataTalksClub Zoomcamp FAQ docs as the knowledge base (forbidden by course)
- Autonomous “generate the entire app” vibe-coding
