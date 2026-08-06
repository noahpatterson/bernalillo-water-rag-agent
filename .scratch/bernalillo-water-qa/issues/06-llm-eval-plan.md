# Plan LLM output evaluation approaches

Type: grilling
Status: resolved
Blocked by: 03

## Question

Which generation flows will we compare for final answers—including citation faithfulness—and how will we score them on CCR-only goldens?

## Answer

**Adapted** from [archive/future-scope/issues/06-llm-eval-plan.md](../archive/future-scope/issues/06-llm-eval-plan.md).

**Axis:** Compare **generation flows** (not model swaps). Hold retrieval/tools fixed to the retrieval winner. Fixtures = CCR goldens from [Define CCR golden questions](07-golden-questions-ccr.md).

**Approaches (two)**

1. **Single-shot** — same context → one answer prompt.
2. **Cite-or-refuse** — citations must bind to harness-logged chunk or tool-row IDs, or refuse/hedge.

**Scorecard:** Auto (required fields + citation ID resolve + correct refuse) then human narrative (correct / partial / wrong). No LLM-as-judge for the graded set.

**Winner (lexicographic):** citation failures disqualify → higher auto-pass → better human scores.

**Ship:** Cite-or-refuse in Streamlit; single-shot remains harness-only. Commit results snapshot + reproducible script.
