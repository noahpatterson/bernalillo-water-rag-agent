# bernalillo-water-rag

LLM Zoomcamp project: ABCWUA Consumer Confidence Report water-quality Q&A (RAG + compliance-table tool).

## Project prep

### 1. Python env

```bash
uv sync
cp .env.example .env
# fill OPENAI_API_KEY, POSTGRES_* , etc.
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

## Documentation

Wayfinding map: `.scratch/bernalillo-water-qa/map.md`

Prior multi-theme exploration (ASR, WQP, GPCD, etc.) is archived under `.scratch/bernalillo-water-qa/archive/future-scope/`.
