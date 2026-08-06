# Confirm OpenAI runtime model IDs

Type: grilling
Status: resolved
Claimed by: wayfinder session

## Question

For the Streamlit app’s OpenAI API calls, which exact `model` string IDs will we use in development vs stronger runs—mapping the human’s intent (“5.4-mini” free-with-data-sharing for dev; “gpt-5.6-luna” when cost allows) onto real OpenAI API model names, and how do we document this for reproducibility without confusing Cursor chat models with app runtime models?

## Answer

**App runtime models (not Cursor chat models):**

| Role | Env var | API `model` string | Default `reasoning.effort` |
|------|---------|--------------------|----------------------------|
| Dev (default) | `OPENAI_MODEL_DEV` | `gpt-5.4-mini` | `none` |
| Strong | `OPENAI_MODEL_STRONG` | `gpt-5.6-luna` | `medium` |

- **Client:** OpenAI Python SDK only (no Pydantic-tools lock for this decision).
- **Default tier:** Streamlit uses DEV unless an explicit UI toggle or `OPENAI_MODEL_TIER=strong`.
- **Docs:** Floating aliases in `.env.example` plus a README section **“App runtime models (not Cursor)”**. Pin dated snapshots later only if an eval run needs lock-in.
- **Caveat:** OpenAI positions Luna as the cheap/efficient 5.6 tier (vs Terra/Sol). This project still uses Luna as the “stronger runs” ID by choice.

## Comments

- Draft notes before grilling: pydantic tool (later dropped); mini for dev; luna low/medium for production.
