import { openai } from "@ai-sdk/openai";
import { defineAgent } from "eve";

export default defineAgent({
  model: openai(process.env.OPENAI_MODEL_DEV ?? "gpt-5.4-mini"),
  reasoning: "none",
});
