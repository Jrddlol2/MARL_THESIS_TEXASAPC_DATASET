# Prompt — Build a Detailed Workplan: Specific Activities Under Each SO / Expected Output

Turn the thesis's three Specific Objectives and their Expected Outputs into a **detailed workplan of
concrete weekly activities**, laid out in the USTe workplan format (an activity list per objective,
plus a week-by-week Gantt grid colour-coded *accomplished / catch-up / original plan*). The current
workplan names the objectives but has **no specific activities under them** — this fills that gap.
Paste everything below the line into a session with file access to the thesis repo.

---

## Role
You are the thesis author preparing the progress workplan a panel expects: each Expected Output broken
into the actual, checkable steps that produce it, scheduled across the reporting weeks, with an honest
status colour on every step. Ground every activity in work that exists (or will exist) in the repo —
no filler tasks.

## The objectives (verbatim from the manuscript — do not restate loosely; read `problem.tex` to confirm)
**Main Objective.** Evaluate a parameter-sharing MARL controller for dynamic bus scheduling in a
public-data-calibrated simulation of CapMetro Route 801, direction code 6, under baseline and
non-ideal conditions.

- **SO 1 — Environment Construction.** Construct a stochastic traffic simulation environment representing a defined traffic area.
  - **EO 1.1** — A simulation model of a defined operational scope, validated against empirical traffic data.
  - **EO 1.2** — An environment simulator capable of introducing environmental variability through adjustable parameters (non-ideal conditions).
- **SO 2 — Algorithm Implementation.** Develop and implement a MARL approach for dynamic bus scheduling.
  - **EO 2.1** — A formulated agent architecture: bus units as agents with discrete state and action spaces and a continuous reward that punishes irregularity and passenger-service delays.
- **SO 3 — Performance Evaluation Under Ideal and Non-Ideal Conditions.** Evaluate the MARL approach under ideal and non-ideal conditions.
  - **EO 3.1** — Quantitative/statistical assessment under **ideal** conditions (waiting time, travel time, headway CV) against baseline methods.
  - **EO 3.2** — Quantitative/statistical assessment under **non-ideal** conditions, reported as degradation relative to ideal.

## Inputs (resolved from the course syllabus — 2026 term)
1. **Reporting window — W1 = Aug 10, 2026 … W18 = Dec 7–12, 2026**, per the syllabus's Teaching &
   Learning Matrix. Milestones: **MSA 1 / Progress Report 1 = W5 (Sept 7–12)**; MSA 2 = W9 (Oct 5–10);
   MSA 3 = W16 (Nov 23–28); Research Paper & Poster = W17 (Nov 30–Dec 5). W13 (Nov 2–7) is Undas Break.
2. **Reporting line at MSA 1 (end of W5).** Per the team's decision, the scope shown **accomplished** at
   MSA 1 is **through SUMO calibration only (EO 1.1)**; EO 1.2 / SO 2 / SO 3 are scheduled **after** the
   line as *original plan*, paced to MSA 2 (environment + MARL formulation) and MSA 3 (training + results).
   Re-run for later MSAs by moving the reporting line to W9 or W16 and greening the completed rows.
3. **Colour semantics** (sample legend): green = **accomplished**, orange = **catch-up** (planned
   earlier, slipped, being recovered), blue = **original plan** (scheduled, not yet due), gold = MSA/milestone.
4. Output — **Excel `.xlsx`** matching the sample (built with openpyxl); a slide-ready copy is optional.

## Sources for grounding the activities (what actually happened / will happen)
- `docs/progress/` — `FULL_CORRIDOR_UPGRADE_2026-09-02.md`, `PHASE0_CONTROL_STOPS_AND_FIXES_2026-09-03.md`,
  `PROGRESS_AND_CHANGES_2026-09-01.md`, and the Word progress reports.
- `starter/` code as evidence each activity is real: `scripts/extract_sim_inputs.py`,
  `scripts/calibrate_corridor.py`, `envs/corridor_sim.py`, `scripts/run_baseline.py`,
  `scripts/run_disturbances.py`, `scripts/mc.py`, `agents/ddqn.py`, `envs/{reward,obs,marl_env}.py`,
  `scripts/{train_marl,eval_marl}.py`; `results/` (calibration.csv, mc_summary.md) as completion proof.
- `MARL_EXPERIMENT_PLAN_2026-09-03.md` / `NEXT_STEPS_PLAN_2026-09-03.md` for the remaining schedule.

## What to produce

### A. Activity lists (one block per Expected Output)
For **each** EO, write a numbered list of **specific, verifiable activities** — the concrete steps that
yield that output, in execution order, in the style of the sample's "Activities (Modeling Part)"
lists. Each activity is one checkable action tied to an artifact, not a vague heading. Ground them in
the real work; representative (not prescriptive) decomposition:

- **EO 1.1 (validated model):** stream the 3.5 GB APC CSV → dir-6 clean subset (229,421 events) with
  the six-rule filter + SHA-256; reduce per-stop dwell/run-time/distance/demand (`stops.csv`); build
  the 26-stop corridor net in SUMO; solve edge speeds by GEH/RMSPE until GEH < 5 on all segments and
  RMSPE ≈ 0.75%; write `calibration.csv` + the validation figure.
- **EO 1.2 (adjustable non-ideal conditions):** implement demand-responsive dwell (Newell–Potts
  coupling); build the D/S/T/W/B disturbance generators; pre-draw per-seed disturbance fields for
  paired comparison; parameterise the synthetic lognormal weather regime (label synthetic).
- **EO 2.1 (agent architecture):** derive the 5 control stops from the four §3.2.2 criteria; define the
  7-vector observation (Table 3.6) and the 10-action space (5 holds × skip); build the reward-term
  library (irregularity/waiting/skip); implement parameter-shared Double-DQN under CTDE with semi-MDP
  transition assembly; build the config-driven training/eval harness; run the fail-fast gate; conduct
  the reward-coefficient (EO 2.1) study; full domain-randomised training run.
- **EO 3.1 (ideal assessment):** implement NC / Forward-Headway / Even-Headway baselines; run the
  N = 30 matched-seed Monte-Carlo under Stage A (D+T) with bootstrap CIs; evaluate the trained policy
  as the fourth controller on the same cells; tabulate wait / travel / headway-CV vs baselines.
- **EO 3.2 (non-ideal assessment):** run the activation matrix (ablations S/W/B and Stage B); report
  degradation relative to ideal with significance; produce the degradation curve and Marey diagram;
  (future) empirical NOAA precipitation join.

Keep each activity short and testable; the grader should be able to point at a file or result for each.

### B. The Gantt workplan table (USTe format)
Columns: **Specific Objective | Expected Output | Activities | W1 … Wn**. Rules:
- Group rows by objective, with a light section-header row before each block (as the sample uses
  "Modeling" / "Model Verification"); merge/repeat the SO and EO cells down their activity rows.
- One activity per row; shade the week cells the activity spans using the three legend colours by its
  **real status as of the reporting date** (green done, orange slipped/recovering, blue planned).
- Put the **legend** and the **date markers** (start date, reporting-time date) in the header band,
  exactly like the sample.
- Keep the wording of the SO/EO cells faithful to the manuscript.

## Truthfulness (this is graded — do not dress it up)
Colour by what the repo actually shows: SO 1 (both EOs) and the **baseline** parts of SO 3 are
complete (green); the SO 2 apparatus is built and gated (green) with the reward study + full training
still ahead (blue, or orange if already behind the original plan); the **trained-policy** parts of
EO 3.1/3.2 and the NOAA join are upcoming (blue). If an activity slipped, mark it orange and let the
grid show the catch-up honestly — a truthful plan is the point of the reporting colours.

## Guardrails
- Do **not** edit the manuscript `.tex` sources; read them only to quote the SO/EO.
- Weather stays labelled **synthetic**; the NOAA join and any OSM/street-level items are future work,
  scheduled as such, not shown as done.
- Write the workplan file into the repo under `docs/progress/` (e.g. `B3_Workplan.xlsx`); don't touch
  unrelated files.

## Deliverables
1. The activity lists (Section A) — one numbered block per EO.
2. `B3_Workplan.xlsx` — the colour-coded Gantt grid (Section B) with legend + date markers.
3. A one-paragraph status note: how many activities per EO, which are green/orange/blue, and the
   assumed reporting window if the user did not supply one.
