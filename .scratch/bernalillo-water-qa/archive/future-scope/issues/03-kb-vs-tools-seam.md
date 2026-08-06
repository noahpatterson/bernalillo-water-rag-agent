# Decide knowledge base vs tools seam

Type: grilling
Status: resolved
Blocked by: 01
Claimed by: wayfinder session

## Question

Given the source inventory, which concrete artifacts become knowledge-base documents/chunks vs tool-backed structured queries for the three priority themes—and what citation shape does each path produce in answers?

## Answer

**Priority themes (revised):** (1) water-quality trends, (2) ASR monitoring-well readings via NM Water Data (not Bear Canyon), (3) per-capita GPCD.

**Seam**

| Path | Knowledge base | Tools |
|------|----------------|-------|
| Quality | Extracted ABCWUA CCR text/tables 2020–2025 in Postgres (no PDF binaries in git); Airflow re-fetches from ABCWUA URLs | WQP ambient (`countycode=US:35:001`); optional NMED for PWS `NM3510701`; curated CCR contaminant×year table for exact lookups. Never answer tap-water trends from WQP alone. |
| ASR readings | Short ASR methodology/context docs only if useful for narrative | Ingest [Water Authority ASR Monitoring Wells](https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells) into Postgres; tools for latest-by-site and range queries; citations must name site/project and disambiguate DWTP Large-Scale ASR vs other wells. |
| Per-capita | Conservation / Water 2120 / denominator methodology | Curated GPCD-by-calendar-year table (e.g. ~125 GPCD CY2024 from AIS). Census ACS only as optional separate population tool—never invent official GPCD from Census÷production. |

**Citations**

- KB hit: `title | publisher | doc date or year | source URL | chunk/section id`
- Tool hit: `metric | value + units | as-of date or year | publisher | query or table key | source URL`
- Refuse or hedge if neither path produced a citeable hit.

**Out of scope (this effort):** Bear Canyon arroyo daily discharge PDFs, Bear Canyon as a must-work demo question, USGS 08329868 as ASR accounting.
