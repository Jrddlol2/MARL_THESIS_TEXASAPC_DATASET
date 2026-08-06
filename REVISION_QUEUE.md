# REVISION QUEUE — Group B3 Thesis Revision 1
# Updated: 2026-08-06
# Total: 22 tasks | Done: 0 | In Progress: 0 | Pending: 22

---

## [ ] E1C1 — Dataset setup discussion
**Examiner:** 1
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.5
**Instruction:** Add a "Dataset Description" subsection explaining
the SafeTravelPH dataset: what it is, when it was collected, what
fields it contains, how it will be used for SUMO calibration.
Use placeholder language — no numerical values yet.
**Constraint:** No fabricated data values. Use %TODO-DATA tags
where specific statistics will go once dataset is processed.

---

## [ ] E1C2 — Dataset to features mapping table
**Examiner:** 1
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.5 or 3.2.7
**Instruction:** Add a table mapping each raw dataset field to its
derived parameter and its role in the MARL formulation.
Columns: Raw Field | Derived Parameter | MARL Component
**Constraint:** No fabricated values. Keep descriptions general.

---

## [ ] E1C3 — Weather disturbance derivation in research gap
**Examiner:** 1
**Priority:** HIGH
**File:** problem.tex
**Section:** 2.2 (Research Gap)
**Instruction:** Add 2-3 sentences tracing how the weather (W)
disturbance column was derived: from operational evidence in 1.1,
to the literature gap in Table 1.2, to the lognormal
parameterization of Patil et al. [50].
**Constraint:** No new citations beyond what is in thesis_refs.bib.

---

## [ ] E2C4 — Severe weather study in comparison table
**Examiner:** 2
**Priority:** MEDIUM
**File:** introduction.tex
**Section:** 1.2.4 and Table 1.2
**Instruction:** Add Verbich and El-Geneidy [25] to the comparison
discussion noting it covers W and B disturbances under heuristic
(non-MARL) control. Add a footnote to Table 1.2 distinguishing
MARL vs non-MARL entries if needed.
**Constraint:** [25] is already in thesis_refs.bib.

---

## [ ] E2C5 — Dataset contents description
**Examiner:** 2
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.5
**Instruction:** Same scope as E1C1 and E4C22. Consolidate into
one well-written dataset description. Do not duplicate — address
all three comments (E1C1, E2C5, E4C22) in a single revision.
**Constraint:** See E1C1 constraints.

---

## [ ] E2C6 — Traditional method performance under disturbances
**Examiner:** 2
**Priority:** HIGH
**File:** introduction.tex
**Section:** 1.2.1 and/or 3.2.8
**Instruction:** Add discussion of how static scheduling, FH, and EH
degrade under bus bunching, severe weather, and breakdowns. For
1.2.1: explain why static methods have no recovery mechanism. For
3.2.8: add one sentence per baseline explaining its expected failure
mode under non-ideal conditions. (Baseline controllers NC/FH/EH are
defined in methods.tex under "Baseline Controllers for Comparison".)
**Constraint:** Do not add new citations beyond thesis_refs.bib.

---

## [ ] E2C7 — Explicit success criteria
**Examiner:** 2
**Priority:** MEDIUM
**File:** methods.tex
**Section:** 3.2.10
**Instruction:** Make Stage A and Stage B acceptance criteria
visually prominent. Add a dedicated paragraph or formatted list
clearly stating what "successful performance" means for each stage.
**Constraint:** Must match existing criteria already in the text.
Do not invent new thresholds.

---

## [ ] E3C8 — Disturbance definitions and independence
**Examiner:** 3-RRW
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.6 (Stochastic Disturbance Generators)
**Instruction:** Add a definition block at the start of 3.2.6
explicitly defining each disturbance (D, S, T, W, B), clarifying
that generators are injected independently (no causal chain), and
distinguishing stochastic baseline demand (D) from demand surge (S).
**Constraint:** No new citations needed.

---

## [ ] E3C9 — ML/SARL disturbance coverage table
**Examiner:** 3-RRW
**Priority:** HIGH
**File:** introduction.tex
**Section:** 1.2.2 (after SARL section)
**Instruction:** Add a new table showing ML and SARL VSP studies
with S/T/W/B disturbance coverage columns. Include: Wang et al.
[15], Barrera Hernandez et al. [21], Zhao et al. [29], Zhang and
Zheng [30], Verbich and El-Geneidy [25].
**Constraint:** Only cite papers already in thesis_refs.bib.

---

## [ ] E3C10 — Fix Table 1.2 breakdown column
**Examiner:** 3-RRW
**Priority:** HIGH
**File:** introduction.tex
**Section:** Table 1.2
**Instruction:** Verify that the B (breakdown) column in Table 1.2
accurately reflects only Shi et al. [46] as the sole MARL bus
paper modeling discrete breakdowns. Add a clarifying footnote
explaining why Cao et al. [39] (train, not bus) is excluded.
**Constraint:** Do not add papers not in thesis_refs.bib.

---

## [ ] E3C11 — Add missing figure citations
**Examiner:** 3-RRW
**Priority:** MEDIUM
**File:** introduction.tex
**Section:** Figures 1.3 and 1.4
**Instruction:** Add "(authors' illustration)" to captions of
Figures 1.3 and 1.4 if they are original diagrams. Review all
figure captions for consistent attribution.
**Constraint:** Only add "adapted from [X]" if truly adapted.

---

## [ ] E3C12 — Explain Figure 1.3 concepts in text
**Examiner:** 3-RRW
**Priority:** MEDIUM
**File:** introduction.tex
**Section:** 1.2.3
**Instruction:** Add 2-3 sentences after the Figure 1.3 reference
explaining what the per-bus state si and action ai represent in
bus-control terms within the SARL vs MARL comparison.
**Constraint:** Keep consistent with Section 3.2.7 definitions
(State Space / Action Space subsections in methods.tex).

---

## [ ] E3C13 — Clarify Reference [10] scope
**Examiner:** 3-Method
**Priority:** MEDIUM
**File:** introduction.tex and methods.tex
**Section:** 1.1 and 3.2.3
**Instruction:** The RTC letter raises TWO separate concerns about [10],
not one — check both are addressed:
  (a) RECENCY: "[10] is not quite new" — add a sentence noting its
      publication date/vintage and why it remains usable as contextual
      evidence despite its age (e.g., the rainfall-impact mechanism it
      documents is not time-sensitive even if the specific study is older).
  (b) CORRIDOR MISMATCH: [10] studies a different corridor (North Luzon
      Expressway, not EDSA) — add a clarifying sentence where [10] is
      cited in 1.1 stating it is used as contextual evidence only, not as
      EDSA-specific calibration data. In 3.2.3, clarify that EDSA segment
      parameters are independently calibrated via GEH/RMSE (see "Bus
      Volume Validation via GEH Statistic" and "Speed Trajectory
      Calibration via RMSE" subsections in methods.tex).
**Constraint:** Do not remove the [10] citation. See RTC_DECISION_LETTER.md
for the verbatim examiner wording.

---

## [ ] E3C14 — Justify minor road exclusion
**Examiner:** 3-Method
**Priority:** MEDIUM
**File:** problem.tex and/or methods.tex
**Section:** 2.5 (Scope and Limitations) and/or 3.2.1
**Instruction:** Expand the justification for excluding minor
feeder roads. Key points: EDSA Carousel is physically separated
by barriers [5]; agent state/reward depends only on bus dynamics
in the dedicated lane; feeder roads affect arrivals only through
demand distributions already captured by calibration.
**Constraint:** No new citations needed beyond [5].

---

## [ ] E3C15 — Fixed and variable parameters summary table
**Examiner:** 3-Method
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.4 (add after Operating Conditions subsection)
**Instruction:** Add Table 3.2 with three sections: (1) Fixed
simulation parameters with target values or %TODO-VAL tags,
(2) Swept/variable parameters with ranges, (3) Derived parameters
from calibration. See CLAUDE.md panel recommendations for full
column list.
**Constraint:** Use %TODO-VAL for any value not yet confirmed.
Do not fabricate specific numbers.

---

## [ ] E3C16 — Figure and table callout sweep
**Examiner:** 3-Other
**Priority:** MEDIUM
**File:** all chapter files (introduction.tex, problem.tex, methods.tex)
**Section:** throughout
**Instruction:** Read all chapters and confirm every figure and
table is explicitly mentioned and discussed in the surrounding
prose. Add callout sentences where missing. Do not just add
"as shown in Figure X" — add a sentence that actually discusses
the content shown.
**Constraint:** Do not alter existing callouts.

---

## [ ] E3C17 — Add presentation-only figures/tables
**Examiner:** 3-Other
**Priority:** LOW
**File:** to be determined by group
**Section:** to be determined
**Instruction:** Group members must identify which figures/tables
were shown during the defense but are not in the manuscript.
Claude Code will add them once the group provides the content.
**Constraint:** BLOCKED — needs group input first.
%TODO-FIG: Group to provide list of missing presentation figures

---

## [ ] E3C18 — Apply 1.5 line spacing
**Examiner:** 3-Other
**Priority:** LOW (do LAST)
**File:** main.tex
**Section:** preamble
**Instruction:** Add \usepackage{setspace} and \onehalfspacing
after all content edits are complete. (setspace is not currently
loaded in main.tex — see CLAUDE.md "LaTeX packages already in use".)
**Constraint:** DO THIS LAST. Applying early disrupts line
references in TRACKER.md.

---

## [ ] E3C19 — Add line numbers
**Examiner:** 3-Other
**Priority:** LOW (do LAST)
**File:** main.tex
**Section:** preamble
**Instruction:** The `lineno` package is already loaded
(`\usepackage[left]{lineno}`), but `\linenumbers` is commented out
around line 228. Uncomment it after all content edits are complete.
**Constraint:** DO THIS LAST. Same reason as E3C18.

---

## [ ] E4C20 — Simulation mechanics explanation
**Examiner:** 4
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.6 (Stochastic Disturbance Generators)
**Instruction:** For each of the four generators (Traffic Delays,
Weather-Induced Anomalies, Bus Breakdowns, Passenger Demand), add
a sentence describing the step-by-step simulation mechanic: when
is the value sampled, what does it affect, how does it propagate
through the simulation. Should read like an algorithm description
in prose.
**Constraint:** No data values. No new citations needed.

---

## [ ] E4C21 — Metric definitions and feature descriptions
**Examiner:** 4
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.9 (Evaluation Methods) and 3.2.7 (State Space and
Local Observations)
**Instruction:** Add formal one-line mathematical definitions for
the three response metrics (mean passenger waiting time, mean
total travel time, headway CV). Add a small summary table for
the observation vector features listing: Feature | Symbol |
Deployment Source | Simulation Source.
**Constraint:** Keep consistent with existing notation in Table 3.1.

---

## [ ] E4C22 — Dataset contents
**Examiner:** 4
**Priority:** HIGH
**File:** methods.tex
**Section:** 3.2.5
**Instruction:** Consolidated with E1C1 and E2C5. Addressed in
that task.
**Constraint:** See E1C1.

---

*Nothing follows.*
