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

The usual fix is a **holding rule**: make an early bus wait a few seconds at a
stop so the spacing evens out. Those rules are simple and fixed.

**We are testing whether a machine-learning controller can do it better** — one
that watches the gap ahead, the gap behind, how full the bus is, and how many
people are waiting, and then decides how long to hold. Each bus is its own agent,
and they all share one learned policy.

The point of the thesis is the **"non-ideal conditions"** part: does the learned
controller still hold up when it rains, when a crowd surges, when a bus breaks
down?

**Case study:** CapMetro Rapid Route 801 in Austin, Texas, direction code 6,
using six months of real automatic-passenger-counter (APC) data, July–December
2021.

---

## 2. Where we are right now

| | Status |
|---|---|
| Proposal | Defended, revised, submitted 2026-08-29 |
| Dataset acquired and cleaned | **Done** — 229,421 stop events, checksummed |
| Weather joined | **Done** — 100% of events matched to NOAA |
| Corridor built in SUMO | **Done** — 26 stops, real road geometry |
| Corridor calibrated | **Done** — RMSPE 0.75%, GEH < 5 on 25/25 segments |
| Baseline controllers (NC / FH / EH) | **Done** — 30 Monte Carlo runs per cell |
| MARL agent | **Built, trained once, plateaued.** The critical path |
| Results / Discussion chapters | **Not written** |

**Milestones**

| | When | Scope |
|---|---|---|
| MSA1 | Sep 7–12, 2026 | Dataset + corridor + calibration only |
| MSA2 | Oct 5–10, 2026 | Empirical extraction, disturbances, MARL formulation |
| MSA3 | Nov 23–28, 2026 | Training and evaluation |

Poster and paper due **Dec 5, 2026**. Results this semester are **preliminary**;
final results run Jan–Apr 2027.

---

## 3. The mental model — the whole project is one line

```
  THE RAW FILE          3.7 GB, 9,197,694 rows, every CapMetro route
        |
        |   scripts/pipeline/     keep only 801 direction 6; attach weather
        v
  CLEAN DATA            229,421 stop events, each with a weather reading
        |
        |   starter/scripts/      average each stop; build the road; calibrate
        v
  SIMULATED CORRIDOR    26 stops in SUMO, real geometry, real travel times
        |
        |   starter/envs/         drive buses down it; add rain/surges/breakdowns
        |   starter/agents/       let the agent decide when to hold
        v
  RESULTS               how bunched were the buses?  ->  figures  ->  slides
```

**`scripts/` is the data half. `starter/` is the simulation half.**
That one sentence explains most of this repository.

---

## 4. What we have found so far

Baseline comparison, 30 paired Monte Carlo runs per cell (2026-09-14). The simulator
now uses the real 2021 headway (600 s), passenger demand, dwell and running-time
variability **fitted from the APC data**, buses that pass stops nobody is using, a 120 s
holding cap (as in the RRL), Daganzo's Forward-Headway rule and a breakdown that removes a bus. Lower headway CV = more evenly spaced buses = better.

| Scenario | No Control | Forward-Headway | Even-Headway |
|---|---|---|---|
| Stage A — ordinary day (demand + traffic) | 0.556 | 0.396 (−29%) | **0.342** (−38%) |
| + surge | 0.596 | 0.427 (−28%) | **0.371** (−38%) |
| + weather | 0.865 | 0.798 (−8%) | 0.786 (−9%) |
| + breakdown (one bus removed) | 0.564 | 0.423 (−25%) | **0.370** (−34%) |
| Stage B — everything at once | 0.876 | 0.804 (−8%) | 0.796 (−9%) |

All reductions are significant (95% CIs exclude zero).

**Is the simulator realistic?** On held-out weekdays real buses have headway CV 0.50;
the No-Control simulation gives 0.56 on the same definition (first stop 0.35 vs 0.36,
stop-by-stop r = 0.87). Buses serve quiet stops on 69% of trips vs 64% observed. Calibration on alternate days tests at RMSPE 3.1% on the rest.

**What this means for the thesis:** fixed holding rules work well on an ordinary day but
lose most of their effect under severe, combined disturbance (−29 to −38% → −8 to −9%).
A 240 s cap (−9 to −12%) or three breakdowns (−8 to −9%) do not change that. The gap is what
the MARL controller has to close. Details: `docs/progress/WEEK2_SIMULATOR_VS_REALITY_2026-09-14.md`.

**Where the MARL agent stands:** trained for 286 episodes. Greedy evaluation went
`0.244 → 0.255 → 0.235 → 0.234 → 0.251 → 0.251 → 0.228` — i.e. it learned
something by episode 40 (roughly matching Forward-Headway) and then **flat for
240 episodes.** That run used the old 300 s headway, so it must be retrained from
scratch. No checkpoint was saved from it.

The simulator now uses the real 2021 headway of 600 s (see
`docs/planning/GTFS_FINDINGS_CHANGE_LIST_2026-09-12.md`). The calibration results
were unaffected by that change.

---

## 5. Folder guide — what every directory is

| Folder | What's in it | Committed? |
|---|---|---|
| *(repo root)* | The LaTeX manuscript. Kept at root because Overleaf expects it there | yes |
| `config/` | **One file**, `texas_capmetro_801.json` — every tunable value in the project | yes |
| `scripts/` | **The data half.** Raw download → cleaned data → weather attached | yes |
| `starter/` | **The simulation half.** Corridor, SUMO, controllers, MARL, results, figures | yes |
| `data/raw/` | Downloads, including the 3.7 GB APC snapshot | **no** — too big |
| `data/processed/` | Normalized NOAA weather tables | **no** |
| `data/audit/` | **The evidence.** Checksums, queries, row counts, feasibility results | yes |
| `docs/` | Planning, per-milestone progress write-ups, reusable prompts | yes |
| `reports/` | Reference and dataset audit reports | yes |
| `Figures/` | Figures used by the manuscript | yes |
| `RRL/` | `sources.md` maps bib keys to source PDFs (the PDFs live outside the repo) | index only |
| `submissions/` | **Frozen** as-submitted checkpoints — never edit these | yes |

---

## 6. Code guide — what every file is for

### The manuscript

```
main.tex           preamble and \input list — do not restructure
title.tex          title page
introduction.tex   Ch 1 — Introduction and Literature Review   (6,874 words) OURS
problem.tex        Ch 2 — Problem Statement                    (1,694 words) OURS
methods.tex        Ch 3 — Methods and Research Design         (10,341 words) OURS
thesis_refs.bib    bibliography
```

🚨 **`results.tex`, `discussion.tex` and `futurework.tex` are NOT OURS.**
They are leftover template text from an unrelated neuroscience thesis — a
calcium-imaging pipeline called *NeuroSEE*, mouse models, Alzheimer's. 3,751
words, zero mentions of buses, headway or CapMetro. They are commented out of
`main.tex` so they have never compiled. **Delete and rewrite; do not edit.**

### `scripts/` — the data half

Raw download through cleaned data with weather attached. **This is what MSA1
presents.** More detail in [`scripts/pipeline/README.md`](scripts/pipeline/README.md).

| File | What it does |
|---|---|
| `pipeline/common.py` | Shared plumbing: paths, config, checksums, safe file writing, reading the snapshot, and **the six cleaning rules**. Does no processing itself |
| `pipeline/audit_route_selection.py` | Compares Route 801 against 803 and proves 801 has more usable data. **Produces the cleaning-funnel numbers on the slide** |
| `pipeline/01_extract_dir6.py` | Extracts the 229,421 clean rows from the snapshot. **← THE STUDY SET** |
| `pipeline/02_prepare_weather.py` | Reads both NOAA files and fixes the local-standard-time offset |
| `pipeline/03_join_weather.py` | Attaches the nearest weather reading to every stop event |
| `pipeline/04_gtfs_gate.py` | Writes down why we may not yet call direction 6 "southbound" |
| `pipeline/run_all.py` | Runs steps 01–05 in order |
| `texas_capmetro_pipeline.py` | **Archived reference** — the original 900-line version, which downloads from the portal instead of reading local files. Kept in case the extraction ever needs re-verifying against the source |

### `starter/envs/` — the simulator core

| File | What it does |
|---|---|
| `corridor_sim.py` | **THE HEART.** Drives buses down the corridor with dwell, demand and disturbances. Every experiment in the project calls this one file |
| `obs.py` | Builds the 7-number observation a bus "sees" (headways, load, queue, weather flag, breakdown flag) |
| `reward.py` | The 3 penalties that score the agent, plus action decoding |
| `marl_env.py` | Glues the neural network into `corridor_sim` as a controller; holds the `Config` with every experiment knob |
| `bus_env.py` | Older PettingZoo wrapper. **Superseded** by `corridor_sim.py` |

### `starter/agents/` and `starter/baselines/`

| File | What it does |
|---|---|
| `agents/ddqn.py` | The neural network — shared Double-DQN, replay buffer, ε-greedy |
| `baselines/even_headway.py` | The simple fixed rule we compare against |

### `starter/scripts/` — building the corridor

| File | What it does |
|---|---|
| `extract_sim_inputs.py` | 229,421 rows → 29 stops × 6 average numbers. **Where the data half meets the simulation half** |
| `extract_route_shape.py` | Pulls the real road path from the OpenStreetMap route relation |
| `build_real_net.py` | Builds the SUMO road network from that path |
| `calibrate_corridor.py` | Tunes edge speeds until simulated travel time matches real travel time. **Produces RMSPE 0.75%** |
| `verify_real_net.py` | Checks the real-geometry network behaves like the straight-line one |

### `starter/scripts/` — running experiments

| File | What it does |
|---|---|
| `run_baseline.py` | One run, no disturbances |
| `run_disturbances.py` | One run with demand / surge / traffic / weather / breakdown |
| `mc.py` | Runs the whole activation matrix 30 times in parallel and averages. **Produces `mc_results.csv`** |
| `train_marl.py` | Trains the agent |
| `eval_marl.py` | Evaluates a trained agent on given seeds |
| `watch.py` | Opens **sumo-gui** so you can watch buses bunch and be held |
| `watch_gate.py` | Live text view of a training run against the baseline targets |

### `starter/scripts/` — figures

| File | What it draws |
|---|---|
| `_figstyle.py` | Shared publication styling — colours, fonts, sizes. Imported by all the others |
| `figures.py` | The main paper figures from `calibration.csv` and `mc_results.csv` |
| `figures_datacleaning.py` | The MSA1 cleaning-funnel and route-selection figures |
| `figures_weather.py` | The NOAA join figures |
| `marey.py` | **Time–space (Marey) diagram** — bunching shows as converging lines |
| `convergence.py` | Training curves: episode return and headway CV |
| `plot_curve.py` | A single training run's learning curve |
| `degradation.py` | Headway CV vs weather intensity, per controller |

### `starter/` — data files

| File | What it is |
|---|---|
| `corridor.txt` | **The 26 modelled stops, in order.** The corridor definition |
| `reduced_corridor.txt` | An older 6-stop corridor used during early development |
| `sim_inputs/stops.csv` | 29 stops × boardings, alightings, dwell, run time, distance |
| `sim_inputs/stop_coordinates.csv` | Each stop's mean GPS position and event count |
| `sim_inputs/route_shape.csv` | The road polyline in projected coordinates |
| `sim_inputs/route_shape_stops.csv` | Each stop's distance along that polyline |
| `sumo/` | The generated SUMO networks — `corridor.*` (schematic) and `corridor_real.*` (real geometry) |
| `results/calibration.csv` | Per-segment observed vs simulated time, GEH, % error |
| `results/mc_results.csv` | Every Monte Carlo run |
| `results/mc_summary.md` | **The baseline results table** |
| `results/figures/` | Generated charts, `.png` and `.pdf` |
| `experiments/gate1/` | The 286-episode training run (no checkpoint saved) |

### `config/` and `data/`

| Path | What it is |
|---|---|
| `config/texas_capmetro_801.json` | **EVERY TUNABLE VALUE.** Routes, direction code, study dates, NOAA stations, the 90-minute join tolerance. Change this file, not the code |
| `data/audit/texas_capmetro/*.json` | The evidence: queries, row counts, checksums, coverage results |
| `data/audit/texas_capmetro/*.md` | The same evidence in readable form |

---

## 7. "I want to…" — where to look

| I want to… | Open / run |
|---|---|
| See the cleaning rules | `scripts/pipeline/common.py` → `clean_where()` |
| See where 229,421 comes from | `data/audit/texas_capmetro/route_selection_audit.json` |
| Rebuild every evidence file | `python scripts/pipeline/run_all.py` |
| Set up a new machine | README §8, "Getting the data" |
| Understand the weather join | `scripts/pipeline/03_join_weather.py` (read the header) |
| See the calibration result | `starter/results/calibration.csv` |
| See the baseline results | `starter/results/mc_summary.md` |
| Change how the simulation behaves | `starter/envs/corridor_sim.py`, PART 2 settings (line 153) |
| Change what the agent sees or is scored on | `starter/envs/obs.py`, `starter/envs/reward.py` |
| Watch buses move on screen | `cd starter` then `python scripts/watch.py EH StageB` |
| Redraw the figures | `python starter/scripts/figures.py` |
| Know what still has to change | `docs/planning/GTFS_FINDINGS_CHANGE_LIST_2026-09-12.md` |

---

## 8. Getting the data (do this first on a new machine)

The pipeline **never downloads anything** — it reads our archived copies. Those
files are too big for git, so a fresh clone does not have them. You need three.

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

Everything downstream is generated. Run `python scripts/pipeline/run_all.py`
and the cleaned study set, the normalized weather tables and all the evidence
files are rebuilt from these three inputs.

**Faster option:** ask a teammate for the files directly rather than
re-downloading 3.7 GB. Check the hashes either way.

---

## 9. How to run things

```bash
# the whole data pipeline (asks the Texas portal; reuses local files if present)
python scripts/pipeline/run_all.py

# same thing offline, from the local 3.7 GB snapshot — no network at all
python scripts/pipeline/audit_route_selection.py --local
python scripts/pipeline/01_extract_dir6.py --local

# everything under starter/ runs FROM the starter folder
cd starter

# build + calibrate the real-geometry corridor
python scripts/build_real_net.py

# baselines, 30 seeds, 10 parallel workers (~25 min)
python scripts/mc.py 30 10

# watch buses move (needs SUMO installed and SUMO_HOME set)
python scripts/watch.py EH StageB
```

The whole pipeline takes about **100 seconds** (42 s + 54 s for steps 1 and 2,
which read the 3.7 GB file; the rest are 1–2 s each). Re-running is safe —
every output is rewritten from the same inputs.

**Requirements:** Python 3.12 · `pandas numpy torch pettingzoo gymnasium` ·
SUMO with `SUMO_HOME` set for anything under `starter/`.

---

## 10. Things that will confuse you (they confused us)

**1. Three `.tex` chapters are someone else's thesis.** See the warning in §5.

**2. There are two folders on the Desktop.** `THESIS/MARL/` is this repo and is
canonical for all code. `THESIS Claude/` is a workspace holding the report and
deck generators (`dstyle.py`, `make_msa1*.py`) plus `starter_kit/` — an
**outdated copy** of `starter/`, missing three figure scripts and stale on five
more. Ignore `starter_kit/`.

**3. The cleaning rules are implemented three times, on purpose.**
As a text query the Texas portal runs (`clean_where`), as a Python function for
the offline path (`passes_clean_rules`), and in pandas inside
`extract_sim_inputs.py`. All three produce 229,421 rows — that agreement is a
cross-check, not a bug. The **canonical** one for anything quoted in the
manuscript is `clean_where()`.

**4. "Direction 6" is a vendor software code, not a compass direction.** The APC
file has no headsigns and no stop names. It is almost certainly southbound
(Tech Ridge → Southpark Meadows, corroborated by overlaying our stop IDs on the
current GTFS feed), but the 2021 schedule snapshot needed to state it as fact is
not publicly archived. See `data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md`.

**5. Two files have "extract" in the name and do unrelated things.**
`extract_sim_inputs.py` turns rows into per-stop averages.
`extract_route_shape.py` pulls road geometry from OpenStreetMap.

**6. `rev_seconds` already contains the stop's dwell time.** It is recorded
door-open to door-open. Everywhere we need pure running time we compute
`rev_seconds - dwell_time`, because dwell is modelled separately. Forgetting this
double-counts.

**7. `rev_distance` units are unresolved.** The APC metadata says miles or
kilometres depend on an external odometer setting. Our corridor geometry comes
from GPS coordinates instead, so nothing depends on it — but do not use it for
speed without checking.

---

## 11. The rule that matters most

**Never write a number you cannot trace to a file.**

Every figure in the deck and manuscript comes from `data/audit/texas_capmetro/`
or `starter/results/`. If you need a number, take it from there or regenerate it.
Do not retype it off a slide.

This is not paranoia — errors have been caught this way repeatedly: a raw row
count with two digits transposed, citations that misstated what their source
papers actually said, a stop dropped for the wrong reason. `CLAUDE.md` has the
full rules; `reports/` has the audits.

---

## 12. Git

Default branch `dataset/texas-capmetro-801`, remote **`jared`**
(`Jrddlol2/MARL_THESIS_TEXASAPC_DATASET`). There is also an `origin` pointing at
`khalil-badal/MARL` — do not push there by accident.
