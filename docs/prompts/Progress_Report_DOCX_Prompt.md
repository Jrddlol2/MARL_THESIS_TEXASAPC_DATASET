# Prompt — Manuscript-Style Implementation Progress Report (.docx)

Produce a Microsoft Word (`.docx`) report that documents **everything implemented since the revised
submitted manuscript**, organized by the study's Specific Objectives, showing each objective and what
has been achieved against it — **written in the register of the manuscript itself** (formal academic
prose, not a bullet-point changelog). Paste everything below the line into a session with file access
to the thesis workspace.

---

## Role
You are the thesis's technical author. Write as if drafting a "Chapter 4 — Implementation and
Preliminary Results" (or an Implementation Progress addendum) for the manuscript: measured academic
prose, past tense for completed work, present tense for standing facts, third person, no first-person
"we did X" changelog phrasing. Every claim must be grounded in the artifacts below — **invent nothing**;
if a number or result is not in the sources, do not state it.

## Baseline and authoritative sources
The **starting point is the revised submitted manuscript** (`B3-Post-Revision-Manuscript.pdf`; LaTeX at
`THESIS/MARL/*.tex` — `problem.tex` for objectives/scope, `methods.tex` for Chapter 3; plain-text
extract at `…/scratchpad/MANUSCRIPT.txt`). Report only what has changed or been built *relative to* it.

Draw the implementation facts and numbers from (read these — they contain the exact results):
- `FULL_CORRIDOR_UPGRADE_2026-09-02.md` — full-corridor build, calibration, disturbance suite, MC.
- `PHASE0_CONTROL_STOPS_AND_FIXES_2026-09-03.md` — control-stop derivation, wait-metric & GEH fixes,
  the N=30 NC/FH/EH results at the designated control stops.
- `MARL_EXPERIMENT_PLAN_2026-09-03.md` and `NEXT_STEPS_PLAN_2026-09-03.md` — the MARL harness design.
- `MARL_Manuscript_Grounding_Audit_Prompt.md` (the audit that was run) and the code under
  `THESIS/MARL/starter/` (`scripts/`, `envs/`, `agents/`, `results/mc_summary.md`).

## Output — a `.docx`
**Load the `docx` skill (anthropic-skills:docx) and author the document with it.** Save as
`B3_Implementation_Progress_Report.docx` in the thesis workspace. Use real Word structure: a title,
heading styles (Heading 1 per objective, Heading 2 per sub-topic), justified body paragraphs, at least
one formatted results **table**, and figure captions referencing the generated PNGs
(`results/figures/mc_headway_cv.png`, `calibration_validation.png`). Number sections.

## Structure and content

**Title page / header:** the thesis title, "Implementation and Preliminary Results," date, Group B3.

**1. Overview (1–2 paragraphs).** State that the environment and baseline evaluation are complete and
the MARL apparatus is built and under experiment; frame the report as progress against the three
Specific Objectives since revision.

**Then one numbered section per Specific Objective.** For each, (a) quote the objective and its Expected
Outputs verbatim from the manuscript, then (b) write a prose account of what has been achieved, with the
concrete results woven into sentences (not lists). Use this content backbone — verify each figure
against the sources before writing it:

- **SO1 — Environment Construction (EO 1.1, EO 1.2).** The CapMetro APC subset was independently
  reproduced (229,421 direction-6 events; a full raw scan confirmed 29 stops are the complete
  direction-6 set, of which 26 revenue stops are modelled, the two terminal layovers and one
  post-terminal anomaly excluded and documented). The 26-stop corridor was constructed in SUMO from the
  stop coordinates and calibrated to the empirical segment running times: every one of the 25 segments
  satisfies GEH < 5 and the overall RMSPE is 0.75%. A configurable disturbance layer implements the
  D/S/T/W/B classes (baseline demand, demand surge, traffic-speed variation, heavy-tailed weather,
  vehicle breakdown), with demand-responsive dwell reproducing the demand–headway (Newell) bunching
  mechanism; the weather regime realised so far is the synthetic lognormal stress, labelled as such,
  with the empirical NOAA join identified as remaining work.

- **SO2 — Algorithm Implementation (EO 2.1).** The parameter-shared Double-DQN under CTDE has been
  implemented and unit-tested, together with the environment interface: the seven-component observation
  of Table 3.6, the ten-action space (holding strength α ∈ {0,0.1,0.2,0.3,0.4} scaled by ΔT, with a
  binary stop-skip), and the three-term penalty reward (headway irregularity, passenger waiting,
  degenerate-skip) implemented as a configurable library whose coefficient tuning constitutes the
  EO 2.1 deliverable. The designated control stops were derived from the four Section 3.2.2 criteria on
  the demand/through-volume profile, yielding five stops. Training and evaluation harnesses are in
  place; policy training and the reward-coefficient study are in progress.

- **SO3 — Performance Evaluation (EO 3.1, EO 3.2).** A baseline evaluation against No-Control,
  Forward-Headway and Even-Headway was conducted at the designated control stops over N = 30
  matched-seed Monte-Carlo replications per cell, following the activation matrix (Stage A = D+T; the
  single-class ablations; Stage B = D+T+S+W+B), with bootstrap 95% confidence intervals. Under mild
  non-ideal conditions the holding heuristics significantly reduce headway irregularity (Stage A:
  Forward-Headway −28%, Even-Headway −18%; comparable under surge and breakdown), whereas under weather
  and the combined Stage B their benefit is not statistically distinguishable from No-Control — a
  degradation that establishes the evaluation apparatus and motivates the learned controller. The MARL
  policy's own assessment (its EO 3.1 / EO 3.2 comparison as a fourth controller on the same cells)
  awaits training.

**Results table (required).** Reproduce the N=30 headway-CV table from `results/mc_summary.md` (NC/FH/EH
by scenario, with the paired % change vs No-Control) as a formatted Word table.

**Closing section — "Objectives status at a glance."** A short table: each Specific Objective / Expected
Output × status (Achieved / Partially achieved / In progress) × one-line evidence. Then one paragraph on
remaining work (MARL training and the reward-coefficient sweep; the empirical weather join).

**Optional appendix.** A concise, prose list of the methodological corrections made during
implementation and their justification (the control-stop derivation replacing an ad-hoc choice; the
wait metric reconciled to an expected-wait-under-random-arrivals form with a direct-measurement
cross-check; the GEH-on-travel-time reconciliation) — framed as strengthening rigour, since the
submitted manuscript is not being altered.

## Style rules
- Manuscript register throughout: formal, impersonal, complete sentences; **no bullet-list changelog**
  in the body (bullets allowed only in the status table and optional appendix).
- Report numbers exactly as they appear in the sources; mark statistical significance where the sources
  do (CIs excluding zero). Do not overstate — where a result is not significant, say so.
- Keep it faithful to the manuscript's terminology (Specific Objective, Expected Output, activation
  matrix, Stage A/B, control stop, headway CV).
- Do not modify the manuscript; this is a companion progress report.

## Length
6–10 pages: enough for full prose per objective plus the two tables and figure references, without
padding.
