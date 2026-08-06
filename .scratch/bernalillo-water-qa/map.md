# Wayfinder map: Bernalillo County water Q&A (CCR-only)

## Destination

A public, docker-composed Streamlit app that answers **ABCWUA Consumer Confidence Report (CCR)** water-quality questions from (1) ingested CCR narrative/chunks and (2) extracted **COMPLIANCE MONITORING RESULTS** tables—with citations—scoring full LLM Zoomcamp project 2s plus hybrid search, reranking, and query rewriting; Airflow-automated ingestion into Postgres/pgvector; Grafana + user-feedback monitoring (≥5 charts); OpenAI for the runtime LLM. Built so the human learns by implementing retrieval, tools, prompts, and eval—not vibe-coded.

## Notes

- **Domain**: ABCWUA finished drinking water / CCR compliance story (PWS NM35-10701). See `CONTEXT.md`.
- **Course**: [LLM Zoomcamp project](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md). Separate repo; peer-reviewed.
- **Corpus on disk**: `data/raw/abcwua/ABCWUA-CCR-2020.pdf` … `2025.pdf` + `SOURCE.txt` (seeded 2026-08-06). Compliance table: `data/raw/processed/CCR_Compliance_Results.csv` + `SOURCE.txt`.
- **Stack locks**: Streamlit; Postgres + pgvector; Airflow for CCR ingest; Grafana + feedback; OpenAI (`OPENAI_MODEL_DEV` / `_STRONG`—see Decisions).
- **Architecture**: Knowledge base for CCR narrative + surrounding report text; **one** structured tool for COMPLIANCE MONITORING RESULTS lookups (contaminant × year). No WQP/ASR/GPCD tools on this path.
- **Learning mode (fatal)**: Agent may scaffold structure, tests, and review diffs. Human implements retrieval, tools, prompts, and eval loops. No whole-app generation dumps. Prefer explaining *why* before code.
- **Prior broader map**: [archive/future-scope/](archive/future-scope/) (ASR, WQP, GPCD, aquifer, old tickets).
- **Airflow findings (still live)**: [`research/airflow-local-compose.md`](../../research/airflow-local-compose.md)
- **Timeline**: ~4 intensive days.
- **Skills**: `/grilling`, `/domain-modeling`, `/research` for research tickets; `/prototype` only when a cheap artifact unblocks a decision.
- **Tracker**: local markdown under `.scratch/bernalillo-water-qa/`.
- **Git remote**: local only until the human asks to push (`noahpatterson/...`).

## Decisions so far

<!-- index — one line per closed ticket -->

- [Cut scope to CCR PDFs + compliance tables](issues/01-ccr-only-scope.md) — Graded path = ABCWUA CCR 2020–2025 + COMPLIANCE MONITORING RESULTS; prior multi-theme work archived under `archive/future-scope/`
- [Minimal local Airflow pattern for this ingestion](issues/02-airflow-local-compose.md) — Official Airflow 3.3.0 docker-compose baseline; separate app Postgres/pgvector ([findings](../../research/airflow-local-compose.md); archived research ticket)
- [Decide CCR knowledge base vs compliance-table tool seam](issues/03-kb-vs-tools-seam.md) — CCR text → KB; COMPLIANCE MONITORING RESULTS → one table tool; dual citation shapes; refuse if neither hits
- [Confirm OpenAI runtime model IDs](issues/04-openai-runtime-models.md) — Dev `gpt-5.4-mini` (effort none) / strong `gpt-5.6-luna` (effort medium); `OPENAI_MODEL_DEV`/`_STRONG`; OpenAI SDK; floating aliases
- [Plan retrieval evaluation approaches](issues/05-retrieval-eval-plan.md) — Core vector/FTS/hybrid(RRF); add-ons rewrite+rerank on hybrid; hit_rate@5+MRR; CCR KB fixtures ≥10; local script → `docs/eval/retrieval.md`
- [Plan LLM output evaluation approaches](issues/06-llm-eval-plan.md) — Single-shot vs cite-or-refuse; auto field/ID checks + human narrative; ship cite-or-refuse; CCR-only goldens
- [Define CCR golden questions for must-work queries](issues/07-golden-questions-ccr.md) — GQ-T1 arsenic 2020–2025 + GQ-T2 nitrate 2024 (table); GQ-K1 arsenic FAQ + GQ-K2 source/treatment (KB); shape+cite pass bar; paraphrases later
- [Decide CCR chunking and embeddings](issues/08-chunk-embed-ccr.md) — pymupdf extract; section-aware chunks + MiniLM ONNX `models/Xenova/all-MiniLM-L6-v2` (384-d); strip compliance tables, keep year stubs
- [Choose rerank and query-rewrite libraries](issues/09-rerank-rewrite-libraries.md) — FlashRank `ms-marco-MiniLM-L-12-v2` (top 20→5); OpenAI SDK rewrite on active DEV/STRONG tier
- [Decide COMPLIANCE MONITORING RESULTS extract and table schema](issues/10-compliance-table-schema.md) — Curated CSV seed; full compliance-section rows 2020–2025; canonical columns for table tool
- [Seed CCR compliance-results CSV](issues/11-seed-compliance-csv.md) — `data/raw/processed/CCR_Compliance_Results.csv` + SOURCE.txt (curated 2026-08-06; full 2020–2025 compliance rows)

## Not yet specified

- Exact Grafana chart set (≥5) once metrics exist
- Whether Airflow later runs eval/batch jobs (retrieval harness is local scripts for v1)
- How much non-table CCR prose to embed vs skip (boilerplate mailer pages) — section-aware policy locked; tune which sections to drop in implementation
- Numeric fixtures for GQ-T1/T2 from the curated CSV (arsenic trend; nitrate 2024)
- KB retrieval fixture expansion to ≥10 labeled questions (beyond GQ-K1/K2) once chunk IDs exist
- Optional later: automated pymupdf table extract to refresh the curated CSV
- Fill empty `source_url` / normalize `pws_id` on compliance CSV rows at ingest if still Null

## Out of scope

- Cloud deployment (bonus only if time remains after full 2s)
- Statewide New Mexico water beyond ABCWUA CCR footprint
- Using DataTalksClub Zoomcamp FAQ docs as the knowledge base (forbidden by course)
- Autonomous “generate the entire app” vibe-coding
- **Future scope (archived):** ASR / NM Water Data wells, Bear Canyon, WQP ambient tools, NMED DWW tools, GPCD/per-capita, aquifer depth/quantity expansion — see [archive/future-scope/](archive/future-scope/)
