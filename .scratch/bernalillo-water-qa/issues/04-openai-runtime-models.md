# Confirm OpenAI runtime model IDs

Type: grilling
Status: resolved

## Question

Which exact OpenAI API `model` strings does the Streamlit app use for development vs stronger runs, and how are they documented without confusing Cursor chat models?

## Answer

**Carried forward** from [archive/future-scope/issues/07-openai-runtime-models.md](../archive/future-scope/issues/07-openai-runtime-models.md).

| Role | Env var | API `model` string | Default `reasoning.effort` |
|------|---------|--------------------|----------------------------|
| Dev (default) | `OPENAI_MODEL_DEV` | `gpt-5.4-mini` | `none` |
| Strong | `OPENAI_MODEL_STRONG` | `gpt-5.6-luna` | `medium` |

- **Client:** OpenAI Python SDK.
- **Default tier:** DEV unless UI toggle or `OPENAI_MODEL_TIER=strong`.
- **Docs:** Floating aliases in `.env.example` + README **“App runtime models (not Cursor)”**.
