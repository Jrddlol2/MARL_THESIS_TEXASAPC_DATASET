# Reproduced Route 801 selection audit

Generated from the official Socrata API at `2026-08-23T13:17:49.331805+00:00`.

| Metric | Route 801 | Route 803 |
|---|---:|---:|
| All route records | 547,616 | 468,689 |
| Matching current-route records | 524,728 | 445,369 |
| Error-free matching-route records | 480,452 | 403,254 |
| Clean stop events (directions 4 and 6) | 455,654 | 376,801 |
| Service-day codes | 184 | 184 |
| Distinct trip-day pairs | 24,943 | 26,609 |
| Boardings | 810,309 | 532,063 |
| Mean reported max load | 11.414 | 8.088 |
| Median dwell (s) | 18.0 | 18.0 |
| Positive time-and-distance segments | 441,779 | 361,852 |
| High-quality GPS (%) | 98.136 | 97.479 |

## Decision

Under identical cleaning rules, Route 801 provides larger clean stop-event, boarding, and usable-segment samples despite fewer distinct trip-day pairs, while retaining comparable GPS quality.

Route 801 has 20.93% more clean stop events, 52.3% more recorded boardings, and 22.09% more usable positive-time/distance segments than Route 803.
This justifies Route 801 as the primary case by data coverage, not by a claim about service quality.

Direction code 6 remains provisional code-only. A compass-direction name is blocked until a checksum-verified 2021 GTFS snapshot is obtained.
