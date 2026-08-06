# CHANGE TRACKER — Group B3 Thesis Revision 1
# Thesis: An Evaluation of Multi-Agent Reinforcement Learning
#         for Dynamic Bus Scheduling Under Non-Ideal Conditions
# Start date: 2026-08-06
# Target submission: August 8, 2026

---

## Summary
| Metric | Count |
|--------|-------|
| Total recommendations | 22 |
| Completed | 4 |
| In progress | 0 |
| Pending | 18 (3 BLOCKED — no dataset access; see Reverted Work below) |

---

## Reverted Work

### E1C1 + E2C5 + E4C22 — Dataset Description — REVERTED 2026-08-06
**Originally added:** 2026-08-06. **Reverted:** 2026-08-06, same session, before any commit/push.
**Why:** The group does not have access to the SafeTravelPH dataset yet. The added
"Dataset Description" paragraph and Table (SafeTravelPH dataset fields) made
qualitative claims about the dataset's structure — e.g. that it is a "crowdsourced
mobile application" yielding "a per-trip trajectory log rather than a fixed-interval
sensor feed," with record density varying "by segment and time of day according to
rider participation" — that assume familiarity with data the group has not actually
seen. All numeric values used `%TODO-DATA` placeholders correctly, but the
qualitative narrative overstepped what R1/R6 (CLAUDE.md) permit before data access.
**What was removed:** The full "Dataset Description" paragraph, the 6-row field
table ("SafeTravelPH dataset fields and their role in simulation calibration"),
and the closing DOTr FOI sentence — all in methods.tex, Section 3.2.5, between the
"Corridor bus operational data" itemize block and the "Severe-weather conditions..."
paragraph. The file was restored to its pre-edit state at that location.
**Side effect:** Removing this table means all subsequent table numbers in the
compiled PDF shift down by one (the table that was "Table 3.3" in the now-reverted
plan is Table 3.2; what was "Table 3.4" is Table 3.3). Table entries below have been
corrected to reflect this. No hardcoded "Table 3.X" text exists in methods.tex itself
— all in-text references use `\ref{}`, so this is a numbering note only, not a
required manuscript fix.
**Status:** E1C1, E2C5, E4C22 reset to `[ ]` pending in REVISION_QUEUE.md, marked
BLOCKED pending dataset access. Do not resume without explicit user go-ahead, even
though the task is technically satisfiable with placeholder-only language.

---

## Completed Changes

---
### E3C8 — Disturbance definitions and independence
**Date:** 2026-08-06
**File edited:** methods.tex
**Section:** 3.2.6, at the start of "Stochastic Disturbance Generators" (before the existing "Four stochastic generators inject variability..." paragraph)
**Lines changed:** approx. new block of ~12 lines inserted immediately before the existing generator-overview paragraph
**What was added/changed:**
> Added a "Disturbance Classes and Independence" block defining five disturbance classes (D, S, T, W, B) as an itemized list, explicitly distinguishing baseline stochastic demand (D, always present) from demand surge (S, the controlled variable layered on top), and tying each definition to its existing symbol in Table 3.1 ($\sigma_d$, $\sigma_s$, $\eta$, $\lambda$) rather than inventing new notation. Added a paragraph stating the four generators (S/T/W/B) are injected independently with no causal chain, with the rain-causing-both-slowdown-and-crowding example from the panel comment, and linking to the single-disturbance ablation in the Evaluation Methods section.
**Conformity table entry:**
| 8 | "Define each 'disturbance' explicitly. Dependencies? ... difference between stochastic demand and demand surge?" | Added an explicit definition block for disturbance classes D/S/T/W/B at the start of Section 3.2.6, clarifying that D (baseline demand) is always present while S (surge) is the controlled variable added on top, and stating the generators are independently injected with no causal chain. | 3.2.6 | TBD |
**Commit message:** `E3C8: add disturbance class definitions and independence statement (3.2.6)`

---
### E3C15 — Fixed and variable parameters summary table
**Date:** 2026-08-06
**File edited:** methods.tex
**Section:** 3.2.4 (Operating Conditions), inserted at the end of the section, before "Data Processing" (3.2.5)
**Lines changed:** approx. 40-line table block inserted
**What was added/changed:**
> Added a table ("Simulation parameter summary," compiles as Table 3.2 now that the reverted Dataset Description table is gone — labeled `tab:sim-parameters`, so it auto-numbers correctly regardless) with three grouped sections: fixed parameters, swept/variable parameters, and derived (calibration-time) parameters. Reused two values already established elsewhere in the manuscript rather than re-deriving them — stop count $M=24$ and fleet size $N \approx 12$--$30$, both from the state-space dimensionality discussion in Section 1.2.2 — and cited that section as their source. All values with no prior basis in the manuscript (scheduled headway $H_0$, bus capacity, control stop count, max holding duration $\Delta T$, breakdown rate $\lambda$, discount parameters) use %TODO-VAL placeholders; all data-derived values ($\mu$, $\sigma$, $CV_0$) use %TODO-DATA. Corrected a section-reference slip during drafting: the holding-action parameters ($\Delta T$, $\Omega$, $|A_i|$) belong to the Action Space subsection under 3.2.7, not 3.2.3 as first written.
**Conformity table entry:**
| 15 | "Summarize the different fixed and variable simulation parameters. Include target values." | Added a parameter summary table (compiles as Table 3.2) at the end of Section 3.2.4, collecting fixed, swept, and derived parameters into one table; values not yet available (schedule, capacity, breakdown rate, calibration outputs) marked with %TODO-VAL/%TODO-DATA rather than fabricated. | 3.2.4 | TBD |
**Commit message:** `E3C15: add simulation parameter summary table (3.2.4)`

---
### E4C20 — Simulation mechanics explanation
**Date:** 2026-08-06
**File edited:** methods.tex
**Section:** 3.2.6, within each of the four generator subsubsections (Passenger Demand, Traffic Delays, Weather-Induced Anomalies, Bus Breakdowns)
**Lines changed:** one sentence inserted into each of the four generator paragraphs
**What was added/changed:**
> Added one implementation-mechanics sentence per generator: Passenger Demand — clarifies $f_d$ is sampled once per episode and applied uniformly to all per-stop arrival rates; Traffic Delays — clarifies $f_s$ is sampled once per episode and applied per-segment-traversal; Weather-Induced Anomalies — clarifies a fresh lognormal sample is drawn per bus per segment traversal when $\eta>0$, referencing the existing Eq. 3.4/3.5 method-of-moments parameters; Bus Breakdowns — adds the per-timestep Bernoulli-trial mechanic ($\lambda \cdot dt$) that was implied but not stated before the existing removal/headway description.
**Conformity table entry:**
| 20 | "Explain in detail the different scenarios, and how to simulate this data." | Added one sentence to each of the four disturbance-generator subsections describing the concrete sampling/application mechanic (when sampled, what it's applied to, how it propagates). | 3.2.6 | TBD |
**Commit message:** `E4C20: add per-generator simulation mechanics sentences (3.2.6)`

---
### E4C21 — Metric definitions and feature descriptions
**Date:** 2026-08-06
**File edited:** methods.tex
**Section:** 3.2.9 (Data Analysis Methods, start of section) and 3.2.7 State Space and Local Observations subsubsection
**Lines changed:** two blocks inserted (~14 lines of definitions/equations; ~25-line table)
**What was added/changed:**
> Part A: added formal one-line definitions with numbered equations (Eq. eq:waiting_time, eq:headway_cv) for mean passenger waiting time ($\bar{W}$), mean total travel time ($\bar{T}$), and headway coefficient of variation ($CV_h$), at the start of Data Analysis Methods. Noted that $CV_h$'s construction mirrors the existing $CV_0$ definition in Table 3.1. Part B: added a table ("Agent observation vector: features, symbols, and data sources," compiles as Table 3.3 — labeled `tab:observation-features`) after the observation-vector bullet list in the State Space subsubsection, listing each feature's deployment-time sensor source (AVL/APC/AFC/weather API/incident system) versus its simulation-time source (bus model / generator output), plus a closing sentence noting all simulated features are synthetic.
**Conformity table entry:**
| 21 | "Include details on the metrics and description of features." | Added formal mathematical definitions for the three response metrics in Section 3.2.9, and a 7-row feature/symbol/source table (compiles as Table 3.3) in Section 3.2.7 mapping each observation feature to its real-world sensor source and its simulation-time source. | 3.2.7, 3.2.9 | TBD |
**Commit message:** `E4C21: add metric definitions (3.2.9) and observation feature table (3.2.7)`

---

## Source Verification / Citation Corrections

Not RTC-requested tasks — these are fact-checks against the actual RRL source
PDFs (see RRL/sources.md), done at the user's request to catch claims that
were unverifiable or wrong before a panelist could catch them. Two errors
found and fixed so far, both pre-existing (written before this session).

### Patil2025Conformal — "INRIX freeway data" correction
**Date:** 2026-08-06
**File edited:** methods.tex
**Section:** 3.2.6, Weather-Induced Anomalies subsubsection
**What was wrong:** Text claimed Patil et al. validated the lognormal parameterization "against INRIX freeway data via the Kolmogorov-Smirnov test." Checked against the actual paper: (1) the paper's own Table V classifies its test route as "Local, Minor/Principal Arterials," not a freeway; (2) the KS test was run on SUMO-simulated travel times to check log-normal shape fit, not directly against INRIX data — INRIX was used only to pick representative time windows and anchor mean travel times.
**Fix:** Reworded to say the parameterization was tested via SUMO-simulated travel times anchored to INRIX data for an "urban arterial corridor," with the KS test confirming the simulated distribution's shape, not a direct INRIX comparison. The numeric result itself ($KS=0.036$, $p=0.94$ at $CV=1.0$) was independently confirmed correct against the paper's Section IV.F.
**Commit message:** `Fix Patil2025Conformal citation: correct "freeway" to "arterial road," clarify KS test mechanism`

### Rodriguez2023Cooperative — unsupported "vs. continuous formulations" claim
**Date:** 2026-08-06
**File edited:** methods.tex
**Section:** 3.2.7, Action Space subsubsection
**What was wrong:** Text attributed to Rodriguez et al. the claim that their 5-bin discretization "achieves combined holding-and-skipping control... without measurable loss of performance versus continuous formulations." Checked against the full paper: no continuous-action baseline exists anywhere in it — this comparison isn't made. Also, Rodriguez's actual action space is a 6-way mutually-exclusive choice (5 holding strengths, where $\omega=0$ already covers "no holding," plus 1 skip action), not this thesis's 5×2=10 independent Cartesian combination — the two designs are similar in spirit but not the same.
**Fix:** Removed the fabricated continuous-vs-discrete comparison. Reframed the $|A_i|=10$ design as this study's own choice (broader than Rodriguez's), correctly described Rodriguez's actual 6-action mutually-exclusive space, and kept the citation only for what's verifiably true: the matching $\Omega$ holding-strength values, and the driver-compliance argument (Rodriguez models non-compliant drivers executing 60-80% of instructed holding time — confirmed against Section 6.3 "Driver compliance"). Did NOT change the study's own $|A_i|=10$ design, since that value is load-bearing elsewhere (Table 3.1 notation, the SARL state/action-space dimensionality discussion in introduction.tex, and the ~960-run computational budget in Methodological Challenges) and correcting the citation doesn't require touching it.
**Commit message:** `Fix Rodriguez2023Cooperative citation: remove unsupported continuous-vs-discrete claim, correct action-space description`

---

*Nothing follows.*
