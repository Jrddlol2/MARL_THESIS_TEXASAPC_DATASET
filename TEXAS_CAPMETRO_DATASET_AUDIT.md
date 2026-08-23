# Texas CapMetro APC Dataset Audit and Paper Implementation Plan

> **Dataset identity:** Texas — Capital Metropolitan Transportation Authority (CapMetro), Austin, Texas, USA  
> **Primary candidate corridor:** CapMetro Rapid Route 801, direction code 6  
> **Secondary validation corridor:** CapMetro Rapid Route 803  
> **Working branch:** `dataset/texas-capmetro-801`  
> **Audit date:** 2026-08-23  
> **Status:** Preliminary feasibility audit. These are not final thesis results.

## 1. Decision

The Texas CapMetro Automatic Passenger Counter (APC) dataset is suitable as the
empirical foundation of the study if the paper is reframed around MARL bus
scheduling rather than around the EDSA Carousel specifically.

The defensible study design is:

> Texas CapMetro operational data + an Austin CapMetro Rapid corridor network +
> a calibrated simulation + MARL scheduling evaluation.

Do **not** combine Texas operating parameters with EDSA geometry and describe the
result as an EDSA-calibrated environment. If the Texas dataset replaces the
unavailable EDSA dataset, the empirical case-study corridor must also be labelled
as Texas/Austin/CapMetro throughout the title, objectives, methods, results,
figures, tables, filenames, and claims.

Recommended working title:

> **An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus
> Scheduling under Non-Ideal Conditions: A CapMetro Rapid Case Study**

## 2. Official Sources

- Texas APC dataset landing page:  
  https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9
- Public Socrata API endpoint:  
  https://data.texas.gov/resource/im6q-3pc9.json
- CapMetro Rapid service description:  
  https://www.capmetro.org/rapid
- CapMetro developer resources and terms:  
  https://www.capmetro.org/developertools
- NOAA Local Climatological Data:  
  https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data
- NOAA Austin Camp Mabry station (WBAN 13958):  
  https://www.ncei.noaa.gov/cdo-web/datasets/LCD/stations/WBAN%3A13958/detail

The portal describes the source as raw, unprocessed APC/AVL data and warns that
invalid records remain. Cleaning and validation are therefore mandatory.

## 3. Dataset Scope

- Published period: July 2021 through December 2021
- Dataset size: approximately 9.2 million rows
- Schema size: 47 text-typed fields
- Geographic scope: CapMetro network, Austin, Texas, USA
- Candidate mode: CapMetro Rapid, a high-frequency bus service
- Candidate routes found in the data: Rapid 801 and Rapid 803

All reported figures below were calculated through aggregate queries against the
public API. They are an exploratory audit snapshot and must be reproduced by the
final version-controlled processing pipeline before being cited as manuscript
results.

## 4. Route-Level Audit Results

| Metric | Rapid 801 | Rapid 803 |
|---|---:|---:|
| All scheduled-route records | 547,616 | 468,689 |
| Records where current route equals scheduled route | 524,728 | 445,369 |
| Records with `import_error = 0` and `import_trip_error = 0` | 480,452 | 403,254 |
| Error-free rate among matching-route records | 91.6% | 90.5% |
| Clean stop events in direction codes 4 and 6 | 455,654 | 376,801 |
| Service days represented | 184 | 184 |
| Distinct stops per direction | 29 | 28 |
| Distinct actual trip-start timestamps | 24,952 | 26,626 |
| Recorded boardings | 810,309 | 532,063 |
| Mean onboard load | 11.4 | 8.1 |
| Median dwell time | 18 seconds | 18 seconds |
| Usable positive-distance/positive-time segments | 441,779 | 361,852 |
| Approximate share with high-quality GPS/RSA position fixes | 98.1% | 97.5% |

Other routes such as 300, 7, 10, and 20 contain more stop-event records, but
they have much larger stop sets and represent conventional bus services. Rapid
801 offers the best balance of data density, passenger loading, operational
similarity to a controlled high-frequency corridor, and tractable simulation
scope.

## 5. Recommended Experimental Corridor

### Primary route

Use **Texas CapMetro Rapid Route 801**.

### Primary direction

Use **direction code 6**, subject to confirmation against the historical GTFS
or the CapMetro direction-code lookup table. Its northern terminal coordinates
suggest that this is the southbound direction.

Preliminary direction-code-6 profile:

| Metric | Route 801, direction 6 |
|---|---:|
| Clean stop events | 229,421 |
| Distinct actual trip-start timestamps | 12,503 |
| Recorded boardings | 420,201 |
| Recorded alightings | 370,261 |
| Mean onboard load | 11.6 |
| Median dwell time | 18 seconds |

### Preliminary headway diagnostic

At stop ID `5867`, using records between 05:00 and 23:00 and excluding gaps
longer than 60 minutes:

| Metric | Actual headways | Scheduled headways |
|---|---:|---:|
| Number of usable gaps | 10,422 | 10,488 |
| Mean headway | 16.9 minutes | 17.1 minutes |
| Median headway | 14.9 minutes | 15.0 minutes |
| Headway coefficient of variation | 0.650 | 0.552 |
| Gaps below 5 minutes | 10.4% | 0.0% |
| Gaps above 20 minutes | 29.3% | 16.2% |

This one-stop calculation is evidence that the corridor contains a meaningful
scheduling-regularity problem, but it is not a final research result. The final
analysis must stratify by time-of-day service regime so that scheduled peak and
off-peak frequency changes are not mistaken for bunching.

### Secondary route

Use **Texas CapMetro Rapid Route 803** as an optional holdout/generalization
corridor after developing and selecting the controller on Route 801. Do not use
Route 803 for model selection if it is intended to serve as an external test.

## 6. Variables Required for the MARL Study

### 6.1 Route, vehicle, trip, and stop identifiers

| Raw field | Required use |
|---|---|
| `route_id` | Scheduled route selection |
| `current_route_id` | Remove non-revenue and route-mismatch events |
| `direction_code_id` | Separate directional corridors |
| `variation` | Distinguish route patterns where needed |
| `vehicle_id` | Identify bus agents |
| `block_id` | Reconstruct scheduled vehicle work |
| `ext_trip_id` | Identify scheduled trips |
| `act_trip_start_time` | Identify actual trip executions |
| `actual_sequence` | Order events inside a trip |
| `bs_id` | Identify passenger stops |
| `transit_date_time` | Identify the service day |

### 6.2 Passenger demand and load

| Raw field | Required use |
|---|---|
| `ons` | Boarding demand per stop and time-of-day bin |
| `offs` | Alighting distribution and through-volume calculation |
| `max_load` | Onboard-passenger observation and load profile |
| `raw_on` | Audit the adjusted boarding value |
| `raw_off` | Audit the adjusted alighting value |
| `raw_max_load` | Audit the adjusted onboard-load value |

Use the adjusted `ons`, `offs`, and `max_load` fields for the operational model,
while retaining the raw versions for quality checks. Boarding counts are not the
same as passenger arrival timestamps. Waiting queues, denied boarding, and
individual passenger waiting times remain unobserved.

### 6.3 Timing and schedule adherence

| Raw field | Required use |
|---|---|
| `open_date_time` | Actual stop arrival/service timestamp |
| `close_date_time` | Actual stop departure timestamp |
| `dwell_time` | Observed door-open service interval |
| `sched_time` | Scheduled stop timestamp at timepoints |
| `start_trip_time` | Scheduled trip start |
| `act_trip_start_time` | Actual trip start |
| `seg_arr_time` | Scheduled segment arrival reference |
| `seg_dep_time` | Scheduled segment departure reference |
| `rev_seconds` | Revenue travel time to the next recorded location |
| `time_id` | Published time-period category |
| `day_type_vs` | Service-day/schedule category |

### 6.4 Location and movement

| Raw field | Required use |
|---|---|
| `veh_lat` | Stop-event coordinate and spatial quality check |
| `veh_long` | Stop-event coordinate and spatial quality check |
| `rev_distance` | Revenue distance to the next recorded location |
| `rev_seconds` | Revenue duration to the next recorded location |
| `position_source` | Position-source validity check |
| `quality_indicator` | Position-fix quality check |
| `num_sat` | Supporting GPS quality indicator |

The dataset supports event-level locations and inter-stop average speed, not a
continuous high-frequency GPS trajectory. The manuscript should therefore use
segment travel-time or segment-average-speed RMSE unless a separate continuous
AVL feed is acquired.

The units of `rev_distance` must be independently verified. The field description
references a reporting-unit setting that is not included in this 47-column
dataset.

### 6.5 Mandatory quality fields

- `import_error`
- `import_trip_error`
- `current_route_id`
- `bs_id`
- `position_source`
- `quality_indicator`
- `insert_date_time`

### 6.6 Optional or non-model fields

`operator_id`, `garage_id`, and `insert_date_time` should not enter the MARL
observation vector. Non-revenue distance and time may be retained for fleet-cycle
auditing but are not required for the first single-direction corridor model.

## 7. Derived Variables

The processing pipeline should derive:

1. Actual stop arrival and departure times.
2. Actual and scheduled headways by stop, direction, and time-of-day bin.
3. Schedule deviation by trip and stop.
4. Boarding and alighting rates by stop and time-of-day bin.
5. Onboard-load profile by trip segment.
6. Through-passenger volume at each candidate control stop.
7. Passenger-service dwell distributions excluding terminal layover.
8. Inter-stop travel-time distributions.
9. Segment-average speed after confirming distance units.
10. Hourly bus volumes for GEH validation.
11. Headway coefficient of variation within homogeneous schedule periods.
12. Candidate control-stop rankings using demand, through-volume, and headway
    irregularity.

## 8. Minimum Cleaning Protocol

### 8.1 Initial record filter

For the primary corridor, begin with:

```text
route_id = 801
current_route_id = route_id
direction_code_id = 6
import_error = 0
import_trip_error = 0
bs_id != 0
```

Do not treat this filter as sufficient by itself.

### 8.2 Type conversion

All 47 source fields are published as text. Parse timestamps using the source
format `yyyyMMddHHmmss`; parse counts, distances, durations, coordinates, and
quality codes to explicit numeric types. Preserve the original raw text in an
immutable raw-data layer.

### 8.3 Trip reconstruction

Build a trip-execution key from the service date, vehicle, actual trip-start
timestamp, and trip identifier. Confirm that:

- `actual_sequence` increases;
- stop order is operationally plausible;
- timestamps are nondecreasing;
- positive revenue segments have plausible time and distance;
- the directional stop pattern is consistent;
- duplicate door events are identified;
- incomplete trips are flagged rather than silently treated as complete.

### 8.4 Terminal and outlier treatment

The audit found median non-terminal dwell near 18 seconds, but maximum recorded
dwell exceeded seven hours. Candidate terminal stops showed median dwell of
roughly 11–17 minutes, indicating scheduled layover mixed into the same field.

Therefore:

- identify both terminal stop IDs from historical GTFS/stop metadata;
- separate terminal layover from passenger-service dwell;
- retain explicit flags for terminal, missing, implausible, and extreme events;
- use distribution-aware or domain-justified thresholds;
- report sensitivity to the cleaning thresholds;
- never delete extreme records solely because they are inconvenient, since some
  may represent genuine disruptions.

### 8.5 Calendar and time bins

Separate weekdays, Saturdays, Sundays, and holidays before selecting the final
scope. Within the chosen calendar, define homogeneous time-of-day service bins so
that peak/off-peak schedule changes do not inflate the headway CV.

### 8.6 Chronological calibration and validation

Use a chronological split rather than a random record split. Select the exact
date boundary only after checking booking changes, service changes, missing days,
and weather coverage. Avoid leakage by keeping complete service days on one side
of the split.

## 9. Weather Assessment

Weather is **not present** in the Texas APC dataset. There are no direct fields
for precipitation, temperature, humidity, wind, visibility, storm type, or a
weather-related delay cause.

Weather can be added through a timestamp join:

```text
APC open_date_time
    -> round or match to the applicable observation hour
NOAA Austin Camp Mabry hourly record
    -> precipitation
    -> present weather type
    -> visibility
    -> wind speed/gust
    -> temperature and humidity
```

Recommended empirical weather use:

1. Join cleaned segment events to NOAA hourly observations.
2. Define dry/wet and, if adequately represented, intensity categories using
   explicit meteorological variables rather than travel-time outliers.
3. Estimate segment travel-time effects while controlling for segment,
   time-of-day, service-day type, and scheduled frequency.
4. Use observed 2021 weather to calibrate ordinary rain-related effects.
5. Retain the synthetic heavy-tailed travel-time sweep for extreme stress tests
   if the six-month sample contains too few severe events.

Do not label an APC travel-time anomaly as weather-induced unless it has been
joined to an external weather observation or other documented event source.

## 10. Missing Inputs and Companion Data

The APC dataset does not directly provide:

- passenger arrival timestamps;
- passengers waiting before a bus arrives;
- denied boarding or passengers left behind;
- individual passenger waiting time;
- vehicle passenger capacity;
- explicit breakdown events or mechanical causes;
- continuous high-frequency GPS trajectories;
- weather observations;
- complete human-readable stop metadata and route geometry in this table;
- a confirmed reporting unit for `rev_distance`.

Acquire or construct the following companions:

1. Historical 2021 CapMetro GTFS corresponding to the APC booking periods.
2. Stop-ID/name/coordinate lookup compatible with `bs_id`.
3. Route shape and road network for the Texas Route 801 SUMO model.
4. Vehicle/fleet specifications for capacity.
5. NOAA Austin Camp Mabry hourly weather for July–December 2021.
6. Optional incident or maintenance records if an empirical breakdown rate is
   required; otherwise keep breakdowns explicitly synthetic.

## 11. Required Manuscript Reframing

When implementation is authorized, update the paper consistently:

1. Replace EDSA-specific wording in the title, problem, objectives, scope, and
   significance with Texas CapMetro Rapid case-study wording.
2. Preserve MARL bus scheduling under non-ideal conditions as the primary
   contribution.
3. Replace the EDSA network description and map with the selected Texas Route
   801 corridor and direction.
4. Replace SafeTravelPH/DOTr dataset placeholders with the verified Texas APC
   schema and companion-data plan.
5. Describe the public dataset as raw APC/AVL stop-event data requiring a
   documented cleaning pipeline.
6. Change speed-trajectory RMSE claims to segment travel-time or
   segment-average-speed RMSE unless continuous AVL data are added.
7. Derive GEH bus volumes by counting valid trip passages per segment and hour;
   do not describe operating speed as the source of bus-volume counts.
8. Make passenger waiting time explicitly simulation-derived, since the APC
   data do not observe individual passenger arrival times.
9. Keep weather and breakdown disturbances synthetic unless joined empirical
   sources are implemented and validated.
10. Add the pandemic-era July–December 2021 observation period as a limitation
    on contemporary demand generalization.
11. Label every new dataset, table, output folder, and figure with
    `Texas`, `Austin`, or `CapMetro` so that it cannot be confused with EDSA.

## 12. Proposed Output Labels

Use names such as:

```text
data/raw/texas_capmetro_apc_2021/
data/processed/texas_capmetro_route_801_direction_6/
configs/texas_capmetro_801/
outputs/texas_capmetro_801_calibration/
outputs/texas_capmetro_801_marl/
figures/texas_capmetro_801/
```

Do not commit the 9.2-million-row raw dataset unless repository policy explicitly
allows large data files. Prefer a reproducible download/query script, checksums,
and a data dictionary, with raw data ignored by Git.

## 13. Acceptance Gates Before Final Paper Claims

- [ ] Historical GTFS or compatible stop/route lookup acquired.
- [ ] Direction code 6 formally mapped to the human-readable direction.
- [ ] Route 801 terminal stops identified.
- [ ] `rev_distance` units verified.
- [ ] Error-code meanings documented.
- [ ] Trip reconstruction and completeness rates reported.
- [ ] Dwell and travel-time cleaning thresholds justified and sensitivity-tested.
- [ ] Calendar and time-of-day bins finalized.
- [ ] Chronological calibration/validation split frozen.
- [ ] NOAA weather join coverage audited if empirical weather is used.
- [ ] All exploratory audit numbers reproduced by version-controlled code.
- [ ] Manuscript compiled and visually inspected.
- [ ] Every empirical claim explicitly identifies Texas CapMetro as its source.

## 14. Claim Boundary

Until the acceptance gates are satisfied, the paper may state that the public
Texas CapMetro dataset has been selected and that its schema and preliminary
coverage have been audited. It must not claim that final calibration has been
completed, that the MARL controller has been trained, or that performance
improvements have been observed.
