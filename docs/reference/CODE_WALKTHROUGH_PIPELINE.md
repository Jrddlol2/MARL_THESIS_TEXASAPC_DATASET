# Code walkthrough — `scripts/pipeline/`

Block-by-block explanation of the data pipeline: raw CapMetro file → cleaned study
set → weather attached. This is the code behind everything MSA1 presents.

Generated with [`docs/prompts/Code_Walkthrough_Prompt.md`](../prompts/Code_Walkthrough_Prompt.md).
**Line numbers are current as of 2026-09-14**, after the files were rewritten for
beginner readability. That rewrite changed no output: every file the pipeline writes
was re-generated and compared byte-for-byte (only the "generated at" timestamps differ).

## File index

| File | Lines | What breaks if you delete it |
|---|---|---|
| `common.py` | 226 | Everything. Holds the paths, the checksums, and the cleaning rules |
| `audit_route_selection.py` | 291 | The cleaning-funnel numbers and the 801-vs-803 justification |
| `01_extract_dir6.py` | 127 | The 229,421-row study set — the input to the whole simulation |
| `02_prepare_weather.py` | 262 | The NOAA tables. Weather would be unusable |
| `03_join_weather.py` | 266 | The rain flag on each stop event, and the feasibility verdict |
| `04_gtfs_gate.py` | 103 | The written record of what direction 6 may be called |
| `run_all.py` | 62 | Convenience only — the four steps still run individually |

**Runtime (measured 2026-09-13):** step 1 ≈ 55 s (reads 9.2 M rows), step 2 1 s,
step 3 3 s, step 4 0.1 s. The route-selection audit is a separate ≈ 45 s evidence run.

**Style used in every file:** a header saying WHAT IT DOES / INPUT / OUTPUT / RUN,
one statement per line, plain `for` loops, no type hints, and `import common` so every
shared helper is written `common.name` and you can see where it comes from.

---

# `common.py` — the shared plumbing

Does no data processing itself.

## L40–60 — where everything lives

```
L40   ROOT = Path(__file__).resolve().parent.parent.parent
      WHAT  the repository root (this file is <repo>/scripts/pipeline/common.py)
      WATCH move this file and every path breaks. It is the anchor.

L42-46 CONFIG_PATH, AUDIT_DIR, RAW_CAPMETRO_DIR, RAW_NOAA_DIR, PROCESSED_DIR
L50   RAW_FULL_SNAPSHOT = .../APC_Raw_July_2021_December_2021_full.csv
      WHAT  THE DATASET. The only place its name appears. Not in git (3.7 GB).

L56   NOAA_LOCAL_STANDARD_TIME = timezone(timedelta(hours=-6), name="CST")
      WHY   NOAA LCD timestamps are local STANDARD time, no daylight saving
            (NOAA's documented convention)
      WATCH get this wrong and every summer reading shifts one hour, smearing
            rain onto dry events for half the study window. Silently.

L60   NUMBER_PATTERN = re.compile(r"[-+]?\d+(?:\.\d+)?")
      WHY   NOAA writes values like "0.05s" — a number plus a quality letter
```

## L66–79 — settings and folders

```
L66   load_config()   read config/texas_capmetro_801.json
      WHY   routes, direction codes, study window, NOAA stations and the 90-minute
            tolerance all live in the config. Change the config, not the scripts.
L76   ensure_dirs()   create the output folders
```

## L85–127 — fingerprints and safe writing

```
L85   sha256_file()   reads 1 MB at a time in a while loop
      WHY   a 3.7 GB file cannot be read into memory at once

L102  write_json()    write <name>.part, then rename
      WHY   sort_keys=True keeps output stable run-to-run (clean git diffs);
            the rename means an interrupted run never leaves a half-written
            audit file that looks valid
L111  write_text()    same pattern for markdown
L119  require_file()  a clear "Missing ... see Getting the data" message
                      instead of a stack trace
```

## L133–173 — `clean_masks()` ← **the most important function in the project**

The six cleaning rules, as four **cumulative** True/False columns ("masks").

```
L161-162 Rule 1     route_id is one of the study routes
L164-165 Rule 2     route_id == current_route_id
         WHY        drops records logged while a bus was being reassigned mid-trip
L167-168 Rules 3-4  import_error == "0" and import_trip_error == "0"
L170-171 Rules 5-6  bs_id != "0" (0 = unknown stop: garage, deadhead, logon)
                    and direction_code_id is a study direction
L173     return on_route, matching, error_free, clean
         WHY   each mask is a superset of the next, so these four ARE the bars
               of the cleaning funnel. Every step calls this one function, so the
               funnel and the study set cannot drift apart.
```

No rule looks at a passenger count, so no row is dropped for looking odd.

## L176–197 — `clean_where()`

The same rules as one SQL-style sentence. **Nothing executes it** — it exists so the
audit JSONs and the manuscript can quote the rule in one line. Do not delete it.

## L203–226 — reading messy NOAA values

```
L203  first_value(row, "DATE", "Date")   first non-empty among several spellings
L216  parse_flagged_number("0.05s")      -> 0.05 ; "" -> None
```

---

# `audit_route_selection.py` — why 801, and the funnel

**Not a pipeline step.** No code reads its output. It is kept runnable so the route
choice stays defensible rather than asserted.

## L45–67 — constants

```
L45   NEEDED_COLUMNS   19 of the 47 columns (reading fewer is about twice as fast)
L52   ROWS_PER_CHUNK = 1_000_000
L55   TABLE_ROWS       (label, statistic) pairs for the markdown table
```

## L73–107 — Part A: `read_and_count()`

```
L85-86 pd.read_csv(..., dtype=str, na_filter=False, chunksize=ROWS_PER_CHUNK)
      WHY   dtype=str        the source stores every column as text
      WHY   na_filter=False  keeps blanks as "" instead of NaN, so the text
                             comparisons in clean_masks behave predictably
      WATCH remove na_filter=False and the cleaning rules silently change meaning

L92   on_route, matching, error_free, clean = common.clean_masks(chunk, routes, ["4","6"])
L96-100 for each route: add (mask & is_this_route).sum() to each funnel level
L105  clean_rows = pd.concat(clean_pieces)   about 832,000 rows, fits in memory
```

## L113–170 — Part B: `route_statistics()`

```
L124  service_day = first 8 characters of transit_date_time (YYYYMMDD)
L126-130 trip_key = service day + ext_trip_id, or start time + vehicle when blank
      WHY   no single APC column is a reliable trip key
L133  usable_segment = rev_seconds > 0 AND rev_distance > 0
L136  good_gps = non-zero coordinates AND quality_indicator 3..6
L143  one pass per route (groupby), L148 one pass per direction inside it
```

## Numbers this file produces

| Number | Line | Appears in |
|---|---|---|
| 547,616 / 468,689 all-route records | L98 | Funnel slide |
| 524,728 / 445,369 matching | L99 | Funnel slide |
| 480,452 / 403,254 error-free | L100 | Funnel slide |
| 455,654 / 376,801 clean (both directions) | L157 | Funnel slide |
| 184 service days | L158 | Dataset slide |
| 810,309 boardings (route 801) | L160 | Route-selection slide |
| 11.414 mean max load | L162 | Audit JSON |
| 18.0 median dwell (s) | L163 | Audit JSON |
| 98.136% high-quality GPS | L166 | Dataset slide |
| 29 stops per direction | L149 | Corridor slides |
| 20.93% clean-event advantage over 803 | L213 | Route-selection slide |

---

# `01_extract_dir6.py` — the study set

## L46–108 — `extract_study_set()`

```
L48   require_file(RAW_FULL_SNAPSHOT)
L50   output path comes from the config, not hardcoded
L54   write to ".part" first — an interrupted run must not leave a truncated
      study set that looks complete. Everything downstream trusts this file.
L64-65 read in 1 M-row chunks, all 47 columns kept (no usecols)
L72   clean_masks(chunk, ["801"], ["6"]) — only `clean` is used
L78-82 first chunk: create the file with a header; later chunks: append, no header
      WATCH break this and you get a header row in the middle of the file
L86   rename .part -> final name
L88-107 the manifest: rows, bytes, SHA-256, the cleaning rule as text,
      direction_label deliberately null (see step 4)
```

| Number | Line | Appears in |
|---|---|---|
| 229,421 rows | L98 | The study set itself |
| 47 columns | L101 | Dataset slide |
| SHA-256 `8368412e…f7a23e21` | L100 | Provenance |

---

# `02_prepare_weather.py` — NOAA onto the bus clock

Deliberately a plain loop over rows, so each NOAA quirk gets its own commented lines.

## L63–208 — `clean_one_station()`, per row

```
L75-90  1. read the time
        L89-90 treat the NOAA time as UTC-06:00, then convert to UTC
        WHY    NOAA "15:00" in July is 16:00 on an Austin clock
        WATCH  the highest-consequence lines in the whole pipeline
L94-96  2. keep only 2021-07-01 .. 2021-12-31 (Austin date)
L98-115 3. read the measurements; skip admin rows with no measurement at all
L117-128 4. rain_flag = 1 if ANY of: amount > 0, trace "T", code has RA/DZ/TS
        WHY    deliberately inclusive — an EXPOSURE flag, not a rainfall amount
L147-157 5. two reports at the same instant -> keep the one with more fields filled
        WHY    merge_asof in step 3 must have no ties
L161    write rows sorted by time (step 3 relies on sorted input)
```

## L211–248 — `prepare_weather()`

```
L223  the saved raw file is named after the last part of the NOAA URL
      (the URL itself is not downloaded — no network in this folder)
```

| Number | Appears in |
|---|---|
| 6,484 Camp Mabry observations, 584 rain-flagged | Weather slide |
| 5,472 Bergstrom observations, 480 rain-flagged | Audit JSON |

---

# `03_join_weather.py` — was it raining?

## L52–80 — `load_bus_events()`

```
L61   read only apc_date_time, rev_seconds, rev_distance
L65   "20210701053012" -> timestamp, no time zone yet
L70-74 attach Austin time twice (first / second pass of the repeated
      7-Nov-2021 01:00 hour); where they differ, the time was ambiguous
      WHY   report the count instead of silently guessing (it is 0 for dir 6)
L76   convert to UTC — matching is done on unambiguous instants
```

## L83–93 and L96–116 — `load_weather()`, `match_nearest_reading()`

```
L92   sort by obs_time — merge_asof REQUIRES both sides sorted
L106-113 pd.merge_asof(..., direction="nearest", tolerance=90 min)
      WHAT  closest reading before OR after, within 90 minutes
      WATCH unmatched events get NaN — that is how coverage is measured
L115  minutes between event and reading
```

## L119–244 — `join_weather()`

```
L131-132 join Camp Mabry (primary), then Bergstrom (cross-check)
L141     median join gap
L143-145 p95 = sorted value at position ceil(0.95 n) - 1
         WATCH deliberately NOT pandas .quantile() (which interpolates)
L154     how often the two stations agree on rain
L171-182 dry vs rainy median segment time — DESCRIPTIVE ONLY
         WATCH Austin rain clusters in the afternoon rush, so part of the gap is
               traffic. The warning is written into the output JSON.
L191     feasible = coverage >= 95% and >= 1,000 rain-exposed rows
         WHY   rule declared BEFORE seeing the result
```

| Number | Line | Appears in |
|---|---|---|
| 100% join coverage | L186 | Weather slide |
| 11,804 rain-exposed events | L159 | Weather slide |
| 12.667 min median join gap | L141 | Weather slide |
| 27.933 min p95 | L145 | Defense material |
| 215,705 / 229,421 = 94.0% station agreement | L154 | Weather slide |
| 204 s dry vs 212 s rain | L176–180 | Weather slide |

---

# `04_gtfs_gate.py` — the direction-label gate

No data processing. Reads the `gtfs` block of the config and writes the JSON record
(L43–51) and the markdown page (L53–89).

---

# `run_all.py`

Runs steps 1–4 in order with `subprocess.run` (L48) and stops at the first failure
(L51–53). `STEPS` is at L31–36.

---

# Consolidated findings

| | Where | Status |
|---|---|---|
| GTFS gate wording ("not yet verified") contradicts what we now know: 2021 GTFS confirmed not publicly archived; direction 6 = southbound from the 2026 feed | config `gtfs` block → `04` output | Open — update the config, not the script |
| `alightings` in the route audit JSON is published but never read (the simulator reads `mean_alightings` from `starter/sim_inputs/stops.csv` instead) | `audit_route_selection.py:161` | Open — harmless |
| `clean_where()` has no callers **by design** | `common.py:176` | Not a defect. Do not delete |

## The traceability rule

Every number in the deck traces to a line in this document, and from there to a file
in `data/audit/texas_capmetro/`. If you need a figure, take it from the audit JSON or
regenerate it — never retype it from a slide.
