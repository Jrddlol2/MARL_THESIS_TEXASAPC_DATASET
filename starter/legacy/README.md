# `starter/legacy/` — old code, kept for reference

Nothing current imports or runs these. They are kept because earlier progress notes and the
MSA1 material describe them. Current equivalents are in the right-hand column.

| File | What it was | Replaced by |
|---|---|---|
| `calibrate_corridor.py` | Built and calibrated the early straight-line network (`sumo/corridor.*`, `results/calibration.csv`) | `scripts/build_real_net.py` (real road geometry, calibration and test days) |
| `verify_real_net.py` | Checked the real-geometry network against the straight-line one | `scripts/build_real_net.py`, `scripts/validate_simulator.py` |
| `run_baseline.py` | One early No-Control run (12 buses, riders to the last stop) | `envs/corridor_sim.py` + `scripts/mc.py` |
| `run_disturbances.py` | One early run with D/S/T/W/B disturbances | `envs/corridor_sim.py` + `scripts/mc.py` |
| `bus_env.py` | PettingZoo AEC skeleton | `envs/marl_env.py` (the agent plugs into `corridor_sim.simulate`) |
| `even_headway.py` | Stand-alone Even-Headway rule | `even_headway_hold()` in `envs/corridor_sim.py` |
| `reduced_corridor.txt` | The first 6-stop test corridor | `corridor.txt` (27 stops) |

If you run one, run it from `starter/` (for example `python legacy/run_baseline.py`). Their
numbers are **not** the thesis results.
