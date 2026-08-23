# Thesis Revision Progress

- **Last updated:** 2026-08-23
- **Working branch:** `dataset/texas-capmetro-801`
- **Protected branch:** `main` remains at `a64f44c` and has not been edited or merged
- **Case-study decision:** Full pivot to CapMetro Rapid Route 801, direction code 6
- **Implementation status:** Public-data pipeline and manuscript revision complete; simulation, training, and controller evaluation have not been run

## Current Audit Status

| Workstream | Done | In progress | Pending | Interpretation |
|---|---:|---:|---:|---|
| RTC-requested items | 22 | 0 | 0 | All requested proposal-text revisions are implemented |
| Self-identified notices | 2 | 0 | 0 | Reward and CTDE descriptions are aligned |

The RTC audit is **closed at the proposal-text level**. The final source review
removed an unsupported Verbich record, corrected Shi et al. from breakdown to
demand/travel-time uncertainty, added verified weather and adjacent breakdown
evidence, and made the parameter-table placeholders explicit. This does not
mean the simulation is empirically complete: historical operations inputs,
scenario choices, calibration, training, and results remain implementation
gates and are still stated as such in the manuscript.

## Completed on the Texas Branch

- Created a reproducible CapMetro/NOAA pipeline in
  `scripts/texas_capmetro_pipeline.py`, controlled by
  `config/texas_capmetro_801.json`.
- Downloaded the official 47-field CapMetro APC source and preserved raw files
  locally outside Git, with SHA-256 manifests and compact audit evidence in
  `data/audit/texas_capmetro/`.
- Compared Routes 801 and 803 using the same declared cleaning rules. Route 801
  was chosen for its larger clean stop-event, boarding, and usable-segment
  samples, despite having fewer distinct trip-day pairs. This is a coverage
  choice, not a service-quality claim.
- Selected direction code 6 because it has the larger clean-event and boarding
  samples within Route 801. The historical inbound/outbound label is not claimed
  until a contemporaneous 2021 GTFS or agency source is obtained.
- Produced a 229,421-row primary subset covering 184 service days and 29 stop
  IDs. Its raw CSV checksum is
  `8368412e47df32ff8a3c2837048797664315c0e7ae51c44676766b5af7f23e21`.
- Joined NOAA LCDv2 observations from Camp Mabry and Austin-Bergstrom. Both
  stations matched 100% of APC rows within the declared 90-minute tolerance;
  Camp Mabry identified 11,804 rain-exposed rows.
- Kept the weather interpretation honest: the pooled dry/rain medians are
  descriptive only, the APC time basis remains an explicit assumption, and
  severe/extreme weather remains a labeled synthetic stress test.
- Reframed Chapters 1–3 and the title around the CapMetro case; aligned the
  disturbance matrix, CTDE description, calibration claims, parameter table,
  and empirical-versus-synthetic boundaries.
- Corrected the RTC literature evidence: Sun et al. (2025) now supplies verified
  W-only rainfall evidence; Cao et al. (2022) and Guedes and Borenstein (2018)
  are explicitly labeled adjacent B evidence; Shi et al. (2022) is D,T, not B.
- Corrected Chapter 1 so W composes with the always-active empirical T baseline,
  matching Chapters 2 and 3 and the evaluation activation matrix.
- Updated the revision queue, tracker, audit trails, repository guidance, data
  documentation, and team handoff report.

## Feasibility Decision

The route is feasible for an APC-driven simulation baseline and an observed
ordinary-rain covariate because the required stop events, ordering fields,
travel-time fields, loads, coordinates, and weather matches exist at useful
coverage. This does **not** make every thesis component empirically identified.

| Component | Current status | Boundary |
|---|---|---|
| Stop-event demand and dwell calibration | Feasible | APC boardings, alightings, load, dwell, and event order are available |
| Segment travel-time calibration | Feasible with validation | `rev_seconds` is usable; distance-derived speed is gated on distance-unit confirmation |
| Ordinary-rain analysis | Feasible as an adjusted observational model | Must control for segment, time of day, and day type; no causal multiplier is claimed yet |
| Severe/extreme weather robustness | Feasible only as a synthetic stress test | It must remain labeled out-of-support simulation, not observed CapMetro behavior |
| 2021 route shape, stop names, scheduled headway | Not yet authoritative | Requires contemporaneous historical GTFS or agency archive |
| Vehicle capacity and fleet size | Not yet authoritative | Requires an agency/fleet source or a documented scenario assumption |
| Breakdown and demand-surge disturbances | Synthetic by design | APC does not directly observe breakdown events or passenger arrivals left behind |
| SUMO calibration and MARL results | Not performed | No controller-performance result is claimed in the manuscript |

## Local Backups

No checkpoint has been overwritten. Existing checkpoints are under:

- `C:\Users\jared\Desktop\THESIS\Backups\MARL\Texas_CapMetro\20260823-201254_baseline_before_texas_implementation`
- `C:\Users\jared\Desktop\THESIS\Backups\MARL\Texas_CapMetro\20260823-205643_pre_manuscript_after_public_data_pipeline`
- `C:\Users\jared\Desktop\THESIS\Backups\MARL\Texas_CapMetro\20260823-212903_final_post_commit_pre_push`
- `C:\Users\jared\Desktop\THESIS\Backups\MARL\Texas_CapMetro\20260823-213632_before_rtc_tex_repairs`

The final checkpoint contains a verified all-ref Git bundle, a committed-source
archive, the original manuscript PDF, and a compressed copy of the actual raw
and processed CapMetro/NOAA data. Its payload hashes and recovery note are stored
inside the checkpoint folder.

## Recommended Next Order

1. Acquire a contemporaneous 2021 CapMetro GTFS archive and a defensible fleet
   or vehicle-capacity source; keep current direction code 6 unlabeled until then.
2. Resolve the implementation-stage numeric targets and replace the remaining `TODO-DATA`/
   `TODO-VAL` placeholders only with sourced values or declared scenario inputs.
3. Implement the SUMO network and chronological calibration/validation split,
   then document its goodness-of-fit before training any controller.
4. Estimate an adjusted ordinary-rain effect; do not promote the pooled 204 s
   versus 212 s medians into a causal multiplier.
5. Run NC/FH/EH/SARL/MARL experiments only after calibration passes, then report
   the actual seeds, run counts, confidence intervals, and failures.
6. Compile and visually inspect the full manuscript in Overleaf before the next
   PDF is circulated.

## Validation and Publication Record

- Reproduced route and weather evidence: passed.
- Python syntax check: passed.
- Git whitespace/error check: passed; only expected Windows line-ending notices.
- Bibliography duplicate/missing-key scan: passed.
- LaTeX label/reference and named-environment static checks: passed.
- Active graphic audit: nine referenced assets (two title-page logos and seven
  manuscript diagrams) are absent from this Git checkout. The tracker records
  that these are maintained in the Overleaf `Figures` folder; synchronize them
  before attempting a repository-only compile.
- Full LaTeX compilation: not available locally because no TeX engine is
  installed and the active graphic assets above are absent; Overleaf compilation
  with the complete `Figures` folder remains required.
- Remote publication target:
  `dataset/texas-capmetro-801` on `https://github.com/khalil-badal/MARL`.
  Only this branch is authorized; the final remote hash must be verified after
  every push and reported in the task handoff.
- Pull request/merge: intentionally not created. `main` must remain untouched.

Update this file before any later branch push that materially changes these
facts or statuses.
