# NM Water Data — Water Authority ASR Monitoring Wells access

Research date: 2026-08-06  
Scope: Catalog dataset [Water Authority ASR Monitoring Wells](https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells) and resource `5bc7cc13-934c-4bda-8664-2a13ada21d44` (Large-Scale ASR MW-01 transducer CSV), for Airflow ingest + ASR tools.  
Method: primary sources only (catalog HTML/JSON-LD, CKAN Action API docs, NMWDI FAQ/developer docs). Live catalog fetches from this environment hit Cloudflare bot challenge (HTTP 403 / “Just a moment…”); dataset metadata and resource inventory were recovered from the Internet Archive snapshot of the owning catalog page ([Wayback 2024-07-13](https://web.archive.org/web/20240713094532/https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells)). Column schema for `5bc7cc13-…` is from a catalog DataStore/preview row of that resource (operator extract in the seam decision thread), cross-checked against the resource’s own catalog description.

---

## Summary (ingest gist)

Treat this as a **CKAN file package**: Airflow should `package_show` (or hardcode resource IDs), download each CSV/GeoJSON from the stable `/dataset/{package_id}/resource/{resource_id}/download/{filename}` URLs, filter to **Large-Scale / DWTP** resources for the graded ASR theme, and load transducer (+ optional manual) rows keyed by `Date` + nested `depth` (`s`/`d`). Expect **quarterly** catalog refreshes of files that themselves contain **hourly** (historically 15‑min) logger series. Cloudflare may require a browser-derived cookie/UA or a human seed drop for the first pull.

---

## 1. Dataset identity

| Field | Value | Source |
| --- | --- | --- |
| Title | Water Authority ASR Monitoring Wells | Catalog dataset page / JSON-LD |
| Slug | `water-authority-asr-monitoring-wells` | Catalog URL |
| Package UUID | `5adccfb7-c0a1-442c-9f69-efe1145a6cd9` | Download URL paths in JSON-LD |
| Organization | Albuquerque Bernalillo County Water Utility Authority (ABCWUA) | Catalog |
| Contact | Kelsey Bicknell `<kbicknell@abcwua.org>` | JSON-LD `schema:ContactPoint` |
| Groups | water-planning, water-quantity | Catalog |
| Published | 2024-03-21 | Catalog “Published” / JSON-LD `schema:datePublished` |
| Last updated (snapshot) | 2024-05-08 | Catalog “Last Updated” / JSON-LD `schema:dateModified` |
| License field | **License not specified** | Catalog / JSON-LD `schema:license` |
| Geography | Albuquerque, NM | Catalog extras |
| Publishing frequency (catalog) | **Quarterly** | Catalog “Data Publishing Frequency” |
| Known uses | Reports to OSE and NMED for permit conditions | Catalog extras |

**Purpose (catalog notes):** ABCWUA operates two ASR projects—**Bear Canyon ASR** and **Large-Scale ASR**. Monitoring wells support USR permits (OSE) and Groundwater Discharge permits (NMED).

---

## 2. Access methods

### 2.1 Human / browser download (works; bots blocked)

Landing page: `https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells`  
Each resource has Explore / Preview / Download. As of 2026-08-06, unattended `curl`/`WebFetch` to the catalog hostname receives Cloudflare’s JS challenge (verified on `package_show`, `resource_show`, `datastore_search`, and direct CSV download).

### 2.2 CKAN Action API (documented; same host, same CF wall)

NMWDI points developers at the catalog and at upstream CKAN API docs ([Developer](https://newmexicowaterdata.org/developer/) → [CKAN API](https://docs.ckan.org/en/latest/api/index.html)).

Useful endpoints (base `https://catalog.newmexicowaterdata.org`):

| Endpoint | Use |
| --- | --- |
| `/api/3/action/package_show?id=water-authority-asr-monitoring-wells` (or package UUID) | Full metadata + resource list/URLs |
| `/api/3/action/resource_show?id={resource_id}` | Single resource metadata |
| `/api/3/action/datastore_search?resource_id={resource_id}&limit=N` | Tabular preview if DataStore is enabled (preview rows include CKAN `_id`) |
| `/dataset/{package_id}/resource/{resource_id}/download/{filename}` | Direct file download |

Example download URL for the DWTP Large-Scale transducer file (from catalog JSON-LD):

`https://catalog.newmexicowaterdata.org/dataset/5adccfb7-c0a1-442c-9f69-efe1145a6cd9/resource/5bc7cc13-934c-4bda-8664-2a13ada21d44/download/largescaletransducer.csv`

Slug form also appears in catalog HTML:  
`/dataset/water-authority-asr-monitoring-wells/resource/5bc7cc13-934c-4bda-8664-2a13ada21d44`.

### 2.3 NMWDI SensorThings / FROST (separate path — do not assume this dataset)

[FAQ](https://newmexicowaterdata.org/faq/) distinguishes **static catalog uploads** (CSV/JSON files posted at a point in time) from **dynamic** SensorThings time series. [Developer docs](https://developer.newmexicowaterdata.org/docs/intro) document FROST/SensorThings (e.g. `st2.newmexicowaterdata.org`) for agency water-level APIs. This ASR package is published as **CKAN CSV/GeoJSON resources** with an explicit **quarterly** publishing frequency—ingest should target CKAN downloads, not SensorThings, unless a future ticket proves these wells are also mirrored there.

### 2.4 Operational note for Airflow

Plan for Cloudflare: seed files under something like `data/raw/nm-water-data-asr/`, or run the fetch step with a browser-capable session. Re-check `package_show` periodically so resource IDs/filenames have not changed.

---

## 3. Resources (inventory)

From catalog JSON-LD / resource list (Wayback 2024-07-13). Resource IDs matched via `data-id` on the same snapshot.

### 3.1 Large-Scale ASR @ San Juan-Chama DWTP (priority theme)

| Resource ID | Name | File | Format |
| --- | --- | --- | --- |
| **`5bc7cc13-934c-4bda-8664-2a13ada21d44`** | Large Scale ASR MW-01 Transducer | `largescaletransducer.csv` | CSV |
| `bace582d-b5c1-420a-9f3c-408882bb954d` | Large Scale ASR MW-01 Manual | `largescalemanual.csv` | CSV |

Catalog description (transducer): measurements from **shallow and deep** Large-Scale ASR monitoring wells; **“Monitoring Well is located near the ASR injection well at the San Juan Chama Drinking Water Plant in Albuquerque, NM.”** Nested completion:

- Total depth: **325.0 ft bgs**
- **MW-01S**: screen 155–175 ft bgs; 2.0-in Sch 80 PVC  
- **MW-01D**: screen 295–315 ft bgs; 2.5-in Sch 80 PVC  

Manual resource: interface-probe measurements for the same nested well / DWTP location.

### 3.2 Bear Canyon ASR (same package; out of scope for graded demo)

| Resource ID | Name | File |
| --- | --- | --- |
| `a31531aa-a548-4f51-92b7-4d906b1ee82b` | Bear Canyon MW-01R Transducer | `mw1_xducer.csv` |
| `d532b296-a5cf-4e28-bb35-9de0da1ff904` | Bear Canyon MW-02 Transducer | `mw2_xducer.csv` |
| `d8d05ec7-471b-4fbb-ae03-8af38f86dbaf` | Bear Canyon MW-03 Transducer | `mw3_xducer.csv` |
| `f1519177-24c3-48e7-880d-5b334c0e4580` | Bear Canyon MW-01R Manual | `mw1_man.csv` |
| `5e094e50-4f84-441d-9c90-b3d597eb52db` | Bear Canyon MW-02 Manual | `mw2_man.csv` |
| `1d0ce206-a315-486c-86a1-319c7137a18c` | Bear Canyon MW-03 Manual | `mw3_man.csv` |

Well notes (catalog): MW-01R ~587 ft; MW-02 ~585 ft (**drilled on a fault**—levels differ drastically from other wells); MW-03 ~575 ft. Period of record stated as **2007–present**.

### 3.3 Locations

| Resource ID | Name | File |
| --- | --- | --- |
| `039f329d-b491-4dc5-9302-61b93ad4e00c` | Point Locations of Monitoring Wells… | `waterauthority_asr_monitoringwells.geojson` |

GeoJSON / PJSON, **WGS 1984**, points for Bear Canyon **and** Large-Scale wells.

---

## 4. How to tell Large-Scale DWTP from Bear Canyon

There is **no single project column inside every CSV**; disambiguation is by **which resource you ingested** (and site naming):

| Signal | Large-Scale (DWTP) | Bear Canyon |
| --- | --- | --- |
| Resource name / filename | “Large Scale ASR…”, `largescale*.csv` | “Bear Canyon MW-…”, `mw{1,2,3}_*.csv` |
| Resource ID | `5bc7cc13-…` (transducer), `bace582d-…` (manual) | `a31531aa-…`, `d532b296-…`, `d8d05ec7-…`, etc. |
| Catalog site text | San Juan-Chama **Drinking Water Plant**; nested **MW-01S / MW-01D** | MW-01R, MW-02, MW-03 |
| Nested depth key (Large-Scale sample) | column `depth` = `s` or (expected) `d` | N/A (one completion per file) |
| App policy | **In scope** for ASR tools | Same package but **out of scope** for must-work demo ([seam decision](../.scratch/bernalillo-water-qa/issues/03-kb-vs-tools-seam.md)) |

Recommended ingest tags: `project=large_scale_dwtp` vs `project=bear_canyon`, `site_id=MW-01S|MW-01D|MW-01R|…`, `measurement_type=transducer|manual`.

---

## 5. Schema / fields (Large-Scale transducer `5bc7cc13-…`)

Catalog DataStore/preview sample for this resource (one row; `_id` is the CKAN DataStore surrogate key):

| Column | Sample value | Role |
| --- | --- | --- |
| `_id` | `160444` | DataStore row id (drop or keep as provenance) |
| `Date` | `2022-09-12T07:52:00` | Observation timestamp |
| `seconds` | `8294400` | Logger/elapsed seconds field (retain raw) |
| `pressure_psi` | `17.928` | Transducer pressure (psi) |
| `WaterLevel_ft_toc` | `14.64` | Water level, feet to top of casing |
| `WaterLevel_ft_bgs` | `136.964` | Water level, feet below ground surface |
| `Note` | (empty) | Free-text note |
| `depth` | `s` | Nested completion: shallow (`s`) / deep (`d` expected) → MW-01S / MW-01D |
| `dt` | `2022-09-12T00:00:00` | Date (day) companion field |

Instruments (dataset notes): **In-Situ Level TROLL** transducers; manual checks with an **interface probe**.

Manual CSVs were not re-sampled under Cloudflare; expect a sparser schema (date + level columns, possibly without `pressure_psi`). Confirm on first successful download.

---

## 6. Time coverage and refresh cadence

| Layer | Cadence / coverage | Source |
| --- | --- | --- |
| Logger sampling | Currently **hourly**; historically as fine as **15 minutes** | Dataset notes |
| Manual levels | **Monthly** (separate files) | Dataset notes |
| Catalog republish | **Quarterly** (“Data Publishing Frequency”) | Catalog extras |
| Large-Scale POR | **2015–present** (stated) | Dataset notes |
| Bear Canyon POR | **2007–present** (stated) | Dataset notes |
| Sample observation date | at least through **2022-09-12** in preview row `_id=160444` | Schema sample |
| Snapshot last_updated | **2024-05-08** (Wayback); live page may be newer—re-check when CF allows | Catalog |

Ingest implication: pull full CSV replacements on a quarterly (or monthly) Airflow schedule; do not assume SensorThings-style daily append unless proven.

---

## 7. License / ToS notes (student public app)

- Catalog license field: **“License not specified.”** ([dataset JSON-LD](https://web.archive.org/web/20240713094532/https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells))
- NMWDI is a **conduit**; agencies remain responsible for their data ([FAQ – “Does the NMWDI take the data?”](https://newmexicowaterdata.org/faq/)). Ideal submissions are “open for sharing without restriction,” but that is aspirational guidance for contributors, not a blanket license on every catalog file.
- Practical posture for a non-commercial student citation app:
  - Attribute **ABCWUA** + **NM Water Data catalog** + resource name/ID + observation timestamp.
  - Prefer linking to the catalog URL over redistributing bulk CSV binaries in a public git repo.
  - Contact `kbicknell@abcwua.org` (or ABCWUA) if redistributing full series or commercializing.
  - Do not confuse this package with NMED Open Data Portal API terms ([api.env.nm.gov terms](https://api.env.nm.gov/terms-and-conditions-for-use/))—those govern a different portal.

---

## 8. Recommended Airflow / tool shape

1. **Discover**: `package_show` when reachable; else pin resource IDs from this inventory.  
2. **Download**: `largescaletransducer.csv` (+ optional `largescalemanual.csv`, GeoJSON for map context).  
3. **Normalize**: map `depth` `s`/`d` → `MW-01S`/`MW-01D`; set `project=large_scale_dwtp`; parse `Date` to timestamptz.  
4. **Store**: Postgres table for tool queries (`latest`, `range by site`).  
5. **Cite**: `WaterLevel_ft_bgs` (or toc) | value | as-of `Date` | ABCWUA via NM Water Data | site MW-01S/D | catalog resource URL.  
6. **Exclude** Bear Canyon resources from must-work paths unless product scope changes.

---

## Sources

1. Catalog dataset page (archived): https://web.archive.org/web/20240713094532/https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells  
2. Live catalog URL (CF-protected from this environment on 2026-08-06): https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells  
3. Resource `5bc7cc13-934c-4bda-8664-2a13ada21d44` download path / description in catalog JSON-LD (same Wayback snapshot)  
4. CKAN Action API documentation: https://docs.ckan.org/en/latest/api/index.html  
5. NMWDI Developer page (CKAN + SensorThings links): https://newmexicowaterdata.org/developer/  
6. NMWDI FAQ (conduit model; static vs dynamic; SensorThings): https://newmexicowaterdata.org/faq/  
7. NMWDI developer intro (FROST/SensorThings examples): https://developer.newmexicowaterdata.org/docs/intro  
8. Schema sample row for resource `5bc7cc13-…` from catalog DataStore/preview (operator extract used in seam decision, 2026-08-06)
