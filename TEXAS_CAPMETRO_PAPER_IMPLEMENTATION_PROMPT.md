# Copy-Ready Prompt — Implement the Texas CapMetro Dataset in the Paper

Copy everything inside the following block into a new Codex task or another
careful implementation session.

```text
You are working on the MARL bus-scheduling thesis repository.

Branch and identity constraints
-------------------------------
1. Work only on the branch `dataset/texas-capmetro-801`. Verify the current
   branch before editing.
2. The replacement dataset and empirical case study are TEXAS data:
   Capital Metropolitan Transportation Authority (CapMetro), Austin, Texas,
   USA, APC Raw July 2021–December 2021.
3. Label all new data paths, configurations, manuscript descriptions, tables,
   figures, and outputs with `Texas`, `Austin`, or `CapMetro`. Never present the
   Texas data as EDSA data.
4. The main scientific contribution is MARL for dynamic bus scheduling under
   non-ideal conditions. The corridor is the empirical case study, not the
   contribution itself.
5. Use Texas CapMetro Rapid Route 801 as the primary corridor. Use direction
   code 6 as the provisional primary direction, but do not call it southbound
   in the final paper until historical GTFS or the direction-code lookup
   formally confirms the mapping.
6. Treat Texas CapMetro Rapid Route 803 as an optional holdout/generalization
   corridor. Do not use it for model selection if it will be reported as an
   external test.

Read before acting
------------------
Read these repository files completely before making changes:

- `CLAUDE.md`
- `README.md`
- `PROGRESS.md`
- `REVISION_QUEUE.md`
- `TRACKER.md`
- `TEXAS_CAPMETRO_DATASET_AUDIT.md`
- `main.tex` and all included chapter `.tex` files
- `thesis_refs.bib`

Treat `TEXAS_CAPMETRO_DATASET_AUDIT.md` as the decision record and preliminary
data audit. Do not blindly copy its exploratory figures into the manuscript as
final results. Reproduce all statistics with version-controlled code first.

Official sources
----------------
- Texas APC dataset:
  https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9
- Socrata API:
  https://data.texas.gov/resource/im6q-3pc9.json
- CapMetro Rapid:
  https://www.capmetro.org/rapid
- CapMetro developer tools and terms:
  https://www.capmetro.org/developertools
- NOAA Local Climatological Data:
  https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data
- NOAA Austin Camp Mabry, WBAN 13958:
  https://www.ncei.noaa.gov/cdo-web/datasets/LCD/stations/WBAN%3A13958/detail

Objective
---------
Revise the proposal manuscript and implementation plan so that the empirical
case study is Texas CapMetro Rapid Route 801 rather than the EDSA Carousel,
while preserving the thesis's central MARL scheduling architecture,
non-ideal-condition stress tests, baseline-controller comparisons, and outcome
metrics.

Use this working title unless a repository instruction or supervisor decision
requires another:

"An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus Scheduling
under Non-Ideal Conditions: A CapMetro Rapid Case Study"

Non-negotiable scientific boundaries
------------------------------------
1. Do not fabricate calibration values, cleaned-data statistics, MARL results,
   hyperparameters, or performance improvements.
2. Use `%TODO-DATA` and `%TODO-VAL` for quantities not yet reproduced and
   validated.
3. State that the portal publishes raw APC/AVL data and warns that invalid
   records remain.
4. Passenger waiting time is a simulation output. The APC dataset records
   boardings, not individual passenger arrival times or passengers left behind.
5. The data support event-level locations and inter-stop average speed, not a
   continuous GPS speed trajectory. Use segment travel-time or
   segment-average-speed RMSE unless a separate continuous AVL source is added.
6. Weather is not included in the 47 APC fields. Do not call a travel-time
   outlier weather-induced without an external timestamped weather join.
7. Breakdown events are not present. Keep the breakdown generator explicitly
   synthetic unless a verified incident/maintenance source is added.
8. Historical July–December 2021 demand may reflect pandemic-era travel and
   must be identified as a limitation.
9. Do not mix Texas calibration data with EDSA geometry while calling the model
   empirically calibrated. Replace the case-study corridor consistently.

Required dataset implementation
-------------------------------
Create a reproducible, clearly Texas-labelled data pipeline. Do not commit the
full raw 9.2-million-row dataset unless repository policy explicitly allows it.
Prefer an API download/query script, checksums, a data dictionary, and Git-ignore
rules for raw data.

Use paths such as:

- `data/raw/texas_capmetro_apc_2021/`
- `data/processed/texas_capmetro_route_801_direction_6/`
- `configs/texas_capmetro_801/`
- `outputs/texas_capmetro_801_calibration/`
- `outputs/texas_capmetro_801_marl/`

Begin the primary extraction with:

- `route_id = 801`
- `current_route_id = route_id`
- `direction_code_id = 6`
- `import_error = 0`
- `import_trip_error = 0`
- `bs_id != 0`

Then implement and document additional checks:

- parse `yyyyMMddHHmmss` timestamps;
- reconstruct trip executions from service date, vehicle, actual trip start,
  and trip identifier;
- check monotonic sequence and timestamps;
- identify duplicates and incomplete trips;
- identify terminal stops from historical GTFS or compatible stop metadata;
- separate terminal layover from passenger-service dwell;
- verify `rev_distance` units;
- retain explicit quality and outlier flags;
- define calendar and homogeneous time-of-day bins;
- use a chronological calibration/validation split without service-day leakage;
- record row counts after every cleaning stage.

Required variables and derivations
----------------------------------
Use these source-field groups:

Identifiers:
`route_id`, `current_route_id`, `direction_code_id`, `variation`, `vehicle_id`,
`block_id`, `ext_trip_id`, `act_trip_start_time`, `actual_sequence`, `bs_id`,
`transit_date_time`.

Demand and load:
`ons`, `offs`, `max_load`, plus `raw_on`, `raw_off`, and `raw_max_load` for
auditing.

Timing and scheduling:
`open_date_time`, `close_date_time`, `dwell_time`, `sched_time`,
`start_trip_time`, `act_trip_start_time`, `seg_arr_time`, `seg_dep_time`,
`rev_seconds`, `time_id`, and `day_type_vs`.

Location and quality:
`veh_lat`, `veh_long`, `rev_distance`, `position_source`,
`quality_indicator`, `num_sat`, `import_error`, and `import_trip_error`.

Derive:

- actual and scheduled headways by stop and time bin;
- schedule deviation;
- per-stop/time-bin boarding and alighting profiles;
- onboard-load and through-passenger profiles;
- non-terminal passenger-service dwell distributions;
- inter-stop travel-time and average-speed distributions;
- hourly bus volumes for GEH validation;
- within-service-bin headway CV;
- data-driven candidate control-stop rankings.

Weather implementation
----------------------
Weather is absent from the APC data. If implementing empirical weather:

1. Acquire NOAA Austin Camp Mabry hourly observations for July–December 2021.
2. Join each cleaned APC segment/stop event to the applicable observation hour.
3. Retain precipitation, present weather type, visibility, wind, temperature,
   and humidity where available.
4. Define wet/dry or intensity categories from meteorological variables.
5. Estimate travel-time effects while controlling for route segment,
   time-of-day, service-day type, and scheduled frequency.
6. Use observed data for ordinary rain effects and retain the synthetic
   heavy-tailed sweep for extreme stress tests if severe events are sparse.
7. Report weather-data gaps and join coverage.

Required manuscript changes
---------------------------
Review every occurrence of `EDSA`, `Carousel`, `SafeTravelPH`, `DOTr`, `MMDA`,
`Metro Manila`, `Philippines`, and corridor-specific claims. Do not perform a
blind replacement; classify each occurrence as background, obsolete case-study
content, method content, or literature context.

Update consistently:

1. Title and abstract/summary, if present.
2. Introduction and practical motivation.
3. Problem statement, research gap, objectives, significance, scope,
   delimitations, and limitations.
4. Simulation corridor description, map, stop count, direction, fleet, and
   schedule assumptions.
5. Required-dataset description and raw-field mapping.
6. Data cleaning and chronological validation protocol.
7. SUMO calibration procedure.
8. Stochastic demand, traffic, weather, and breakdown generators.
9. State/observation source table.
10. Evaluation metrics and claim boundaries.
11. Discussion and future-work framing.
12. Bibliography and source notes.

Preserve Philippine/EDSA literature only when it remains genuinely relevant as
general background or a comparative example. It must not remain the stated
empirical calibration source or practical deployment claim.

Calibration corrections
-----------------------
- Compute observed hourly bus volumes by counting valid trip passages; do not
  map operating speed itself to GEH volume calibration.
- Use segment travel-time or segment-average-speed RMSE.
- Stratify headway calculations by homogeneous scheduled-service periods.
- Exclude or separately model terminal layover when estimating passenger dwell.
- Do not use the preliminary one-stop headway audit as a final outcome.

Companion data gates
--------------------
Before replacing placeholders with final values, verify:

- historical 2021 CapMetro GTFS or compatible stop/route lookup;
- direction-code mapping;
- Route 801 terminal stop IDs;
- stop names, coordinates, and route shape;
- distance units;
- vehicle capacity;
- error-code meanings;
- NOAA weather coverage if empirical weather is used.

Verification and handoff
------------------------
1. Preserve unrelated user changes.
2. Compile the LaTeX manuscript and visually inspect the PDF if a TeX runtime
   is available; otherwise report that limitation clearly.
3. Search the final manuscript for stale EDSA-specific empirical claims and
   inconsistent Texas labels.
4. Update `PROGRESS.md`, `REVISION_QUEUE.md`, `TRACKER.md`, and the audit trail
   accurately. Do not mark dataset-dependent tasks complete until the verified
   schema, cleaning pipeline, and companion data support the new prose.
5. Show the exact files changed and summarize all unresolved `%TODO-DATA` and
   `%TODO-VAL` items.
6. Do not push, merge, or delete branches unless explicitly requested.

At completion, report:

- the verified current branch;
- files changed;
- dataset and companion sources used;
- reproduced route-quality statistics;
- cleaning-stage counts;
- unresolved data gaps;
- manuscript compilation/visual-QA status;
- confirmation that every empirical case-study claim is labelled Texas
  CapMetro rather than EDSA.
```
