import { defineEval } from "eve/evals";
import { satisfies } from "eve/evals/expect";

const ARSENIC_AVERAGE =
  /\b2\.5\b|\b0(\.0+)?\s*(ppb|µg\/l|ug\/l|μg\/l)\b/i;
const ARSENIC_ZERO_2025 =
  /not detected|below.{0,40}detection|non-?detect|\b0(\.0+)?\s*(ppb|µg\/l|ug\/l|μg\/l)\b/i;

function is2025ArsenicLookup(input: unknown): boolean {
  if (!input || typeof input !== "object") {
    return false;
  }
  const value = input as Record<string, unknown>;
  const year = value.sample_year ?? value.sampleYear;
  const contaminant = String(value.contaminant ?? "");
  return Number(year) === 2025 && /arsenic/i.test(contaminant);
}

export default defineEval({
  description:
    "A yearless arsenic question should ask which year, then answer 0 ppb for sample year 2025.",
  tags: ["multi-turn"],
  timeoutMs: 180_000,
  metadata: {
    sampleYear: 2025,
    expectedAveragePpb: 0,
    mclPpb: 10,
  },
  async test(t) {
    const first = await t.send(
      "What was the average arsenic level in Albuquerque drinking water?",
    );
    first.expectOk();
    first.notCalledTool("knowledge__lookup_compliance");
    first.messageIncludes(/year/i);
    t.check(
      first.message,
      satisfies(
        (value) => !ARSENIC_AVERAGE.test(String(value ?? "")),
        "first turn does not report an arsenic average",
      ),
    );
    t.judge.autoevals
      .closedQA(
        "Asks which year (sample year or report year) to use. Does not report a specific arsenic average, MCL, or ppb value yet.",
        { on: first.message },
      )
      .label("asks-year")
      .gate(0.8);

    const second = await t.send("Sample year 2025.");
    second.expectOk();
    t.succeeded();
    t.noFailedActions();
    second.calledTool("knowledge__lookup_compliance", {
      input: is2025ArsenicLookup,
    });
    t.check(
      second.message,
      satisfies(
        (value) => ARSENIC_ZERO_2025.test(String(value ?? "")),
        "2025 arsenic average is 0 ppb or not detected",
      ),
    );
    t.judge.autoevals
      .factuality(
        "The 2025 system-wide average arsenic was 0 ppb (not detected), with an MCL of 10 ppb.",
        { on: second.message },
      )
      .label("arsenic-2025")
      .atLeast(0.7);
    t.judge.autoevals
      .closedQA("Includes a source_url from the compliance lookup.", {
        on: second.message,
      })
      .label("citation")
      .atLeast(0.8);
  },
});
