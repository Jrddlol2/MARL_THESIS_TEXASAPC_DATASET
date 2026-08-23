# CapMetro APC field-use and limitation map

This map is derived from the official Socrata metadata saved as
`socrata_metadata.json`. The portal types all 47 columns as text, so the
pipeline parses numeric and timestamp fields explicitly.

| Official field | Verified meaning | Intended use | Gate or limitation |
|---|---|---|---|
| `route_id`, `current_route_id` | Static route and route active for the event | Keep records where both equal `801` | Prevents route-transition/error records from entering the case subset |
| `direction_code_id` | Software key for route direction/path | Select code `6` for the primary one-direction experiment | Code is not labeled north/south without 2021 GTFS/direction-code metadata |
| `transit_date_time` | Service day; early-morning events may belong to the prior day | Day grouping and chronological split | Not the event timestamp |
| `apc_date_time` | Vehicle logger system timestamp | Event ordering and NOAA nearest-time join | Austin wall-clock interpretation is explicit but not confirmed by a timezone field |
| `act_trip_start_time`, `ext_trip_id`, `vehicle_id` | Actual start, customer trip key, and vehicle key | Construct trip-day identities and chronological sequences | No single field is assumed globally unique |
| `actual_sequence` | Observed door/logon/trip event order | Stable within-trip ordering and integrity checks | It is not scheduled stop sequence |
| `bs_id` | Stop identifier | Segment and stop-level grouping | `0` is excluded; stop name requires 2021 stop metadata/GTFS |
| `ons`, `offs` | Load-balanced boardings/alightings | Stop/time demand profile | Counts are events, not passenger arrival timestamps |
| `max_load` | Load-balanced onboard count after the stop event | Load state and capacity diagnostics | Vehicle capacity is absent and must come from fleet specifications |
| `dwell_time` | Seconds from earliest door open to latest door close | Empirical dwell distributions | Controller holding time is not included and must be simulated separately |
| `rev_seconds` | Revenue travel seconds to the next logged location | Segment travel-time distributions and RMSE calibration | Only positive values paired with positive distance are used |
| `rev_distance` | Revenue distance to the next logged location | Segment filtering and average-speed derivation | Metadata says miles or kilometres depend on an external odometer-units setting; units remain `%TODO-DATA` |
| `veh_lat`, `veh_long`, `quality_indicator` | Event coordinates and GPS-fix quality code | Stop-event trace and coordinate QA | These are event-level points, not continuous trajectories |
| `day_type_vs` | Day/schedule key | Candidate weekday/day-type control | Human-readable schedule meaning needs the external day-type table |
| `import_error`, `import_trip_error` | Event/trip import error keys | Both must equal `0` | Error-code labels require the external APC error table |

## Variables not present

The raw APC file does not contain passenger arrival timestamps, waiting time,
vehicle capacity, breakdown events, weather, incident severity, continuous GPS
trajectories, authoritative compass-direction labels, stop names, or a complete
historical schedule. These variables are respectively simulated, joined from a
verified public source, obtained from a separate authoritative source, or kept
as `%TODO-DATA`; they are not inferred silently.
