# Wayfinder map: Bernalillo County water Q&A

## Destination

A public, docker-composed Streamlit app that answers Bernalillo County water questions—priority themes ASR monitoring-well readings (NM Water Data), water-quality trends, and per-capita use (aquifer depth / quantity next)—via hybrid knowledge base + tools with citations; scores full LLM Zoomcamp project 2s plus hybrid search, reranking, and query rewriting; Airflow-automated ingestion into Postgres/pgvector; Grafana + user-feedback monitoring (≥5 charts); OpenAI for the runtime LLM. Built so the human learns by implementing retrieval, tools, prompts, and eval—not vibe-coded.

## Notes

- **Domain**: Bernalillo County, NM water; institutions in scope: ABCWUA, USGS, NMED, NM Water Data catalog ASR wells. See `CONTEXT.md`.
- **Course**: [LLM Zoomcamp project](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md). Separate repo; peer-reviewed.
- **Stack locks**: Streamlit UI; Postgres + pgvector; Airflow for ingestion (resume-relevant; expect extra teaching help); Grafana + feedback for monitoring; OpenAI API key (dev: cheaper/free-tier mini model; stronger model when cost allows—confirm exact API model IDs in a ticket).
- **Architecture**: Hybrid (B)—KB for narrative/methodology docs; tools for exact series/readings. Seam locked in [Decide knowledge base vs tools seam](issues/03-kb-vs-tools-seam.md).
- **Learning mode (fatal)**: Agent may scaffold structure, tests, and review diffs. Human implements retrieval, tools, prompts, and eval loops. No whole-app generation dumps. Prefer explaining *why* before code.
- **ASR ingest note**: NM Water Data CKAN downloads often need a human browser seed (Cloudflare); see [Seed Large-Scale ASR CSV for first ingest](issues/09-seed-asr-csv.md) and [Inventory NM Water Data ASR monitoring wells access](issues/08-asr-nm-water-data-access.md).
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
- [Seed Large-Scale ASR CSV for first ingest](issues/09-seed-asr-csv.md) — `data/raw/nm-water-data-asr/largescaletransducer.csv` + manual + SOURCE.txt (fetched 2026-08-06; ~160k rows through 2022-09-12)
- [Define golden questions for must-work queries](issues/04-golden-questions.md) — GQ-Q1/Q2 (CCR arsenic, WQP nitrate), GQ-A1/A2 (MW-01S latest + CY2022 range), GQ-P1 (~125 GPCD CY2024), GQ-AQ1 best-effort; shape+cite pass bar
- [Plan LLM output evaluation approaches](issues/06-llm-eval-plan.md) — Compare single-shot vs cite-or-refuse (retrieval fixed); auto field/ID checks + human narrative; lexicographic winner; ship cite-or-refuse; snapshot + reproducible harness
- [Plan retrieval evaluation approaches](issues/05-retrieval-eval-plan.md) — Core vector/FTS/hybrid(RRF); add-ons rewrite+rerank on hybrid; hit_rate@5+MRR; KB-only fixtures ≥10; local script → `docs/eval/retrieval.md`
- [Confirm OpenAI runtime model IDs](issues/07-openai-runtime-models.md) — Dev `gpt-5.4-mini` (effort none) / strong `gpt-5.6-luna` (effort medium); `OPENAI_MODEL_DEV`/`_STRONG`; OpenAI SDK; floating aliases in `.env.example` + README “not Cursor”

## Not yet specified

- Exact Grafana chart set (≥5) once metrics exist
- Aquifer expansion: which USGS Albuquerque Basin wells/parameters when priority themes ship (GQ-AQ1 stays best-effort until then)
- ABCWUA site ToS operational detail: how much CCR text to store vs summarize (ingest-extracted is decided; chunk policy on [Decide CCR / methodology chunking and embeddings](issues/11-chunk-embed-ccr.md))
- Whether Airflow later runs eval/batch jobs (retrieval harness is local scripts for v1)
- Numeric fixtures for GQ-Q1/Q2/A1/A2 after CCR/WQP/ASR ingest; optional paraphrase variants of goldens
- KB retrieval fixture expansion to ≥10 labeled questions (beyond GQ-Q1) once chunk IDs exist after [Decide CCR / methodology chunking and embeddings](issues/11-chunk-embed-ccr.md)

## Out of scope

- Cloud deployment (bonus only if time remains after full 2s)
- Statewide New Mexico water (outside county / ABCWUA footprint except as needed to interpret a county series)
- Using DataTalksClub Zoomcamp FAQ docs as the knowledge base (forbidden by course)
- Autonomous “generate the entire app” vibe-coding
- Bear Canyon arroyo recharge as a must-work theme (daily diversion PDFs, Bear Canyon demo questions, USGS 08329868 as ASR meter)—replaced by NM Water Data ASR monitoring wells; see [Decide knowledge base vs tools seam](issues/03-kb-vs-tools-seam.md)
