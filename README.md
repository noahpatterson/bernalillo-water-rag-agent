# bernalillo-water-rag

LLM Zoomcamp project: ABCWUA Consumer Confidence Report water-quality Q&A (RAG + compliance-table tool).

## Problem description

Albuquerque Bernalillo County Water Utility Authority (ABCWUA) publishes yearly Consumer Confidence Reports. Those PDFs answer common questions (is my tap water safe, where it comes from, lead, arsenic, PFAS) but they are long, split across years, and mix narrative with compliance tables.

This RAG tool lets a resident ask in plain language and get an answer grounded in the 2020-2025 reports. Narrative questions go through hybrid search over report chunks. Measured levels and contaminant definitions go through structured lookups so the model does not invent numbers. If the reports do not cover the question, the agent should say so and point at the official site.

### Limitations

- Corpus is ABCWUA CCRs for 2020-2025 only. No other utilities, no data newer than the last ingested report, and no household-specific plumbing or tap-test results.
- Live `/search` does not filter by report year, so hits can mix years. Evaluation does filter to 2025.
- PDF ingest splits narrative and tables poorly. Some chunks are headers, figure OCR, or empty, so search can miss or land on a neighbor page.
- Compliance numbers come from a hand-extracted CSV, not live lab feeds. Lookups need a recognizable contaminant name and one year filter.
- MiniLM + RRF is a first-stage retriever, not a reranker. Nearby glossary or lead pages often outrank the exact chunk.
- The agent answers only from tool results. Out-of-scope or empty-evidence questions get a refusal, even when a general water-safety answer exists.

## Tech stack

- **API:** Python 3.13, FastAPI, Pydantic
- **Store:** Postgres 17 + pgvector (hybrid vector and full-text search)
- **Embeddings:** Xenova all-MiniLM-L6-v2 via ONNX Runtime
- **Agent / UI:** Eve + Next.js chat; OpenAI for the LLM; tools via FastAPI OpenAPI
- **Ingest:** PyMuPDF / pymupdf4llm for CCR PDFs; hand-curated compliance CSV
- **Ops:** Docker Compose, Grafana, uv, Ruff, Black

## Project prep

### 1. Python env

```bash
uv sync
cp .env.example .env
# fill OPENAI_API_KEY, POSTGRES_* , etc.
```

### Python linting and formatting

Ruff checks Python lint rules, and Black formats Python files:

```bash
uv run ruff check .
uv run black --check .
```

To apply automatic fixes and formatting:

```bash
uv run ruff check . --fix
uv run black .
```

### 2. Download CCR source PDFs

Raw PDFs are **not** in git (large, upstream-owned). After clone, pull them from ABCWUA:

```bash
uv run python scripts/download_raw_ccr.py
```

That writes `data/raw/abcwua/ABCWUA-CCR-2020.pdf` … `2025.pdf` from the URLs listed in `data/raw/abcwua/SOURCE.txt` (same mapping lives in the script). Re-run with `--force` to refresh existing files.

The curated compliance CSV **is** committed at `data/processed/abcwua/CCR_Compliance_Results.csv` (hand-extracted from those PDFs).

### 3. App Postgres (pgvector)

```bash
cp docker-compose.example.yml docker-compose.yml   # if you use a local compose file
docker compose -f docker-compose.example.yml up -d --build
uv run python db/init/db_init.py
```

Compose starts Postgres, Grafana (`http://localhost:3001`), and FastAPI (`http://localhost:8000`). The Eve knowledge connection uses that FastAPI origin. Mount `models/` into the API container (see step 4) before the first `up`.

### 4. Embedding model

Place / download the Zoomcamp ONNX MiniLM under `models/` (gitignored). See `.env.example` for `ONNX_EXECUTION_PROVIDER`.

### 5. Eve chat UI

The browser chat is Eve's official Next.js Web Chat starter, colocated with the agent in `bernalillo-water-rag-agent/`.

```bash
cd bernalillo-water-rag-agent
pnpm install
# needs OPENAI_API_KEY in the repo-root .env or this directory
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000). `pnpm dev` runs Next.js and Eve together. Use `pnpm dev:eve` if you only want Eve's terminal UI.

## Retrieval flow

CCR narrative search is the FastAPI `GET /search` tool. Eve sends the user question; the API embeds it with MiniLM, then runs two Postgres lookups on `knowledge_base_chunks`: `pgvector_search` (nearest neighbors) and `pg_full_text_search_soft_match` (any query term, not AND). Each list is 20 hits. `new_rrf` fuses those lists and returns the top 5 `FusedHit`s (chunk text, ranks, RRF score). Unlike the evaluation run, live search does not filter by `report_year`.

### Eve operations

Eve talks to FastAPI through the `knowledge` OpenAPI connection (`bernalillo-water-rag-agent/agent/connections/knowledge.ts`). The spec is `http://127.0.0.1:8000/openapi.json`.

On the first turn the agent calls Eve `connection_search` once with `search lookup_compliance lookup_contaminant_info`. That unlocks the qualified tools `knowledge__search`, `knowledge__lookup_compliance`, and `knowledge__lookup_contaminant_info`. Later turns reuse them. `agent/instructions.md` tells the model to call `knowledge__search` once per question, add the other tools when the question needs numbers or EPA context, and answer only from those results.

### Tools

- `search` (`GET /search`): hybrid CCR narrative retrieval described above.
- `lookup_compliance` (`GET /lookup_compliance`): measured values from `compliance_results` by contaminant and one year filter (`sample_year` / `sample_year_range` preferred unless the user says report year). Returns rows plus citations.
- `lookup_contaminant_info` (`GET /lookup_contaminant_info`): name, code, units, and source for one contaminant. Not part of hybrid search.

## Retrieval evaluation

Scores CCR chunk search against `data/processed/search_ground_truth.csv`. Each row is a resident-style question plus the `knowledge_base_chunks.id` that should answer it. The run filters to report year 2025 and compares four methods: `pgvector_search`, `pg_full_text_search`, `pg_full_text_search_soft_match`, and reciprocal rank fusion (`rrf`). Metrics are hit rate (labeled chunk in the top-k list) and MRR (mean of `1/rank` of that chunk).

Postgres and the MiniLM model from the steps above must be available. From the repo root:

```bash
uv run python -m evaluation.retrieval_evaluation
```

Each run appends one row per method to `evaluation/retrieval_evaluation_results.csv`, keyed by `run_date`:

```text
run_date,method,report_year,hit_rate,mrr
2026-08-14T18:21:57-06:00,pgvector_search,2025,0.94,0.72
```

### Ground-truth generation

`evaluation/retrieval_evaulation_ground_truth_generation.ipynb` builds that CSV. It loads 2025 `knowledge_base_chunks` from Postgres, asks an LLM for a few resident-style questions that each chunk can answer, and writes `{question, document}` rows. Re-run the notebook only when you want a new ground truth set. **Note: I manually and used a more advanced LLM (grok-4.6) to re-write the questions to be more realistic.** This brought down the hit rate and mrr, but is a more realistic evaluation of the search functions.

## LLM evaluation

Placeholder

## Interface

Residents use the Eve Next.js chat in `bernalillo-water-rag-agent/` at [http://localhost:3000](http://localhost:3000). Type a water-quality question; the agent calls the FastAPI tools and answers in the thread. Tool calls show up in the message stream. `pnpm dev:eve` is the same agent in Eve's terminal UI.

The machine interface is FastAPI at [http://localhost:8000](http://localhost:8000) (`/search`, `/lookup_compliance`, `/lookup_contaminant_info`, `/health`, OpenAPI at `/openapi.json`).

### TODO: Why Eve (draft)

The interesting work in this project is retrieval, ingest, and eval, not another chat stack. Eve already has a Next.js web chat, a terminal UI, streaming, session state, and tool-call rendering. Rolling that myself would mean owning the LLM loop, function-calling, and UI for little extra learning.

The `knowledge` OpenAPI connection is the other reason. FastAPI already exposes `/search`, `/lookup_compliance`, and `/lookup_contaminant_info`. Eve reads `/openapi.json` and turns those routes into `knowledge__*` operations after one `connection_search`. I did not want a second, hand-written tool schema next to the API.

Tradeoff to revisit: Eve is another runtime (not in Compose), first-turn discovery is ceremony, and model choice is whatever Eve's OpenAI provider supports. If the course writeup needs "I built the agent loop," this is the section to replace or defend.

## Ingestion pipeline

Placeholder

## Monitoring

Placeholder

## Containerization

`docker-compose.example.yml` runs the backend stack: pgvector Postgres, Grafana on port 3001, and the FastAPI image from `Dockerfile` on port 8000. The API container mounts `models/` read-only and talks to Postgres on the compose network.

Eve and the Next.js chat stay on the host (`pnpm dev`) and call `http://127.0.0.1:8000`. They are not in Compose. Copy the example file to `docker-compose.yml` if you want a local override, then `docker compose up -d --build`.

