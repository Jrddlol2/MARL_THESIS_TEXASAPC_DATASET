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
| Completed | 17 |
| In progress | 0 |
| Pending | 5 (3 blocked on dataset access, 1 blocked on group input, 1 dataset-adjacent pending confirmation — see Reverted Work / REVISION_QUEUE.md) |

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
### E1C3 — Weather disturbance derivation in research gap
**Date:** 2026-08-06 (entry backfilled — task was completed and pushed in commit `34017d3` but its TRACKER.md entry was missed at the time)
**File edited:** problem.tex
**Section:** 2.2 (Research Gap)
**What was added/changed:**
> Added two sentences after the existing gap statement tracing the weather (W) disturbance class's derivation: identified through the MARL-applied-to-bus-scheduling literature survey (cross-referenced via new `\label{subsec:marl-applied}`), motivated by the rainfall and typhoon-suspension evidence in Section 1.1, and addressed via Patil et al.'s lognormal parameterization (cross-referenced via new `\label{subsec:disturbance-gap}`).
**Conformity table entry:**
| 3 | "Research gap should include how you arrived at the column of sudden weather disturbance." | Added derivation trail for the W disturbance class to Section 2.2, linking the literature-survey gap, the EDSA operational evidence, and the lognormal parameterization source. | 2.2 | TBD |
**Commit message:** (included in `34017d3`, see AUDIT_TRAIL.md)

---
### E2C6 — Traditional method performance under disturbances
**Date:** 2026-08-06 (entry backfilled, same commit as above)
**File edited:** introduction.tex (1.2.1), methods.tex (Baseline Controllers subsection)
**What was added/changed:**
> introduction.tex: added a paragraph after the Daganzo citation describing, in general conceptual terms (no forward-reference to FH/EH acronyms not yet defined at that point), why fixed timetables have no corrective mechanism, why local reactive control handles congestion but not breakdowns, and why global reactive control still can't adapt to weather's heavy tails. methods.tex: added one sentence to each of NC/FH/EH's subsubsections stating its expected failure mode under non-ideal conditions.
**Conformity table entry:**
| 6 | "Expound on how traditional, non-AI scheduling systems perform under the conditions you have specified." | Added a paragraph in 1.2.1 explaining static/local/global reactive control's disturbance failure modes conceptually, plus one failure-mode sentence per baseline (NC/FH/EH) in Section 3.2.8. | 1.2.1, 3.2.8 | TBD |
**Commit message:** (included in `34017d3`, see AUDIT_TRAIL.md)

---
### E2C7 — Explicit success criteria
**Date:** 2026-08-06 (entry backfilled, same commit as above)
**File edited:** methods.tex
**Section:** 3.2.10 (Evaluation Methods)
**What was added/changed:**
> Pulled the existing Stage A and Stage B acceptance criteria out of paragraph prose into dedicated `\paragraph{}` callouts (Stage A as an itemized two-part list, Stage B as a standalone paragraph), without changing or inventing any threshold values.
**Conformity table entry:**
| 7 | "Can you describe what a successful performance will look like?" | Made the existing Stage A/B acceptance criteria visually prominent via dedicated callouts, no new thresholds introduced. | 3.2.10 | TBD |
**Commit message:** (included in `34017d3`, see AUDIT_TRAIL.md)

---
### E3C12 — Explain Figure 1.3 concepts in text
**Date:** 2026-08-06 (entry backfilled, same commit as above)
**File edited:** introduction.tex
**Section:** 1.2.3 (Multi-Agent Reinforcement Learning), after Figure 1.3
**What was added/changed:**
> Added a paragraph after Figure 1.3 explaining what the per-bus state and action mean in bus-control terms, tying the figure's $o_i$ notation to the formal $s_{i,t}$ notation defined in methods.tex's State Space subsection, and explaining the SARL-vs-MARL panel difference (concatenated global state vs. independent local processing).
**Conformity table entry:**
| 12 | "Explain the concepts in Figure 1.3, like the bus states and actions." | Added explanatory paragraph after Figure 1.3 tying its notation to the formal state/action-space definitions in Chapter 3. | 1.2.3 | TBD |
**Commit message:** (included in `34017d3`, see AUDIT_TRAIL.md)

---
### E3C13 — Clarify Reference [10] scope
**Date:** 2026-08-06 (entry backfilled, same commit as above)
**File edited:** introduction.tex (1.1), methods.tex (3.2.3)
**What was added/changed:**
> introduction.tex: added a sentence after the TSSP_Rain2018 citation noting it's a 2018 North Luzon Expressway study, used only as general contextual motivation, not EDSA-specific calibration. methods.tex: added a sentence at the start of Environment Model Validation (3.2.3) clarifying that GEH/RMSE calibration is independent of that motivating citation. Addresses both halves of the RTC comment (recency AND corridor mismatch), per the earlier cross-check against RTC_DECISION_LETTER.md that caught the original queue entry only covering the corridor half.
**Conformity table entry:**
| 13 | "Reference 10 is not quite new and simulates a different corridor. Will you adopt the same information or tune for EDSA northbound?" | Clarified in Section 1.1 that [10]/TSSP_Rain2018 (2018, North Luzon Expressway) is contextual motivation only; clarified in Section 3.2.3 that EDSA calibration is independently derived via GEH/RMSE, not adopted from [10]. | 1.1, 3.2.3 | TBD |
**Commit message:** (included in `34017d3`, see AUDIT_TRAIL.md)

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

### Wangsun — demand-surge clip range mismatch
**Date:** 2026-08-06
**File edited:** methods.tex
**Section:** 3.2.6, Passenger Demand subsubsection
**What was wrong:** Text claimed the demand-surge scaling factor is "clipped to $[1,3]$, following Wang and Sun." Checked against the actual paper (Eq. 22): their scaling factor $p_d \sim \mathcal{N}(1,\sigma_d^2)$ is clipped to $[1, 10]$, not $[1,3]$. The manuscript's follow-up justification ("upper bound of 3 corresponds to roughly a tripling... spanning the range observed during major event let-outs and severe-weather mode shifts") also does not appear anywhere in the source — it reads as an invented rationale for a number that was never Wang & Sun's.
**Fix:** Kept the study's own $[1,3]$ clip value (changing it to match $[1,10]$ would be a substantive experimental redesign, outside the scope of a citation fix) but stopped attributing the specific bound to Wang & Sun — cited them only for the general Gaussian-clipped scaling mechanism, and reframed $[1,3]$ explicitly as this study's own choice with a %TODO-VAL flag to revisit it against the wider literature range during implementation.
**Commit message:** `Fix Wangsun citation: correct demand-surge clip attribution, flag [1,3] as study's own choice not Wang & Sun's`

---

### E3C9 + E2C4 — ML/SARL disturbance table + severe-weather comparison study
**Date:** 2026-08-06
**File edited:** introduction.tex
**Section:** end of 1.2.2 (Single-Agent RL and Its Limitations), before 1.2.3 (Multi-Agent RL)
**What was added/changed:**
> Added Table~\ref{tab:ml_sarl_coverage} ("Disturbance coverage across ML and SARL vehicle-scheduling studies"), a 5-row companion to Table 1.2 covering Wang2017 (ML), Barrera2025Optimization (ML-assisted), Zhao2022STDH (SARL), Zhang2025SADRL (SARL), and verbich2021 (heuristic, non-MARL — the severe-weather-and-breakdown study E2C4 asked for). Added a discussion paragraph connecting the new table to Table 1.2, explaining that no ML/SARL study covers W or B, and that Verbich & El-Geneidy's coverage of both is explicitly non-MARL, sharpening the stated gap. Also folded in a sentence distinguishing Patil et al.'s role (lognormal parameterization source, not a bus-control baseline).
**Citation caution:** Only Barrera2025Optimization has a local PDF to verify against (RRL/, confirmed). The other four sources' D/S/T/W/B classifications are attributed to the RTC panel's own characterization (verbatim in RTC_DECISION_LETTER.md comment 9), flagged as such in the table footnote rather than presented as independently verified.
**Conformity table entry:**
| 9, 4 | "Consider adding an ML/SARL VSP table showing the disturbance column." / "Include study that considers severe weather conditions in your comparison." | Added a 5-row ML/SARL disturbance-coverage table after the SARL subsection, including Verbich & El-Geneidy (severe weather + breakdowns, heuristic control) as the E2C4-requested comparison study, with a discussion paragraph sharpening the stated gap. | 1.2.2/1.2.3 boundary | TBD |
**Commit message:** `E3C9+E2C4: add ML/SARL disturbance coverage table incl. severe-weather study`

---
### E3C10 — Fix Table 1.2 breakdown column
**Date:** 2026-08-06
**File edited:** introduction.tex
**Section:** immediately before the "Table~\ref{tab:marl_performance} summarizes..." paragraph
**What was added/changed:**
> Added a clarifying paragraph stating Shi et al. is the only B-entry in Table 1.2, and explicitly excluding Cao et al. (train rescheduling, not bus — confirmed via bib title) and Verbich & El-Geneidy (heuristic, non-MARL — now in the new Table~\ref{tab:ml_sarl_coverage}) with the reasons why each doesn't belong in a MARL-bus-scoped table.
**Judgment call:** Could not verify what the group's presentation actually showed (no slide access), so used the RTC letter's own suggested fallback (a clarifying footnote) instead of guessing at adding an unverified second B-row.
**Conformity table entry:**
| 10 | "In the MARL VSP table (table 1.2), there is only 1 paper that has B disturbance. But in the presentation, there were two. Make sure to update the manuscript to the accurate information." | Added a paragraph before Table 1.2's summary clarifying that Shi et al. is the sole MARL-bus B-entry, with explicit reasoning for excluding Cao et al. (train) and Verbich & El-Geneidy (non-MARL). | 1.2.4 (before Table 1.2 discussion) | TBD |
**Commit message:** `E3C10: clarify Table 1.2 breakdown-column scope (exclude train/non-MARL papers)`

---
### E3C11 — Add missing figure citations
**Date:** 2026-08-06
**File edited:** introduction.tex, methods.tex
**Section:** 7 figure captions across both files
**What was added/changed:**
> Added "Authors' illustration." to the captions of introduction.tex Figures 1.3 (SARL vs MARL) and 1.4 (CTDE) — the two the RTC named explicitly — and to methods.tex Figures 3.1–3.5 (pipeline, calibration, AEC training, Stage A, Monte Carlo evaluation), all of which are original diagrams with no prior attribution. Figures 1.1 and 1.2 already carried citations and were left unchanged.
**Conformity table entry:**
| 11 | "Some figures do not have citations (e.g., Figure 1.3)." | Added "Authors' illustration" to all 7 previously-unattributed original figure captions across Chapters 1 and 3. | 1.2.3, 1.2.3(fig1.4), 3.1–3.10 (various) | TBD |
**Commit message:** `E3C11: add "authors' illustration" attribution to 7 original figure captions`

---
### E3C14 — Justify minor road exclusion
**Date:** 2026-08-06
**File edited:** problem.tex
**Section:** Scope and Limitations, Delimitations item (a)
**What was added/changed:**
> Expanded delimitation (a) to explicitly name and justify the minor-feeder-road exclusion (previously only the sub-corridor restriction was justified): ties both restrictions to the barrier-protected busway fact, explains the agents' state/reward depends only on in-lane bus dynamics, and notes feeder-road effects are already captured through calibrated per-stop demand distributions.
**Conformity table entry:**
| 14 | "Explain the justification why the minor roads leading to the corridor are no longer considered." | Expanded Delimitation (a) to explicitly justify feeder-road exclusion via the barrier-separated busway argument and the calibrated-demand-distribution argument. | 2.5 (Scope and Limitations) | TBD |
**Commit message:** `E3C14: justify minor feeder-road exclusion in Delimitations`

---
### E3C16 — Figure and table callout sweep
**Date:** 2026-08-06
**File edited:** introduction.tex, methods.tex
**Section:** throughout both chapters
**What was added/changed:**
> Swept all 15 figures/tables (7 in introduction.tex, 8 in methods.tex) for an explicit `\ref{}` callout in surrounding prose. Found 10 with zero references anywhere despite adjacent topical discussion (Figures 1.1, 1.2, 1.4, 3.1–3.5, and Tables tab:sim-parameters, tab:observation-features). Added one short inline reference to each — e.g. "(Figure~\ref{fig:bg-ridership})", "illustrated in Figure~\ref{fig:ctde}", "Table~\ref{tab:sim-parameters} therefore serves as..." — without altering the existing discussion content itself. Confirmed Table 3.1 (tab:notation), the RTC's specific example of a too-thin callout ("Table 3.1 collects the symbols"), is in fact substantially discussed at 5 separate points elsewhere in the chapter where individual symbols are used in context, so no further fix was needed there beyond what already existed.
**Conformity table entry:**
| 16 | "When putting figures and tables, they should also be called and discussed in the paragraphs." | Added explicit `\ref{}` callouts to 10 previously-unreferenced figures/tables, tying each to its existing surrounding discussion. | throughout | TBD |
**Commit message:** `E3C16: add missing figure/table callouts throughout`

---
### E3C18 — Apply 1.5 line spacing
**Date:** 2026-08-06
**File edited:** main.tex
**Section:** preamble and start of document
**What was added/changed:**
> Added `\usepackage{setspace}` to the preamble (it was not previously loaded) and `\onehalfspacing` immediately after `\begin{document}`, applying 1.5 line spacing to the whole manuscript. Applied last, per CLAUDE.md's own guidance, after all content edits in this revision round were complete.
**Conformity table entry:**
| 18 | "Consider using 1.5 line spacing for easier readability." | Added setspace package and \onehalfspacing to main.tex. | preamble | TBD |
**Commit message:** `E3C18: apply 1.5 line spacing`

---
### E3C19 — Add line numbers
**Date:** 2026-08-06
**File edited:** main.tex
**Section:** preamble (near table of contents)
**What was added/changed:**
> The `lineno` package was already loaded; only `\linenumbers` itself was commented out. Uncommented it. Applied last, alongside E3C18, for the same reason.
**Conformity table entry:**
| 19 | "Consider putting line numbers for non-final manuscript versions." | Uncommented `\linenumbers` in main.tex. | preamble | TBD |
**Commit message:** `E3C19: enable line numbers`

---

*Nothing follows.*
