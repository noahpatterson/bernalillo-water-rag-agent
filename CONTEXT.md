# Bernalillo Water Q&A

Domain language for a Zoomcamp RAG/agent app that answers ABCWUA Consumer Confidence Report water-quality questions with citations.

## Language

**Theme**:
A subject area of water questions. On the graded path the sole theme is finished drinking-water quality as reported in ABCWUA Consumer Confidence Reports.
_Avoid_: Topic, category (when meaning a water subject area)

**Priority theme**:
The theme that must work for the graded demo: ABCWUA CCR water-quality / compliance results.
_Avoid_: Nice-to-have theme; ASR, GPCD, WQP, aquifer (those are future scope)

**Consumer Confidence Report (CCR)**:
ABCWUA’s annual water-quality report PDF for customers (also titled Water Quality Report / mailer), including narrative sections and **COMPLIANCE MONITORING RESULTS** tables for the Albuquerque Water System (PWS NM35-10701).
_Avoid_: Ambient environmental sample report; WQP download

**COMPLIANCE MONITORING RESULTS**:
The CCR table(s) of EPA-required compliance sampling results (contaminant, detected level, MCL/MCLG, units, etc.) used for exact structured lookups.
_Avoid_: Voluntary monitoring tables when meaning the graded compliance tool; narrative FAQ answers

**Knowledge base**:
The searchable store of ingested CCR document chunks used for retrieval (Postgres + pgvector in this project).
_Avoid_: Database (when meaning the retrieval corpus), index (alone)

**Tool**:
A callable function the application flow may invoke to fetch exact structured compliance-table rows—not free-text retrieval. On this path there is one primary tool: compliance-results lookup.
_Avoid_: Plugin, function calling (as the product term), API (when meaning the app-side callable)

**Citation**:
A traceable pointer on an answer to the source CCR chunk or compliance-table row and its report year.
_Avoid_: Reference, source (when meaning the in-answer provenance line)

**Retrieval approach**:
One concrete way of fetching knowledge-base context to evaluate (e.g. vector-only, text-only, hybrid, hybrid+rerank).
_Avoid_: Search method (vague)

**Retrieval fixture**:
A KB-grounded golden or eval question paired with manually labeled relevant knowledge-base chunk IDs for scoring retrieval approaches.
_Avoid_: Test case (vague), Q&A pair (when meaning retrieval labels only)

**Generation flow**:
One concrete way of turning fixed retrieval/tool context into a final answer for LLM evaluation (e.g. single-shot vs cite-or-refuse).
_Avoid_: LLM approach (vague), prompt variant (when meaning the whole flow), model swap

**Single-shot**:
A generation flow that answers once from the provided context without requiring citations to bind to harness-logged chunk or tool-row IDs.
_Avoid_: Naive prompt, baseline prompt

**Cite-or-refuse**:
A generation flow that must emit citations bound to harness-logged chunk or tool-row IDs, or refuse/hedge when none apply.
_Avoid_: Grounded answer, forced citation (vague)

**Citation faithfulness**:
Whether each citation on an answer resolves to the retrieval or tool payload actually logged for that run.
_Avoid_: Groundedness (alone), attribution quality

**Golden question**:
A fixed natural-language question with an expected answer shape used for retrieval and LLM evaluation.
_Avoid_: Test query, sample question (when meaning an eval fixture)

**Must-work golden**:
A golden question that must pass the graded demo gate (shape + citation kind; numeric check when a fixture exists).
_Avoid_: Required question (vague)

**Best-effort golden**:
A golden question logged in eval that does not fail the demo gate if missing or wrong.
_Avoid_: Optional question, stretch goal (when meaning an eval fixture)

**Future scope**:
Themes and datasets deliberately deferred (ASR monitoring wells, WQP ambient, NMED tools, GPCD/per-capita, aquifer depth/quantity). Archived under `.scratch/bernalillo-water-qa/archive/future-scope/`.
_Avoid_: Out of scope (use for course-forbidden or never-this-repo items); backlog (vague)
