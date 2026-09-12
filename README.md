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

Baseline comparison, 30 paired Monte Carlo runs per cell. Lower headway CV =
more evenly spaced buses = better.

| Scenario | No Control | Forward-Headway | Even-Headway |
|---|---|---|---|
| Stage A — demand + traffic | 0.331 | **0.237** (−28%) | 0.271 (−18%) |
| + surge | 0.364 | **0.304** (−17%) | 0.316 (−13%) |
| + weather | 0.977 | 0.918 (−6%, n.s.) | 0.893 (−9%, n.s.) |
| + breakdown | 0.442 | **0.365** (−17%) | 0.376 (−15%) |
| Stage B — everything at once | 0.941 | 0.929 (−1%, n.s.) | 0.929 (−1%, n.s.) |

**The finding that motivates the whole thesis:** simple holding rules work under
mild disturbance and **stop working under severe disturbance** — under weather
and under everything-at-once, the confidence intervals span zero. That gap is
what the MARL controller is supposed to fill.

**Where the MARL agent stands:** trained for 286 episodes. Greedy evaluation went
`0.244 → 0.255 → 0.235 → 0.234 → 0.251 → 0.251 → 0.228` — i.e. it learned
something by episode 40 (roughly matching Forward-Headway) and then **flat for
240 episodes.** Diagnosing that plateau is MSA2's main job. No checkpoint was
saved from that run.

⚠️ **Read `docs/planning/GTFS_FINDINGS_CHANGE_LIST_2026-09-12.md` before trusting
the numbers above.** The simulator was parameterised with a scheduled headway of
300 s; the real 2021 published headway is 600 s. Everything scaled by that value
has to be re-run. The calibration results are unaffected.

---

## 5. Where everything lives

### The manuscript

```
main.tex           preamble and \input list — do not restructure
title.tex          title page
introduction.tex   Ch 1 — Introduction and Literature Review   (6,874 words) OURS
problem.tex        Ch 2 — Problem Statement                    (1,694 words) OURS
methods.tex        Ch 3 — Methods and Research Design         (10,341 words) OURS
thesis_refs.bib    bibliography
Figures/           figures used by the manuscript
```

🚨 **`results.tex`, `discussion.tex` and `futurework.tex` are NOT OURS.**
They are leftover template text from an unrelated neuroscience thesis — a
calcium-imaging pipeline called *NeuroSEE*, mouse models, Alzheimer's. 3,751
words of it. They are commented out of `main.tex` so they have never compiled,
but **do not read them expecting our work, and do not edit them — delete and
rewrite.**

### The data half — `scripts/`

Raw download through cleaned data with weather attached. **This is what MSA1
presents.** Detail in [`scripts/pipeline/README.md`](scripts/pipeline/README.md).

```
scripts/pipeline/
    common.py               shared tools: downloads, checksums, the six cleaning rules
    01_audit_routes.py      Route 801 vs 803; produces the cleaning-funnel numbers
    02_download_dir6.py     the 229,421-row study set        <- THE STUDY SET
    03_prepare_weather.py   NOAA download + timezone correction
    04_join_weather.py      attaches a weather reading to every stop event
    05_gtfs_gate.py         records why we may not call direction 6 "southbound"
    run_all.py              runs 01 through 05 in order

scripts/texas_capmetro_pipeline.py
    The OLD version: all five steps in one 900-line file. Still works, still
    correct. Kept until the team has run the split version. Then delete.
```

### The simulation half — `starter/`

```
starter/envs/
    corridor_sim.py      THE HEART. drives buses down the corridor.
                         every experiment in the project calls this one file.
    obs.py               the 7 numbers a bus "sees"
    reward.py            the 3 penalties that score the agent
    marl_env.py          glues the neural network into corridor_sim
    bus_env.py           older wrapper, superseded by corridor_sim

starter/agents/ddqn.py             the neural network
starter/baselines/even_headway.py  the simple rule we compare against

starter/scripts/
    extract_sim_inputs.py   229,421 rows -> 29 stops x 6 average numbers
    extract_route_shape.py  the real road path, from OpenStreetMap
    build_real_net.py       builds the SUMO road network
    calibrate_corridor.py   tunes speeds until sim time = real time
    verify_real_net.py      checks real-road and straight-line agree
    run_baseline.py         runs with no disturbances
    run_disturbances.py     runs with rain / surges / breakdowns
    mc.py                   runs it 30 times and averages
    train_marl.py           trains the agent
    eval_marl.py            tests a trained agent
    watch.py                opens sumo-gui so you can watch buses move
    figures*.py, marey.py, plot_curve.py, convergence.py, degradation.py
                            chart generation (_figstyle.py holds shared styling)

starter/corridor.txt     the 26 modelled stops, in order
starter/sim_inputs/      the per-stop averages and coordinates
starter/sumo/            the road networks
starter/results/         calibration.csv, mc_results.csv, mc_summary.md, figures/
starter/experiments/     training runs (gate1 = the 286-episode run)
```

### Data and evidence

```
config/texas_capmetro_801.json
    EVERY TUNABLE VALUE lives here — routes, direction code, study dates, NOAA
    stations, the 90-minute join tolerance. Change this file, not the code.

data/raw/         downloads — git-ignored, too big to commit
data/processed/   normalized weather — git-ignored
data/audit/       THE EVIDENCE. checksums, queries, row counts. committed.
                  every number in the deck traces to a file in here.
```

### Documents and history

```
docs/planning/    roadmaps, experiment plans, the GTFS change list
docs/progress/    per-milestone write-ups, the replication guide, demo runbook
docs/prompts/     reusable audit and verification prompts
reports/          reference and dataset audit reports
submissions/      FROZEN as-submitted checkpoints — do not edit
RRL/sources.md    maps bib keys to source PDFs (the PDFs live outside the repo)
CLAUDE.md         the no-fabrication rules for AI sessions
```

---

## 6. How to run things

```bash
# the whole data pipeline (asks the Texas portal; reuses local files if present)
python scripts/pipeline/run_all.py

# same thing offline, from the local 3.7 GB snapshot — no network at all
python scripts/pipeline/01_audit_routes.py --local
python scripts/pipeline/02_download_dir6.py --local

# calibrate the corridor
python starter/scripts/calibrate_corridor.py

# baselines, 30 seeds, parallel
python starter/scripts/mc.py 30 4

# watch buses move (needs SUMO installed and SUMO_HOME set)
python starter/scripts/watch.py EH Weather+Breakdown
```

Re-running the pipeline is cheap and safe: every download checks for a local copy
first and records `"reused_existing_file": true` instead of fetching again.

**Requirements:** Python 3.12 · `pandas numpy torch pettingzoo gymnasium` ·
SUMO with `SUMO_HOME` set for anything under `starter/`.

---

## 7. Things that will confuse you (they confused us)

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

## 8. The rule that matters most

**Never write a number you cannot trace to a file.**

Every figure in the deck and manuscript comes from `data/audit/texas_capmetro/`
or `starter/results/`. If you need a number, take it from there or regenerate it.
Do not retype it off a slide.

This is not paranoia — errors have been caught this way repeatedly: a raw row
count with two digits transposed, citations that misstated what their source
papers actually said, a stop dropped for the wrong reason. `CLAUDE.md` has the
full rules; `reports/` has the audits.

---

## 9. Git

Default branch `dataset/texas-capmetro-801`, remote **`jared`**
(`Jrddlol2/MARL_THESIS_TEXASAPC_DATASET`). There is also an `origin` pointing at
`khalil-badal/MARL` — do not push there by accident.
