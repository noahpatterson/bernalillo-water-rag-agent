import { type EveEvalContext } from "eve/evals";

/** Whole-token match for numbers so "0" does not hit "2025". */
type Case = {
  id: string;
  prompt: string;
  expectTools: string[];
  forbidTools?: string[];
  requireCitation?: boolean;
  mustInclude?: string[];
  expected?: string;
  criteria?: string;
};

export function isCase(value: unknown): value is Case {
  if (!value || typeof value !== "object") {
    return false;
  }
  const row = value as Record<string, unknown>;
  return (
    typeof row.id === "string" &&
    typeof row.prompt === "string" &&
    Array.isArray(row.expectTools) &&
    row.expectTools.every((tool) => typeof tool === "string")
  );
}

function tokenMatcher(token: string): RegExp {
  const escaped = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  if (/^\d+(\.\d+)?$/.test(token)) {
    return new RegExp(`\\b${escaped}\\b`);
  }
  return new RegExp(escaped, "i");
}

export async function runCase(t: EveEvalContext, row: Case): Promise<void> {
  await t.send(row.prompt);
  t.succeeded();
  t.noFailedActions();
  for (const tool of row.expectTools) {
    t.calledTool(tool);
  }
  for (const tool of row.forbidTools ?? []) {
    t.notCalledTool(tool);
  }
  for (const token of row.mustInclude ?? []) {
    t.messageIncludes(tokenMatcher(token)).label(`mustInclude:${token}`);
  }
  if (row.expected) {
    t.judge.autoevals.factuality(row.expected).label("factuality").atLeast(0.7);
  }
  if (row.criteria) {
    t.judge.autoevals.closedQA(row.criteria).label("criteria").atLeast(0.8);
  }
  if (row.requireCitation) {
    t.judge.autoevals
      .closedQA("Includes a source url as a citation. Can be plain text or markdown link.")
      .label("citation")
      .atLeast(0.8);
  }
}