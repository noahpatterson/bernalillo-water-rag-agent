import { runCase, isCase } from "./helpers";

import { defineEval, type EveEvalContext } from "eve/evals";
import { loadJson } from "eve/evals/loaders";


const loaded = await loadJson("evals/data/compliance.json");
if (!Array.isArray(loaded) || !loaded.every(isCase)) {
  throw new Error(
    "evals/data/compliance.json must be an array of cases",
  );
}

export default loaded.map((row) =>
  defineEval({
    description: row.id,
    tags: ["compliance"],
    timeoutMs: 120_000,
    metadata: { id: row.id },
    async test(t) {
      await runCase(t, row);
    },
  }),
);
