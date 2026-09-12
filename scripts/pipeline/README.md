# Data pipeline — Route 801 / direction 6

Everything from the raw CapMetro APC dataset to the cleaned study set and the
weather join, split into five steps you can read one at a time.

This replaces the single 900-line `scripts/texas_capmetro_pipeline.py`. The
logic is identical — it was extracted, not rewritten — and the outputs were
verified to match field-for-field.

## Run it

```bash
python scripts/pipeline/run_all.py          # all five steps, in order
python scripts/pipeline/run_all.py --force  # ignore cached downloads
```

Or one step at a time:

```bash
python scripts/pipeline/01_audit_routes.py
python scripts/pipeline/02_download_dir6.py
python scripts/pipeline/03_prepare_weather.py
python scripts/pipeline/04_join_weather.py
python scripts/pipeline/05_gtfs_gate.py
```

Re-running is cheap and safe. Every download checks for a local copy first and
records `"reused_existing_file": true` instead of fetching again.

## The steps

| # | Script | What it answers | Key output |
|---|---|---|---|
| 1 | `01_audit_routes.py` | Why Route 801 and not 803? Where do the funnel numbers come from? | `route_selection_audit.json` |
| 2 | `02_download_dir6.py` | The 229,421-row study set | `route_801_direction_6_clean.csv` |
| 3 | `03_prepare_weather.py` | NOAA observations, put on the same clock as the buses | `weather_camp_mabry_2021_jul_dec.csv` |
| 4 | `04_join_weather.py` | Was it raining at each stop event? | `weather_join_audit.json` |
| 5 | `05_gtfs_gate.py` | What we're allowed to claim about direction 6 | `GTFS_ACQUISITION_STATUS.md` |

`common.py` holds the shared plumbing — paths, config loading, checksums, safe
file writing, downloads, the Socrata paging loop, and the cleaning predicate.
It does no data processing of its own.

## Order

- **2 needs 1** — it uses the column list that step 1 saves.
- **4 needs 2 and 3** — the study set and the weather tables.
- **1, 3 and 5** can each be run on their own.

## Where things land

```
data/raw/capmetro/     route_801_803_clean_comparison.csv   (step 1)
                       route_801_direction_6_clean.csv      (step 2)
data/raw/noaa/         LCD_USW000139*.csv                   (step 3)
data/processed/        weather_*_2021_jul_dec.csv           (step 3)
data/audit/            every *.json and *.md                (all steps)
config/                texas_capmetro_801.json              (inputs, not outputs)
```

## The one rule

**Change the config, not the code.** Routes, direction codes, the study window,
the NOAA stations and the 90-minute join tolerance all live in
`config/texas_capmetro_801.json`. Nothing tunable is hardcoded in these scripts.

## What this does NOT cover

The pipeline stops at the cleaned CSV plus the weather join. The corridor, the
SUMO network and the calibration are separate and live in `starter/scripts/`:

- `extract_sim_inputs.py` — per-stop aggregation into `sim_inputs/stops.csv`
- `extract_route_shape.py` — corridor geometry
- `build_real_net.py` — the SUMO network
- `calibrate_corridor.py` — GEH / RMSPE / the speed-update loop

Note that `extract_sim_inputs.py` re-implements the same six cleaning rules
locally, because it needs clean rows before it can aggregate them. Both
implementations produce 229,421 rows — that agreement is a cross-check, not a
duplication bug. The authoritative filter for anything quoted in the manuscript
is the one here, in `common.clean_where()`.
