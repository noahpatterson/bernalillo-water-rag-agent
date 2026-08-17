import { defineEval } from "eve/evals";

export default defineEval({
  description:
    "Cheap in-scope 2025 source-water check against the live Eve agent.",
  tags: ["smoke", "fast"],
  timeoutMs: 120_000,
  async test(t) {
    await t.send(
      "Where does Albuquerque tap water come from? Use the 2025 water quality report.",
    );
    t.succeeded();
    t.noFailedActions();
    t.calledTool("knowledge__search");
    t.notCalledTool("knowledge__lookup_compliance");
    t.messageIncludes(/ground\s*water/i);
    t.messageIncludes(/surface\s*water/i);
    t.judge.autoevals
      .closedQA(
        "Names both groundwater and San Juan-Chama or surface water, and includes a source_url from the tool results. Does not invent measured contaminant levels.",
      )
      .label("source-water")
      .atLeast(0.8);
  },
});
