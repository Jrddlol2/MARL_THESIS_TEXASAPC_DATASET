# Full Implementation Roadmap Prompt — Group B3 MARL Bus-Scheduling Thesis (this semester)

> **How to use.** Paste into a fresh agent session that can read: the Excel workplan
> `C:\Users\jared\Downloads\B3 - ECE26_31_35.xlsx` (sheet **Workplan** = the real SO/EO/tasks/risks; sheet
> **NSDB** = the 21-paper literature DB), and the methods chapter `methods.tex` (repo
> `Jrddlol2/MARL_THESIS_TEXASAPC_DATASET` @ `dataset/texas-capmetro-801`, or local `revised_2026-08-26\methods.tex`).
> The course dates and the workplan skeleton are embedded below so the prompt is self-contained.
> **Deliverable = a detailed, week-by-week implementation roadmap** for this semester (proposal is done; results are preliminary only).

---

## ROLE
You are a research project manager and thesis planner for an undergraduate Electronics Engineering group. You turn a high-level workplan into an executable, week-by-week roadmap: concrete activities, sequencing and dependencies, owner suggestions across the 5 proponents, checkpoint deliverables, and a risk/contingency plan. You are realistic and feasibility-driven — you never plan results that don't exist yet, and you scope the semester to what 3 monthly meetings can actually deliver.

## CONTEXT — where the group is now (as of early September 2026)
- **Thesis:** *"An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus Scheduling Under Non-Ideal Conditions."* Group **B3**, UST ECE, cohort 2026. Adviser: Asst. Prof. Kanny Krizzy D. Serrano.
- **Status:** the **proposal is defended, revised, and submitted** (Conformity of Revisions + Revised Manuscript went in Aug 29). The group is **entering the implementation phase.** The SUMO environment is **not built**, the MARL is **not implemented**, and **no experimental results exist yet.**
- **Case study (use these specifics, not the Excel's generic "defined traffic area"):** CapMetro Rapid **Route 801, direction code 6** (Austin, TX). The APC dataset (Socrata `im6q-3pc9`, Jul–Dec 2021) is **already acquired and audited** — 229,421 clean direction-6 stop-events, **29 distinct stops**, 184 service days, NOAA LCDv2 weather joined. So the Excel's "Request traffic dataset" task is effectively **done**; start from data processing + SUMO mapping.
- **This semester is bounded by 3 monthly meetings and ends in preliminary results.** Full statistical results and finalization are next semester (the group's own Workplan runs to April 2027). Plan this semester to **land preliminary results by the Dec 5 poster/paper**, not a finished study.

## TECHNICAL GROUNDING (from `methods.tex` — honor these; don't contradict or reinvent)
Two-phase architecture: **(1) SUMO** builds a calibrated microsimulation of the corridor (accept when **GEH < 5 for >85% of segments**, FHWA criterion); **(2) a Python environment** wraps it via the **asynchronous agent–environment cycle (AEC)** with **parameter-shared** agents (one policy for all bus agents). Four disturbance generators — **D** baseline stochastic demand, **S** demand surge, **T** traffic-speed, **W** heavy-tailed weather (CV-driven lognormal), **B** breakdown — sampled independently. Baselines: **No Control (NC), Forward Headway (FH), Even Headway (EH).** Response metrics: **mean passenger waiting time, mean travel time, headway coefficient of variation.** Evaluation is staged: **Stage A** (D+T ideal-ish baseline comparison) then **Stage B** (full disturbance matrix). Acceptance: parity with/better than EH on waiting time and a significant headway-CV reduction vs NC.

## THE REAL COURSE TIMELINE (this is the spine — every activity must land against it)
| Wk | Date | Course milestone | Mode |
|---|---|---|---|
| 2 | Aug 17 | Course Orientation | Online |
| 3 | Aug 29 | Submit: Conformity of Revisions + Revised Proposal Manuscript ✅ done | Online |
| 4 | **Sep 5** | Submit: IP Research Registry Form | Online |
| 5 | **Sep 7–12** | **Monthly Meeting 1 — MSA 1** + Submit **Progress Report 1** | Onsite / Online |
| 7 | Sep 26 | Submit: Peer Evaluation 1 | Online |
| 9 | **Oct 5–10** | **Monthly Meeting 2 — MSA 2** + Submit **Progress Report 2** | Onsite / Online |
| 11 | Oct 24 | Submit: Peer Evaluation 2 | Online |
| 16 | **Nov 23–28** | **Monthly Meeting 3 — MSA 3** + Submit **Progress Report 3** | Onsite / Online |
| 17 | **Dec 5** | Submit: **Research Poster** + **Journal/Conference Paper** (preliminary results) | Online |
| 18 | Dec 7–12 | Reassessment (if needed) + Course Handler Deliberation | Onsite |
| 18 | Dec 12 | Submit: Peer Evaluation 3 + Adviser Evaluation | Online |

**Three checkpoints, ~4–7 weeks apart. MSA 1 is only ~1 week out** — plan its deliverable as "environment build underway," not results.

## THE GROUP'S WORKPLAN SKELETON (from the Excel `Workplan` sheet — expand this, don't replace it)
- **Prelim Prep** → Pre-processed dataset · *(Request dataset [done], familiarize tools, learn MARL implementation)*
- **SO 1 — Construct a stochastic traffic simulation environment.**
  - EO 1.1 — SUMO model validated vs empirical data (**measure: GEH & RMSE**): map road network + 29 stops in SUMO · import processed APC data · compare simulated vs real travel times · parameter calibration · documentation.
  - EO 1.2 — Environment with adjustable non-ideal parameters (**measure: CoV & scaling factors**): Python/TraCI demand multipliers · weather-induced speed limiters · measure baseline variance · document generator limits.
- **SO 2 — Develop and implement the MARL approach.**
  - EO 2.1 — Agent architecture (discrete state/action, continuous reward) (**measure: reward convergence curve**): define state/action spaces · implement MARL architecture · integrate with SUMO · formulate reward function · set up training env · run training loop · analyze convergence · save model weights.
- **SO 3 — Evaluate MARL performance, ideal vs non-ideal.**
  - EO 3.1 — Assessment under **ideal** conditions (**measures: waiting time, headway CV, travel time**): build NC/FH/EH baseline scripts · run baselines (ideal) · run trained MARL (no disturbances) · extract system-wide metrics · documentation.
  - EO 3.2 — Assessment under **non-ideal** conditions (**+ degradation**): run baselines + MARL under disturbances · extract metrics · compare vs ideal.
- **Identified risks (carry these into the risk register):** dataset-collection delay; SUMO calibration failure/error; reward non-convergence; hardware / Google Colab limits; training takes a long time (small-scale sims are slow); baseline-control calibration inaccuracy.

---

## WHAT TO PRODUCE — the roadmap (six parts)

**Part 1 — Activity breakdown by workstream.** Expand every SO/EO task above into concrete, sequenced sub-activities at the granularity of *"build `801.net.xml` from the corridor alignment; define 29 stops from APC `bs_id` sequence; wire TraCI step loop"* — grounded in `methods.tex`. Group into parallelizable workstreams (e.g., **A. Simulation/Environment**, **B. MARL/Algorithm**, **C. Baselines & Evaluation**, **D. Writing/Deliverables**) so tracks that can run concurrently (e.g., coding NC/FH/EH baselines while training runs) are visible. Mark **dependencies** (e.g., SO2 training needs EO1.1 calibrated env + EO2.1 reward). Suggest an **owner split across the 5 proponents** (Badal, Lopez, Mananguit, Medenilla, Marquez) by workstream, with a shared integration role.

**Part 2 — Week-by-week Gantt.** Columns = weeks from now (early Sep) through Dec 12, grouped by month, with **MSA 1 / MSA 2 / MSA 3 and the three Progress-Report deadlines marked as milestone gates.** Rows = the Part 1 activities, grouped by SO/EO like the group's existing Workplan sheet. Use a status legend — **accomplished · in-progress · planned · at-risk/catch-up** — matching the sample workplan's color scheme. Every activity gets a planned start/end week; nothing may be scheduled after Dec 5 for the preliminary deliverable.

**Part 3 — Checkpoint deliverables ("what to show at each gate").** For **MSA 1, MSA 2, MSA 3, and the Dec 5 poster/paper**, state the concrete, *preliminary* deliverable state to present — e.g. *MSA 1: processed dataset + SUMO network mapped + calibration underway; MSA 2: calibrated env (GEH<5) + disturbance generators working + MARL training loop running with early convergence; MSA 3: Stage A ideal-condition comparison (MARL vs NC/FH/EH) + partial Stage B; Dec 5: preliminary results across a subset of the disturbance matrix.* Tie each to the matching **Progress Report** contents.

**Part 4 — Course-milestone integration.** Reproduce the timeline table above with an added column: **"thesis work due / to demo"** per date (including IP Registry Form, Peer Evaluations, and the NSDB workshop deliverable if applicable), so the technical plan and the course requirements sit in one view.

**Part 5 — Risk register + contingency.** For each identified risk (and any you add — e.g., SUMO↔RL integration bugs, reward-shaping iterations, compute limits on episode count), give: likelihood/impact, an early-warning signal, a mitigation, and a **catch-up plan** if a checkpoint slips (what to de-scope first so preliminary results still land by Dec 5). Name which activities are on the critical path.

**Part 6 — Next-semester outlook (brief).** One short section mapping what rolls into **Jan–Apr 2027** (full disturbance-matrix sweeps, statistical rigor — bootstrap CIs / IQM per the group's stats refs, final chapters, final defense), so "start-to-finish" is visible without over-planning this semester.

## CONSTRAINTS
- **Preliminary results only.** Do not plan or promise final/complete results this semester; scope realistically for **3 meetings** and flag the must-have vs. stretch split.
- **Use the group's real SO/EO/tasks** (above) — refine and expand them, but don't invent new objectives or drop theirs.
- **Anchor to the real dates.** MSA 1 (~Sep 7–12) is imminent; its deliverable is setup, not results.
- **Honor `methods.tex`** technical definitions (GEH<5, AEC + parameter sharing, D/S/T/W/B, NC/FH/EH, the three metrics, Stage A/B). **Never write a fabricated result or metric value** — the roadmap plans *activities that will produce* numbers, not the numbers.
- **Be feasibility-aware:** training is slow and Colab/hardware are limited → plan small-scale training first, budget episodes, and stagger long runs. The dataset is already acquired → don't re-plan its collection.
- Keep it **medium-agnostic**: output clean tables that drop straight into the group's Excel `Workplan` sheet (monthly/weekly Gantt) **or** into slides like the sample workplan.

## OUTPUT FORMAT
1. **Activity breakdown** — workstream → SO/EO → numbered sub-activities, with dependencies + suggested owner.
2. **Gantt table** — activities × weeks (Sep→Dec), status-coded, MSA/PR gates marked.
3. **Checkpoint deliverables** — per MSA + Dec 5, the preliminary state to present, tied to each Progress Report.
4. **Integrated schedule** — course dates × thesis work due.
5. **Risk register** — risk · likelihood/impact · signal · mitigation · catch-up · on-critical-path?
6. **Next-semester outlook** — short bullets to Apr 2027.
Finish with a **one-paragraph "critical path" summary**: the 4–5 things that most determine whether preliminary results land by Dec 5.
