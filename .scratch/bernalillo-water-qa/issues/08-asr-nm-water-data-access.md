# Inventory NM Water Data ASR monitoring wells access

Type: research
Status: resolved

## Question

For the New Mexico Water Data catalog dataset [Water Authority ASR Monitoring Wells](https://catalog.newmexicowaterdata.org/dataset/water-authority-asr-monitoring-wells) (and resource `5bc7cc13-934c-4bda-8664-2a13ada21d44` if still current): what download/API access methods exist, what is the schema (fields like Date, pressure_psi, WaterLevel_ft_toc/bgs, site identifiers, project labels), which wells/sites are present and how to tell Large-Scale DWTP ASR from others, what time coverage and refresh cadence look like, and any license/ToS notes for a public student app?

Primary sources only (catalog pages, CKAN/API docs, resource metadata). Output a findings file under `research/` suitable for building the ASR monitoring tool + Airflow ingest.

## Answer

Resource `5bc7cc13-…` is still the **Large Scale ASR MW-01 Transducer** CSV (`largescaletransducer.csv`) at the San Juan-Chama DWTP (nested MW-01S/D). Access is CKAN download / `package_show` (Cloudflare blocks unattended scrapes); schema includes `Date`, `pressure_psi`, `WaterLevel_ft_toc`, `WaterLevel_ft_bgs`, `depth` (`s`/`d`), plus Note/seconds/dt. Same package also has Bear Canyon wells (filter by resource). Catalog republish **quarterly**; loggers hourly (manual monthly); Large-Scale POR from **2015**. License field: not specified—attribute ABCWUA + catalog. Findings: [research/asr-nm-water-data-access.md](../../research/asr-nm-water-data-access.md).
