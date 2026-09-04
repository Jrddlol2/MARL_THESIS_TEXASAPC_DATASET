# Prompt — Progress-Presentation LaTeX Document (a duplicate of the manuscript's format)

Produce a **standalone LaTeX document that reuses the current manuscript's format** (document class,
preamble, packages, bibliography, and academic style) to present **the progress made since the revised
manuscript**, for a panel of experienced researchers. It must read like the thesis itself — proper
prose, equations, figures, code, and literature grounding — and be compilable. **It is a separate
copy: never edit the existing manuscript `.tex` files.** Paste everything below the line into a session
with file access to the thesis repo.

---

## Role
You are the thesis author preparing a rigorous progress document for a defense-style panel. The
audience are professional researchers, so every procedure must be explained, grounded in the
literature where the manuscript grounds it, and defensible. Match the manuscript's register and
LaTeX conventions exactly.

## Hard guardrail — do not touch the live manuscript
Write **only new files** under a new directory `THESIS/MARL/progress_report/` (create it). Do **not**
modify `problem.tex`, `methods.tex`, `results.tex`, `main.tex`, `thesis_refs.bib`, or any existing
`.tex`/`.bib`. Copy what you need (preamble, bib) into the new folder; leave the originals untouched.

## Sources
- **Manuscript LaTeX (to mirror the format + cite):** `THESIS/MARL/main.tex` (document class,
  packages, preamble), the chapter `.tex` files, `title.tex`, and `thesis_refs.bib`. Read `main.tex`
  first to replicate the class, packages, margins, fonts, and citation style. Plain-text of the
  submitted manuscript: `…/scratchpad/MANUSCRIPT.txt`.
- **What changed & why:** `FULL_CORRIDOR_UPGRADE_2026-09-02.md`, `PHASE0_CONTROL_STOPS_AND_FIXES_2026-09-03.md`,
  `MARL_EXPERIMENT_PLAN_2026-09-03.md`, the grounding audit, `DATA_CLEANING.md`.
- **Code (for excerpts + the appendix):** `THESIS/MARL/starter/` —
  `scripts/{extract_sim_inputs,calibrate_corridor,run_baseline,run_disturbances,mc,figures,marey,degradation,train_marl,eval_marl}.py`,
  `envs/{corridor_sim,reward,obs,marl_env}.py`, `agents/ddqn.py`.
- **Figures:** `THESIS/MARL/starter/results/figures/` —
  `calibration_validation.png`, `mc_headway_cv.png`, `mc_wait.png`, `marey_diagram.png`,
  `degradation_curve.png`, `gate1_convergence.png`. Copy the ones you use into
  `progress_report/figures/`.
- **Results numbers:** `starter/results/mc_summary.md`.

## Output
`progress_report/progress_report.tex` (main), plus `progress_report/sections/*.tex` if the format
splits chapters, `progress_report/refs.bib` (a copy of `thesis_refs.bib` you may extend), and
`progress_report/figures/`. It must compile (pdfLaTeX + BibTeX/biber, matching `main.tex`). Reproduce
the manuscript's document class, packages, and title style so the PDF looks like the thesis.

## Content — progress since the revised manuscript (scope)
Open with a short framing paragraph ("progress since the revised submission"). Then one section per
area below, in manuscript prose, each with: what was done, the procedure and its **grounding**, the
relevant **equation(s)**, a short **code excerpt**, and the **figure/result** where applicable.
1. **Data processing** — reproduction of the 229,421-event dir-6 subset; the thirteen retained columns
   and why; the six-rule filter and funnel (~9.2M → 229,421); SHA-256 provenance; derivation of the
   per-stop simulation inputs. Excerpt: the filter + aggregation.
2. **Corridor construction & calibration** — empirical parameterisation of the 26-stop corridor; GEH
   on travel time + RMSPE (all segments GEH<5, RMSPE 0.75%). Equations (GEH, RMSPE, speed solve),
   the calibration figure, a code excerpt.
3. **Disturbance layer** — D/S/T/W/B with demand-responsive dwell, per-seed paired fields, synthetic
   weather labelling. Equations (dwell, weather/traffic factors).
4. **Control-stop selection** — the four §3.2.2 criteria applied to the demand/through-volume profile
   → five control stops; the sufficiency check.
5. **MARL formulation & harness** — parameter-shared DDQN under CTDE; the 7-vector observation, the
   10-action space, the three-term reward library; the config-driven training/eval harness. Equations
   (reward, event-discounted return, Double-DQN target), the convergence figure.
6. **Baseline results** — NC/FH/EH at the control stops, N=30 matched-seed MC, activation matrix;
   the results table + the CV bar chart, Marey diagram, and degradation curve; the finding (control
   degrades under weather/Stage B).
End with an "Objectives status" summary and remaining work.

## Grounding (RRL)
Cite the same related work the manuscript uses, via the copied bib — Rodriguez et al. (cooperative
DDQN holding-and-skipping), Wang & Sun (holding under stochastic conditions), Patil et al. (SUMO
calibration / lognormal weather), Wangsun (abstract-corridor parameterisation), and the GEH/FHWA and
even-headway (Daganzo) sources. **Read `thesis_refs.bib` for the exact citekeys** and use them. If a
claim needs support not in the bib, add a new, real entry to `refs.bib` (do not fabricate references —
use genuine, verifiable ones) and cite it. Ground each *procedure* (not just the intro): e.g., the GEH
acceptance criterion to FHWA/Patil, the abstract-corridor choice to Wangsun/Rodriguez, DDQN+CTDE to
Rodriguez/Wang & Sun.

## Code
Use the manuscript's code-listing package if it has one (`listings`/`minted`); otherwise `lstlisting`
with a clean monochrome style. **Inline excerpts** in the body where they illustrate a procedure
(short, the key lines), and a **full-listings appendix** with every script above, read verbatim from
the working tree, each headed by its path and one-line role.

## Style rules
- Match the manuscript's register: formal, impersonal, complete sentences; section/equation numbering
  in its style. No changelog/bullet voice in the body.
- Numbers exactly as in the sources (RMSPE 0.75%; funnel 229,421; the N=30 CV table; the −28%/−18%
  reductions with significance where CIs exclude zero). Do not overstate; where a result is not
  significant, say so.
- Every figure captioned and referenced in text; every equation's symbols defined.
- Compile-clean: no undefined references, no missing figures.

## Verification
After writing, compile it (or at minimum check that every `\includegraphics` file exists in
`progress_report/figures/`, every `\cite` key exists in `refs.bib`, and the listings files are found).
Report the section list, figure/table count, and any unresolved cites.
