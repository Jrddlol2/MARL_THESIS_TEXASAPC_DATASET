# `starter/` — the simulation half

The Route 801 corridor in SUMO, the NC / FH / EH controllers, the MARL agent, and every
simulation result. **Run everything from this folder.** The full guide (what each file does,
results, how to run) is the main [`README.md`](../README.md), sections 4, 7 and 10.

```
envs/          corridor_sim.py (the simulator), obs.py, reward.py, marl_env.py
agents/        ddqn.py (the shared Double-DQN)
scripts/       fit, build, check, run and plot (see the main README §7)
corridor.txt   the 27 modelled stops, in driving order
sim_inputs/    per-stop data; fitted/ holds what the simulator actually uses
sumo/          SUMO networks (the simulator uses corridor_real.* and stops_real.add.xml)
results/       calibration_real.csv, validation/, mc_summary*.md, figures/; archive/ = older versions
legacy/        old scripts kept for reference, not used by anything current
experiments/   training runs (not in Git)
```

## Requirements

- **SUMO 1.27.1** installed, with `SUMO_HOME` set (`traci` and `sumolib` come with it).
- **Python 3.12** and `pip install -r requirements.txt` (numpy, pandas, matplotlib, torch).

## Quick check that everything works

```bash
python scripts/test_simulator.py                                          # ~3 min, 18 PASS lines
python scripts/train_marl.py --episodes 3 --eval_every 3 --save_every 3 --name smoke     # ~2 min
```
