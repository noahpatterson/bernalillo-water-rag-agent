# Plan retrieval evaluation approaches

Type: grilling
Status: resolved
Blocked by: 03
Claimed by: wayfinder session

## Question

Which retrieval approaches will we implement and compare for the rubric (at least two; include hybrid text+vector, and plan where rerank and query rewriting enter the comparison), and what metrics / harness will decide the winner?

## Answer

**Scope:** Retrieval metrics only on **KB-grounded** questions (CCR / methodology chunks). Tool-path goldens (GQ-Q2 WQP, GQ-A1/A2 ASR, GQ-P1 GPCD number) stay out of hit_rate/MRR—covered by routing / LLM eval. Must-work set alone is too tool-heavy for a retrieval bake-off; expand with additional KB questions / paraphrases (target **≥10** labeled items) once chunk IDs exist. GQ-Q1 is the primary must-work KB anchor; GQ-P1 methodology text may contribute optional KB labels.

**Core approaches (multiple-approaches rubric):**
1. **vector-only** (pgvector)
2. **text-only** (Postgres FTS / tsvector)
3. **hybrid** — pgvector + FTS fused with **RRF**

**Add-on stacks (always evaluated for best-practice evidence; hybrid-based):**
4. hybrid + **rerank** (retrieve top **20**, keep top **5**)
5. **query rewrite** → hybrid
6. query rewrite → hybrid + rerank

**Winner / production:** Run the full table every eval. Production stack = best **hit_rate@5** among {core winner} ∪ {hybrid add-on stacks}; **MRR** breaks ties. Core bake-off documents “multiple approaches, best used”; add-ons always measured so hybrid / rerank / rewrite best-practice points are evidenced even if a core non-hybrid somehow leads.

**Metrics:** hit_rate@5 (primary), MRR (tiebreak). Ground truth = manually labeled **relevant chunk IDs** per KB fixture question.

**Harness:** Local Python eval script (human implements retrieval; agent may scaffold) writing a comparison table to `docs/eval/retrieval.md` for README / peer review. Not Airflow for v1.

**Deferred (fog → follow-on tickets):** Rerank and rewrite **library** choices; CCR chunking/embedding (needed before chunk-ID labels).
