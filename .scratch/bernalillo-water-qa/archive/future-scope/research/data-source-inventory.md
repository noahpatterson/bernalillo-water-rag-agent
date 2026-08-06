# Public data sources for Bernalillo County water priority themes

Research date: 2026-08-06  
Scope: Bernalillo County, NM — (1) water quality trends ~2020–2025, (2) Bear Canyon recharge readings, (3) water use suitable for per-capita ~2024, plus a short note on aquifer depth/quantity.  
Method: primary sources only (official agency sites, API docs, dataset landing pages). Secondary case studies used only to locate owning sources, then discarded for claims.

---

## Summary recommendations

| Theme | Best primary sources | KB vs tool |
| --- | --- | --- |
| Water quality trends 2020–2025 | ABCWUA Consumer Confidence Reports (CCR) PDFs 2020–2025; NMED Drinking Water Watch / Viewer for PWS `NM3510701`; EPA/USGS Water Quality Portal API for ambient (non-tap) samples | CCR + RAPP → **KB**; WQP / Samples / DWW sample tables → **tools** |
| Bear Canyon recharge | ABCWUA Diversion & Recharge Data (daily PDFs, mostly 2014–2015); ABCWUA Annual Information Statements for current recoverable storage; RAPP for methodology | Methodology PDFs → **KB**; storage totals & any parsed daily discharge → **tools** (sparse recent daily series) |
| Per-capita use ~2024 | ABCWUA AIS / Annual Report / Performance Plan GPCD figures (utility-defined denominator) | Narrative plans → **KB**; GPCD time series table → **tool** or curated table |
| Aquifer depth / quantity (later) | USGS Albuquerque Basin groundwater-level network via NWIS / modern Water Data APIs; USGS data series reports | Network description → **KB**; levels/depths → **tools** |

---

## 1. Water quality trends (~2020–2025)

### 1.1 ABCWUA Consumer Confidence Reports (CCR) — owner: ABCWUA

- **Landing page (downloads 2018–2025 EN/ES):** [Your Drinking Water – Download Report](https://www.abcwua.org/your-drinking-water-download-report-english-spanish/)
- **Overview page:** [Water Quality Report](https://www.abcwua.org/your-drinking-water-water-quality-report/)
- **Example latest PDF:** [2025 Water Quality Report](https://www.abcwua.org/wp-content/uploads/2026/05/ABCWUA-2025WaterQualityMailerWeb.pdf)
- **Themes:** finished drinking-water compliance for the Albuquerque Water System (PWS ID cited in the 2025 CCR as **NM35-10701** / `NM3510701`).
- **Access:** bulk PDF download (no public machine API). Annual reports available at least for **2020–2025** on the download page.
- **Geography:** ABCWUA service area (Albuquerque + much of Bernalillo County), not every private well in the county.
- **Time coverage:** annual CCR snapshots; compliance monitoring windows vary by contaminant (not a continuous daily series).
- **License / ToS:** site [Terms and Conditions](https://www.abcwua.org/terms-and-conditions/) state Content is proprietary and licensed for **information and personal use only**; commercial reuse requires prior written permission. A non-commercial student citation app should attribute heavily and avoid redistributing full PDF binaries if possible (link + quote/extract tables with attribution). Confirm with ABCWUA if bulk republishing of PDF text is planned.
- **KB vs tool:** **KB-first** (ingest PDFs for narrative + yearly tables). Optional tool: scrape/parse yearly contaminant result tables into a structured store for “what was arsenic in 2023?” style queries.

### 1.2 ABCWUA distribution-zone water quality — owner: ABCWUA

- **Page:** [Water Quality by Distribution Zone](https://www.abcwua.org/your-drinking-water-water-quality-by-distribution-zone/)
- **Content:** interactive map of ~20 distribution zones; compliance EPTDS results plus **voluntary** quarterly monitoring tables.
- **Access:** web UI / linked tables (not a documented public API).
- **Geography:** ABCWUA service area zones.
- **Time coverage:** “most recent” compliance event + ongoing voluntary quarterly samples (good for current spatial detail; weaker for a clean 2020–2025 trend API).
- **License:** same ABCWUA site ToS as above.
- **KB vs tool:** zone report pages → **KB**; if stable table URLs exist, selective **tool** extraction later.

### 1.3 NMED Drinking Water Watch / Drinking Water Viewer — owner: NMED Drinking Water Bureau

- **Bureau hub:** [NMED Drinking Water Bureau](https://www.env.nm.gov/drinking_water/)
- **PWS search guidance:** [Public Water System Information](https://www.env.nm.gov/drinking_water/pws-info-2/)
- **Drinking Water Watch:** [https://dww.water.net.env.nm.gov/NMDWW/](https://dww.water.net.env.nm.gov/NMDWW/) (also linked as [dww.water.env.nm.gov](https://dww.water.env.nm.gov/))
- **Drinking Water Viewer (updated UI):** [https://nmdwv.gecsws.com/](https://nmdwv.gecsws.com/)
- **Themes:** regulated public-system sample results, schedules, violations for systems serving Bernalillo County (filter by Principal County Served = BERNALILLO; ABCWUA system **NM3510701**).
- **Access:** interactive search; sample search defaults to last 2 years unless a date range is supplied. Related **Drinking Water Watch API v1.0** docs/examples: [e-enterprise SDWIS DWW API](https://e-enterprise-prod.apigee.net/sdwis/dww/v1.0) (example `…/wsd/?id=NM3510701` returns Albuquerque Water System metadata — verified 2026-08-06).
- **Geography:** statewide PWS inventory; county filter available.
- **Time coverage:** multi-year sample history in DWW (explicit range supported); Viewer marketed for single- or multi-system search.
- **License:** public government compliance data; still attribute NMED/EPA. No separate open-data license called out on the bureau page—treat as public records with attribution.
- **KB vs tool:** violation narratives / annual compliance reports → **KB**; sample/result lookups by PWS ID → **tool**.

### 1.4 EPA / USGS Water Quality Portal (WQP) — owners: EPA + USGS (+ contributing agencies)

- **Portal:** [https://www.waterqualitydata.us/](https://www.waterqualitydata.us/)
- **Web services guide:** [WQP Web Services Documentation](https://www.waterqualitydata.us/webservices_documentation/)
- **User guide (countycode format):** [WQP Portal User Guide](https://www.waterqualitydata.us/portal_userguide/)
- **County filter for Bernalillo, NM:** `countycode=US:35:001` (URL-encoded `US%3A35%3A001`).
- **Verified pull (2026-08-06):** Station search returned **~2,966** monitoring locations; Result narrow profile for **2020-01-01 … 2024-12-31** returned **~46,000** result rows. Dominant station provider in this pull: USGS; also NMED SWQB (`21NMEX` / `21NMEX_WQX`), AMAFCA, tribal programs, etc.
- **Themes:** discrete ambient / environmental water-quality results (streams, wells, etc.)—**not** a substitute for the ABCWUA CCR tap-water compliance story, but excellent for environmental trends in the county footprint.
- **Access:** REST download API (CSV/TSV/Excel); also modern USGS Samples API listed at [api.waterdata.usgs.gov/docs](https://api.waterdata.usgs.gov/docs/).
- **License:** USGS-produced data are U.S. public domain with requested attribution ([USGS copyright FAQ](https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted); OGC API landing notes public-domain government work at [api.waterdata.usgs.gov](https://api.waterdata.usgs.gov/ogcapi/v0/)). Multi-agency WQP rows inherit each provider’s terms—cite provider per record.
- **KB vs tool:** **tool-backed** structured queries (filter by characteristic, media, date). Optionally cache summaries in Postgres.

### 1.5 EPA Envirofacts / SDWIS — owner: EPA

- **API overview:** [Envirofacts Data Service API](https://www.epa.gov/enviro/envirofacts-data-service-api)
- **SDWIS downloads / model:** [Download Additional Envirofacts Datasets – SDWIS](https://www.epa.gov/enviro/download-additional-envirofacts-datasets)
- **Use:** federal inventory of PWS characteristics, violations, enforcement—complements NMED DWW for compliance context.
- **KB vs tool:** violation definitions → **KB**; PWS/violation queries → **tool**.

---

## 2. Bear Canyon recharge project readings

### 2.1 ABCWUA Diversion and Recharge Data — owner: ABCWUA

- **Page:** [Diversion and Recharge Data](https://www.abcwua.org/your-drinking-water-diversion-and-recharge-data/)
- **Published Bear Canyon daily recharge PDFs on that page (as of fetch):** Dec 2014; Jan–Mar 2015; plus Bear Canyon USR-2 Monthly Report Nov 2014. Example table PDF: [Bear Canyon Daily Discharge January 2015](https://www.abcwua.org/wp-content/uploads/Your_Drinking_Water-PDFs/Bear-Canyon-Daily-Discharge_January-2015.pdf) (daily gallons / acre-feet).
- **Also on page:** San Juan-Chama hourly/daily diversion & return-flow downloads; DWTP large-scale daily recharge PDFs for Jan–Mar 2020.
- **Disclaimer on page:** data are provisional and subject to revision.
- **Geography:** Bear Canyon Arroyo reach (NE Albuquerque / Bernalillo County); not county-wide.
- **Time coverage gap:** public daily Bear Canyon discharge tables on this page stop around **early 2015**. Recent *operations* continue (see AIS below), but **machine-friendly recent daily readings are not published there**.
- **License:** ABCWUA site ToS (personal/informational use; see §1.1).
- **KB vs tool:** parse historical daily PDFs into a table (**tool**); keep methodology/context in **KB**.

### 2.2 ABCWUA Annual Information Statements (recoverable storage) — owner: ABCWUA

- **AIS 2024 PDF:** [ABCWUA-AIS-2024-v4-Final.pdf](https://www.abcwua.org/wp-content/uploads/2025/04/ABCWUA-AIS-2024-v4-Final.pdf) — Bear Canyon recoverable volume **2,351.3 acre-feet**; permit up to **3,000 AF/yr**, max storage **10,000 AF**; large-scale ASR recoverable **4,662 AF**.
- **AIS 2025 PDF:** [ABCWUA-AIS-2025-FINAL.pdf](https://www.abcwua.org/wp-content/uploads/2025/04/ABCWUA-AIS-2025-FINAL.pdf) — Bear Canyon recoverable volume **2,795 AF**; large-scale ASR recoverable **4,890 AF**; same permit caps.
- **Themes:** point-in-time recoverable ASR storage and permit limits (not daily discharge hydrographs).
- **Access:** PDF bulk download.
- **KB vs tool:** narrative ASR section → **KB**; storage totals → small curated **tool**/table keyed by statement year.

### 2.3 ABCWUA Rivers and Aquifers Protection Plan (RAPP) — owner: ABCWUA

- **PDF:** [2018 Final RAPP](https://www.abcwua.org/wp-content/uploads/Your_Drinking_Water-PDFs/2018_Final_RAPP-1.pdf)
- **Content (primary):** describes Bear Canyon as first permitted operating artificial recharge project in NM; ~2,800-ft arroyo reach; San Juan-Chama source via Arroyo del Oso non-potable tank; OSE permit max **3,000 AF/yr**; NMED groundwater discharge plan; typical release season roughly Oct–Mar.
- **KB vs tool:** **KB** (methodology, permitting, hydrologic narrative).

### 2.4 USGS NWIS site “Bear Canyon near Albuquerque” — owner: USGS

- **Inventory:** [USGS 08329868](https://waterdata.usgs.gov/nm/nwis/inventory/?site_no=08329868&agency_cd=USGS)
- **Available discharge:** roughly **2006-10-01 … 2009-09-30** only (not useful for current ASR accounting).
- **Note:** do **not** treat this gage as the operational Bear Canyon ASR meter series; ABCWUA owns the recharge accounting publications.

### 2.5 Education / overview pages — owner: ABCWUA

- [Education – Aquifer Storage and Recovery](https://www.abcwua.org/education-23b_recharge/) — public narrative on ASR intent (KB only).

---

## 3. Water use suitable for per-capita figures (~2024)

### 3.1 ABCWUA-reported GPCD (preferred for “utility per-capita”) — owner: ABCWUA

ABCWUA publishes **gallons per capita per day (GPCD)** using its **own service-population denominator**, not raw county Census population. Prefer these figures for app answers about “Albuquerque/ABCWUA per-capita use.”

| Source | Claim (with link) |
| --- | --- |
| [AIS 2025](https://www.abcwua.org/wp-content/uploads/2025/04/ABCWUA-AIS-2025-FINAL.pdf) | Service population ≈ **657,511**; usage ≈ **125 GPCD** in **Calendar Year 2024**; goal **110 GPCD by 2037** (Water 2120). |
| [AIS 2024](https://www.abcwua.org/wp-content/uploads/2025/04/ABCWUA-AIS-2024-v4-Final.pdf) | Service population ≈ **656,237**; usage ≈ **129 GPCD** in **CY 2023**. |
| AIS 2025 statistical section “Per Capita Water Usage” | Tabulated GPCD: 2023 **129**, 2022 **127**, 2021 **128**, 2020 **128**, … (source note: ABCWUA Financial/Business Services Division). |
| [2024 Annual Report](https://www.abcwua.org/wp-content/uploads/2024/12/ABCWUA-2024AnnualReport-R4.pdf) | Narrative: mid-1990s ≈ **252** GPCD → about **124** GPCD “now” (chart). |
| [FY24 Proposed Budget & Performance Plan](https://www.abcwua.org/wp-content/uploads/2024/04/FY24-Proposed-Budget-and-Performance-Plan.pdf) | CY22 **127** GPCD; conservation goal 110 by 2037. |
| [2037 Water Conservation Plan](https://www.abcwua.org/wp-content/uploads/Conservation_Rebates/2037_Water_Conservation_Plan.pdf) | Policy basis for 110 GPCD goal under Water 2120. |
| [Drought Management Plan (2023)](https://www.abcwua.org/wp-content/uploads/2023/05/ABCWUA-Water-Resources-Drought-Management-Plan_Final-1.pdf) | GPCD used as drought-trigger metric (e.g., cites 127 GPCD in 2022). |

- **Access:** PDF reports (no public GPCD time-series API found).
- **Geography:** ABCWUA service area (≈ city + Bernalillo County customers), **not** identical to county Census geography.
- **License:** ABCWUA ToS as in §1.1.
- **KB vs tool:** conservation/drought methodology → **KB**; extract GPCD-by-year into a curated table for **tools**.

### 3.2 Census population (denominator only; do not invent GPCD) — owner: U.S. Census Bureau

- **ACS 1-year API docs:** [2024 ACS 1-Year](https://www.census.gov/data/developers/data-sets/acs-1year/2024.html)
- **Example pattern:** `https://api.census.gov/data/2024/acs/acs1?get=NAME,B01003_001E&for=county:001&in=state:35&key=…`
- **Role:** optional comparison denominator for Bernalillo County population. **Do not divide ABCWUA production by Census population and call it “official GPCD”**—ABCWUA already publishes GPCD with its customer-population method.
- **License:** Census data are generally public for reuse with attribution; API key required for Census Data API.
- **KB vs tool:** **tool** for population pulls; keep GPCD methodology explanation in **KB**.

---

## 4. Aquifer depth / quantity (short note for later)

### 4.1 USGS Albuquerque Basin groundwater-level network — owner: USGS (coop. ABCWUA / others)

- **Project page:** [Groundwater-level data for the Albuquerque Basin and Adjacent Areas](https://www.usgs.gov/centers/new-mexico-water-science-center/science/groundwater-level-data-albuquerque-basin-and)
- **Facts from that page:** network currently **122** wells/piezometers (69 hourly, 51 semiannual, 2 quarterly); data stored in NWIS and public via USGS Water Data for the Nation.
- **Related program:** [Middle Rio Grande Basin piezometers](https://www.usgs.gov/centers/new-mexico-water-science-center/science/groundwater-level-monitoring-middle-rio-grande)
- **Published data series example:** [USGS Data Series 1129](https://doi.org/10.3133/ds1129) (levels through WY 2019; cites NWIS as ongoing store).
- **Modern API hub:** [USGS Water Data APIs](https://api.waterdata.usgs.gov/) / [docs](https://api.waterdata.usgs.gov/docs/); OGC collections include `monitoring-locations`, `daily`, `continuous`, etc. Verified query pattern for Bernalillo County monitoring locations: `state_code=35&county_code=001` on `…/collections/monitoring-locations/items` (2026-08-06).
- **Legacy note:** older `waterservices.usgs.gov` groundwater-levels endpoints are being decommissioned; prefer modern `api.waterdata.usgs.gov` for new work ([Water Data APIs announcement](https://www.usgs.gov/tools/usgs-water-data-apis)).
- **National aquifer:** many local wells are completed in the **Rio Grande aquifer system** (example site metadata pattern on NWIS).
- **License:** USGS public domain + attribution.
- **KB vs tool:** basin/network narrative & DS reports → **KB**; water-level / well-depth series → **tools**.

### 4.2 ABCWUA aquifer / ASR narrative

- RAPP and AIS sections (§2) discuss aquifer storage strategy and recoverable ASR volumes—useful quantity *management* context, not a full aquifer volumetric model.

---

## Cross-cutting license notes (student public app)

| Owner | Constraint gist | Source |
| --- | --- | --- |
| USGS | Public domain; attribute USGS | [USGS FAQ](https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted) |
| EPA WQP / Envirofacts | Public federal data; attribute; multi-provider rows need provider credit | [WQP](https://www.waterqualitydata.us/), [Envirofacts API](https://www.epa.gov/enviro/envirofacts-data-service-api) |
| NMED DWW / Viewer | Public compliance portals; attribute NMED | [DWB](https://www.env.nm.gov/drinking_water/) |
| ABCWUA website/PDFs | Proprietary site Content; personal/informational use; no commercial exploitation without permission | [Terms](https://www.abcwua.org/terms-and-conditions/) |
| Census | Public statistical data via API (key required) | [ACS API](https://www.census.gov/data/developers/data-sets/acs-1year/2024.html) |

For the Zoomcamp student app: prefer **link-out + short quoted figures with citations** for ABCWUA PDFs; use USGS/EPA APIs freely with attribution for structured tools.

---

## Decision-quality takeaways

1. **Water quality trends:** ingest ABCWUA CCR PDFs 2020–2025 for tap-water story; use NMED DWW/Viewer (+ optional DWW/SDWIS API) for compliance samples/violations on `NM3510701`; use **WQP** (`US:35:001`) for ambient environmental trends via tools.
2. **Bear Canyon:** no rich public recent daily API—use historical daily PDFs + AIS recoverable storage snapshots + RAPP methodology; do not rely on USGS 08329868 for ASR accounting.
3. **Per-capita ~2024:** use ABCWUA **125 GPCD (CY2024)** from AIS 2025 (and the GPCD history table); treat Census ACS only as a separate population denominator.
4. **Aquifer later:** USGS Albuquerque Basin network + modern Water Data APIs are the clear structured path.
