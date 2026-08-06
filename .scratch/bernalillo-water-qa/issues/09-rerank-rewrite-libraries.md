# Choose rerank and query-rewrite libraries

Type: grilling
Status: resolved
Blocked by: 05
Claimed by: wayfinder session

## Question

Which concrete libraries (or APIs) will implement document re-ranking and user query rewriting for the hybrid add-on stacks in [Plan retrieval evaluation approaches](05-retrieval-eval-plan.md)—and what constraints (local vs OpenAI-only, cost, learning-mode fit) decide them?

## Answer

**Rerank:** Local **`flashrank`** with **`ms-marco-MiniLM-L-12-v2`** (`Ranker(model_name="ms-marco-MiniLM-L-12-v2")`). No third-party rerank API. Fits hybrid add-on: retrieve top **20**, keep top **5**.

**Query rewrite:** OpenAI Python SDK one-shot rewrite prompt into a retrieval-oriented query string. Uses the **active app tier** (`OPENAI_MODEL_DEV` or `OPENAI_MODEL_STRONG` + that tier’s `reasoning.effort`). No HyDE for v1.

**Constraints that decided this:** Prefer free/local for ranking (learning-mode + no second vendor); reuse existing OpenAI key for rewrite; keep eval stacks easy to ablate.
