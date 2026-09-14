# Change Report: Khalil MARL Baseline, RTC Revisions, and Texas CapMetro Branch

**Prepared:** 2026-08-23

**Original repository:** [khalil-badal/MARL](https://github.com/khalil-badal/MARL)

**Original baseline:** main at commit **a64f44c**

**Working branch:** **dataset/texas-capmetro-801**

**Compared Texas revision:** commit **a572672**

**Texas publication repository:** [Jrddlol2/MARL_THESIS_TEXASAPC_DATASET](https://github.com/Jrddlol2/MARL_THESIS_TEXASAPC_DATASET)

**Protected branch:** Khalil main remains at **a64f44c** and was not edited, merged, or replaced

## Purpose of This Report

This is the catch-up document for members who know the original Khalil MARL
repository but have not followed the later audit, RTC close-out, Texas dataset
pivot, and figure restoration.

The comparison boundary is exact:

- **Before:** khalil-badal/MARL, main, commit a64f44c.
- **After:** dataset/texas-capmetro-801, commit a572672.
- **Difference at that boundary:** 44 changed files, 7,951 added lines, and 229
  deleted lines, including binary figure and logo additions.

The line count is large mainly because the branch adds a reproducible data
pipeline, downloaded-source metadata, audit evidence, and tracking documents.
It does not mean that thousands of lines of thesis claims were added.

## Executive Summary

The current branch is not a cosmetic rename of EDSA to Texas. It changes the
active case study to CapMetro Rapid Route 801 in Austin and updates the title,
Chapters 1–3, empirical sources, route-selection logic, calibration plan,
disturbance design, figures, and limitations together.

The branch also closes the **22 written RTC proposal-text comments** and the two
separate team-identified consistency notices. “Closed” here means that the
requested explanation, table, definition, formatting, citation correction, or
methodological boundary is now present in the manuscript source. It does
**not** mean that SUMO calibration, MARL training, controller comparisons, or
results have already been completed.

The most important integrity rule throughout the revision was:

> When the public data or verified literature do not support a value or claim,
> the manuscript states the limitation, retains a TODO-DATA/TODO-VAL marker, or
> labels the component as a synthetic scenario input. It does not invent the
> missing fact.

## 1. What Changed at Repository Level

| Area | Change from Khalil main | Reason |
|---|---|---|
| Branch safety | All work was kept on dataset/texas-capmetro-801 | The user explicitly required main to remain untouched |
| Manuscript title and case study | EDSA-centered active text was replaced by a CapMetro Rapid Route 801 case study | The original EDSA operational dataset was still unavailable; a public-data-supported backup was approved |
| RTC governance | A formal audit report, progress file, revised queue, trackers, and readable audit trails were added or updated | Members need an auditable link from each panel comment to the implemented source change |
| Public-data workflow | Added a CapMetro APC and NOAA acquisition/audit pipeline, configuration, field maps, queries, checksums, and compact evidence | Dataset claims must be reproducible and independently checkable |
| Raw data handling | Raw, cached, processed, and output folders are ignored by Git | Large data remain local while scripts, checksums, and evidence remain version-controlled |
| Manuscript assets | Added both title logos and all active figures; adapted five diagrams that contradicted the Texas methods | The earlier Texas repository was incomplete in Overleaf and several old diagram labels were methodologically wrong |
| Binary safety | Added .gitattributes rules for PDF, PNG, JPG, and JPEG files | Prevent Windows line-ending conversion from damaging manuscript assets |
| Validation | Added static checks and recorded route/weather reproduction results | A revision is not considered auditable merely because the prose sounds plausible |

### Commit sequence after Khalil main

| Commit | Purpose |
|---|---|
| **7680bd0** | Added the repository/manuscript audit and refreshed revision progress |
| **1f843c3** | Finalized audit validation metadata |
| **da55c5a** | Recorded the initial GitHub publication blocker |
| **39d7bc6** | Recorded publication of the audit branch |
| **f18c6bf** | Added the Texas CapMetro dataset handoff and implementation plan |
| **5722aad** | Implemented the CapMetro Route 801 case study and reproducible public-data pipeline |
| **c356187** | Recorded backup and Texas publication-target details |
| **dfca22e** | Resolved the remaining RTC manuscript and citation findings |
| **a572672** | Restored the V3 figures/logos and adapted conflicting diagrams |

## 2. RTC Changes and Why They Were Made

The source of truth for the panel wording remains
[RTC_DECISION_LETTER.md](RTC_DECISION_LETTER.md). The status record is
[REVISION_QUEUE.md](REVISION_QUEUE.md).

### Examiner 1

| RTC item | What changed | Justification and evidence boundary |
|---|---|---|
| **E1C1 — Dataset setup discussion** | Methods now identifies the official CapMetro APC source, collection period, 47-field schema, selected Route 801 subset, cleaning rules, field uses, limitations, and calibration role | This replaces vague SafeTravelPH placeholders with a dataset that was actually acquired and audited. No unavailable EDSA value is presented as known |
| **E1C2 — Dataset-to-features mapping** | Added a table mapping raw APC or companion fields to derived quantities and MARL/simulation uses | Readers can now trace each state, baseline, or validation quantity to a source instead of assuming every feature is directly observed |
| **E1C3 — Weather derivation in the research gap** | The research gap now links operational weather relevance, missing W coverage in prior MARL bus studies, observed NOAA joins, and the separate synthetic stress formulation | This explains why W exists in the experiment while preventing ordinary observed rain and synthetic severe weather from being conflated |

### Examiner 2

| RTC item | What changed | Justification and evidence boundary |
|---|---|---|
| **E2C4 — Severe-weather comparison study** | The unsubstantiated Verbich and El-Geneidy entry was removed. A content-verified Sun et al. 2025 rainfall/dwell-time study was added and labeled W-only, prediction rather than control | Exact-title, author, journal, volume, and page checks did not substantiate the old record. Keeping it would risk citation fabrication. Sun et al. supports weather relevance but is not misrepresented as MARL or breakdown control |
| **E2C5 — Dataset contents description** | Consolidated with E1C1 and E4C22 into one dataset section instead of duplicating three similar panel requests | One authoritative description reduces contradictions and lists both available and absent variables |
| **E2C6 — Traditional methods under disturbance** | Added discussion of why static scheduling, No Control, Forward Headway, and Even Headway can degrade or lack recovery under bunching and disruptions | The comparison now explains expected method behavior, rather than merely listing controller names |
| **E2C7 — Explicit success criteria** | Stage A and Stage B acceptance language was made visually explicit without adding unsupported numeric thresholds | The panel asked for clear criteria, but actual effect sizes and acceptance values must come from the later experiment |

### Examiner 3 — Related Work

| RTC item | What changed | Justification and evidence boundary |
|---|---|---|
| **E3C8 — Disturbance definitions and independence** | Added explicit definitions for D, T, S, W, and B plus one activation matrix: D+T always active; S/W/B randomized in training; Stage A is D+T; Stage B is D+T+S+W+B; ablations add one of S/W/B to D+T | This removes conflicting uses of “ideal,” “weather only,” and baseline travel time. W now composes with T instead of replacing it |
| **E3C9 — ML/SARL disturbance table** | Added/updated the literature-coverage table for D/S/T/W/B and clearly separated prediction, heuristic control, SARL, MARL, bus, and adjacent-mode evidence | A coverage table is useful only if rows do not imply that every cited paper studies the same task or mode |
| **E3C10 — Breakdown column** | Corrected Shi et al. from D,B to D,T. Added Cao et al. as adjacent MARL train-malfunction evidence and Guedes and Borenstein as heuristic bus/public-transit vehicle-failure rescheduling evidence | Full-source verification did not support classifying Shi et al. as a breakdown paper. The replacement presentation makes the bus-MARL gap clearer without inventing a prior study |
| **E3C11 — Figure citations** | Added source attribution or “Authors’ illustration” wording where appropriate and documented which V3 assets were copied versus adapted | Original figures should not look externally sourced, and adapted assets should not be passed off as untouched originals |
| **E3C12 — Explain SARL/MARL figure concepts** | Added bus-specific explanations of local state and action. The CTDE prose and figure now agree on local observations, per-agent rewards/transitions, one shared replay buffer, and a shared DDQN learner | The old figure suggested joint-state training and one team reward, while the methods described per-agent rewards. The correction removes that architecture contradiction |

### Examiner 3 — Method and Presentation

| RTC item | What changed | Justification and evidence boundary |
|---|---|---|
| **E3C13 — Reference [10] scope** | The earlier revision distinguished contextual rainfall evidence from corridor calibration. After the approved Texas pivot, the EDSA/NLEX background is retained only in an inactive source-history block; the active study instead uses CapMetro and NOAA evidence | A different-corridor source must not be treated as Texas calibration evidence. The pivot makes the former corridor-mismatch claim inactive rather than silently transferring it |
| **E3C14 — Minor-road exclusion** | Reframed the delimitation for the Route 801 study: agents use route-level headway, load, queue, and segment behavior; feeder effects enter through empirical demand/travel-time distributions rather than a fully modeled street network | This gives a model-scope reason for the exclusion and avoids retaining an EDSA barrier-specific justification in a Texas case |
| **E3C15 — Fixed/variable/derived parameter table** | Retained the required parameter summary with fixed, swept, and calibration-derived sections. Unsupported targets remain TODO-DATA or TODO-VAL; breakdown rate is a declared scenario input | The requested table is present without turning unknown capacity, fleet, schedule, or disturbance values into fake empirical facts |
| **E3C16 — Figure/table callout sweep** | Added meaningful prose callouts for figures and tables and checked active references/labels | A figure or table should be interpreted in the surrounding text, not inserted as decoration |
| **E3C17 — Presentation-only material** | The defense deck was reviewed. Useful nonduplicative concepts were incorporated. The old EDSA corridor map remains only in inactive source history after the Texas pivot; incompatible diagrams were adapted to the current methods | The review obligation was completed, but retaining an EDSA map in the active Texas paper would create a geographic contradiction |
| **E3C18 — 1.5 line spacing** | Added the setspace package and enabled one-and-a-half spacing in main.tex | This directly implements the RTC formatting requirement |
| **E3C19 — Line numbers** | Enabled line numbering in main.tex | This is why numbers appear in the left margin of the current review PDF. They are intentional for the RTC revision copy and can be disabled for the final clean copy |

### Examiner 4

| RTC item | What changed | Justification and evidence boundary |
|---|---|---|
| **E4C20 — Simulation mechanics** | Added when and how demand, ordinary travel time, surge, weather stress, and breakdown values are sampled and how they affect the simulated episode | The disturbance section now reads as an implementable design rather than a list of distributions |
| **E4C21 — Metrics and feature descriptions** | Added formal definitions for simulated mean waiting time, bus travel time, and headway coefficient of variation, plus a feature/source table | This separates deployment sources, simulation sources, measured variables, and simulated passenger states |
| **E4C22 — Dataset contents** | Resolved through the same consolidated dataset section as E1C1 and E2C5 | The section records missing passenger-arrival, capacity, continuous-trajectory, historical-schedule, breakdown, and native-weather fields instead of implying they exist |

## 3. Team-Identified Changes That Were Not RTC Comments

These are tracked separately so they are not falsely presented in the formal
conformity-of-revisions table.

| Notice | What changed | Why |
|---|---|---|
| **N1 — Reward mechanics and CTDE consistency** | Defined a per-agent reward at each control event, a weighted sum of non-positive penalties, TODO-VAL weights, local transition tuples, shared replay/network training, and decentralized execution | The manuscript and old CTDE graphic previously disagreed about team reward versus per-agent reward |
| **N2 — MARL versus bus-scheduling framing** | Rewrote the significance and research-gap framing so MARL is the control method being evaluated and route service reliability under disturbance is the object of study | This keeps the thesis centered on a transport scheduling problem rather than presenting algorithm development as the only contribution |

## 4. Texas Dataset Pivot

### Why a Texas backup route was adopted

The original EDSA operational dataset had still not been delivered. Continuing
to write dataset-specific EDSA claims would have forced the team to guess
schema, coverage, values, and calibration feasibility. The public CapMetro APC
dataset offered a verifiable alternative with event times, route/direction/stop
identifiers, boardings, alightings, load, dwell, segment revenue time/distance,
coordinates, and quality fields.

The correct scientific route was therefore a full case-study pivot:

- CapMetro data support a Texas/Austin/Route 801 simulation.
- They do not support calling the model EDSA-calibrated.
- Any future return to EDSA would require a separate evidence review and another
  manuscript-wide reframing.

### Source and reproducibility

**Primary source:** Texas Open Data, “APC Raw July 2021–December 2021,” Socrata
dataset **im6q-3pc9**.

The branch adds:

- [config/texas_capmetro_801.json](config/texas_capmetro_801.json) — approved
  route, source, join, and evidence settings.
- [scripts/texas_capmetro_pipeline.py](scripts/texas_capmetro_pipeline.py) —
  repeatable APC/NOAA acquisition and audit workflow.
- [data/README.md](data/README.md) — local-data layout and reproduction guide.
- [data/audit/texas_capmetro/](data/audit/texas_capmetro/) — filters, metadata,
  route comparison, weather evidence, GTFS status, checksums, and manifests.

Raw and processed data are not committed. This keeps the repository practical
while allowing another member to reproduce the selected subset and compare
checksums.

### Route-selection justification

Routes 801 and 803 were compared under identical rules:

- reported route equals current route;
- both import-error fields equal zero;
- stop ID is nonzero; and
- direction code is 4 or 6.

| Reproduced measure | Route 801 | Route 803 | Interpretation |
|---|---:|---:|---|
| Clean stop events | 455,654 | 376,801 | Route 801 has 20.93% more |
| Recorded boardings | 810,309 | 532,063 | Route 801 has 52.30% more |
| Positive-time/positive-distance segments | 441,779 | 361,852 | Route 801 has 22.09% more |
| Distinct trip-day pairs | 24,943 | 26,609 | Route 801 does not lead on every metric |
| High-quality GPS share | 98.136% | 97.479% | Both are high and comparable |

Route 801 was selected for denser stop-event, boarding, and usable-segment
evidence. This is a **data-coverage decision**, not a claim that Route 801 has
better service.

Within Route 801, direction code 6 was selected because it has 229,421 clean
events and 420,201 boardings, compared with 226,233 and 390,108 for code 4.
The branch deliberately does not call code 6 northbound or southbound until a
compatible 2021 GTFS or agency source verifies the label.

### Primary subset

The selected direction-code 6 subset has:

- 229,421 clean stop events;
- 184 service-day codes;
- 29 distinct stop IDs;
- 420,201 recorded boardings; and
- raw CSV SHA-256
  **8368412e47df32ff8a3c2837048797664315c0e7ae51c44676766b5af7f23e21**.

## 5. Weather Variables: What Is Feasible and What Is Not

Weather is not a native field in the APC dataset. It was added using NOAA
Local Climatological Data Version 2:

- **Primary station:** Austin Camp Mabry, USW00013958.
- **Sensitivity station:** Austin-Bergstrom, USW00013904.
- **Join rule:** nearest observation within 90 minutes after documented
  local-time handling.

Reproduced feasibility results:

- both stations matched 100% of the 229,421 APC rows;
- Camp Mabry identified 11,804 rain-exposed events;
- median absolute join difference was 12.667 minutes; and
- 95th-percentile absolute join difference was 27.933 minutes.

The raw pooled positive-segment medians were 204 seconds for dry rows and 212
seconds for rain rows. This difference is retained only as a **descriptive
diagnostic**. It is not a causal rain multiplier. Any ordinary-rain estimate
must control at minimum for segment, time of day, and day type.

The methods now keep two different weather roles:

1. **Observed ordinary weather:** joined NOAA exposure/covariates that may be
   used in an adjusted empirical model.
2. **Synthetic severe/extreme stress:** a labeled out-of-support robustness
   scenario, not a claim about observed CapMetro behavior.

This split is justified because the six-month APC period provides useful
ordinary weather overlap but cannot establish every severe-weather intensity
needed for a stress-test sweep.

## 6. Manuscript Changes by File

### main.tex

- Changed the active title to the CapMetro Rapid case study.
- Added and enabled one-and-a-half line spacing.
- Enabled left-margin line numbers for RTC review.
- Removed an incomplete includeonly command that could break the preamble.
- Kept the V3 document class, margins, title layout, package structure, and
  chapter-loading pattern.

### introduction.tex

- Added active CapMetro background and dataset context.
- Added the reproducible Route 801 versus 803 selection table.
- Stated the direction-code and missing-data limitations.
- Added NOAA weather feasibility and the observed-versus-synthetic boundary.
- Reworked ML, SARL, and MARL framing around bus scheduling.
- Corrected literature disturbance classifications.
- Aligned the CTDE description with the implemented reward/training design.
- Kept superseded EDSA background in an inactive LaTeX block only for source
  history; it does not compile into the active Texas manuscript.

### problem.tex

- Reframed the research gap around robustness on a public-data-calibrated
  CapMetro route.
- Rewrote objectives and expected outputs so acquisition, calibration,
  implementation, and evaluation are distinct stages.
- Replaced the “ideal/non-ideal” ambiguity with the D/T/S/W/B activation matrix.
- Rewrote significance, scope, limitations, and delimitations for the Texas
  evidence that actually exists.
- Removed unsupported implications about EDSA ridership benefits and future
  controller performance.

### methods.tex

- Replaced the EDSA network/data plan with the Route 801 APC/NOAA plan.
- Added field-to-model mappings and explicit missing-input gates.
- Changed calibration emphasis from continuous speed trajectories to evidence
  the APC supports more directly: stop-event counts and segment revenue time.
- Added the authoritative disturbance definitions and activation matrix.
- Made W compositional with ordinary T.
- Separated observed ordinary rain from unit-mean synthetic lognormal stress.
- Clarified the per-step synthetic breakdown process.
- Aligned local observations, per-agent rewards, local transitions, shared
  replay/shared DDQN training, and decentralized execution.
- Retained TODO markers for unverified capacity, schedule, fleet, numeric
  thresholds, and scenario values.
- Added metrics, feature sources, matched-seed evaluation, and clear Stage A,
  Stage B, and ablation reporting rules.

### thesis_refs.bib

- Corrected the Shi et al. author metadata and added its DOI.
- Removed the unsubstantiated Verbich entry.
- Added the verified Sun et al. rainfall study.
- Added the verified Guedes and Borenstein vehicle-failure rescheduling study.
- Added official CapMetro APC, CapMetro Rapid, current-GTFS caution, and NOAA
  LCDv2 records.

### Figures/

The V3 source repository was
[Jrddlol2/Group-B3---Manuscript-Draft-V3](https://github.com/Jrddlol2/Group-B3---Manuscript-Draft-V3)
at commit **9de47c5**.

Exact compatible copies:

- UST_logo.jpg
- ustenglogo.png
- bg_fig1_ridership.pdf
- bg_fig2_rainfall_traffic.pdf
- rrl_fig1_sarl_vs_marl (3).pdf
- fig_3_2_aec_training.pdf

Texas-adapted diagrams:

- fig_3_1_pipeline (2).pdf — CapMetro calibration and D/T/S/W/B gates.
- rrl_fig2_ctde (2).pdf — local transitions/per-agent rewards/shared learner.
- meth_fig_eo1_1_calibration (2).pdf — stop-event GEH and travel-time RMSE
  templates, not continuous-speed claims.
- meth_fig_eo3_1_ideal_results.pdf — blank Stage A reporting template with no
  sample results.
- fig_3_2b_aec_evaluation.pdf — D+T Stage A and D+T+S+W+B Stage B labels.

No adapted figure reports a calibration score, training outcome, or controller
result. Full provenance and SHA-256 values are in
[Figures/ASSET_PROVENANCE.md](Figures/ASSET_PROVENANCE.md).

### Tracking and handoff files

- [AUDIT_REPORT_2026-08-23.md](AUDIT_REPORT_2026-08-23.md) records the
  pre-Texas audit findings.
- [RE_AUDIT_TEXAS_CAPMETRO_2026-08-23.md](RE_AUDIT_TEXAS_CAPMETRO_2026-08-23.md)
  records the post-implementation verdict.
- [PROGRESS.md](PROGRESS.md) is the live next-step file.
- [TRACKER.md](TRACKER.md) is the chronological decision log.
- [AUDIT_TRAIL_READABLE.md](AUDIT_TRAIL_READABLE.md) is the member-friendly
  edit history.
- [REVISION_QUEUE.md](REVISION_QUEUE.md) maps all 22 RTC items and both team
  notices to their resolutions.

## 7. Why the Changes Are Defensible

### The dataset is real and the route choice is reproducible

The source URL, Socrata metadata, filter rules, route counts, selected subset,
and raw-file checksum are recorded. Route 801 was not selected based on an
unsupported performance claim.

### Weather is joined, not invented

NOAA observations are joined to APC timestamps with a declared station,
time-handling assumption, and tolerance. A raw dry/rain difference is not called
causal. Severe-weather stress remains synthetic and visibly labeled.

### Missing inputs are visible

Historical route geometry/schedules, capacity, fleet size, passenger arrival
times, breakdown events, and some numeric targets are not silently inferred
from unrelated APC fields.

### Literature corrections favor accuracy over literal but unsupported wording

Where the RTC wording depended on an unverified citation or classification, the
branch did not repeat the error. It replaced or qualified the evidence and
documented the reason.

### No results were fabricated

The branch describes a proposal, data foundation, and experimental design.
Figure templates contain no example performance values. No text claims that
MARL has already beaten NC, FH, EH, or SARL.

## 8. Validation Already Performed

- Route 801/803 evidence was reproduced from the downloaded APC source.
- NOAA joins and compact weather evidence were reproduced.
- The Python pipeline passed syntax validation.
- Bibliography duplicate-key and active-citation checks passed.
- Active LaTeX label/reference and named-environment static checks passed.
- All nine active graphics targets resolve locally: two title logos and seven
  manuscript diagrams.
- Every active PDF figure was rendered and visually inspected.
- Adapted figure text was checked for superseded EDSA, team-reward,
  joint-state, continuous-speed, and sample-result content.
- Binary working files and Git index blobs were hash-checked.
- Git whitespace/error checking passed.
- Khalil main was verified unchanged at a64f44c.

### Validation still required

A full local LaTeX compile was not possible because no TeX engine is installed
in the current environment. The manuscript must be compiled in Overleaf and
visually checked for page flow, line breaks, tables, references, and figure
placement before the next PDF is circulated.

## 9. Work That Is Still Open

The following are implementation tasks, not unresolved RTC prose edits:

1. Obtain a contemporaneous 2021 CapMetro GTFS archive or authoritative agency
   source for stop names, route shape, schedule semantics, and direction label.
2. Obtain a defensible vehicle-capacity and fleet source, or explicitly declare
   a scenario assumption.
3. Confirm units needed before using distance-derived continuous speed.
4. Replace remaining TODO-DATA/TODO-VAL entries only with sourced values,
   calibration outputs, or clearly declared scenario inputs.
5. Build and calibrate the SUMO corridor using a chronological train/validation
   split.
6. Estimate an adjusted ordinary-rain relationship; do not use the pooled
   204-versus-212-second diagnostic as a causal multiplier.
7. Run NC, FH, EH, SARL, and MARL experiments with matched seeds.
8. Report actual run counts, uncertainty intervals, failures, and sensitivity
   results.
9. Compile and visually inspect the complete manuscript in Overleaf.

## 10. Claims the Current Branch Does Not Make

- It does not claim an EDSA-calibrated model.
- It does not claim a completed or validated SUMO network.
- It does not claim MARL training has occurred.
- It does not claim one controller outperforms another.
- It does not claim rain causally added a specific travel-time percentage.
- It does not call synthetic severe weather an observed CapMetro event.
- It does not infer breakdowns from missing APC records.
- It does not guess the human-readable meaning of direction code 6.
- It does not guess capacity, fleet size, or historical headway.
- It does not present Texas results as evidence about Manila.

## 11. Recommended Reading Order for Group Members

1. This report for the complete baseline-to-current explanation.
2. [PROGRESS.md](PROGRESS.md) for the current task order.
3. [REVISION_QUEUE.md](REVISION_QUEUE.md) for examiner-by-examiner close-out.
4. [RE_AUDIT_TEXAS_CAPMETRO_2026-08-23.md](RE_AUDIT_TEXAS_CAPMETRO_2026-08-23.md)
   for the re-audit verdict and reproduced evidence.
5. [data/audit/texas_capmetro/ROUTE_SELECTION_EVIDENCE.md](data/audit/texas_capmetro/ROUTE_SELECTION_EVIDENCE.md)
   for the route choice.
6. [data/audit/texas_capmetro/WEATHER_FEASIBILITY_EVIDENCE.md](data/audit/texas_capmetro/WEATHER_FEASIBILITY_EVIDENCE.md)
   for weather feasibility.
7. [data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md](data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md)
   for the unresolved historical-feed gate.
8. introduction.tex, problem.tex, and methods.tex for the actual Overleaf
   manuscript source.

## Final Status

**RTC proposal-text status:** 22 of 22 written items addressed.

**Team consistency notices:** 2 of 2 addressed.

**Dataset foundation:** Public CapMetro APC and NOAA pipeline implemented and
audited.

**Figures/assets:** Active set complete and version-controlled.

**Simulation/results:** Not yet performed.

**Overleaf compile:** Still required.

**Main branch:** Untouched.
