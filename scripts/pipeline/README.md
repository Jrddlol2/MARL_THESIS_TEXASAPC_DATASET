# Data pipeline — Route 801 / direction 6

Everything from the raw CapMetro APC dataset to the cleaned study set and the
weather join, split into five steps you can read one at a time.

## This pipeline never touches the internet

Every step reads our own archived, checksummed copies of the source data.
There is no download code here at all:

```bash
grep -r urllib scripts/pipeline/    # returns nothing
```

That is deliberate. The APC dataset is a **closed historical archive** —
published 2022-01-14, rows last updated 2022-01-14, covering July–December
2021. It cannot change. Re-fetching it would prove nothing that the recorded
SHA-256 does not already prove.

If a file is missing, the scripts fail with a message pointing at the
**"Getting the data"** section of the [repository README](../../README.md)
rather than a stack trace.

## Run it

```bash
python scripts/pipeline/run_all.py     # all five steps, in order
```

Or one step at a time:

```bash
python scripts/pipeline/01_audit_routes.py
python scripts/pipeline/02_extract_dir6.py
python scripts/pipeline/03_prepare_weather.py
python scripts/pipeline/04_join_weather.py
python scripts/pipeline/05_gtfs_gate.py
```

## The steps

| # | Script | What it answers | Key output |
|---|---|---|---|
| 1 | `01_audit_routes.py` | Why Route 801 and not 803? Where do the funnel numbers come from? | `route_selection_audit.json` |
| 2 | `02_extract_dir6.py` | The 229,421-row study set | `route_801_direction_6_clean.csv` |
| 3 | `03_prepare_weather.py` | NOAA observations, put on the same clock as the buses | `weather_camp_mabry_2021_jul_dec.csv` |
| 4 | `04_join_weather.py` | Was it raining at each stop event? | `weather_join_audit.json` |
| 5 | `05_gtfs_gate.py` | What we're allowed to claim about direction 6 | `GTFS_ACQUISITION_STATUS.md` |

`common.py` holds the shared plumbing — paths, config loading, checksums, safe
file writing, reading the snapshot, and the cleaning rules. It does no data
processing of its own.

## Built on pandas

Steps 1, 2 and 4 use pandas, so the code reads the way an analyst would expect:

- the cleaning rules are boolean masks, one line per rule
- the per-route statistics are a `groupby`, not hand-maintained accumulators
- the weather join is `pd.merge_asof(direction="nearest", tolerance=...)`,
  which is the standard tool for a nearest-in-time join

The 3.7 GB file is read with `chunksize=1_000_000` so it never has to fit in
memory. `na_filter=False` keeps blanks as empty strings rather than NaN, which
keeps the string comparisons in the cleaning rules predictable.

Step 3 is deliberately still a plain Python loop. It handles NOAA's
irregularities one at a time — trace precipitation written as `"T"`,
present-weather codes matched as substrings, column names that change
capitalisation between files, numbers carrying quality letters like `0.05s`,
and duplicate observations at the same instant resolved by completeness. Each
of those gets its own commented line; vectorising it would be shorter but would
bury the reasoning in a chain of `.str` calls.

Requires `pandas` and `numpy` (already project dependencies). `tabulate` is
deliberately NOT used — the evidence tables are built by hand so the output
stays byte-identical and there is no extra dependency.

## How long it takes

Measured end to end, ~100 seconds total:

```
01_audit_routes.py      42 s     streams all 9.2M rows, 19 of 47 columns
02_extract_dir6.py      54 s     streams all 9.2M rows, all 47 columns
03_prepare_weather.py    2 s
04_join_weather.py       2 s
05_gtfs_gate.py          1 s
```

Steps 1 and 2 are dominated by the time it takes to read the 3.7 GB file off
disk; every pandas operation inside them is sub-second. There is no meaningful
speed-up available short of merging the two passes, which would cost more in
readability than it saves in seconds.

## Order

- **4 needs 2 and 3** — the study set and the weather tables.
- **1, 2, 3 and 5** can each be run on their own.

## The cleaning rules

`common.clean_masks()` is the canonical implementation — the six rules, built
as four **cumulative** boolean masks:

```python
on_route   = frame["route_id"].isin(routes)                          # 1
matching   = on_route   & (frame["route_id"] == frame["current_route_id"])   # 2
error_free = matching   & (import_error == "0") & (import_trip_error == "0") # 3, 4
clean      = error_free & (bs_id != "0") & direction_code_id.isin(directions) # 5, 6
```

Each mask is a superset of the next, so those four **are** the bars on the
cleaning-funnel slide. Step 1 uses all four; Step 2 uses only `clean`. Defining
them in one place means the funnel and the study set can never drift apart.

`common.clean_where()` writes the same six rules as an SQL-style string.
**Nothing executes it** — it exists so the audit files and the manuscript can
quote the cleaning rule as one readable line, and so anyone can re-run the
identical filter against the public API if they ever want to.

## Where things land

```
data/raw/capmetro/     route_801_direction_6_clean.csv       (step 2)
data/processed/        weather_*_2021_jul_dec.csv            (step 3)
data/audit/            every *.json and *.md                 (all steps)
config/                texas_capmetro_801.json               (input, not output)
```

## The one rule

**Change the config, not the code.** Routes, direction codes, the study window,
the NOAA stations and the 90-minute join tolerance all live in
`config/texas_capmetro_801.json`. Nothing tunable is hardcoded in these scripts.

## What this does NOT cover

The pipeline stops at the cleaned CSV plus the weather join. The corridor, the
SUMO network and the calibration live in `starter/scripts/`:

- `extract_sim_inputs.py` — per-stop aggregation into `sim_inputs/stops.csv`
- `extract_route_shape.py` — corridor geometry
- `build_real_net.py` — the SUMO network
- `calibrate_corridor.py` — GEH / RMSPE / the speed-update loop

Note that `extract_sim_inputs.py` re-implements the same six cleaning rules in
pandas, because it needs clean rows before it can aggregate them. Both produce
229,421 rows — that agreement is a cross-check, not a duplication bug. The
authoritative filter for anything quoted in the manuscript is
`common.clean_masks()`.

## The old version

`scripts/texas_capmetro_pipeline.py` is the original 900-line single-file
implementation. It downloads from the Texas Open Data portal rather than
reading local files. It still works and is kept as an archived reference — if
you ever need to re-verify our extraction against the source of record, that is
the script to run.
