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
- **Evals** Local and Eve Evals
- **Monitoring** Arize AX with OpenTelemetry - managed by Eve framework
- **Ops:** Docker Compose, uv, Ruff, Black

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

Compose starts Postgres, FastAPI (`http://localhost:8000`), and the Eve + Next.js chat (`http://localhost:3000`). The Eve knowledge connection uses that FastAPI origin. Mount `models/` into the API container (see step 4) before the first `up`.

### 4. Embedding model

Place / download the Zoomcamp ONNX MiniLM under `models/` (gitignored). See `.env.example` for `ONNX_EXECUTION_PROVIDER`.

### 5. Eve chat UI

The browser chat is Eve's official Next.js Web Chat starter, colocated with the agent in `bernalillo-water-rag-agent/`. Compose builds and starts it on [http://localhost:3000](http://localhost:3000) with the rest of the stack. Set `OPENAI_API_KEY` in the repo-root `.env` before `docker compose up`. Arize tracing keys (`ARIZE_SPACE_ID`, `ARIZE_API_KEY`) live in `bernalillo-water-rag-agent/.env.local`.

For local Next.js / Eve development instead of the container, stop the compose `eve` service first (port 3000) and run:

```bash
cd bernalillo-water-rag-agent
pnpm install
# needs OPENAI_API_KEY in the repo-root .env or this directory
pnpm dev
```

`pnpm dev` runs Next.js and Eve together. Use `pnpm dev:eve` if you only want Eve's terminal UI.

## Retrieval flow

CCR narrative search is the FastAPI `GET /search` tool. Eve sends the user question; the API embeds it with MiniLM, then runs two Postgres lookups on `knowledge_base_chunks`: `pgvector_search` (nearest neighbors) and `pg_full_text_search_soft_match` (any query term, not AND). Each list is 20 hits. `new_rrf` fuses those lists and returns the top 5 `FusedHit`s (chunk text, ranks, RRF score). Unlike the evaluation run, live search does not filter by `report_year`.

### Eve operations

Eve talks to FastAPI through the `knowledge` OpenAPI connection (`bernalillo-water-rag-agent/agent/connections/knowledge.ts`). On the host the spec is `http://127.0.0.1:8000/openapi.json`. Inside Compose it is `http://api.localhost:8000/openapi.json` (Docker DNS alias; Eve only allows `http://` for `*.localhost` hosts).

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

There are two types of LLM evaluation I created for this project:

### 1. Simple LLM-As-A-Judge

The simple llm-as-a-judge takes existing `ground_truth` data (without llm generated answers) and creates new answers via the project's Eve API. Then it runs a simple evaluation through a standard OpenAI call and expects a judge in the following format `'NON_RELEVANT' | 'PARTLY_RELEVANT' | 'RELEVANT',`. 

There's a helpful script to run these simple evaluations:

```bash
uv run python -m evaluation.agent_evaluation_simple \
  --eve-model gpt-5.4-mini \
  --judge-model gpt-5.4-mini \
  --sample-size 10 \
  --eve-host http://127.0.0.1:3000

// Optional paths: --ground-truth-path, --data-path, --results-path. 
```

What it does:
1. The script either uses default variables from main, or specific args you pass
2. `--eve-host` defaults to `http://127.0.0.1:3000` (the Compose Eve service, or host `pnpm dev`). Override it if you changed `EVE_PORT` or set `EVE_HOST` in `.env`.
3. NOTE: If you've changed the defaut Eve model in .env `OPENAI_MODEL_DEV` pass `--eve-model` with your model.
4. It uses the specific Eve Model and Judge Model you pass.
5. If the script sees an existing Eve generated evaluation data file e.g. `evaluation/agent_evaluation_data_gpt_5_4_mini.csv` then it skips re-creating those Eve answers. Delete the file to re-create it.
6. It then passes created answers to the Judge and returns each answers relevancy.
7. Finally, to get a quick summary of the last judge run use `uv run python -m evaluation.agent_evaluation_simple --metrics-only` ->

```bash
run_date=2026-08-17T13:17:58-06:00
eve_model=gpt-5.4-mini
judge_model=gpt-5.4-mini
relevance
RELEVANT           0.7
PARTLY_RELEVANT    0.3
Name: proportion, dtype: float64
```

### 2. Vercel Eve evals

Since we are using Vercels Eve package, we have access to a more complete evals platform, see [https://eve.dev/docs/evals/overview](https://eve.dev/docs/evals/overview)

- I've created a few basic evals in `bernalillo-water-rag-agent/evals/`:
  - `smoke`: one cheap in-scope question (where tap water comes from). Checks `knowledge__search` and a citation.
  - `narrative`: CCR story questions from `evals/data/narrative.json` (source water, treatment, sampling). Expects search, not compliance lookup.
  - `compliance`: measured-level questions from `evals/data/compliance.json`. Expects `knowledge__lookup_compliance` and the right ppb values.
  - `definition`: contaminant name / units / source from `evals/data/definition.json`. Expects `knowledge__lookup_contaminant_info`.
  - `refusal`: out-of-scope questions (a specific house, another city). Should refuse and not call tools.
  - `year-clarify`: yearless arsenic question. First turn should ask which year; second turn (sample year 2025) should look up compliance and say 0 ppb.

- To run the evals (FastAPI on `:8000` and Eve on `:3000` must be up so the knowledge tools and judge target work):

```bash
cd bernalillo-water-rag-agent
pnpm exec eve eval              # all evals
pnpm exec eve eval smoke        # one suite
pnpm exec eve eval --list       # print ids without running
```

If Eve logs `[world-local] Queue delivery failed ... TypeError: fetch failed`, stop Eve and delete `bernalillo-water-rag-agent/.eve/.workflow-data`. **Warning** - **This will remove your local sessions. Don't do this if you still need those.** That is Eve's local durable-run store. Crashed sessions stay `running` and get re-queued on every boot. Eve recreates the folder.


## Interface

Residents use the Eve Next.js chat at [http://localhost:3000](http://localhost:3000) (the Compose `eve` service, or host `pnpm dev`). Type a water-quality question; the agent calls the FastAPI tools and answers in the thread. Tool calls show up in the message stream. `pnpm dev:eve` is the same agent in Eve's terminal UI.

The machine interface is FastAPI at [http://localhost:8000](http://localhost:8000) (`/search`, `/lookup_compliance`, `/lookup_contaminant_info`, `/health`, OpenAPI at `/openapi.json`).

### Why Eve

This project focuses on retrieval, ingest, and eval. Eve already has a Next.js web chat, a terminal UI, streaming, session state, and tool-call rendering. While building a web chat from scratch is a worthy goal, I wanted to focus my time on the core RAG internals. 

Eve adds another layer of learning as well. Integrating with Eve, building Next.js as the frontend for Eve, my custom tools, building custom Eve evals, and using a third-party monitoring service are skills in themselves. This shows how I not only understand RAG and how to build it, but also how to integrate with popular frameworks and tools.

## Ingestion pipeline

Postgres tables (`uv run python db/init/db_init.py`) and the MiniLM files under `models/` must exist first. Run these from the repo root.

### 1. Download raw CCR PDFs

PDFs are not in git. Pull the 2020-2025 ABCWUA mailers from the URLs in `data/raw/abcwua/SOURCE.txt`:

```bash
uv run python scripts/download_raw_ccr.py
```

That writes `data/raw/abcwua/ABCWUA-CCR-2020.pdf` … `2025.pdf`. Re-run with `--force` to replace files that already exist.

### 2. Load the hand-compiled compliance CSV

The mailer PDFs put **COMPLIANCE MONITORING RESULTS** in multi-column tables that do not extract cleanly. Those rows were typed and spot-checked by hand into `data/processed/abcwua/CCR_Compliance_Results.csv` (committed; see `data/processed/abcwua/SOURCE.txt`). The script does not scrape the PDFs.

Load the CSV into `compliance_results` (used by `lookup_compliance` and `lookup_contaminant_info`):

```bash
uv run python -m ingestion.ingest_contaminant_data
```

If the rows are already present, the insert is skipped.

### 3. Chunk and embed the PDFs

```bash
uv run python -m ingestion.ingest_pdfs
```

Reads `data/raw/abcwua/SOURCE.txt`, strips table boxes from each page, splits the remaining narrative, embeds with MiniLM, and writes `knowledge_base_chunks` (used by `/search`). Each report year is deleted and re-inserted. A short compliance stub is added so search can point at the compliance tool instead of the raw table text.

## Monitoring

I choose to use []() for monitoring as Eve allows for easy integration of OpenTelemetry data (traces, agent runs, etc.). In the future I hope to add a simple local example where I add Grafana as another example source for the Eve OpenTelemetry data.

## Containerization

`docker-compose.example.yml` runs the full stack: pgvector Postgres, the FastAPI image from `Dockerfile` on port 8000, and the Eve + Next.js image from `bernalillo-water-rag-agent/Dockerfile` on port 3000. The API container mounts `models/` read-only and talks to Postgres on the compose network. Eve calls FastAPI at `http://api.localhost:8000` on that same network.

Copy the example file to `docker-compose.yml` if you want a local override, then `docker compose up -d --build`. Open the chat at [http://localhost:3000](http://localhost:3000). Do not also run host `pnpm dev` while the Compose `eve` service is bound to port 3000.

