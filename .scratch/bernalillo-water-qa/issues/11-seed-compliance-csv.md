# Seed CCR compliance-results CSV

Type: task
Status: resolved
Blocked by: 10
Claimed by: wayfinder session

## Question

Curate the structured COMPLIANCE MONITORING RESULTS table from ABCWUA CCR PDFs so the compliance tool and GQ-T1/T2 fixtures have real numbers.

**Do this:**

1. Create `data/processed/` if needed.
2. Build `data/processed/ccr-compliance-results.csv` with the canonical columns from [Decide COMPLIANCE MONITORING RESULTS extract and table schema](10-compliance-table-schema.md).
3. Include **all** substance rows from each year’s **COMPLIANCE MONITORING RESULTS** section for report years **2020–2025** (PDFs in `data/raw/abcwua/`).
4. Set `source_url` from `data/raw/abcwua/SOURCE.txt` per year; `pws_id` = `NM35-10701` (normalize punctuation consistently).
5. Add `data/processed/SOURCE.txt` noting PDF paths, curation date, and that values were hand-verified from the mailers.
6. Spot-check **arsenic** (all years) and **nitrate 2024** against the PDFs — these gate GQ-T1/T2.

Resolved when the CSV + SOURCE.txt exist and arsenic/nitrate spot-checks match the reports.

## Answer

Seeded 2026-08-06 by operator (hand-processed from CCR PDFs).

- **CSV:** [`data/raw/processed/CCR_Compliance_Results.csv`](../../../data/raw/processed/CCR_Compliance_Results.csv) (~222 data rows; years 2020–2025; includes arsenic + nitrate among full compliance-section contaminants)
- **SOURCE:** [`data/raw/processed/SOURCE.txt`](../../../data/raw/processed/SOURCE.txt)

**Path note:** Lived under `data/raw/processed/` (not `data/processed/…` as first sketched). Schema columns are a superset of the ticket-10 list (e.g. `sample_year_range`, LRAA / lead action-level fields).
