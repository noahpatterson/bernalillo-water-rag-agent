# Plan retrieval evaluation approaches

Type: grilling
Status: resolved
Blocked by: 03

## Question

Which retrieval approaches will we implement and compare for the rubric (at least two; include hybrid text+vector, and plan where rerank and query rewriting enter), and what metrics / harness decide the winner—on the CCR knowledge base?

## Answer

**Adapted** from [archive/future-scope/issues/05-retrieval-eval-plan.md](../archive/future-scope/issues/05-retrieval-eval-plan.md) for CCR-only.

**Scope:** Retrieval metrics on **KB-grounded** CCR questions (narrative/chunks). Compliance-table tool goldens stay out of hit_rate/MRR—covered by routing / LLM eval. Target **≥10** labeled CCR retrieval fixtures once chunk IDs exist.

**Core approaches:**
1. vector-only (pgvector)
2. text-only (Postgres FTS / tsvector)
3. hybrid — pgvector + FTS fused with **RRF**

**Add-on stacks (hybrid-based):**
4. hybrid + **rerank** (retrieve top **20**, keep top **5**)
5. **query rewrite** → hybrid
6. query rewrite → hybrid + rerank

**Winner / production:** Full table every eval; production = best **hit_rate@5** among {core winner} ∪ {hybrid add-ons}; **MRR** breaks ties.

**Harness:** Local Python eval script → `docs/eval/retrieval.md`. Not Airflow for v1.

**Still open:** Concrete rerank/rewrite libraries ([09](09-rerank-rewrite-libraries.md)); chunking/embeddings ([08](08-chunk-embed-ccr.md)).
