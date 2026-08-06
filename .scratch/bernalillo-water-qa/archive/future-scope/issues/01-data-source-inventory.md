# Catalog public data sources for priority themes

Type: research
Status: resolved

## Question

What public datasets and/or APIs can supply Bernalillo County–relevant data for the priority themes—(1) water quality trends ~2020–2025, (2) Bear Canyon recharge project readings, (3) water use suitable for per-capita figures ~2024—plus a short note on what exists for aquifer depth / quantity for later?

For each viable source, record: owner (ABCWUA / USGS / NMED / other), theme(s), access method (API, bulk download, PDFs), geographic coverage relative to the county footprint, time coverage, license/ToS constraints for a public student project, and whether it looks better as knowledge-base documents vs tool-backed structured queries.

## Answer

**Decision-quality summary:** Use **ABCWUA CCR PDFs (2020–2025)** + **NMED Drinking Water Watch/Viewer (PWS NM3510701)** for tap-water quality trends (KB + compliance tools); **EPA/USGS WQP** (`countycode=US:35:001`) for ambient structured trends. For Bear Canyon, rely on **ABCWUA diversion/recharge PDFs** (daily series mostly through early 2015) plus **AIS recoverable-storage snapshots** and **RAPP** methodology—not USGS gage 08329868. For ~2024 per-capita, use **ABCWUA GPCD** (AIS 2025: **~125 GPCD CY2024**, service pop ~657k); Census ACS only as a separate denominator. Aquifer later: **USGS Albuquerque Basin groundwater network** via modern Water Data APIs. ABCWUA site ToS limits reuse to personal/informational use—prefer cite/link over republishing PDFs.

Full catalog with citations: [`research/data-source-inventory.md`](../../../research/data-source-inventory.md)
