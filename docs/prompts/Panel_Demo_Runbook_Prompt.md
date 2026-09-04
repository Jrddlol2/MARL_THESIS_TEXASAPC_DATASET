# Prompt — Build a Panel Demo & Defense Runbook (live VSCode + SUMO walkthrough)

Produce a **runbook the author can follow to demo the implementation live to a thesis panel** — which
files to open in VSCode, which commands to run, what appears on screen, and, for every step, a plain
first-person explanation and the reasoning behind it so the author can present and defend the work as
their own understanding. The panelists are experienced researchers who may ask to *see it run* and to
*explain why*. Paste everything below the line into a session with file access to the thesis repo.

---

## Role
You are preparing the author to demonstrate and defend the implementation without notes-from-nowhere.
The deliverable is a runbook that (a) makes every step runnable live on the author's own machine, (b)
teaches the author to narrate each step in the first person with the correct reasoning and literature
grounding, and (c) is complete enough that **a groupmate with only the repository and a clean machine
can reproduce every result and get the same numbers**. The point is genuine mastery and reproducibility:
after using this, the author can open any file, run any step, say what it does and why, and answer a
follow-up — and a teammate who has never seen it run can rebuild it from zero. Nothing is a black box.

**Write for a reader who is not the author.** Assume no hidden setup, no "it just works on my laptop,"
no artifact that only exists because the author made it once. Every prerequisite is stated; every input
is either in the repo or its acquisition is a documented step.

## Hard requirements
- **Every command must actually work.** Run each one yourself in the repo first, on Windows/PowerShell,
  and record the *real* output and the *real* wall-clock time. If a command fails, is too slow for a
  live demo, or depends on a missing artifact, say so and give the fix or a fallback — never ship a
  command you did not run.
- **Nothing that takes too long live.** Full domain-randomized training is hours — do **not** put it in
  the live path. Demo the fail-fast gate / the DDQN self-test / a pre-made convergence figure instead,
  and explain that the full run is offline.
- Weather stays labelled **synthetic**; the NOAA join and OSM overlay are described as future work.
- Do **not** edit the manuscript `.tex`. Write the runbook into the repo under `docs/progress/`.

## Environment to resolve first (put this in the runbook as step 0)
- The code directory (the "starter kit": `starter/` in the repo, `starter_kit/` in the local Desktop
  working copy — confirm which the author will demo from) and that commands run **from that directory**.
- `SUMO_HOME` set and `sumo` / `sumo-gui` on PATH; Python env with `traci, sumolib, numpy, pandas,
  torch, matplotlib`.
- **Pre-generate the SUMO net** — `scripts/calibrate_corridor.py` writes `sumo/corridor.net.xml`, which
  `watch.py`, `run_baseline.py`, and `mc.py` all need. The checklist must ensure this exists before the
  live demo (either committed or regenerated once beforehand).
- The APC raw CSV path (for the data step) — or use the cached `data/route_801_direction_6_clean.csv`
  / `sim_inputs/stops.csv` so the author isn't streaming 3.5 GB live.
- Confirm the figures in `results/figures/` exist for the "show the result" moments.

## What to produce

### A. Pre-flight checklist
A short list the author runs the night before **and** ten minutes before the panel: env vars, a
one-line import check, "does `sumo/corridor.net.xml` exist", a dry-run of each demo command with
expected output, and the location of every fallback screenshot. Include the exact PowerShell to set
`SUMO_HOME` and activate the Python env.

### B. The live demo script (ordered, fast → visual → substantive)
For **each** segment give four things: **① Open / Run** (exact file to open in VSCode or exact command,
copy-pasteable), **② On screen** (what appears, real output snippet, runtime), **③ Say this** (2–4
sentences the author speaks, first person — "Here I filter the raw APC records to Route 801,
direction 6…"), **④ Why / grounding** (the design reason + the RRL that backs it, so a follow-up is
answerable). Suggested segments (adapt to what actually runs):
1. **The data pipeline** — open `scripts/extract_sim_inputs.py`; point at the six-rule filter and the
   thirteen columns; show `sim_inputs/stops.csv` (don't stream the 3.5 GB file live).
2. **Calibration** — run `python scripts/calibrate_corridor.py`; watch it iterate to GEH < 5 /
   RMSPE 0.75%; open `results/calibration.csv` and `results/figures/calibration_validation.png`.
3. **SUMO live (the visual centrepiece)** — run `python scripts/watch.py EH "Weather+Breakdown"`; show
   buses traversing the 26-stop corridor, the **control stops in red**, a bus flashing **amber when it
   holds**, and bunching under weather; mention the on-screen Delay box to slow it down.
4. **Baselines & results** — run `python scripts/run_baseline.py` (or a tiny `python scripts/mc.py 5 4`)
   for NC/FH/EH numbers; open `results/mc_summary.md` for the N = 30 table and the −28% / −18% finding.
5. **The MARL agent** — open `agents/ddqn.py`, `envs/marl_env.py`, `envs/reward.py`; run the DDQN
   self-test `python agents/ddqn.py` (learns ~0.9 vs 0.1 chance); show
   `results/figures/gate1_convergence.png` as evidence the policy learns; state the full training is
   offline.
6. **The figures** — `marey_diagram.png`, `degradation_curve.png`, `mc_headway_cv.png` as the story of
   bunching and degradation.
Mark each segment **[SAFE]** (fast, reliable) or **[RISKY]** (may fail / slow), and put the SAFE ones
first so the demo always has something working.

### C. Code-navigation guide ("know your codebase")
For the files a panelist might ask to open, give: the one-line purpose, the 3–5 lines that carry the
real logic (with line references), and a first-person sentence explaining them. Cover at least
`corridor_sim.py` (the demand-responsive dwell + control hook and the fh/eh laws), `ddqn.py` (the
double-Q update), `reward.py` (the three terms), and `mc.py` (matched seeds + bootstrap CIs). Enough
that the author can scroll to the right place and explain it, not hunt.

### D. Anticipated panel Q&A (be ready for anything, from "where's the data from?" to the hard ones)
20–30 likely questions with tight, first-person answers. **Every answer must name the concrete evidence
the author can point to** — a specific file, table, figure, or citation in the repo/manuscript — so no
answer is hand-waved ("I got X from `sim_inputs/stops.csv`, derived from the APC subset by
`extract_sim_inputs.py`"). Group them:

- **Data provenance & integrity** (expect these first): *Where did the data come from?* — CapMetro
  Automatic Passenger Counter records, July–December 2021, Route 801 direction 6; public/agency source.
  *Why this route and direction?* — point to the route-selection audit
  (`data_audit/…route_selection_audit.json`) and the boardings/service-day figures in the manuscript
  (≈810,309 boardings over 184 days). *How many records, and what did you drop and why?* — the six-rule
  filter, `9.2M → 229,421`, with the reasons. *How do we know it's the real data and reproducible?* —
  the SHA-256 provenance and the cached subset. *What does the data NOT give you?* — passenger arrival
  times, capacity, breakdowns, an authoritative schedule (hence the simulated/synthetic layers). *Units?*
  — `rev_distance` in miles (flagged). *Where does weather come from?* — synthetic lognormal now; NOAA
  LCD join is future work.
- **Tooling** (expect the naive ones too): *What is SUMO / this "SUMO thing"?* — Simulation of Urban
  MObility, an open-source microscopic traffic simulator (cite Lopez et al., 2018); *why SUMO and not a
  commercial tool?* — open, scriptable via TraCI, standard in the field. *What is TraCI / netconvert?*
  *Why Python and PyTorch?* *Why a Double-DQN library vs writing your own?* *What is a Marey diagram?*
  Each answered plainly, as if to a smart non-specialist.
- **Methodology & modelling choices:** why an abstract corridor and not a street-level OSM network; why
  GEH on travel time (with RMSPE binding); why dwell depends on the queue (Newell–Potts); why these five
  control stops (criteria + the sufficiency check); why Double-DQN + parameter sharing + CTDE; why a
  semi-MDP; why matched-seed Monte-Carlo with bootstrap CIs. Ground to the RRL (Rodriguez et al.; Wang &
  Sun; FHWA/DMRB; Daganzo; van Hasselt; Gupta/Christianos; Bradtke).
- **Validity, limits & threats:** is the calibration good enough (GEH<5, RMSPE 0.75% — what do those
  mean)? is synthetic weather legitimate, and what would NOAA change? does the abstract corridor limit
  generalisation? why 30 seeds — is that enough? are the CI-excludes-zero claims real significance?
  What is the Stage-B degradation and why does it motivate the learned controller?
- **Contribution & scope:** what's actually new here vs. the cited MARL-holding work; what is done vs.
  what remains; what could a follow-up study reuse.

Include a short **"if you don't know, say this"** line coaching honest deferral (e.g. "that's outside
what the APC data supports; we treat it as future work") rather than bluffing — panels reward candour.

### E. Failure fallbacks
For every **[RISKY]** step, capture a screenshot or saved output beforehand and store it under
`docs/progress/demo_fallbacks/`, with an "if it doesn't run, show this and say…" line. Include the
common Windows/SUMO gotchas seen in this project (e.g. GUI won't open → check `SUMO_HOME`; net missing
→ run calibrate first; a run stalls → close and show the pre-captured clip).

### F. Two timings
A **3-minute version** (calibration figure → SUMO live → the results table → the degradation story) and
a **full version** (all of B). One-line "if they only give you three minutes, do these three."

### G. Full replication from a clean clone (so a groupmate can reproduce it)
A separate, numbered end-to-end track that assumes **nothing but a fresh Windows machine and the repo**.
It must let a teammate reproduce every committed result, not just re-run cached ones. Cover, in order,
each with the exact command and the expected outcome:
1. **Install the toolchain** — SUMO (and set `SUMO_HOME`, add `sumo`/`sumo-gui`/`netconvert` to PATH),
   Python, and the packages (`traci, sumolib, numpy, pandas, torch, matplotlib`) with a
   `pip install` line or a `requirements.txt`. State exact versions where they matter.
2. **Get the data** — where the CapMetro APC CSV comes from and where to put it, and the exact path to
   set in `scripts/extract_sim_inputs.py`. If the raw file can't be redistributed, say so and point to
   the committed cleaned subset as the fallback starting point.
3. **Regenerate the inputs** — run `extract_sim_inputs.py`; expect the funnel `~9.2M → 229,421` and a
   `sim_inputs/stops.csv` matching the committed one (note the SHA-256 check).
4. **Build & calibrate the corridor** — run `calibrate_corridor.py`; expect GEH < 5 on all 25 segments,
   RMSPE 0.75%, and `results/calibration.csv` matching the committed file.
5. **Reproduce the baselines** — run the Monte-Carlo (`scripts/mc.py N JOBS`); expect
   `results/mc_summary.md` to match within seed noise (the −28% / −18% Stage-A finding, Stage-B
   degradation). State the runtime and core count used.
6. **Reproduce the figures** — run `figures.py`, `marey.py`, `degradation.py`; expect the PNGs in
   `results/figures/`.
7. **Reproduce the MARL evidence** — run the DDQN self-test and the fail-fast gate; state that the full
   domain-randomized training is the long offline step, with its command, its approximate wall-clock,
   and where its checkpoint/curve land.
For each step give the **expected runtime** and a concrete **acceptance check** ("you succeeded if X").
End with a troubleshooting table for the failures this project actually hit (OOM under low RAM; Windows
`ProcessPool` recycle deadlock; matplotlib-in-worker crash; SUMO net missing; bus-stop placement error).
A teammate who completes this track has reproduced the thesis, not just watched it.

## Verification
Run every command in the repo, record real output and timings, and confirm every referenced file
exists. **Actually walk Section G once** — ideally in a fresh copy of the repo — and confirm the
regenerated `stops.csv`, `calibration.csv`, and `mc_summary.md` match the committed artifacts (exact
for the deterministic ones; within seed noise for the Monte-Carlo). Report: which segments are SAFE vs
RISKY, total live runtime for the 3-minute and full demo paths, the end-to-end replication runtime, and
any command that could not be made demo-safe or reproducible (with the fallback provided).

## Deliverable
`docs/progress/DEMO_RUNBOOK.md` (Sections A–F, the live demo), plus a companion
`docs/progress/REPLICATION_GUIDE.md` (Section G, the from-scratch reproduce-and-verify track) — or both
in one file with clear parts — plus `docs/progress/demo_fallbacks/` with the captured
screenshots/outputs. Optionally a one-page printable cheat-sheet (`.docx`) of just the commands and the
"say this" lines for the author to hold during the demo.
