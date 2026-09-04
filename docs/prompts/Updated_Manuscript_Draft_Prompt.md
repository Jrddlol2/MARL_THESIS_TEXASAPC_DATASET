# Prompt — Updated Manuscript Draft (before→after) + Design & Decisions Companion

Produce **two Microsoft Word (`.docx`) documents** for the B3 thesis. (1) An **updated manuscript
draft** of the sections that changed since the revised submission, each presented **before → after**
so the reader sees exactly what changed, with code excerpts inline. (2) A **design & decisions
companion** that gives the reasoning behind every implementation choice, the roadmap thinking, and the
complete code listings. Paste everything below the line into a session with file access to the thesis
workspace. **Ground everything in the artifacts; invent nothing.**

---

## Role
You are the thesis's author and implementation lead. Document A is written in the manuscript's formal
academic register; Document B is a precise engineering narrative (still clear prose, but it may explain
motivations and trade-offs the manuscript would not). Neither alters the submitted manuscript — Document
A is a *draft revision* for the next iteration.

## Authoritative sources (read before writing; quote, don't paraphrase, for the "before" text)
- **Submitted manuscript (the "before"):** LaTeX at `THESIS/MARL/*.tex` (`problem.tex`, `methods.tex`,
  `results.tex`, …); plain-text extract at `…/scratchpad/MANUSCRIPT.txt`; PDF `B3-Post-Revision-Manuscript.pdf`.
- **What changed and why:** `FULL_CORRIDOR_UPGRADE_2026-09-02.md`, `PHASE0_CONTROL_STOPS_AND_FIXES_2026-09-03.md`,
  `MARL_EXPERIMENT_PLAN_2026-09-03.md`, `NEXT_STEPS_PLAN_2026-09-03.md`, the grounding audit
  (`MARL_Manuscript_Grounding_Audit_Prompt.md`), and `DATA_CLEANING.md`.
- **The code (for excerpts and full listings):** `THESIS/MARL/starter/` —
  `scripts/{extract_sim_inputs,calibrate_corridor,run_baseline,run_disturbances,mc,figures,marey,degradation}.py`,
  `envs/{corridor_sim,reward,obs,marl_env}.py`, `agents/ddqn.py`, `scripts/{train_marl,eval_marl}.py`.
- **Results & figures:** `starter/results/mc_summary.md`, `starter/results/figures/*.png`.

## Tooling
Author both with the **docx skill (docx-js)**: `require('docx')` (install only if that fails). US Letter
(`size:{width:12240,height:15840}`), heading styles, justified body, code in a shaded Consolas block
(build multi-line blocks with separate `TextRun`s using `break:1`, never `\n`), tables with dual DXA
widths, `ShadingType.CLEAR` for fills. Save `B3_Updated_Manuscript_Draft.docx` and
`B3_Design_and_Decisions.docx` in the thesis workspace. Verify each after writing (inspect the unzipped
`word/document.xml` for the headings, tables, and code blocks; confirm images embedded).

---

## DOCUMENT A — Updated Manuscript Draft (changed sections only)

**Presentation.** For every changed section, use a **before → after** block:
- a *Submitted* passage: the original manuscript text quoted verbatim (call out the section, e.g.
  "§3.2.5, submitted");
- a *Revised* passage: the updated manuscript-register prose beneath it.
Set the two apart visually (e.g. a light-tinted "Submitted" box and a normal "Revised" block, or a left
rule and a label). Where the submitted text was a placeholder ("to be finalized during implementation"),
quote that placeholder as the "before" and give the resolved text as the "after."

**Sections to cover** (only these; each as before→after):
1. **Data processing (§3.2.5).** Before: the submitted counts. After: the independently reproduced
   229,421-event subset; the thirteen retained columns and why; the six-rule filter and funnel
   (~9,197,694 → 229,421); the SHA-256 provenance. Include the pipeline code excerpt inline.
2. **Corridor construction & calibration (§3.2.1–3.2.3).** Before vs after: the 26-stop
   parameterised corridor, calibration to segment running times (all 25 segments GEH < 5, RMSPE 0.75%),
   and the GEH-on-travel-time reconciliation. Calibration-loop code excerpt inline; calibration figure.
3. **Disturbance layer.** Before vs after: the D/S/T/W/B generators, demand-responsive dwell, pre-drawn
   per-seed fields, and the synthetic-vs-empirical weather labelling. Key code excerpt inline.
4. **Control-stop selection (§3.2.2).** Before: the placeholder ("to be finalized … using the criteria").
   After: the five stops derived from the four criteria on the demand/through-volume profile.
5. **MARL formulation (§3.2.6–3.2.7).** Before vs after where implementation firmed up the wording:
   the 7-vector observation, the 10-action space (α × ΔT, ΔT = H0 = 300 s, + binary skip), and the
   three-term reward with its library of candidate forms (coefficients as the EO 2.1 deliverable).
6. **Baselines, evaluation, and results (Ch. 3–4).** Before vs after: NC/FH/EH at the designated control
   stops, the activation matrix, N = 30 matched-seed Monte-Carlo; the results table and the finding
   (significant under mild disturbance, not distinguishable under weather/Stage B). Include the results
   table and the CV bar chart, Marey diagram, and degradation curve.

**Code in A:** short excerpts inline where the prose refers to them; a "Code Availability" note pointing
to Document B's full listings (do not repeat full scripts in A).

**End of A:** a one-page **Summary of Changes** table (section · what changed · why · evidence).

---

## DOCUMENT B — Design & Decisions Companion

An engineering narrative that answers "how was each piece designed, and why." Structure:

1. **Roadmap & approach.** The three-phase plan (SUMO calibration → Python training → SUMO deployment),
   the Dec-5 target and how scope was cut to protect it, and the fail-fast-gate philosophy. Draw from
   the roadmap/plan docs.
2. **Per-component design + rationale** — for each: what it does, the design choices, the alternatives
   considered, and why the choice was made. Cover: the data pipeline (why those columns, medians, the
   funnel); the corridor parameterisation (why empirical parameterisation over street microsimulation;
   why GEH repurposed to travel time); the disturbance model (why demand-responsive dwell reproduces
   Newell bunching; why pre-drawn per-seed fields make the comparison paired; why the weather regime is
   labelled synthetic); the control-stop derivation (the four criteria applied, the sufficiency check);
   the MARL design (why parameter-shared DDQN under CTDE; the obs/action/reward choices; the
   config-knob "experiment-first, commit-nothing" philosophy; the reward-term candidate library); and
   the evaluation design (why baselines act at the same control stops; the wait-metric reconciliation
   with its cross-check; the ~4–5× parallelisation and the Windows pitfalls resolved).
   Weave in short code excerpts where they clarify a design point.
3. **Methodological refinements & audit.** The grounding audit and the fixes it drove (control-stop
   derivation, wait metric, GEH), framed as strengthening rigour.
4. **Current status & next steps.** Where each objective stands; the training gate now running; the
   reward sweep, full training, MARL-vs-baseline comparison, and empirical weather join ahead.
5. **Appendix — full code listings.** Every script above, in full, each with a one-line header saying
   its role. This is the complete-code home; Document A refers here.

## Grounding & style rules
- Quote the submitted manuscript **verbatim** for every "before"; cite the section.
- Every number must come from the sources (calibration 0.75% RMSPE; funnel 229,421; the N=30 CV table,
  etc.). Mark significance where the sources do (CIs excluding zero); do not overstate.
- Cite code as `file` (and line where useful); paste code faithfully.
- Document A stays in manuscript register (no first-person, no changelog voice in the Revised prose);
  Document B may be more direct about motivation and trade-offs.
- Do not modify the submitted manuscript; both files are drafts/companions.

## Length
A: as long as the changed sections require in before→after form (likely 10–16 pages). B: the design
narrative plus the full-code appendix (length follows the code).
