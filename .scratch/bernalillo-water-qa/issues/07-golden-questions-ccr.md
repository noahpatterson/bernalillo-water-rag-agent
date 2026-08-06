# Define CCR golden questions for must-work queries

Type: grilling
Status: resolved
Blocked by: 03
Claimed by: wayfinder session

## Question

What fixed golden questions (and expected answer shapes / citation requirements) cover must-work CCR demos—(a) a multi-year compliance trend from COMPLIANCE MONITORING RESULTS (e.g. arsenic 2020–2025), (b) a single-year contaminant lookup via the table tool, (c) a narrative/MCL-context question answered from KB chunks—plus optional paraphrase variants for retrieval fixtures?

Do **not** include WQP, ASR, GPCD, or aquifer goldens (future scope).

## Answer

**Set size:** 4 must-work only for now. Paraphrases / extra KB labels (≥10 retrieval fixtures) wait until chunk IDs exist after [Decide CCR chunking and embeddings](08-chunk-embed-ccr.md). Exact µg/L filled after [Decide COMPLIANCE MONITORING RESULTS extract and table schema](10-compliance-table-schema.md).

**Pass bar:** Shape + correct citation kind (tool vs KB). Numeric check when table fixture exists (±0 for exact lookups; year-by-year list for trends). Wrong-lane fails (e.g. inventing compliance µg/L from KB alone when the table tool should hit).

### Must-work

| ID | Question | Path | Expected shape / truth | Citation |
|----|----------|------|------------------------|----------|
| **GQ-T1** | According to ABCWUA Consumer Confidence Reports, how did finished-water **arsenic** compliance results change from **2020 through 2025**? | Table tool | Year-by-year arsenic + units + MCL context; exact values after extract | Tool |
| **GQ-T2** | What was the ABCWUA CCR **nitrate** compliance result for report year **2024**? | Table tool | Value + units + MCL; year 2024 | Tool |
| **GQ-K1** | According to the ABCWUA water quality report, is there arsenic in Albuquerque drinking water, and what does the report say about meeting EPA standards? | KB | Narrative aligned to CCR FAQ prose; do not invent µg/L from prose alone | KB |
| **GQ-K2** | Where does ABCWUA drinking water come from, and how is surface water made safe to drink, according to the Consumer Confidence Report? | KB | Groundwater + San Juan-Chama surface water; treatment narrative | KB |
