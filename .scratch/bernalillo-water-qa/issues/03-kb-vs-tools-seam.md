# Decide CCR knowledge base vs compliance-table tool seam

Type: grilling
Status: resolved
Blocked by: 01
Claimed by: wayfinder session

## Question

For the CCR-only corpus, which artifacts are knowledge-base documents/chunks vs tool-backed structured queries—and what citation shape does each path produce?

## Answer

**Priority theme (sole):** ABCWUA finished-water quality as reported in Consumer Confidence Reports.

**Seam**

| Path | Knowledge base | Tools |
|------|----------------|-------|
| Quality | Extracted CCR narrative and surrounding report text (2020–2025) in Postgres/pgvector (no need to commit PDF binaries long-term; raw seeds live under `data/raw/abcwua/` for now) | **One** structured tool over extracted **COMPLIANCE MONITORING RESULTS** rows (contaminant × report year, with MCL/units/result fields as available). No WQP, NMED, ASR, or GPCD tools on this path. |

**Citations**

- KB hit: `title | publisher | report year | source URL | chunk/section id`
- Tool hit: `contaminant | value + units | report year | publisher | table/row key | source URL`
- Refuse or hedge if neither path produced a citeable hit.

**Supersedes** the multi-theme seam in [archive/future-scope/issues/03-kb-vs-tools-seam.md](../archive/future-scope/issues/03-kb-vs-tools-seam.md).
