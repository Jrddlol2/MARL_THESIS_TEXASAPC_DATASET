# Texas CapMetro data workspace

This repository commits the acquisition code, study configuration, compact
audit outputs, query definitions, and checksums. It intentionally does not
commit raw APC/NOAA downloads or processed model inputs.

## Reproduce the evidence package

From the repository root, run:

```powershell
python scripts/texas_capmetro_pipeline.py all
```

The command performs four gated steps:

1. downloads the official Socrata metadata and the clean Route 801/803 audit
   subset, then recomputes the route-selection metrics locally;
2. downloads the full clean Route 801 direction-code 6 APC subset;
3. downloads and normalizes NOAA LCDv2 observations for Camp Mabry and
   Austin-Bergstrom; and
4. measures the timestamp-join coverage without treating a descriptive
   wet/dry difference as a causal weather effect.

Generated locations:

- `data/raw/` - official downloads; ignored by Git;
- `data/processed/` - normalized weather and later calibration inputs; ignored;
- `data/audit/texas_capmetro/` - compact, reviewable evidence and manifests;
- `config/texas_capmetro_801.json` - frozen route, weather, timezone, and GTFS
  gates.

## Verified complete APC snapshot

The complete 47-column Socrata export is stored locally, outside Git, at
`data/raw/capmetro/APC_Raw_July_2021_December_2021_full.csv`. It contains
9,197,694 data rows covering APC timestamps `20210701000004` through
`20211230235955`. Its SHA-256 is
`4c2cb9c27355dd8fe1f94ae0d06bc12726c3860153b48ec7f6dad6b1142bc8f7`.

`data/audit/texas_capmetro/full_raw_manifest.json` records the source,
validation results, raw-file checksum, and separate compressed-backup checksum.
The full snapshot is an archival and reproducibility source; routine pipeline
work should continue to use filtered API queries and compact derived subsets
rather than loading all 9.2 million rows unnecessarily.

## Non-fabrication gates

- Direction code `6` remains a code, not “northbound” or “southbound,” until a
  2021-compatible GTFS snapshot is verified.
- The APC timestamp time basis is an explicit Austin-wall-clock assumption and
  is reported as such.
- NOAA LCDv2 timestamps are local standard time with no DST adjustment. The
  pipeline interprets them as UTC-06:00 and converts them to
  `America/Chicago` before matching APC events.
- Ordinary observed rain may be used for empirical baseline calibration only
  after coverage and sample-size checks pass. Severe/extreme weather remains a
  labeled synthetic stress test outside the observed range.
- Passenger waiting time, capacity, breakdown events, and continuous speed
  trajectories are not present in the APC file and are never claimed as
  measured variables.
- A current GTFS feed cannot be substituted for the required 2021 service
  snapshot.
