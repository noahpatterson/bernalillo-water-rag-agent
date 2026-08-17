import { defineEvalConfig } from "eve/evals";
import { openai } from "@ai-sdk/openai";

const default_model = `openai/${process.env.OPENAI_MODEL_DEV ?? "gpt-5.4-mini"}`;
export default defineEvalConfig({
  judge: { model: openai(process.env.OPENAI_MODEL_DEV ?? "gpt-5.4-mini") },
});