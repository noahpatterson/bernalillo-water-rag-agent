# Seed Large-Scale ASR CSV for first ingest

Type: task
Status: resolved

## Question

Cloudflare blocks unattended downloads from catalog.newmexicowaterdata.org. Manually download the DWTP Large-Scale ASR files and place them in the repo so Airflow/local ingest can proceed without a live catalog fetch.

**Do this:**

1. Open https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells
2. Download at least:
   - `largescaletransducer.csv` (resource `5bc7cc13-934c-4bda-8664-2a13ada21d44`)
   - optionally `largescalemanual.csv` (resource `bace582d-b5c1-420a-9f3c-408882bb954d`)
3. Save under `data/raw/nm-water-data-asr/` (create dirs as needed)
4. Add a one-line `data/raw/nm-water-data-asr/SOURCE.txt` with the download URL(s) and the date you fetched

Do **not** download Bear Canyon resources for the graded path. See [research/asr-nm-water-data-access.md](../../../research/asr-nm-water-data-access.md).

Resolved when the transducer CSV is in-tree and SOURCE.txt exists.

## Answer

Seeded 2026-08-06 by operator (browser download; Cloudflare bypass).

Local files under `data/raw/nm-water-data-asr/`:

- `largescaletransducer.csv` (~160k rows; depths `s`≈80k / `d`≈80k; Date range ~2014-12-29 → 2022-09-12; BOM on `_id` column)
- `largescalemanual.csv`
- `SOURCE.txt` — catalog download URLs + fetch date

Provenance: [SOURCE.txt](../../../data/raw/nm-water-data-asr/SOURCE.txt)
