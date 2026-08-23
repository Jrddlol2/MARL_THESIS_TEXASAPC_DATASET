# Thesis Revision Progress

- **Last updated:** 2026-08-23
- **Working branch:** `audit/minor-fixes-progress-2026-08-23`
- **Repository baseline:** `a64f44c` (`main` at audit start)
- **Dataset decision:** Deferred - no public backup dataset has been selected or downloaded

## Current Status

| Workstream | Done | In progress | Pending | Notes |
|---|---:|---:|---:|---|
| RTC-requested items | 13 | 6 | 3 | Six items were reopened after the repository audit |
| Self-identified notices | 1 | 1 | 0 | N1 remains open because the reward/CTDE descriptions conflict |

The three pending RTC items - E1C1, E2C5, and E4C22 - all require inspection
of the actual EDSA operational dataset. They must not be marked complete from a
public analog dataset.

## Completed Before This Audit

The repository already contains the main RTC-requested additions for:

- dataset-field-to-model mapping;
- weather-disturbance derivation;
- traditional-controller failure modes and success criteria;
- disturbance definitions and sampling descriptions;
- ML/SARL/MARL comparison tables;
- NLEX scope clarification and feeder-road exclusion;
- parameter, observation-feature, and evaluation-metric tables;
- figure/table callouts, the corridor map, and the eta-basis table;
- 1.5 line spacing and continuous line numbers; and
- the N2 bus-scheduling-versus-MARL framing clarification.

Completion here means the requested material is present. Items listed as
reopened below still require consistency or evidence checks before final signoff.

## Completed on the Audit Branch

- Corrected `TThe objective` to `The objective` in `problem.tex`.
- Corrected the grammar of the ideal-condition description in `methods.tex`.
- Replaced the premature claim that the SafeTravelPH baseline "is established"
  with explicit pending language. No data source was selected or characterized.
- Reopened items whose checkboxes overstated their verified status.
- Corrected the current SARL/MARL and CTDE figure-number references after the
  corridor map shifted them to Figures 1.4 and 1.5.
- Corrected N2's Significance location from Section 2.3 to Section 2.4.
- Updated stale `CLAUDE.md` notes for line numbering, line spacing, and the
  original submission deadline.
- Added this progress file and `AUDIT_REPORT_2026-08-23.md` for team handoff.

## Reopened Items

| Item | Why it remains open | Decision or evidence needed |
|---|---|---|
| E2C4 | Verbich and El-Geneidy's W/B classification is not source-verified | Read the intended paper and confirm the table entry |
| E3C8 | Disturbances are defined, but S/T activation is inconsistent | Approve one training/Stage A/Stage B activation matrix |
| E3C10 | The repository does not identify the two breakdown papers shown in the defense | Record the slide entries and reconcile them with Table 1.2 |
| E3C12 | Figure 1.5 says shared reward/joint-state training, while Section 3.2.7 says per-agent rewards/local transitions | Approve one reward and training architecture |
| E3C15 | `sigma_d` and `sigma_s` cells contain clip ranges, not standard deviations | Supply values or retain explicit TODO-VAL placeholders |
| E4C20 | Sampling prose exists, but activation conflicts and missing values prevent reproduction | Resolve E3C8/E3C15 and propagate the result |
| N1 | Reward mechanics are written, but CTDE text contradicts them | Resolve together with E3C12 |

## Dataset Position

- The group does not yet have a verified EDSA operational dataset.
- No public backup has been selected in this branch.
- Public analog data may later be used only for pipeline development and must
  never be presented as EDSA calibration or EDSA performance evidence.
- The current shortlist is CapMetro APC 2021 for the six-field pipeline,
  TransMilenio for a BRT-mode plausibility check, MBTA LAMP for operations-event
  validation, and Caltrans PeMS for traffic-disturbance inputs.
- A dataset decision should be recorded in a separate decision entry after the
  team agrees on fitness, licensing, storage size, and the exact role of each
  source.

## Recommended Next Order

1. Approve the reward/CTDE architecture, then align Figure 1.5 and Section 3.2.7.
2. Approve the disturbance activation matrix and unresolved parameter values.
3. Verify the eight gap-critical citations, beginning with `verbich2021` and the
   mismatched `Wang2020Holding` local PDF.
4. Reconcile the defense-deck breakdown entries and preserve the evidence note.
5. Decide whether to use a public analog dataset; keep EDSA and analog outputs
   separated in filenames, tables, and claims.
6. Recompile the manuscript and rerun the full audit after the substantive
   decisions are implemented.

## Validation Record

- Queue counts verified from the file: 22 RTC items = 13 done + 6 in
  progress + 3 pending; 2 notices = 1 done + 1 in progress.
- Internal Markdown links checked: all referenced repository files exist.
- LaTeX structural scan passed: 43 unique labels, 67 references, no missing
  references, no duplicate labels, and balanced named environments.
- Citation-key scan passed: 66 active keys, 75 bibliography entries, no missing
  bibliography keys, and 9 unused entries documented in the audit report.
- Full LaTeX compilation was not run because no TeX engine is installed in the
  local audit environment. Compile and visually inspect in Overleaf before
  circulating the next PDF.
- Dataset download: not performed.
- Local audit commits: `7680bd0`, `1f843c3`.
- Push status: blocked. GitHub returned HTTP 403 because the available Git
  credential is authenticated as `Jrddlol2`, which does not have write access
  to `khalil-badal/MARL`. The in-app GitHub session is signed out, and no
  `Jrddlol2/MARL` fork currently exists.
- Publication can resume after either `Jrddlol2` is added as a collaborator,
  an authorized GitHub account is connected, or the team approves a fork and
  pull-request workflow.

Update this section immediately before every audit-branch push.
