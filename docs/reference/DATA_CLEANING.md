# Dataset Cleaning & Provenance — CapMetro Route 801 APC (dir-6 subset)
**Purpose:** a single, reproducible record of how the raw public dataset becomes the **229,421-event study subset** — so the result can be regenerated and audited. Grounded in `scripts/texas_capmetro_pipeline.py` and the manifests in `data/audit/texas_capmetro/`. Condense into manuscript §3.2.5 / an appendix; keep this as the full version.

## 1. Source
- **Dataset:** Capital Metro *APC Raw July 2021 – December 2021*, Texas Open Data Portal (Socrata asset **`im6q-3pc9`**).
- **Shape:** ~**9,197,694** rows × **47 text-typed fields** (all values arrive as strings).
- **Weather (joined later):** NOAA *Local Climatological Data v2* — Austin **Camp Mabry `USW00013958`** (primary), **Austin-Bergstrom `USW00013904`** (sensitivity).
- Access date recorded in the manifests (2026-08-23). Raw CSVs are git-ignored; the **queries + SHA-256 checksums** are committed.

## 2. Cleaning filter (applied server-side in the Socrata query — `clean_where()`)
A stop-event is **kept** only if **all six** hold:
| # | Rule (SoQL) | Why |
|---|---|---|
| 1 | `route_id in ('801')` | keep only the study route (801; 803 pulled too, only for route selection) |
| 2 | `route_id = current_route_id` | the reported route matches the active route — drops re-routed / mismatched records |
| 3 | `import_error = '0'` | drop rows the agency flagged as import errors |
| 4 | `import_trip_error = '0'` | drop rows on trips flagged as import errors |
| 5 | `bs_id <> '0'` | drop placeholder / non-stop events (stop id 0) |
| 6 | `direction_code_id in ('6')` | keep only the study direction (code 6) |

> **Not filtered (kept, only *reported*):** low-GPS-quality rows and null-load rows are **not** dropped. GPS quality is measured and reported (see §4), not used as a cleaning cut. This keeps the sample complete and the exclusion criteria transparent.

## 3. The row funnel (Route 801 → study subset), with checksums
| Stage | Definition | Rows |
|---|---|---|
| Full asset | all routes, Jul–Dec 2021 | ~9,197,694 |
| Route 801, all records | `route_id='801'` | 547,616 |
| … matching current route | + rule 2 | 524,728 |
| … error-free | + rules 3–4 | 480,452 |
| **Clean (dir 4 & 6)** | + rules 5–6 (both directions) | **455,654** |
| **▶ Primary subset (dir 6)** | full clean filter, direction 6 only | **229,421** |
| *(comparison)* Route 803 clean | same rules, route 803 | 376,801 |

- **Primary subset SHA-256:** `8368412e47df32ff8a3c2837048797664315c0e7ae51c44676766b5af7f23e21`
- **Coverage of the subset:** **29** distinct stop IDs · **184** service-day codes · GPS high-quality **98.136 %** · median dwell **18.0 s** · mean reported `max_load` **11.414** (a *reported-load mean*, **not** a capacity).
- **Route-801-over-803 rationale (data coverage, not service quality):** under identical rules, 801 yields ~20.9 % more clean stop-events and ~52.3 % more boardings than 803, at comparable GPS quality — so 801 is the primary case. (`route_selection_audit.json`.)

## 4. Field handling & derived quantities
- **Type coercion** (`safe_int` / `safe_float`): every field is parsed from text; blank or non-numeric → `null` (the row is kept, the value is missing).
- **Segment running time** = `rev_seconds − dwell_time`, floored at 0. `rev_seconds` is measured **open-to-open** (it already includes that stop's dwell), so using it as travel time *and* modeling dwell separately would **double-count** — hence the subtraction.
- **Usable segments** = rows with `rev_seconds > 0` **and** `rev_distance > 0` (441,779 for 801).
- **GPS high-quality** (reported) = nonzero `veh_lat`/`veh_long` **and** `quality_indicator ∈ {3,4,5,6}`.
- **Service day** = first 8 chars of `transit_date_time`; **trip** = `(transit_day, ext_trip_id)` (fallback `act_trip_start_time|vehicle_id`).
- **Timestamps** are treated as **Austin wall-clock** — a *declared assumption* (the dead 02:00–03:00 window and 05:00 ramp support it), not a metadata-confirmed fact.

## 5. Weather join (`audit_weather_join()`)
- NOAA observations parsed as local standard time → converted to **`America/Chicago`** (DST-aware; ambiguous fall-back timestamps use `fold=0` and are counted).
- Each APC event matched to the **nearest NOAA observation within 90 minutes**.
- Result: **100 %** join coverage of the 229,421 events; **11,804** matched a Camp Mabry rain flag; median join gap **12.7 min** (p95 **27.9 min**).
- Pooled dry vs rain segment medians are **descriptive only** — not a causal weather multiplier (segment / time-of-day / day-type controls required).

## 6. What is deliberately NOT derived (gated pending sources)
- **2021 stop names & compass direction label** — gated pending a checksum-verified **2021 GTFS snapshot** (a current feed is *not* substituted). See `GTFS_ACQUISITION_STATUS.md`.
- **Vehicle capacity** — not an APC field; `max_load` is a reported load, not capacity.
- **Passenger waiting time, breakdowns, continuous speed** — not observed in APC; these are **simulation** variables, not measured facts.

## 7. Reproduce it
```bash
python scripts/texas_capmetro_pipeline.py --all        # downloads, filters, audits, checksums
```
Outputs land under `data/audit/texas_capmetro/`: `primary_subset_manifest.json` (the exact query + row count + SHA-256), `route_selection_audit.json`, `weather_join_audit.json`, `socrata_metadata.json`, plus `APC_FIELD_USE_MAP.md`. Re-running reproduces the identical subset (verify by SHA-256).

## 8. Where this maps in the manuscript
- **§3.2.5 Data Processing** + **Table 3.3** (field → derived quantity → role) already summarize this; this document is the reproducibility long-form behind them.
- Suggested: cite this file (or an appendix built from §2–§5) so the exact filter rules, the funnel with checksums, and the weather-join method are on the record — which is what the panel asked for (describe the dataset + cleaning/filtering rules).
