# Historical GTFS acquisition gate

Status: **open - a 2021-compatible snapshot has not yet been checksum-verified.**

Required service window: `2021-07-01` through
`2021-12-31`.

The current official feed is publicly available at
`https://data.austintexas.gov/download/r4v4-vz24/application/zip`, but it is not valid evidence for a 2021 route
mapping. Candidate historical sources are Transitland Feed Archive or Mobility Database history.

## Retrieval attempts

- **Transitland Feed Archive API:** Public archive documentation verified; feed and feed-version API calls returned HTTP 401 without an account key.
- **Mobility Database mdb-150 history:** Official CapMetro feed and dataset-history page verified; the public page exposed 2026 history, while the history API requires a bearer token. No 2021 file was obtained.
- **Texas Open Data CapMetro GTFS asset r4v4-vz24:** Current official asset and revision sequence 38 verified. Specific revision and source endpoints returned HTTP 401, so no historical blob was obtained anonymously.

Until the gate closes, the manuscript and code must:

- refer to APC direction `6` by code only;
- avoid assigning northbound/southbound labels from the current schedule;
- avoid claiming historical stop names, route shapes, or scheduled headways; and
- keep schedule-derived parameters as `%TODO-DATA`.

This is a source-availability limitation, not a failed weather/APC feasibility
check. The APC records themselves contain stop IDs and stop-event coordinates,
so segment-level empirical work can proceed while authoritative 2021 schedule
semantics remain gated.
