# AUDIT TRAIL — Group B3 Thesis Revision Work
# Every substantive change to this repo's manuscript/process files, with
# before/after context, why it happened, and which git commit it lives in.
#
# This file is a HISTORICAL LOG, not a task list — for current pending work
# see REVISION_QUEUE.md; for the per-task conformity summary see TRACKER.md.
# Append a new dated entry here every session that edits the manuscript or
# the revision-tracking files themselves (CLAUDE.md/REVISION_QUEUE.md/
# TRACKER.md), including reverts. Do not delete old entries — corrections
# get their own new entry that references the one they fix.

---

## 2026-08-06 — Repo setup
**Commit:** `0eff462` "Add thesis manuscript source and Claude Code revision-tracking setup"

**Before:** No git history existed for the local manuscript. The GitHub repo
[khalil-badal/MARL](https://github.com/khalil-badal/MARL) contained only a
`README.md` (elaborated examiner comments), no `.tex` source.

**After:** `CLAUDE.md`, `REVISION_QUEUE.md`, `TRACKER.md` created, adapted from
a generic template to this repo's actual flat-file structure (`introduction.tex`,
`problem.tex`, `methods.tex`, not a `chapters/` subfolder). Verified against
the actual `main.tex` preamble: citations use `natbib` not biblatex, `lineno`
was already loaded (only `\linenumbers` needed uncommenting for E3C19),
`setspace` was not yet loaded (needed in full for E3C18).

**Why:** Needed a working process before any manuscript edit could start.

---

## 2026-08-06 — GitHub merge
**Commit:** `1001e5d` "Merge remote README.md (examiner feedback) with local thesis source"

**Before:** Local repo (17 files: manuscript + tracking files) and GitHub repo
(1 file: `README.md`) had unrelated histories.

**After:** Merged with `--allow-unrelated-histories`; no filename conflicts
since local had no `README.md`. Pushed to `origin/main`.

**Why:** User confirmed local `Desktop/Thesis` and the GitHub repo are meant
to be the same project; needed to unify them without discarding either side.

---

## 2026-08-06 — RTC decision letter cross-check
**Commit:** `af672bc` "Add verbatim RTC decision letter; fix E3C13 to cover both recency and corridor concerns"

User supplied the actual RTC decision email. Cross-checked it against the
GitHub `README.md` (an elaborated/annotated version of the same comments)
and the repo's `REVISION_QUEUE.md`.

**Added:** `RTC_DECISION_LETTER.md` — verbatim copy of the official email,
declared the source of truth (README.md's elaborated wording is
interpretation, not the original ask, if the two ever diverge).

**Before (REVISION_QUEUE.md, E3C13):**
```
**Instruction:** Add a clarifying sentence where [10] is cited in
1.1 stating it is used as contextual evidence only, not as
EDSA-specific calibration data. In 3.2.3, clarify that EDSA
segment parameters are independently calibrated via GEH/RMSE
(see "Bus Volume Validation via GEH Statistic" and "Speed
Trajectory Calibration via RMSE" subsections in methods.tex).
**Constraint:** Do not remove the [10] citation.
```

**After (REVISION_QUEUE.md, E3C13):**
```
**Instruction:** The RTC letter raises TWO separate concerns about [10],
not one — check both are addressed:
  (a) RECENCY: "[10] is not quite new" — add a sentence noting its
      publication date/vintage and why it remains usable as contextual
      evidence despite its age...
  (b) CORRIDOR MISMATCH: [10] studies a different corridor...
**Constraint:** Do not remove the [10] citation. See RTC_DECISION_LETTER.md
for the verbatim examiner wording.
```

**Why:** The original transcription only captured the corridor-mismatch half
of the examiner's comment on Reference [10]; the letter's actual wording —
"Reference 10 is not quite new **and** simulates a different corridor" — has
two separate concerns. Missing the "not quite new" (recency) half would have
left that part of the comment unaddressed even after E3C13 was marked done.

Also logged the oral-exam Q&A-participation comment as a non-actionable
Team Note in `CLAUDE.md` (not a manuscript edit, so it doesn't belong in
`REVISION_QUEUE.md`, but shouldn't be silently dropped either).

---

## 2026-08-06 — First edit batch: E3C8, E3C15, E4C20, E4C21 completed; E1C1+E2C5+E4C22 drafted then reverted
**Commit:** `01c49bf` "Complete E3C8, E3C15, E4C20, E4C21; revert dataset-description task pending data access"

### E3C8 — Disturbance definitions and independence
**File:** `methods.tex`, start of Section 3.2.6 (Stochastic Disturbance Generators)

**Before:**
```
\subsection{Stochastic Disturbance Generators}
\label{subsec:stochastic-vars}

Four stochastic generators inject variability into the Python environment. ...
```

**After:** A `\paragraph{Disturbance Classes and Independence}` block was
inserted immediately before that paragraph, defining five classes (D, S, T,
W, B) as an itemized list — explicitly distinguishing baseline stochastic
demand (D, always present) from demand surge (S, the controlled variable
layered on top) — followed by a paragraph stating the four generators are
injected independently with no causal chain between them.

**Why:** RTC comment 8 asked for explicit definitions of each disturbance
and the difference between stochastic demand and demand surge; the existing
text described the generators' mechanics but never opened with crisp
definitions or stated independence explicitly.

---

### E3C15 — Simulation parameter summary table
**File:** `methods.tex`, end of Section 3.2.4 (Operating Conditions)

**Before:** Section 3.2.4 ended with "...A condition is a state of the
world; a controller is a choice of algorithm." and went straight into
Section 3.2.5 (Data Processing). No consolidated parameter table existed
anywhere in the chapter.

**After:** A new table (`\label{tab:sim-parameters}`, compiles as Table 3.2)
was inserted, with three grouped sections — Fixed / Swept-Variable / Derived
parameters. Values already established elsewhere in the manuscript were
reused rather than re-derived (stop count $M=24$, fleet size $N\approx12$–$30$,
both cited from Section 1.2.2). Values with no prior basis use `%TODO-VAL`;
data-derived values use `%TODO-DATA`.

**Why:** RTC comment 15 asked for a single table summarizing fixed and
variable parameters with target values; these were previously scattered in
prose across 3.2.4–3.2.7 with no consolidated view.

**Correction made during drafting:** the holding-action parameters ($\Delta
T$, $\Omega$, $|A_i|$) were first mis-sourced to "Section 3.2.3"
(Environment Model Validation); caught and corrected to "Section 3.2.7"
(Action Space, their actual location) before finalizing.

---

### E4C20 — Per-generator simulation mechanics
**File:** `methods.tex`, within each of the four generator subsubsections

**Before (Passenger Demand, excerpt):**
```
...Sampling occurs at the start of each simulation run, producing varied
demand profiles across episodes.
```

**After (Passenger Demand, excerpt):**
```
...Sampling occurs at the start of each simulation run, producing varied
demand profiles across episodes. In implementation, the scaling factor
$f_d \sim \mathcal{N}(1, \sigma_d^2)$ is sampled once per episode at
initialization and applied uniformly to every per-stop, per-time-of-day
arrival rate for the duration of that simulated operating day...
```

Equivalent one-sentence mechanics additions were made to Traffic Delays
($f_s$ applied per-segment-traversal), Weather-Induced Anomalies (fresh
lognormal draw per bus per traversal when $\eta>0$, tying back to the
existing Eq. 3.4/3.5), and Bus Breakdowns (per-timestep Bernoulli trial with
probability $\lambda \cdot dt$, which was implied but never stated before).

**Why:** RTC comment 20 asked for a step-by-step account of how each
disturbance scenario is actually simulated (when sampled, what it affects,
how it propagates) — the prior text described *what* each generator
represents statistically but not *when/how* it fires during a run.

---

### E4C21 — Metric definitions and observation feature table
**File:** `methods.tex`, Section 3.2.9 (Data Analysis Methods) and Section
3.2.7 (State Space and Local Observations)

**Before (3.2.9, opening):**
```
\subsection{Data Analysis Methods}

For each (control strategy, disturbance level) cell, $N \geq 30$
independent Monte Carlo runs are executed...
```

**After (3.2.9, opening):** Added formal one-line definitions with numbered
equations for the three response metrics — mean passenger waiting time
($\bar{W}$, Eq. `eq:waiting_time`), mean total travel time ($\bar{T}$), and
headway coefficient of variation ($CV_h$, Eq. `eq:headway_cv`) — before the
existing "For each (control strategy...)" sentence.

**Before (3.2.7, State Space):** The observation vector's four components
(spatial location, system regularity, passenger demand, environmental
flags) were listed as an itemize block with no table connecting each
feature to its real-world sensor source.

**After (3.2.7, State Space):** Added a table (`\label{tab:observation-features}`,
compiles as Table 3.3) listing each feature, its symbol, its deployment-time
source (AVL/APC/AFC/weather API/incident system), and its simulation-time
source (bus model / generator output), followed by a sentence clarifying all
simulated features are synthetic.

**Why:** RTC comment 21 asked for formal metric definitions and a
description of observation features — both existed only as informal prose
mentions before this edit.

---

### E1C1 + E2C5 + E4C22 — Dataset Description — ADDED THEN REVERTED, same session
**File:** `methods.tex`, Section 3.2.5 (Required Datasets)

**Step 1 — Added (mid-session, not committed):**
```
\paragraph{Dataset Description}

The baseline operating point described above is grounded in the
SafeTravelPH dataset: a crowdsourced mobile application through which
commuters submit trip-level GPS trajectory reports while travelling along
Philippine transit corridors. The record used in this study spans the EDSA
Busway corridor during July 2023. Each submission corresponds to a single
commuter trip and yields a per-trip trajectory log rather than a
fixed-interval sensor feed, so record density varies by segment and time of
day according to rider participation. ...
```
plus a 6-row table ("SafeTravelPH dataset fields and their role in
simulation calibration") and a closing sentence on the DOTr FOI source.
All specific numbers used `%TODO-DATA` placeholders correctly.

**Step 2 — User caught the problem before any commit:** "I should have said
that you should not edit yet anything regarding the dataset. Because, we
still dont have access to it yet." The issue wasn't the numeric
placeholders (those were fine) — it was the *qualitative* claims: describing
SafeTravelPH as a specific kind of app, its record structure, why record
density would vary by rider participation, etc. That's asserting knowledge
of a dataset the group hasn't actually seen yet.

**Step 3 — Reverted:** The entire paragraph, table, and closing sentence
were removed from `methods.tex`, restoring the exact pre-edit text (the
"Corridor bus operational data" itemize block flowing directly into the
"Severe-weather conditions are not estimated..." paragraph).

**After (net, in the pushed commit):** No change from the original
`methods.tex` at this location — the add-then-revert nets to zero diff for
this section. Confirmed via `git diff` before committing that no trace of
the dataset-description content remained.

**Why reverted:** Per `CLAUDE.md` R1 (no data fabrication) and R6 (approved
dataset language), the group has no access to the actual dataset yet, so
even well-hedged qualitative description of "what it looks like" oversteps
what can honestly be claimed right now.

**Follow-up state:** E1C1, E2C5, E4C22 reset to `[ ]` pending in
`REVISION_QUEUE.md`, marked **BLOCKED — no dataset access**, with an
explicit instruction not to resume without the user's go-ahead even though
the task is technically satisfiable using placeholder language alone.
`TRACKER.md` carries the full "Reverted Work" writeup this entry
summarizes. Removing the dataset table also shifted subsequent table
numbers: what would have been Table 3.3/3.4 (E3C15/E4C21's tables) compile
as Table 3.2/3.3 instead — noted in `TRACKER.md` and `CLAUDE.md`, though no
fix was needed in `methods.tex` itself since all in-text references use
`\ref{}`, not hardcoded numbers.

---

*Nothing follows.*
