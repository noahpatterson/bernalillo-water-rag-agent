# Plan LLM output evaluation approaches

Type: grilling
Status: resolved
Blocked by: 03, 04
Claimed by: wayfinder session

## Question

Which LLM/prompt (or flow) variants will we compare for final answers—including citation faithfulness—and how will we score them so the rubric’s “multiple approaches, best one used” is clearly evidenced?

## Answer

**Axis:** Compare **generation flows** (not prompt wording alone, not model swaps). Hold retrieval/tools fixed to the winner from [Plan retrieval evaluation approaches](05-retrieval-eval-plan.md). Fixtures = golden questions from [Define golden questions for must-work queries](04-golden-questions.md).

**Approaches (two)**

1. **Single-shot** — same retrieved/tool context → one answer prompt.
2. **Cite-or-refuse** — same inputs; every citation must bind to a harness-logged chunk or tool-row ID, or the flow refuses/hedges.

**Citation faithfulness:** A citation counts only if its ID resolves to the payload the harness actually logged for that run (no hallucinated URLs/keys). Matches dual citation shapes from [Decide knowledge base vs tools seam](03-kb-vs-tools-seam.md).

**Scorecard (per golden × flow)**

- **Auto:** required fields present (year/site/value/units as applicable); citation IDs resolve; correct refuse when neither path produced a hit.
- **Human (only if auto passes):** narrative vs expected answer shape — correct / partial / wrong. No LLM-as-judge for the graded demo set.

**Winner (lexicographic)**

1. Citation-resolution failures disqualify.
2. Else higher auto-pass rate across goldens.
3. Else better human narrative scores.

**Ship:** Cite-or-refuse in the Streamlit app; single-shot remains in the eval harness only.

**Evidence for rubric:** Committed results snapshot (markdown/CSV: golden id × flow × auto × human) **and** a notebook/script that reproduces the table.
