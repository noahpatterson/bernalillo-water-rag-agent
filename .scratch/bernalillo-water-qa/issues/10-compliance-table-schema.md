# Decide COMPLIANCE MONITORING RESULTS extract and table schema

Type: grilling
Status: resolved
Blocked by: 03
Claimed by: wayfinder session

## Question

How will we extract the **COMPLIANCE MONITORING RESULTS** sections from ABCWUA CCR PDFs 2020–2025 into a structured table the tool can query—PDF/table extraction approach, canonical columns (contaminant, result, units, MCL, MCLG, range, report year, PWS id, source URL, …), and how year-to-year layout drift is handled so Airflow can reload deterministically?

## Answer

**Extract approach (v1):** **Curated CSV seed** — human verifies values from each CCR PDF (layout is multi-column; plain `pdftotext` scrambles rows). Airflow/local ingest loads the CSV into Postgres. Optional auto `pymupdf` table extract is future polish, not the graded path.

**Artifact:** [`data/raw/processed/CCR_Compliance_Results.csv`](../../../data/raw/processed/CCR_Compliance_Results.csv) plus [`data/raw/processed/SOURCE.txt`](../../../data/raw/processed/SOURCE.txt) (operator path; supersedes earlier `data/processed/ccr-compliance-results.csv` sketch).

**Coverage:** **Full** COMPLIANCE MONITORING RESULTS section for each report year 2020–2025 — every substance row printed there (including arsenic, nitrate, HAA5/TTHM, etc.). Not voluntary “special distribution” side tables unless they appear inside that compliance section. Lead-survey narrative stays KB-only.

**Canonical columns** (nullable when a year omits a field):

| Column | Meaning |
|--------|---------|
| `report_year` | CCR mailer year (2020–2025) |
| `pws_id` | e.g. `NM35-10701` |
| `contaminant_code` | Short code when present (`As`, `NO3-`, …) |
| `contaminant_name` | Canonical name (`Arsenic`, `Nitrate`, …) |
| `sample_year` | Sample year(s) as reported (string OK if range) |
| `units` | PPB, PPM, pCi/L, NTU, … |
| `detection_limit` | As printed |
| `min_detected` | |
| `avg_system` | System-wide average |
| `avg_sjcp` | San Juan-Chama plant average when present |
| `max_detected` | |
| `mcl` | |
| `mclg` | |
| `source_url` | ABCWUA PDF URL from `data/raw/abcwua/SOURCE.txt` |
| `notes` | Free text (footnotes, LRAA, etc.) |

**Tool:** Query by contaminant (code or name) + `report_year` (and ranges for GQ-T1). Citations use tool shape from [Decide CCR knowledge base vs compliance-table tool seam](03-kb-vs-tools-seam.md).
