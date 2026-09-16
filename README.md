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

## 2. Where we are right now (2026-09-16)

| | Status |
|---|---|
| Proposal | Defended, revised, submitted 2026-08-29 |
| Dataset acquired and cleaned | **Done** — 229,421 stop events, checksummed |
| Weather joined | **Done** — 100% of events matched to NOAA |
| Corridor built in SUMO | **Done** — 27 stops, 26 road segments, real road geometry |
| Corridor calibrated | **Done** — tested on held-out days: RMSPE 3.08%, GEH < 5 on 26/26 segments |
| Simulator checked against real buses | **Done** — bunching, loads and stop service (§4) |
| Baseline controllers (NC / FH / EH) | **Done** — 30 paired Monte Carlo runs per scenario |
| MARL agent | **Training now** — 800 episodes with randomized disturbances, `starter/experiments/dr1/` (§5) |
| Results chapter | **Drafted** from measured outputs; the MARL section waits on the run |
| Discussion / Future Work chapters | **Not written** (still template text from another thesis) |

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
| Same, with a date-order split instead | — | RMSPE 6.83%, GEH < 5 on 26/26 ([why](starter/results/validation/SPLIT_ROBUSTNESS.md)) |
| Headway CV (bunching), whole corridor | 0.504 | 0.556 (about 10% high, in the second half) |
| Headway CV at the first stop | 0.352 | 0.357 |
| Bunching stop by stop | — | r = 0.87 |
| Share of trips that stop at a quiet stop | 64% | 69% (r = 0.96) |
| Riders on board along the route | APC `max_load` | about 2 lower, same shape (r = 0.99) |

### Baselines

The manuscript's evaluation matrix (`methods.tex`, Stage A / Stage B evaluation). 30 paired runs
per scenario, 10-minute headway, holds capped at 120 s (as in the RRL), one bus removed in a
breakdown. Lower headway CV = more evenly spaced buses.

| Scenario | No Control | Forward-Headway | Even-Headway |
|---|---|---|---|
| Stage A — ordinary day (demand + traffic) | 0.556 | 0.396 (−29%) | **0.342** (−38%) |
| + surge | 0.596 | 0.427 (−28%) | **0.371** (−38%) |
| + weather (observed ordinary rain) | 0.559 | 0.400 (−28%) | **0.346** (−38%) |
| + breakdown (one bus removed) | 0.564 | 0.423 (−25%) | **0.370** (−34%) |
| Stage B — everything, observed rain | 0.609 | 0.458 (−25%) | **0.404** (−34%) |

**Stage B weather sweep** — everything on, with the labelled synthetic weather stress η on top of
observed rain (`results/stageB_weather_sweep.csv`, figure `stageB_weather_sweep.png`):

| Weather | No Control | Forward-Headway | Even-Headway |
|---|---|---|---|
| observed rain only | 0.609 | 0.458 (−25%) | 0.404 (−34%) |
| η = 0.3 | 0.685 | 0.574 (−16%) | 0.534 (−22%) |
| η = 0.6 | 0.820 | 0.742 (−9%) | 0.725 (−12%) |
| η = 0.8 *(earlier headline)* | 0.876 | 0.804 (−8%) | 0.796 (−9%) |
| η = 1.0 | 0.904 | 0.836 (−8%) | 0.832 (−8%) |
| η = 1.3 | 0.929 | 0.862 (−7%) | 0.864 (−7%) |

All reductions are significant (95% CIs exclude zero). A 240 s cap (−9/−12% at η = 0.8) or three
breakdowns (−8/−9%) do not change the picture.

**What this means:** surge, breakdowns and observed rain barely weaken fixed holding: Even-Headway
still cuts bunching by about a third. What defeats it is **strong weather stress**: its advantage
shrinks from −34% to −12% by η = 0.6 and to −7% by η = 1.3, and Forward-Headway and Even-Headway
become indistinguishable. That gap — beyond observed conditions, so labelled synthetic — is what the
MARL controller has to close. The earlier "+ weather" row (0.865, −8/−9%) used η = 0.8, not the
manuscript's observed-rain definition.

Full write-up: [`docs/progress/WEEK2_SIMULATOR_VS_REALITY_2026-09-14.md`](docs/progress/WEEK2_SIMULATOR_VS_REALITY_2026-09-14.md)
(its Stage B reading used η = 0.8 only; the sweep above supersedes it).

---

## 5. What's next

**Ready for training (done 2026-09-14):**

- **Event-based discount.** Each transition is discounted by e^(−β·Δt), Δt = seconds between the bus's
  two decisions (Bradtke & Duff, as in `methods.tex`). β defaults to 0.99 per scheduled headway.
- **Checkpoints during training.** `training_state.pt` every 50 episodes (`--resume` continues exactly),
  `checkpoint_best.pt` = best evaluation CV so far (evaluated on seeds 90000+, never the test seeds).
- **Breakdown flag** is 1 only for buses behind the broken-down bus.
- **The pass mark, fixed before training:** in Stage A, the greedy MARL policy's mean headway CV over
  seeds 0–29 must be **below Even-Headway (0.342)**.
- **`eval_marl.py` follows the manuscript:** all 9 evaluation cells (Stage A, S, W observed rain, B, Stage B
  observed rain and η 0.3/0.6/1.0/1.3), the manuscript's acceptance criteria (Stage A: wait no worse than EH
  and CV below NC; Stage B: wait below the best baseline in every cell) plus the training gate. Paired
  Wilcoxon, Holm-corrected, α 0.05, fixed before any MARL result.
- **All baseline cells of that matrix are run** (§4).

**Next:** the Stage A gate run (`train_marl.py --episodes 800 --name gate`, about 3 hours), then
`eval_marl.py --ckpt experiments/gate/checkpoint_best.pt`. If it passes: skip action, then reward weights.

**Manuscript text that no longer matches the code:**

- `methods.tex:18, 38` say training runs in a separate lightweight Python simulator. It runs in
  SUMO (about 13 s per episode). **Decided: change the text.**
- `methods.tex:291` says a chronological calibration/test split. The code alternates service days,
  because weekday ridership varies by month (October is 31% above July), so a date-order split would
  test on busier months than it calibrates on. **Pending decision** (recommended: change the text and
  report a date-order split as a check).
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
| `data/shared/` | **The cleaned datasets** (study set, both directions, weather), zipped, with checksums (§9) | yes |
| `data/raw/`, `data/processed/` | Where the scripts read data from; the 3.7 GB APC snapshot | **no** — too big (§9) |
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

`results.tex` is now ours: a draft built only from `starter/results/`, with the MARL
section left as a commented placeholder. It stays commented out of `main.tex` until that
section is filled in.

🚨 **`discussion.tex` and `futurework.tex` are still NOT OURS.** They are leftover
template text from an unrelated neuroscience thesis. **Delete and rewrite; do not edit.**

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
| `scripts/test_simulator.py` | 18 pass/fail checks (FH, EH, skip, stop serving, breakdown flag) |

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
| `results/mc_summary*.md` | **The baseline tables**: headline, `_observed_rain`, `_stageB_eta*` (the weather sweep), `_hold240` and `_breakdowns3` (checks) |
| `results/stageB_weather_sweep.csv` | Stage B by weather strength, all controllers |
| `results/archive/` | Results from earlier simulator versions |
| `legacy/` | Old scripts kept for reference, not used by anything current ([`legacy/README.md`](starter/legacy/README.md)) |
| `experiments/<run>/` | **Every training run is kept**: `config.json` (what it was), `metrics.csv` (how it went), `checkpoint_best.pt` and `checkpoint.pt` (the policies). Only `training_state.pt`, which carries the replay buffer, stays out of Git |

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

### Fast way: the cleaned data is in the repo

To run the simulator, fit its inputs or check it against real buses, you only need the
cleaned data. It is committed in [`data/shared/`](data/shared/README.md). From the repo root:

```bash
python scripts/unpack_shared_data.py
```

That unpacks the 229,421-row study set and the weather tables to `data/raw/` and
`data/processed/`, and checks each file's SHA-256. Everything under `starter/` then runs.

### Full way: rebuild the cleaned data from the raw snapshot

Only needed to rerun the data pipeline (`scripts/pipeline/`). The pipeline **never
downloads anything** — it reads our archived copies. Those files are too big for Git,
so a fresh clone does not have them. You need three.

#### 1. The APC snapshot (3.7 GB)

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

#### 2. The two NOAA weather files (~16 MB total)

```
data/raw/noaa/LCD_USW00013958_2021.csv    Camp Mabry (primary)
    https://www.ncei.noaa.gov/oa/local-climatological-data/v2/access/2021/LCD_USW00013958_2021.csv
    8,531,389 bytes · sha256 8d2aafedde6f78ef...

data/raw/noaa/LCD_USW00013904_2021.csv    Austin-Bergstrom (cross-check)
    https://www.ncei.noaa.gov/oa/local-climatological-data/v2/access/2021/LCD_USW00013904_2021.csv
    7,645,753 bytes · sha256 fdd8c27f825fb077...
```

Full checksums are in `data/audit/texas_capmetro/weather_source_audit.json`.

#### 3. Nothing else

Everything downstream is generated. **Faster option:** ask a teammate for the
files rather than re-downloading 3.7 GB. Check the hashes either way.

---

## 10. How to run things

**Install:** Python 3.12, SUMO 1.27.1 with `SUMO_HOME` set, then
`pip install -r starter/requirements.txt` (numpy, pandas, matplotlib, torch).

```bash
# ---- the data half (from the repo root) ----------------------------------------
python scripts/unpack_shared_data.py               # ~5 s; the cleaned data from data/shared/
python scripts/pipeline/run_all.py                 # OR ~100 s from the raw snapshot; also rebuilds the evidence

# ---- the simulation half (from starter/) -----------------------------------------
cd starter
python scripts/fit_variability.py                  # ~2 min  -> sim_inputs/fitted/
python scripts/build_real_net.py                   # ~15 s   -> SUMO network + calibration_real.csv
python scripts/test_simulator.py                   # ~3 min  -> 18 PASS lines
python scripts/validate_simulator.py               #         -> results/validation/
python scripts/mc.py 30 10                         # ~25 min on 10 workers -> the baseline table
python scripts/mc.py 30 10 --eta 0 --only W,StageB --tag observed_rain     # manuscript W and Stage B cells
python scripts/mc.py 30 10 --eta 0.3 --only StageB --tag stageB_eta0.3     # sweep; also 0.6, 1.0, 1.3
python scripts/figures.py                          # redraw the figures

# MARL
python scripts/train_marl.py --episodes 3 --eval_every 3 --name smoke     # ~2 min plumbing check
python scripts/train_marl.py --episodes 800 --name gate                   # ~3 h; add --resume to continue
python scripts/eval_marl.py --ckpt experiments/gate/checkpoint_best.pt --cells A   # the gate: Stage A only
python scripts/eval_marl.py --ckpt experiments/gate/checkpoint_best.pt             # full matrix, 270 MARL runs

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
