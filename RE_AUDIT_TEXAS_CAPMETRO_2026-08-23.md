# Texas CapMetro Revision Re-Audit and Team Catch-Up Report

**Date:** 2026-08-23

**Branch:** `dataset/texas-capmetro-801`

**Protected branch:** `main` at `a64f44c` — untouched

**Decision audited:** Full thesis case-study pivot to CapMetro Rapid Route 801,
direction code 6

## Executive Conclusion

The approved Texas pivot is feasible as a **public-data-supported proposal and
simulation design**, and the revisions do not fabricate SUMO, weather-causality,
or MARL results. The RTC proposal-text audit is now closed: all 22 RTC items and
both self-identified notices are resolved.

The close-out does not fabricate implementation maturity. Historical 2021
GTFS/fleet evidence, several numeric design targets, calibration, experiments,
and results remain open implementation gates. The manuscript presents these as
sources, declared scenario choices, or placeholders rather than silently filling
them with unsupported values.

## What Changed

### 1. The case study was changed, not merely relabeled

The title and active Chapters 1–3 now describe CapMetro Rapid Route 801. The
active empirical background, dataset description, calibration plan, scope,
limitations, and disturbance design were revised together. Superseded EDSA-only
background is retained inside an inactive LaTeX block for source history and
does not compile into the manuscript.

The paper does not call the Texas data EDSA data, does not claim to validate the
EDSA corridor, and does not transfer Texas outcomes to Manila.

### 2. Route 801 was selected using a reproducible coverage rule

Routes 801 and 803 were compared with the same filters:

- reported route equals current route;
- both import-error fields equal zero;
- stop ID is nonzero; and
- direction code is 4 or 6.

| Reproduced measure | Route 801 | Route 803 | Route 801 difference |
|---|---:|---:|---:|
| Clean stop events | 455,654 | 376,801 | +20.93% |
| Recorded boardings | 810,309 | 532,063 | +52.30% |
| Positive-time/positive-distance segments | 441,779 | 361,852 | +22.09% |
| Distinct trip-day pairs | 24,943 | 26,609 | fewer on Route 801 |
| High-quality GPS share | 98.136% | 97.479% | comparable |

Route 801 is therefore justified by its denser event, boarding, and usable
segment evidence—not because it wins every metric and not because it is claimed
to provide better service. Direction code 6 was chosen within Route 801 because
it has 229,421 clean events and 420,201 boardings, compared with 226,233 and
390,108 for code 4. It remains a numeric direction code until a 2021 source
authoritatively supplies the human-readable label.

### 3. The source and primary subset are auditable

The source is the Texas Open Data dataset **APC Raw July 2021–December 2021**,
Socrata ID `im6q-3pc9`, with 47 source fields. The selected primary CSV contains:

- 229,421 clean stop-event rows;
- 184 service-day codes;
- 29 distinct stop IDs;
- 420,201 recorded boardings; and
- raw-file SHA-256
  `8368412e47df32ff8a3c2837048797664315c0e7ae51c44676766b5af7f23e21`.

Raw data remain local and ignored by Git. The repository contains the query,
filters, checksums, compact JSON/Markdown evidence, and a rerunnable pipeline.

### 4. Weather is feasible, with explicit limits

NOAA LCDv2 data from Camp Mabry (`USW00013958`) are the primary weather source;
Austin-Bergstrom (`USW00013904`) is the sensitivity station. With a nearest
observation join within 90 minutes:

- both stations match 100% of 229,421 APC rows;
- Camp Mabry marks 11,804 rows as rain-exposed;
- the median absolute join delta is 12.667 minutes; and
- the 95th-percentile absolute delta is 27.933 minutes.

This is feasible for analyzing observed ordinary rain, but it is not permission
to invent a causal multiplier. The unadjusted positive-segment median is 204
seconds in dry rows and 212 seconds in rain rows; that difference is explicitly
labeled descriptive. Any empirical multiplier must be estimated within segment,
time-of-day, and day-type controls.

The APC timestamp is treated as Austin wall-clock time because the source does
not yet confirm its time basis. That assumption is written into the audit. NOAA
local-standard timestamps are converted from fixed UTC−06:00 to
`America/Chicago`; no selected APC event occurs in the ambiguous fall-back hour.

Observed ordinary weather and synthetic severe weather now have different
roles. Ordinary rain can inform the empirical baseline after adjusted modeling.
Severe/extreme weather beyond observed support is a labeled synthetic stress
test and cannot be described as observed CapMetro behavior.

### 5. Internal contradictions were corrected

The manuscript now uses one authoritative activation matrix:

| Phase | D | T | S | W | B |
|---|---|---|---|---|---|
| Training | active | active | randomized | randomized | randomized |
| Stage A | active | active | inactive | inactive | inactive |
| Stage B | active | active | active | active | active |
| One-factor ablations | active | active | one at a time | one at a time | one at a time |

The CTDE description is also consistent: local observations, per-agent rewards,
and local transitions feed a shared replay buffer and shared DDQN learner. The
paper no longer simultaneously claims a team reward and a joint-state actor.

The weather layer now composes with the calibrated travel-time baseline rather
than replacing it. Its synthetic lognormal factor is unit-mean, and standard
deviations are no longer confused with clipping bounds. Continuous-speed claims
were removed because the APC source supports stop-to-stop travel time more
directly than a continuous vehicle trajectory.

## Audit Scorecard

| Category | Before Texas implementation | Current result |
|---|---:|---:|
| RTC done | 13 | 22 |
| RTC in progress | 6 | 0 |
| RTC pending | 3 | 0 |
| Self notices done | 1 | 2 |
| Self notices open | 1 | 0 |

The following RTC items were newly closed by the implementation:

- E1C1 — dataset setup discussion;
- E2C5 — dataset contents description;
- E3C8 — disturbance definitions/activation consistency;
- E3C12 — CTDE/reward consistency;
- E4C20 — reproducible disturbance sampling structure;
- E4C22 — dataset fields and limitations; and
- N1 — reward mechanics versus CTDE narrative.

## Final RTC Close-Out

| Item | Resolution |
|---|---|
| E2C4 | Removed the unsubstantiated Verbich record and replaced it with content-verified Sun et al. (2025) as W-only rainfall evidence; the paper explicitly labels it prediction, not control. |
| E3C10 | Corrected Shi et al. to D,T and added two separated adjacent B studies: Cao et al. (MARL train rescheduling) and Guedes and Borenstein (heuristic bus/public-transit failure rescheduling). Neither is misrepresented as prior MARL bus control. |
| E3C15 | Retained the required fixed/swept/derived parameter table and explicit `%TODO-VAL`/`%TODO-DATA` tags. The breakdown rate is correctly identified as a declared synthetic scenario input because APC has no failure events. |

Historical 2021 GTFS is also an implementation dependency. The current official
feed is not valid for the 2021 APC period; unauthenticated attempts through the
checked public archives did not produce a verified contemporaneous feed. The
paper therefore does not invent stop names, shapes, scheduled headways, or a
human-readable direction label.

## What This Branch Does Not Claim

- No SUMO network has been calibrated or validated yet.
- No NC, FH, EH, SARL, or MARL experiment has been run.
- No controller has been shown to outperform another.
- No causal rain effect has been estimated.
- No severe-weather observation is represented by the synthetic stress layer.
- No vehicle capacity, fleet size, historical headway, or direction label has
  been guessed.
- No Texas result is represented as evidence about EDSA.

## Validation Performed

- Re-ran the Route 801/803 audit from the downloaded public APC data.
- Re-ran the weather join and stored compact evidence and checksums.
- Verified Python syntax.
- Verified no duplicate bibliography keys and no missing active citation keys.
- Verified active LaTeX labels/references and named environments statically.
- Removed an incomplete `\includeonly[` command from the preamble; active
  chapters are loaded through `\input`.
- Verified Git's whitespace/error check.
- Verified the branch is `dataset/texas-capmetro-801` and `main` remains at
  `a64f44c`.

A full LaTeX compile and visual page inspection could not be performed locally
because no TeX engine is installed. The Git checkout also lacks nine active
graphic assets: two title-page logos and seven manuscript diagrams. The existing
tracker records that the original assets are maintained in the Overleaf
`Figures` folder. Synchronize those assets and compile in Overleaf before a new
manuscript PDF is circulated; this branch alone is not currently a self-contained
LaTeX build.

## Files Members Should Read First

1. `PROGRESS.md` — current status and next order.
2. `data/audit/texas_capmetro/ROUTE_SELECTION_EVIDENCE.md` — route evidence.
3. `data/audit/texas_capmetro/WEATHER_FEASIBILITY_EVIDENCE.md` — weather evidence.
4. `data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md` — unresolved GTFS gate.
5. `REVISION_QUEUE.md` — examiner-by-examiner status.
6. `TRACKER.md` — chronological decisions and implementation record.
7. `introduction.tex`, `problem.tex`, and `methods.tex` — revised paper source.

## Backup and Branch Safety

The baseline and pre-manuscript checkpoints are stored outside the repository
under `C:\Users\jared\Desktop\THESIS\Backups\MARL\Texas_CapMetro`. A final
post-commit/pre-push checkpoint will be added before publication. No checkpoint
has been overwritten, no merge or pull request has been created, and `main` is
outside the scope of this implementation.

## Re-Audit Verdict

**All RTC proposal-text feedback is addressed; implementation remains
conditional.** The dataset-dependent revision, route choice, weather
feasibility, literature classifications, parameter summary, and major internal-
consistency findings are addressed with reproducible or source-verified
evidence. The branch is not empirically validated until historical operations
inputs are sourced, justified placeholders are replaced, SUMO calibration and
controller experiments are actually run, and the manuscript compiles cleanly in
Overleaf with the complete graphics set.
