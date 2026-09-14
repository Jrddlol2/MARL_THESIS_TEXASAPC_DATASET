# MARL Bus Scheduling — Group B3

**An Evaluation of Multi-Agent Reinforcement Learning for Dynamic Bus Scheduling
Under Non-Ideal Conditions: A CapMetro Rapid Case Study**

University of Santo Tomas · ECE 21126
Badal · Lopez · Mananguit · Marquez · Medenilla
Adviser: Asst. Prof. Kanny Krizzy D. Serrano, MSc

---

## 1. What we are doing, in plain English

Buses on a frequent route bunch up. One falls slightly behind, picks up the
passengers the bus in front would have taken, falls further behind, and soon two
buses arrive together followed by a long gap. Passengers wait longer even though
the same number of buses are running.

The usual fix is a **holding rule**: make an early bus wait a little at a stop so
the spacing evens out. Those rules are simple and fixed.

**We are testing whether a machine-learning controller can do it better** — one
that watches the gap ahead, the gap behind, how full the bus is and how many
people are waiting, and then decides how long to hold. Each bus is its own agent,
and they all share one learned policy.

The point of the thesis is the **"non-ideal conditions"** part: does the learned
controller still hold up when it rains, when a crowd surges, when a bus breaks
down?

**Case study:** CapMetro Rapid Route 801 in Austin, Texas, direction code 6
(Tech Ridge → Southpark Meadows), using six months of real automatic passenger
counter (APC) data, July–December 2021.

---

## 2. Where we are right now (2026-09-14)

| | Status |
|---|---|
| Proposal | Defended, revised, submitted 2026-08-29 |
| Dataset acquired and cleaned | **Done** — 229,421 stop events, checksummed |
| Weather joined | **Done** — 100% of events matched to NOAA |
| Corridor built in SUMO | **Done** — 27 stops, 26 road segments, real road geometry |
| Corridor calibrated | **Done** — tested on held-out days: RMSPE 3.08%, GEH < 5 on 26/26 segments |
| Simulator checked against real buses | **Done** — bunching, loads and stop service (§4) |
| Baseline controllers (NC / FH / EH) | **Done** — 30 paired Monte Carlo runs per scenario |
| MARL agent | **Built and tested; must be retrained** on the current simulator (§6) |
| Results / Discussion chapters | **Not written** |

**Milestones**

| | When | Scope |
|---|---|---|
| MSA1 | Sep 7–12, 2026 | Dataset + corridor + calibration |
| MSA2 | Oct 5–10, 2026 | Empirical extraction, disturbances, MARL formulation |
| MSA3 | Nov 23–28, 2026 | Training and evaluation |

Poster and paper due **Dec 5, 2026**. Results this semester are **preliminary**;
final results run Jan–Apr 2027.

---

## 3. The whole project in one picture

```
  THE RAW FILE          3.7 GB, 9,197,694 rows, every CapMetro route
        |
        |   scripts/pipeline/          keep only 801 direction 6; attach weather
        v
  CLEAN DATA            229,421 stop events, each with a weather reading
        |
        |   starter/scripts/           fit demand, dwell and running times; build the road
        v
  SIMULATED CORRIDOR    27 stops in SUMO, real geometry, variability fitted from APC
        |
        |   starter/envs/              drive buses down it; add surge, weather, breakdowns
        |   starter/agents/            let the agent decide when to hold
        v
  RESULTS               how bunched were the buses?  ->  figures  ->  slides
```

**`scripts/` is the data half. `starter/` is the simulation half.**

---

## 4. What we have found so far

### Is the simulator realistic?

Everything the simulator randomises on an ordinary day (demand, dwell, running
time, late or early trip starts) is **fitted from the APC data**. It is checked on
service days it was not fitted on (`starter/results/validation/`):

| Check | Real buses | Simulator (No-Control) |
|---|---|---|
| Segment running time, held-out days | — | RMSPE 3.08%, GEH < 5 on 26/26 |
| Headway CV (bunching), whole corridor | 0.504 | 0.556 (about 10% high, in the second half) |
| Headway CV at the first stop | 0.352 | 0.357 |
| Bunching stop by stop | — | r = 0.87 |
| Share of trips that stop at a quiet stop | 64% | 69% (r = 0.96) |
| Riders on board along the route | APC `max_load` | about 2 lower, same shape (r = 0.99) |

### Baselines

30 paired runs per scenario, 10-minute headway, holds capped at 120 s (as in the
RRL), one bus removed in a breakdown. Lower headway CV = more evenly spaced buses.

| Scenario | No Control | Forward-Headway | Even-Headway |
|---|---|---|---|
| Stage A — ordinary day (demand + traffic) | 0.556 | 0.396 (−29%) | **0.342** (−38%) |
| + surge | 0.596 | 0.427 (−28%) | **0.371** (−38%) |
| + weather | 0.865 | 0.798 (−8%) | 0.786 (−9%) |
| + breakdown (one bus removed) | 0.564 | 0.423 (−25%) | **0.370** (−34%) |
| Stage B — everything at once | 0.876 | 0.804 (−8%) | 0.796 (−9%) |

All reductions are significant (95% CIs exclude zero). A 240 s cap gives −9/−12% in
Stage B and three breakdowns give −8/−9%, so neither changes the conclusion.

**What this means:** fixed holding rules work well on an ordinary day but lose most
of their effect under severe, combined disturbance. That gap is what the MARL
controller has to close.

Full write-up: [`docs/progress/WEEK2_SIMULATOR_VS_REALITY_2026-09-14.md`](docs/progress/WEEK2_SIMULATOR_VS_REALITY_2026-09-14.md).

---

## 5. What's next

**Before training (these change what the agent learns):**

1. **Event-based discount.** `methods.tex` discounts by elapsed time (e^(−βt), Bradtke & Duff);
   `agents/ddqn.py` uses a flat γ = 0.99.
2. **Save checkpoints during training** (every 50 episodes, resumable, best model kept). A run takes
   about 3 hours; the earlier run saved nothing.
3. **Write down the pass mark first.** Proposed: greedy evaluation over seeds 0–29 beats
   Forward-Headway in Stage A (0.396); Even-Headway (0.342) is the stretch goal.
4. **Breakdown flag.** It is currently 1 for every bus once any bus breaks down; the manuscript says
   "downstream incident".

**Manuscript text that no longer matches the code:**

- `methods.tex:18, 38` say training runs in a separate lightweight Python simulator. It runs in
  SUMO (about 13 s per episode).
- `methods.tex:291` says a chronological calibration/test split. The code alternates service days.
- `methods.tex:69–83` declare GEH on bus counts and RMSE. The code uses GEH on running times and RMSPE.
- `results.tex`, `discussion.tex`, `futurework.tex` are template text from another thesis (§7).

Open risks: [`docs/planning/RISK_REGISTER_MSA2_2026-09-13.md`](docs/planning/RISK_REGISTER_MSA2_2026-09-13.md).
Manuscript to-do list: [`docs/planning/GTFS_FINDINGS_CHANGE_LIST_2026-09-12.md`](docs/planning/GTFS_FINDINGS_CHANGE_LIST_2026-09-12.md).

---

## 6. Folder guide

| Folder | What's in it | In Git? |
|---|---|---|
| *(root)* | The LaTeX manuscript (`main.tex` + chapters, `thesis_refs.bib`), `README.md`, `CLAUDE.md`. Kept at root for Overleaf | yes |
| `Figures/` | Figures used by the manuscript | yes |
| `config/` | `texas_capmetro_801.json` — every data-pipeline setting | yes |
| `scripts/` | **The data half.** Raw download → cleaned data → weather attached | yes |
| `starter/` | **The simulation half.** Corridor, SUMO, controllers, MARL, results, figures | yes |
| `data/raw/`, `data/processed/` | The 3.7 GB APC snapshot, the clean subset, NOAA tables | **no** — too big (§9) |
| `data/audit/` | **The evidence.** Checksums, queries, row counts, coverage results | yes |
| `docs/progress/` | The current write-up and the MSA deliverables (.docx) | yes |
| `docs/planning/` | Risk register, manuscript change list, experiment plan, roadmap | yes |
| `docs/reference/` | Code walkthroughs, the code demo guide, data-cleaning notes | yes |
| `docs/prompts/` | Reusable prompts | yes |
| `docs/archive/` | Superseded notes, runbooks and figures, kept for the record | yes |
| `revision/` | The proposal-revision workflow: RTC letter, revision queue, tracker, audit trail | yes |
| `reports/` | Reference and dataset audit reports | yes |
| `RRL/` | `sources.md` maps bib keys to source PDFs (the PDFs stay outside the repo) | index only |
| `submissions/` | **Frozen** as-submitted checkpoints — never edit | yes |

---

## 7. Code guide

### The manuscript (root)

```
main.tex           preamble and \input list — do not restructure
title.tex          title page
introduction.tex   Ch 1 — Introduction and Literature Review   OURS
problem.tex        Ch 2 — Problem Statement                    OURS
methods.tex        Ch 3 — Methods and Research Design          OURS
thesis_refs.bib    bibliography
```

🚨 **`results.tex`, `discussion.tex` and `futurework.tex` are NOT OURS.** They are
leftover template text from an unrelated neuroscience thesis. They are commented
out of `main.tex`. **Delete and rewrite; do not edit.**

### `scripts/` — the data half

More detail in [`scripts/pipeline/README.md`](scripts/pipeline/README.md).

| File | What it does |
|---|---|
| `pipeline/common.py` | Shared plumbing: paths, config, checksums, reading the snapshot, and **the six cleaning rules** |
| `pipeline/audit_route_selection.py` | Compares Route 801 against 803; produces the cleaning-funnel numbers |
| `pipeline/01_extract_dir6.py` | Extracts the 229,421 clean rows. **← THE STUDY SET** |
| `pipeline/02_prepare_weather.py` | Reads both NOAA files and fixes the local-standard-time offset |
| `pipeline/03_join_weather.py` | Attaches the nearest weather reading to every stop event |
| `pipeline/04_gtfs_gate.py` | Records the direction-label evidence |
| `pipeline/run_all.py` | Runs the steps in order |
| `texas_capmetro_pipeline.py` | **Archived reference** — the original portal-download version |

### `starter/` — the simulation half

Everything under `starter/` runs **from the `starter/` folder**.

**Simulator and agent**

| File | What it does |
|---|---|
| `envs/corridor_sim.py` | **THE HEART.** Runs the corridor in SUMO with any controller. Every experiment calls `simulate()` |
| `envs/obs.py` | The 7 numbers a bus "sees" (headways, load, queue, weather flag, breakdown flag) |
| `envs/reward.py` | The 3 penalties that score the agent, plus action decoding |
| `envs/marl_env.py` | Plugs the network into `corridor_sim` as a controller; `Config` holds every experiment knob |
| `agents/ddqn.py` | The shared Double-DQN network, replay buffer, ε-greedy |

**Building and checking the corridor**

| File | What it does |
|---|---|
| `scripts/extract_sim_inputs.py` | Clean rows → per-stop averages (`sim_inputs/stops.csv`) |
| `scripts/extract_route_shape.py` | The real road path from OpenStreetMap |
| `scripts/fit_variability.py` | **Fits demand, dwell, running-time spread and trip-start spread from APC** → `sim_inputs/fitted/`; splits service days into calibration and test days |
| `scripts/build_real_net.py` | Builds the SUMO network and calibrates it on calibration days → `results/calibration_real.csv` |
| `scripts/validate_simulator.py` | Bunching, loads and stop service vs real buses → `results/validation/` |
| `scripts/test_simulator.py` | 13 pass/fail checks of the control rules (FH, EH, skip, stop serving) |

**Running experiments**

| File | What it does |
|---|---|
| `scripts/mc.py` | All scenarios × NC/FH/EH × 30 seeds in parallel → `results/mc_results.csv`, `mc_summary.md` |
| `scripts/train_marl.py` | Trains the agent → `experiments/<name>/` |
| `scripts/eval_marl.py` | Evaluates a trained agent next to NC/FH/EH on seeds 0–29 |
| `scripts/watch.py` | Opens **sumo-gui** to watch buses bunch and be held |
| `scripts/watch_gate.py` | Live text view of a training run |

**Figures** (`results/figures/`)

| File | What it draws |
|---|---|
| `scripts/_figstyle.py` | Shared styling, imported by all the others |
| `scripts/figures.py` | Calibration, load and stop-service validation; baseline bar charts |
| `scripts/marey.py` | Time–space (Marey) diagram — bunching shows as converging lines |
| `scripts/degradation.py` | Headway CV vs weather strength, per controller |
| `scripts/convergence.py`, `plot_curve.py` | Training curves |
| `scripts/figures_datacleaning.py`, `figures_weather.py` | The MSA1 data figures |

**Data and results**

| Path | What it is |
|---|---|
| `corridor.txt` | **The 27 modelled stops, in order** |
| `sim_inputs/` | Per-stop averages, stop coordinates, road shape |
| `sim_inputs/fitted/` | **What the simulator uses:** fitted stop parameters, dwell model, trip-start spread, calibration/test days |
| `sumo/` | SUMO networks; the simulator uses `corridor_real.net.xml` and `stops_real.add.xml` |
| `results/calibration_real.csv` | Per-segment running time, observed vs simulated, calibration and test days |
| `results/validation/` | Simulator vs real buses |
| `results/mc_summary.md` | **The baseline table** (`_hold240`, `_breakdowns3` = checks) |
| `results/archive/` | Results from earlier simulator versions |
| `legacy/` | Old scripts kept for reference, not used by anything current ([`legacy/README.md`](starter/legacy/README.md)) |
| `experiments/` | Training runs (not in Git) |

---

## 8. "I want to…" — where to look

| I want to… | Open / run |
|---|---|
| See the cleaning rules | `scripts/pipeline/common.py` → `clean_where()` |
| See where 229,421 comes from | `data/audit/texas_capmetro/route_selection_audit.json` |
| See the calibration result | `starter/results/calibration_real.csv` |
| See how realistic the simulator is | `starter/results/validation/simulator_validation_summary.json` |
| See the baseline results | `starter/results/mc_summary.md` |
| Change how the simulation behaves | `starter/envs/corridor_sim.py`, PART 2 settings |
| Change what the agent sees or is scored on | `starter/envs/obs.py`, `starter/envs/reward.py` |
| Change training settings | `starter/envs/marl_env.py` → `Config` |
| Understand the simulator line by line | [`docs/reference/CODE_WALKTHROUGH_SIMULATOR.md`](docs/reference/CODE_WALKTHROUGH_SIMULATOR.md) |
| Prepare a code demo for the panel | `docs/reference/B3_Code_Demo_Guide.docx` |
| Watch buses move on screen | `cd starter` then `python scripts/watch.py EH StageB` |

---

## 9. Getting the data (do this first on a new machine)

The pipeline **never downloads anything** — it reads our archived copies. Those
files are too big for Git, so a fresh clone does not have them. You need three.

### 1. The APC snapshot (3.7 GB)

From the Texas Open Data portal, dataset **`im6q-3pc9`**:
<https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9>

Use the portal's Export button to download the full CSV, then save it as:

```
data/raw/capmetro/APC_Raw_July_2021_December_2021_full.csv
```

Verify before using it:

```
rows    9,197,694
bytes   3,708,582,383
sha256  4c2cb9c27355dd8fe1f94ae0d06bc12726c3860153b48ec7f6dad6b1142bc8f7
```

```bash
sha256sum data/raw/capmetro/APC_Raw_July_2021_December_2021_full.csv
```

If the hash does not match, stop — do not run the pipeline on it.

### 2. The two NOAA weather files (~16 MB total)

```
data/raw/noaa/LCD_USW00013958_2021.csv    Camp Mabry (primary)
    https://www.ncei.noaa.gov/oa/local-climatological-data/v2/access/2021/LCD_USW00013958_2021.csv
    8,531,389 bytes · sha256 8d2aafedde6f78ef...

data/raw/noaa/LCD_USW00013904_2021.csv    Austin-Bergstrom (cross-check)
    https://www.ncei.noaa.gov/oa/local-climatological-data/v2/access/2021/LCD_USW00013904_2021.csv
    7,645,753 bytes · sha256 fdd8c27f825fb077...
```

Full checksums are in `data/audit/texas_capmetro/weather_source_audit.json`.

### 3. Nothing else

Everything downstream is generated. **Faster option:** ask a teammate for the
files rather than re-downloading 3.7 GB. Check the hashes either way.

---

## 10. How to run things

**Install:** Python 3.12, SUMO 1.27.1 with `SUMO_HOME` set, then
`pip install -r starter/requirements.txt` (numpy, pandas, matplotlib, torch).

```bash
# ---- the data half (from the repo root) ----------------------------------------
python scripts/pipeline/run_all.py                 # ~100 s; rebuilds the clean data and evidence

# ---- the simulation half (from starter/) -----------------------------------------
cd starter
python scripts/fit_variability.py                  # ~2 min  -> sim_inputs/fitted/
python scripts/build_real_net.py                   # ~15 s   -> SUMO network + calibration_real.csv
python scripts/test_simulator.py                   # ~2 min  -> 13 PASS lines
python scripts/validate_simulator.py               #         -> results/validation/
python scripts/mc.py 30 10                         # ~1.5 h on 10 workers -> the baseline table
python scripts/figures.py                          # redraw the figures

# MARL
python scripts/train_marl.py --episodes 3 --eval_every 3 --name smoke     # ~2 min plumbing check
python scripts/train_marl.py --episodes 800 --name gate                   # ~3 h
python scripts/eval_marl.py --ckpt experiments/gate/checkpoint.pt         # vs NC/FH/EH, seeds 0-29

# watch buses move
python scripts/watch.py EH StageB
```

For quick tests of `mc.py`, always add `--tag NAME` so the committed results are not overwritten.

---

## 11. Things that will confuse you (they confused us)

**1. Three `.tex` chapters are someone else's thesis.** See §7.

**2. There are two folders on the Desktop.** `THESIS/MARL/` is this repo and is
canonical for all code. `THESIS Claude/` is a workspace holding the report and deck
generators; the demo guide is built there and copied into `docs/reference/`.

**3. The cleaning rules are implemented three times, on purpose.** As the query the
Texas portal runs (`clean_where`), as a Python function for the offline path
(`passes_clean_rules`), and in pandas inside `extract_sim_inputs.py`. All three give
229,421 rows — that agreement is a cross-check. The canonical one is `clean_where()`.

**4. "Direction 6" is a vendor code, not a compass direction.** Overlaying our stop IDs
on the current GTFS feed shows it is southbound; the 2021 schedule snapshot is not
publicly archived. See `data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md`.

**5. APC writes a record only when the doors open.** A stop with no record on a trip
was passed, not missing data. So demand is counted **per trip**, not per record, and
running time is only taken between consecutive stops.

**6. `rev_seconds` already contains the stop's dwell time.** It is recorded door-open
to door-open. Pure running time is `rev_seconds - dwell_time`.

**7. `rev_distance` units are unresolved.** Corridor geometry comes from GPS instead,
so nothing depends on it — but do not use it for speed without checking.

**8. `sumo/corridor.*` is the old straight-line network.** The simulator uses
`sumo/corridor_real.*`.

---

## 12. The rule that matters most

**Never write a number you cannot trace to a file.**

Every figure in the deck and manuscript comes from `data/audit/texas_capmetro/` or
`starter/results/`. If you need a number, take it from there or regenerate it. Do not
retype it off a slide.

---

## 13. Git

Default branch `dataset/texas-capmetro-801`, remote **`jared`**
(`Jrddlol2/MARL_THESIS_TEXASAPC_DATASET`). There is also an `origin` pointing at
`khalil-badal/MARL` — do not push there by accident.
