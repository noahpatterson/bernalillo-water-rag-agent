# Wayfinder map: Bernalillo County water Q&A

## Destination

A public, docker-composed Streamlit app that answers Bernalillo County water questions—priority themes ASR monitoring-well readings (NM Water Data), water-quality trends, and per-capita use (aquifer depth / quantity next)—via hybrid knowledge base + tools with citations; scores full LLM Zoomcamp project 2s plus hybrid search, reranking, and query rewriting; Airflow-automated ingestion into Postgres/pgvector; Grafana + user-feedback monitoring (≥5 charts); OpenAI for the runtime LLM. Built so the human learns by implementing retrieval, tools, prompts, and eval—not vibe-coded.

## Notes

- **Domain**: Bernalillo County, NM water; institutions in scope: ABCWUA, USGS, NMED, NM Water Data catalog ASR wells. See `CONTEXT.md`.
- **Course**: [LLM Zoomcamp project](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md). Separate repo; peer-reviewed.
- **Stack locks**: Streamlit UI; Postgres + pgvector; Airflow for ingestion (resume-relevant; expect extra teaching help); Grafana + feedback for monitoring; OpenAI API key (dev: cheaper/free-tier mini model; stronger model when cost allows—confirm exact API model IDs in a ticket).
- **Architecture**: Hybrid (B)—KB for narrative/methodology docs; tools for exact series/readings. Seam locked in [Decide knowledge base vs tools seam](issues/03-kb-vs-tools-seam.md).
- **Learning mode (fatal)**: Agent may scaffold structure, tests, and review diffs. Human implements retrieval, tools, prompts, and eval loops. No whole-app generation dumps. Prefer explaining *why* before code.
- **Timeline**: ~4 intensive days.
- **Skills**: `/grilling`, `/domain-modeling`, `/research` for research tickets; `/prototype` only when a cheap artifact unblocks a decision.
- **Tracker**: local markdown under `.scratch/bernalillo-water-qa/`.
- **Git remote**: local only until the human asks to push (`noahpatterson/...`).

## Decisions so far

<!-- index — one line per closed ticket -->

- [Catalog public data sources for priority themes](issues/01-data-source-inventory.md) — CCR/NMED/WQP for quality; ABCWUA ASR PDFs+AIS for Bear Canyon; ABCWUA GPCD (~125 CY2024) for per-capita; USGS basin levels later ([findings](../../research/data-source-inventory.md))
- [Minimal local Airflow pattern for this ingestion](issues/02-airflow-local-compose.md) — Official Airflow 3.3.0 docker-compose (Celery) baseline; separate app Postgres/pgvector; thin DAG → `@task` + PostgresHook ([findings](../../research/airflow-local-compose.md))
- [Decide knowledge base vs tools seam](issues/03-kb-vs-tools-seam.md) — CCR→KB (+ contaminant table tool); WQP/NMED tools; NM Water Data ASR wells→tools; GPCD table tool + methodology KB; Bear Canyon out of scope; dual citation shapes
- [Inventory NM Water Data ASR monitoring wells access](issues/08-asr-nm-water-data-access.md) — CKAN CSV download (CF may block bots); `5bc7cc13` = DWTP Large-Scale MW-01S/D transducer; quarterly catalog refresh; license unspecified ([findings](../../research/asr-nm-water-data-access.md))

## Not yet specified

- Chunking and embedding choices for CCR PDFs vs structured WQP / ASR rows
- Exact Grafana chart set (≥5) once metrics exist
- Aquifer expansion: which USGS Albuquerque Basin wells/parameters when priority themes ship
- ABCWUA site ToS operational detail: how much CCR text to store vs summarize (ingest-extracted is decided; chunk policy TBD)
- Query-rewrite and rerank library choices
- Whether Airflow runs ingestion only or also eval/batch jobs
- Ground-truth construction method beyond golden questions (LLM-as-judge thresholds, etc.)

## Out of scope

- Cloud deployment (bonus only if time remains after full 2s)
- Statewide New Mexico water (outside county / ABCWUA footprint except as needed to interpret a county series)
- Using DataTalksClub Zoomcamp FAQ docs as the knowledge base (forbidden by course)
- Autonomous “generate the entire app” vibe-coding
- Bear Canyon arroyo recharge as a must-work theme (daily diversion PDFs, Bear Canyon demo questions, USGS 08329868 as ASR meter)—replaced by NM Water Data ASR monitoring wells; see [Decide knowledge base vs tools seam](issues/03-kb-vs-tools-seam.md)
