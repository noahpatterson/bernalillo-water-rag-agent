# Implementation task list (CCR-only)

Locked decisions live in [map.md](map.md). You implement; agent may scaffold/review if asked.

**Already done**

- [x] CCR PDFs 2020–2025 in `data/raw/abcwua/`
- [x] Compliance CSV in `data/raw/processed/CCR_Compliance_Results.csv` + `SOURCE.txt`
- [x] Wayfinder decisions (models, seam, eval plans, goldens, chunk/embed, rerank/rewrite)

---

## 0. Repo / env bootstrap

- [x] Python project layout (`pyproject.toml` / `uv` or pip) + `.env.example`
- [x] Env vars: `OPENAI_API_KEY`, `OPENAI_MODEL_DEV=gpt-5.4-mini`, `OPENAI_MODEL_STRONG=gpt-5.6-luna`, `OPENAI_MODEL_TIER=dev`, DB URL for app Postgres
- [ ] README section **“App runtime models (not Cursor)”**
- [x] `.gitignore`: `.env`, `models/`, `.venv/`, Airflow logs, etc.
- [x] Download Zoomcamp ONNX MiniLM → `models/Xenova/all-MiniLM-L6-v2/` (onnxruntime embedder)

## 1. App Postgres + schema

- [x] Docker service: Postgres **with pgvector** (separate from Airflow metadata DB)
- [ ] Tables roughly:
  - [x] `kb_chunks` — id, report_year, section, source_url, text, tsv (FTS), embedding `vector(384)`
  - [x] `compliance_results` — columns matching the CSV (+ normalize `pws_id=NM35-10701`, fill `source_url` on load)
  - [ ] Optional: feedback / query_log tables for Grafana later

## 2. Ingest: compliance tool data

- [x] Loader: CSV → `compliance_results` (idempotent upsert by report_year + contaminant)
- [x] Spot-check: arsenic 2020–2025 + nitrate 2024 match CSV/PDF
- [x] Tool function: `lookup_compliance(contaminant, report_year | year_range)` → rows + citation fields

## 3. Ingest: CCR knowledge base

- [x] `pymupdf` / `pymupdf4llm` extract text from CCR PDFs (`ingest_pdfs.py`; start with 2020, same path for 2021–2025)
- [x] Strip COMPLIANCE MONITORING RESULTS table bodies; keep **year stub** chunks
- [x] Page-based chunking (CCR mailer layout not heading-friendly); metadata: year, section=`page_N`, URL; skip near-empty pages
- [x] Embed with local MiniLM ONNX; write pgvector + generated FTS `tsv`
- [x] Smoke: GQ-K1 / GQ-K2 vector retrieval returns sensible 2020 chunks (`page_4` / `page_2`)

## 4. Retrieval stack (implement + compare)

- [x] vector-only (pgvector)
- [x] text-only (Postgres FTS)
- [x] hybrid + **RRF**
- [ ] hybrid + **FlashRank** `ms-marco-MiniLM-L-12-v2` (top 20 → top 5)
- [ ] **query rewrite** (OpenAI SDK, active DEV/STRONG tier) → hybrid
- [ ] rewrite → hybrid + rerank
- [ ] Local eval script → `docs/eval/retrieval.md` (hit_rate@5, MRR)
- [ ] After chunk IDs exist: label **≥10** KB retrieval fixtures (start from GQ-K1/K2 + paraphrases)
- [ ] Pick production retrieval stack from eval winner rule

## 5. Generation flows

- [ ] Wire OpenAI SDK: DEV (`gpt-5.4-mini`, effort `none`) / STRONG (`gpt-5.6-luna`, effort `medium`)
- [ ] Router: compliance-ish questions → table tool; narrative → KB retrieval (or both)
- [ ] **Single-shot** flow (eval only)
- [ ] **Cite-or-refuse** flow (ship this) — citations bind to logged chunk/tool row IDs
- [ ] Citation shapes: KB vs tool (see seam ticket)
- [ ] LLM eval harness on goldens → snapshot + reproducible script; ship cite-or-refuse

## 6. Must-work goldens (demo gate)

| ID    | Path | Question focus                        |
| ----- | ---- | ------------------------------------- |
| GQ-T1 | Tool | Arsenic 2020–2025 trend               |
| GQ-T2 | Tool | Nitrate 2024                          |
| GQ-K1 | KB   | Arsenic FAQ / EPA standards narrative |
| GQ-K2 | KB   | Source water + treatment narrative    |

- [ ] Encode expected numerics from CSV into fixture file
- [ ] Auto checks (fields + citation IDs) + human narrative pass
- [ ] Fail wrong-lane answers (µg/L from KB alone when tool should hit)

## 7. next.js app with eve agent

- [ ] Chat UI: ask → answer + citations
- [ ] Tier toggle (DEV / STRONG) or `OPENAI_MODEL_TIER`
- [ ] Show/refuse when no citeable hit
- [ ] Optional: user feedback widget (thumbs / note) → DB

## 8. Airflow

- [ ] Official Airflow 3.3.0 compose (see `research/airflow-local-compose.md`)
- [ ] Thin DAG: CCR PDF extract/chunk/embed + compliance CSV load via `@task` + PostgresHook
- [ ] Do **not** put domain tables in Airflow metadata Postgres

## 9. Monitoring

- [ ] Grafana + ≥5 charts (e.g. query volume, latency, feedback score, retrieval mode mix, refuse rate, token/cost proxy)
- [ ] Document chart list in README once metrics exist

## 10. Project packaging for Zoomcamp

- [ ] `docker compose` brings up app + Postgres (+ Airflow + Grafana as needed)
- [ ] README: setup, models note, data sources, eval links, how to run goldens
- [ ] Commit eval snapshots under `docs/eval/`
- [ ] Push to `noahpatterson/...` when you choose

---

## Suggested build order (4-day style)

1. **Day 1:** §0–2 (env, DB, compliance load + tool)
2. **Day 2:** §3–4 (KB ingest + retrieval bake-off)
3. **Day 3:** §5–7 (cite-or-refuse + Streamlit + goldens green)
4. **Day 4:** §8–10 (Airflow, Grafana, README polish)

## Do not build (future scope)

ASR / NM Water Data, WQP, NMED tools, GPCD, aquifer — see `archive/future-scope/`.
