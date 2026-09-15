# Historical GTFS acquisition gate

Status: **closed 2026-09-12 - a 2021-compatible snapshot is not publicly archived.**

Required service window: `2021-07-01` through
`2021-12-31`.

The current official feed is publicly available at
`https://data.austintexas.gov/download/r4v4-vz24/application/zip`, but it is not valid evidence for a 2021 route
mapping. Candidate historical sources were Transitland Feed Archive and Mobility Database history (both exhausted).

## Retrieval attempts

- **Transitland Feed Archive API:** Public archive documentation verified; feed and feed-version API calls returned HTTP 401 without an account key.
- **Mobility Database mdb-150 history:** Official CapMetro feed and dataset-history page verified; the public page exposed 2026 history, while the history API requires a bearer token. No 2021 file was obtained.
- **Texas Open Data CapMetro GTFS asset r4v4-vz24:** Current official asset and revision sequence 38 verified. Specific revision and source endpoints returned HTTP 401, so no historical blob was obtained anonymously.
- **Internet Archive, Texas Open Data asset r4v4-vz24:** One capture (December 2024) and it returns HTTP 302 only; no 2021 blob.
- **Internet Archive, data.austintexas.gov mirror:** Four captures (2024-2025), all HTTP 302; no 2021 blob.
- **transitfeeds.com / OpenMobilityData:** Live site is behind Cloudflare; the Internet Archive holds only its 2013-10 to 2014-12 CapMetro versions.
- **Transitland v1 API:** Retired; no anonymous historical endpoint remains.
- **Mobility Database full catalog:** CapMetro is mdb-150 and its archive URL resolves to mdb-latest, i.e. the current feed only.

## Conclusion

A 2021-compatible GTFS snapshot is not publicly archived. The gate is closed as unavailable rather than pending, and the two parameters it blocked are sourced elsewhere.

## What the blocked parameters use instead

- **direction label:** Direction code 6 = southbound, corroborated by overlaying the 29 study stop IDs on the current published feed: 28 match the southbound pattern in identical order, median offset 8.5 m, and the three feed-only stops postdate 2021. Reported as corroboration from the current feed, not as a 2021 record.
- **scheduled headway:** 600 s on weekdays 07:00-18:00, from the archived Route 801 timetable captured 2021-07-20 (data/raw/capmetro/schedule_2021/801_20210720110345.pdf, SHA-256 8dfd88258b3b8f8288e5c23498b77bb69dabb6534c10facab1617c8f18307c5f); the same headways appear in the Nov-2020, Apr-2021, Nov-2021 and Aug-2022 captures.
- **route shape:** Taken from the OpenStreetMap route relation; the current feed's shape distance for 5280 to 5872 (27,918 m) agrees with the modelled arc length (27,599 m) to 1.2%.

## The standing rule

Do not present 2021 stop names or any schedule semantics beyond the archived timetable as 2021 records. The direction label and route shape are corroborated from present-day sources and must be described that way.

This is a source-availability limitation, not a failed weather/APC feasibility
check. The APC records themselves contain stop IDs and stop-event coordinates,
so segment-level empirical work proceeds on those records.
