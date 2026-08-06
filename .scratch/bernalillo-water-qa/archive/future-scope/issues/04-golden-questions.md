# Define golden questions for must-work queries

Type: grilling
Status: resolved
Blocked by: 01
Claimed by: wayfinder session

## Question

What fixed golden questions (and expected answer shapes / citation requirements) cover must-work types (a) water-quality change over a time range, (b) latest or ranged ASR monitoring-well reading from the NM Water Data Water Authority ASR wells dataset, (d) per-capita use (GPCD) for a year—plus 1–2 exploratory aquifer questions marked best-effort?

Note: Bear Canyon arroyo recharge is out of scope; do not include Bear Canyon golden questions.

## Answer

**Set size:** 5 must-work + 1 best-effort aquifer. Hard numbers where known (GPCD); shapes elsewhere until ingest fixtures. CCR + WQP as separate quality goldens. ASR = latest + CY2022 range on **MW-01S**. Aquifer logged but does not fail the demo gate.

### Must-work

| ID | Question | Expected shape / truth | Citation |
|----|----------|------------------------|----------|
| **GQ-Q1** | According to ABCWUA Consumer Confidence Reports, how did finished-water arsenic results change from 2020 through 2025? | Year-by-year (or first/last) arsenic + units; MCL context; never from WQP alone. Exact µg/L after CCR table ingest. | KB and/or CCR contaminant-table tool (`title \| publisher \| year \| URL \| section` and/or tool cite) |
| **GQ-Q2** | Using Water Quality Portal data for Bernalillo County (`US:35:001`), what was the range of dissolved nitrate (as N) sample results in surface water from 2020 through 2024? | n samples + min–max (or median + range) + units; labeled ambient/environmental, not tap. Stats after WQP tool. | Tool (`metric \| value+units \| as-of \| publisher \| query key \| URL`) |
| **GQ-A1** | What is the most recent `WaterLevel_ft_bgs` for Large-Scale ASR monitoring well **MW-01S** at the San Juan-Chama DWTP (NM Water Data Water Authority ASR wells)? | value + units + timestamp + Large-Scale/DWTP site label (not Bear Canyon). Exact after CSV seed ([09](09-seed-asr-csv.md) / [08](08-asr-nm-water-data-access.md)). | Tool |
| **GQ-A2** | What were the min and max `WaterLevel_ft_bgs` for **MW-01S** in calendar year **2022**? | min, max, units, window, optional n readings; same site disambiguation. Exact after seed. | Tool |
| **GQ-P1** | What was ABCWUA’s gallons per capita per day (GPCD) for calendar year 2024, and what service-population basis does that figure use? | **~125 GPCD**, service pop **≈657,511** (AIS 2025); utility denominator—not Census÷production. | Tool for number; optional KB for methodology |

### Best-effort (does not fail demo)

| ID | Question |
|----|----------|
| **GQ-AQ1** | What is the most recent USGS groundwater level for a monitored well in the Albuquerque Basin within Bernalillo County? |

Shape when tool exists: value + site id + as-of + USGS cite. Missing/wrong does not fail the graded gate; log separately.

### Pass bar (must-work)

Shape + correct citation kind; no wrong-lane mix (e.g. tap answered only from WQP). Numeric check when a fixture exists: GPCD ±0; CCR/WQP/ASR vs post-ingest fixtures. Paraphrase variants, LLM-as-judge thresholds, and retrieval hit@k are **out of this ticket** → [05](05-retrieval-eval-plan.md) / [06](06-llm-eval-plan.md).

### Explicitly excluded

Bear Canyon arroyo recharge golden questions.
