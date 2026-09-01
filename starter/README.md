# MARL Bus-Scheduling — Runnable Starter Kit
A verified, runnable slice of the implementation: real data → calibrated reduced-corridor SUMO env → PettingZoo AEC env → Even-Headway baseline. Everything here was **run and checked**, not just written. Reduced 6-stop corridor (scale to 29 next).

## What's inside
```
sim_inputs/
  stops.csv            real per-stop point values (demand, dwell, segment time) — 29 stops, from the 3.5 GB raw asset
  stop_coordinates.csv 29 dir-6 stops with event counts + lat/lon (for geometry + corridor pick)
reduced_corridor.txt   the chosen 6-stop corridor: 5857, 5858, 4540, 467, 5859, 5606
sumo/                  the CALIBRATED scenario (corridor.net.xml / .rou.xml / stops.add.xml / corridor.sumocfg)
scripts/
  extract_sim_inputs.py  streams the raw APC CSV -> dir-6 clean subset (229,421 rows) -> sim_inputs/stops.csv
  calibrate_corridor.py  builds the corridor from real geometry + dwells and calibrates edge speeds to GEH<5
envs/bus_env.py        PettingZoo AEC env; pass sumo_cfg to run end-to-end with SUMO (SO2 logic is TODO)
baselines/even_headway.py  Even-Headway controller (0.4*H cap), no trained model needed
```

## Requirements
- **SUMO** installed (`SUMO_HOME` set) + Python 3.12 with `pip install pettingzoo gymnasium pandas numpy`.
- `traci`/`sumolib` ship with SUMO (the scripts add `%SUMO_HOME%\tools` to the path).

## Run it
```bash
# 1) (optional) regenerate sim_inputs from the raw CSV — set RAW path inside the script first
python scripts/extract_sim_inputs.py            # -> sim_inputs/stops.csv (expect 229,421 clean rows)

# 2) calibrate the reduced corridor to segment-time targets
python scripts/calibrate_corridor.py            # -> GEH<5 on >85% of segments; writes sumo/corridor.*

# 3) smoke-test the AEC env driving the calibrated SUMO corridor
python -c "import sys; sys.path.insert(0,'.'); from envs.bus_env import env; \
e=env(n_buses=3, sumo_cfg='sumo/corridor.sumocfg'); e.reset(); \
[e.step(None if (e.last()[2] or e.last()[3]) else e.action_space(a).sample()) for a in e.agent_iter(max_iter=120)]; \
e.close(); print('OK')"

# 4) baseline sanity
python baselines/even_headway.py
```

## Calibration result (first pass — reproducible)
Reduced corridor, real geometry (lengths 1164/895/1103/1044/1463 m), real dwells, targets = empirical `run_s`:

| segment | target (s) | simulated (s) | GEH |
|---|---|---|---|
| 5857→5858 | 156 | 166 | 0.83 |
| 5858→4540 | 119 | 129 | 0.90 |
| 4540→467  | 163 | 176 | 1.00 |
| 467→5859  | 106 | 117 | 1.04 |
| 5859→5606 | 193 | 207 | 0.99 |

**GEH < 5 on 100% of segments (criterion: >85%), RMSPE 8.2%.**

### Honest caveats (read before citing)
1. **Scope:** reduced 6-stop corridor, one bus, one pass. Scaling to the full 29 stops and multi-bus runs is next.
2. **GEH semantics:** methods define GEH on hourly bus **volume** (trivially matched by injecting at the observed frequency). Here GEH is applied to segment **travel times** as a closeness statistic, paired with **RMSPE** — RMSPE 8.2% (a systematic ~7% overshoot from bus accel/decel at stops) is the real signal; one more speed-correction iteration trims it.
3. **`rev_distance` is MILES, not metres** (column labeled `dist_mi`). Geometry here comes from coordinates, so it's unaffected.
4. **Terminal stop:** stop `5304` (not in this corridor) has an 781 s layover dwell — model it as a terminal if you include it.
5. **No passenger demand yet** → onboard load = 0. Demand injection is SO1.2 (uses `mean_boardings` from `sim_inputs`).

## Data provenance
The cleaning that produces `sim_inputs` was **independently reproduced** from the 3.5 GB raw asset and matches the committed manifest exactly (229,421 rows / 29 stops / 184 days / median dwell 18.0 s). Full record: `../DATA_CLEANING.md`.

## To commit into the repo
Copy this folder into the repo (e.g. as `starter/` or merge into existing `scripts/`, `envs/`), then:
```bash
git checkout -b implementation
git add starter_kit && git commit -m "runnable kit: real sim_inputs + calibrated corridor + AEC env + EH baseline"
```
Keep the raw CSV and the 229,421-row clean subset git-ignored (only `sim_inputs/*.csv` and code are tracked).

## Next (roadmap)
- Fill `bus_env.observe()` with real TraCI features (position, fwd/bwd headway, load, queue — prototype in the run scripts).
- Inject demand (SO1.2) so load/queue are non-zero.
- Wire a headway-CV reward, then the EH baseline into the running sim for a first MARL-vs-EH comparison (SO3).
