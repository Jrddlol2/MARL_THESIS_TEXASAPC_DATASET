# Manuscript and Repository Audit Report

**Thesis:** *An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus Scheduling Under Non-Ideal Conditions*  
**Audit date:** 2026-08-23  
**Audited repository baseline:** `main` at `a64f44c`  
**Audit branch:** `audit/minor-fixes-progress-2026-08-23`  
**RTC outcome:** Accepted with major revisions

## Executive Summary

Most requested revision content is present, but the repository previously
treated several partially resolved items as complete. This audit reopens six
RTC items and one self-identified notice so the trackers match the manuscript's
actual state.

The three most important unresolved matters are:

1. The CTDE figure describes a shared reward and joint-state training, while the
   methods chapter describes per-agent rewards, local transitions, a shared
   DDQN network, and a shared replay buffer.
2. The training, Stage A, and Stage B descriptions do not use one consistent
   disturbance-activation matrix, and several distribution parameters remain
   unspecified.
3. The intended EDSA dataset has not been acquired or inspected. Its actual
   record structure, field coverage, granularity, and quality therefore remain
   unknown.

No public backup dataset was selected as part of this audit.

## Scope and Evidence

The audit compared:

- the current LaTeX source and tracking records on GitHub `main`;
- the externally supplied Phase 1 manuscript PDF named
  `Group_B3___Manuscript_Draft_V2__Copy___Copy_.pdf`;
- `RTC_DECISION_LETTER.md`, `REVISION_QUEUE.md`, `TRACKER.md`, both audit trails,
  `RRL/sources.md`, `CLAUDE.md`, and `thesis_refs.bib`; and
- the repository's recent commit history.

The external Phase 1 PDF is not added to this repository. The audit did not
edit or regenerate a PDF, select a dataset, run the simulation, or invent any
calibration values or results.

## Changes Made on This Branch

### Manuscript source

- Fixed `TThe objective` in `problem.tex`.
- Fixed a missing `is` and punctuation in the ideal-condition paragraph.
- Changed the SafeTravelPH baseline statement from completed/present tense to
  acquisition-pending language in `methods.tex`.

The revised dataset sentence now makes three boundaries explicit: acquisition
is pending, schema and coverage must be verified, and no dataset-specific
statistics or calibration are claimed yet.

### Revision governance

- Reopened E2C4, E3C8, E3C10, E3C12, E3C15, and E4C20.
- Reopened N1 for the unresolved reward/CTDE contradiction.
- Updated the official queue summary to 13 done, 6 in progress, and 3 pending.
- Corrected N2's Significance location to Section 2.4.
- Documented the current SARL/MARL and CTDE numbering as Figures 1.4 and 1.5.
- Updated stale agent guidance stating that line numbers and 1.5 spacing were
  not yet enabled; both are already active.
- Flagged the original August 8, 2026 deadline for confirmation rather than
  silently treating it as current.

### Team handoff

- Added `PROGRESS.md` as the live operational status document.
- Added this report to explain findings, changes, limits, and next decisions.
- Linked both documents from `README.md`.

## Detailed Findings

### 1. Reward and CTDE architecture - blocking consistency issue

Figure 1.5 says that agents share one reward and train using joint-state
information. Section 3.2.7 instead says that each bus receives an independent
reward and stores its own local transition while all buses update a common
network from a shared replay buffer.

The smallest coherent design is parameter sharing with per-agent rewards and
local transitions during centralized training, followed by decentralized local
execution. The team must still approve this. The audit does not rewrite the
architecture without that decision.

Affected items: E3C12 and N1.

### 2. Disturbance activation and parameter specification - blocking reproducibility issue

The manuscript defines D, S, T, W, and B and explains their sampling mechanics,
but its operating-condition and evaluation passages do not consistently state
which are active during training, Stage A, Stage B, and the ablations.

In addition, `sigma_d` and `sigma_s` are labeled as standard deviations while
their table cells show only clip ranges. The breakdown rate `lambda` also
remains unresolved. These are legitimate TODO values, but the table must not
make clip bounds look like distribution parameters.

Affected items: E3C8, E3C15, and E4C20.

### 3. Dataset status - unresolved by design

Section 3.2.5 correctly defines the six fields the study needs: vehicle
location, boardings, alightings, onboard occupancy, operating speed, and dwell
time. That is a requirements specification, not proof that SafeTravelPH
contains all six fields.

The dataset-dependent tasks remain pending:

- E1C1 - dataset setup discussion;
- E2C5 - actual dataset contents; and
- E4C22 - actual dataset contents and processing relevance.

They can be completed only after the EDSA records are acquired and inspected.
A public analog may support pipeline development, but it cannot close these
EDSA-specific RTC comments.

### 4. Citation verification - high evidence risk

The source scan found 66 active citation keys with matching bibliography
entries, so there are no orphaned active citations. However, only
`Patil2025Conformal`, `Rodriguez2023Cooperative`, and `Wangsun` were cleanly
content-verified during the prior audit work.

The local file mapped to `Wang2020Holding` is the wrong paper. The highest-value
next checks are `verbich2021`, `Wang2020Holding`, `Shi2022DistDRL`,
`Zhang2025SADRL`, `Zhao2022STDH`, `TSSP_Rain2018`, `DOTr2020Suspension`, and the
EDSA-specific sources supporting N2.

E2C4 remains open until Verbich and El-Geneidy's W/B classification is verified.

### 5. Defense-deck breakdown reconciliation - incomplete evidence trail

The manuscript explains why Shi et al. is counted as a MARL bus-breakdown study
and why Cao et al. and Verbich and El-Geneidy fall outside that table's scope.
But the repository does not preserve the identities of the two papers shown in
the defense presentation or a direct reconciliation of those slide entries.

E3C10 therefore remains open even though the explanatory paragraph is present.

### 6. PDF and source drift

The external Phase 1 PDF does not include the two N2 additions currently present
in `problem.tex`. A fresh compilation from the resolved source is required before
the next manuscript is circulated. The compilation should happen after the
architecture and activation decisions so another stale PDF is not distributed.

### 7. Lower-risk housekeeping

- Nine bibliography entries appear unused:
  `Cai2024Multiairport`, `Fan2019HPPO`, `Kingman1993Poisson`,
  `Ning2024Survey`, `Ranpura2025Calibration`, `Schrader2024SUMO`,
  `Wardman2004VOT`, `Yang2024AMAHPPO`, and `Zhao2023AGV`.
- Historical audit entries used Figure 1.3/1.4 before the corridor map shifted
  the current numbers to Figure 1.4/1.5. The live trackers now state the current
  numbering while retaining the original RTC wording where relevant.
- The original deadline is in the past and needs formal confirmation.

## Public Dataset Contingency - Decision Deferred

No candidate has been adopted. The current research shortlist is:

| Candidate | Potential role | Important limitation |
|---|---|---|
| [CapMetro APC 2021](https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9) | Main six-field pipeline-development source; speed can be derived | Austin bus analog, not EDSA; raw quality filtering required |
| [Bogota TransMilenio](https://datosabiertos.bogota.gov.co/dataset/especificacion-gtfs-general-transport-feed-specification-sitp) | BRT-mode and demand-envelope plausibility check | Live/aggregate pieces do not provide complete onboard load records |
| [MBTA LAMP](https://performancedata.mbta.com/) | Travel-time, headway, and event-processing validation | No passenger counts; stopped duration is not confirmed door dwell |
| [Caltrans PeMS](https://dot.ca.gov/programs/traffic-operations/mpr/pems-source) | Road-speed and traffic-disturbance inputs | Not a bus passenger dataset |

If the team later selects an analog source, the manuscript and outputs must say
that it is for pipeline development only and is not EDSA calibration evidence.

## Recommended Next Decisions

1. Approve one reward/CTDE architecture.
2. Approve one disturbance activation matrix and identify which parameter values
   are fixed now versus explicitly deferred.
3. Verify the eight gap-critical citations.
4. Record and reconcile the two defense-deck breakdown entries.
5. Decide whether a public analog dataset should be used, and document its
   allowed role before downloading a large file.
6. Recompile and visually inspect the manuscript, then rerun the audit.

## Validation Status

The final branch validation results are recorded in `PROGRESS.md` and should be
updated immediately before each push. At report creation time, no dataset had
been downloaded and no simulation had been run.
