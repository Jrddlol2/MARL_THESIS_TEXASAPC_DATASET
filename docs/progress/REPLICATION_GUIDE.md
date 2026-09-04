# Replication Guide — Reproduce the Results From a Clean Clone (Group B3)

Follow this end to end and you will **reproduce every result from scratch** — calibration, baselines,
figures, and the MARL evidence — and be able to check your numbers against the committed ones. It
assumes nothing but a fresh Windows machine and this repository. Commands run from `MARL/starter/` in
PowerShell. Timings below are the *actual* wall-clock on the project machine (Python 3.12, CPU only).

> The repo already commits the calibrated net, `sim_inputs/stops.csv`, and `results/*`, so a clone runs
> out-of-the-box. This guide has you **regenerate** them and confirm they match — that's the proof.

---

## 1. Install the toolchain

1. **SUMO** — install Eclipse SUMO 1.27.x, then set the environment so the binaries are found:
   ```powershell
   $env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
   $env:Path += ";$env:SUMO_HOME\bin"
   sumo --version                     # expect: Eclipse SUMO 1.27.x
   ```
2. **Python 3.12** and the packages:
   ```powershell
   pip install "traci" "sumolib" "numpy" "pandas" "torch" "matplotlib"
   python -c "import traci, sumolib, numpy, pandas, torch, matplotlib; print('deps ok')"
   ```
   Verified versions: SUMO 1.27.1, Python 3.12.0, torch 2.12.0 (CPU is fine — no GPU needed),
   matplotlib 3.11.1. `traci`/`sumolib` also ship inside `%SUMO_HOME%\tools` if pip install is blocked.

**Acceptance:** `deps ok` prints and `sumo --version` shows 1.27.x.

## 2. Get the data (optional — only for the very first step)

The raw CapMetro APC CSV (≈3.5 GB, July–December 2021) is the input to `extract_sim_inputs.py`. Two paths:
- **You have the raw CSV:** set its path at the top of `scripts/extract_sim_inputs.py` (`RAW = ...`) and
  do Step 3.
- **You don't (can't be redistributed here):** **skip Step 3** and start from the committed
  `sim_inputs/stops.csv` — every downstream result (Steps 4–7) reproduces fully from it. This is the
  supported fallback; note in your report that the funnel step was taken as given.

## 3. Regenerate the simulation inputs  *(only if you have the raw CSV)*

```powershell
python scripts\extract_sim_inputs.py
```
**Expect:** `raw 9,2xx,xxx -> dir-6 clean 229,421 (expect 229,421)` and a written `sim_inputs/stops.csv`.
**Acceptance:** the printed count is **229,421**, and the new `stops.csv` matches the committed one:
```powershell
git diff --stat sim_inputs\stops.csv        # expect: no change (or only float-rounding noise)
```

## 4. Build and calibrate the corridor  **(~6 s)**

```powershell
python scripts\calibrate_corridor.py
```
**Expect (actual output):**
```
iter 2: <5:100% RMSPE=0.75% GEHmax=0.29
calibration criterion met (RMSPE 0.75%, GEH<5 on 100%)
wrote results/calibration.csv (RMSPE 0.75%)
```
**Acceptance:** RMSPE **0.75 %**, GEH < 5 on **100 %** of the 25 segments; `results/calibration.csv`
matches the committed file (`git diff --stat results\calibration.csv` → no change). This also writes
`sumo/corridor.net.xml`, which everything else needs.

## 5. Reproduce the baselines  **(single seed ~21 s; full Monte-Carlo ~15–22 min)**

Quick single-seed sanity check:
```powershell
python scripts\run_baseline.py         # ~21 s; NC/FH/EH table, holding cuts CV sharply (single seed, dwell noise only)
```
The rigorous, reported numbers — the N = 30 matched-seed activation matrix:
```powershell
python scripts\mc.py 30 6              # 5 scenarios x 3 controllers x 30 seeds; ~15-22 min on 6 workers
```
**Timing basis:** N = 5 at 4 workers took **226 s** (~12 s/run), so N = 30 is ~15 min at 6 workers,
~22 min at 4. **Expect** `results/mc_summary.md` to reproduce the pattern within seed noise:
Stage A (D+T) **FH −28 %**, **EH −18 %** headway-CV vs No-Control (CIs exclude zero); ablations keep the
gain; **Stage B ≈ −1 %** (CI includes zero — control degrades). The matched seeds make this close to
exact, not just directional.
**Acceptance:** your Stage-A FH/EH reductions are significantly negative and Stage-B is ~0 with a
zero-crossing CI. (A small N=5 run reproduces the *direction* only, with wide CIs — expected.)

## 6. Reproduce the figures  **(~4 s + ~34 s + sweep)**

```powershell
python scripts\figures.py       # ~4 s  -> results/figures/{calibration_validation,mc_headway_cv,mc_wait}.png
python scripts\marey.py         # ~34 s -> results/figures/marey_diagram.png
python scripts\degradation.py   # weather-intensity sweep -> results/figures/degradation_curve.png (longer; run with small N first)
```
**Acceptance:** the five PNGs regenerate in `results/figures/` and visually match the committed ones
(identity-line calibration, CV bars with CIs, bunching trajectories, the degradation curve).

## 7. Reproduce the MARL evidence

```powershell
python agents\ddqn.py                              # ~31 s -> "greedy accuracy ... = 0.92 (chance = 0.10)"
python envs\reward.py                              # instant -> on-time -0.075, bunched -0.480, bunched+skip -0.730
python scripts\train_marl.py --episodes 6 --name smoke     # ~1 min plumbing check -> experiments/smoke/
python scripts\train_marl.py --episodes 800 --name gate    # the fail-fast gate (longer; offline)
python scripts\eval_marl.py --ckpt experiments\gate\checkpoint.pt --N 20   # evaluate the checkpoint as 4th controller
```
**Expect:** the DDQN self-test reaches ~0.9 vs 0.1 chance; the smoke run creates `experiments/smoke/`
with `metrics.csv`; the gate's evaluation CV converges toward the fixed-holding baseline (see
`results/figures/gate1_convergence.png`). The **full domain-randomised training** is the long offline
step (hours) — start it, then let it run; it writes a checkpoint + curve under `experiments/<name>/`.
**Acceptance:** self-test accuracy ≫ 0.1; the gate run produces a converging eval-CV curve.

---

## Troubleshooting (failures this project actually hit)

| Symptom | Cause / fix |
|---|---|
| `sumo` / `netconvert` not found | `SUMO_HOME` unset or `\bin` not on PATH — set them (Step 1). |
| Viewer/MC error: net missing | Run `calibrate_corridor.py` once to write `sumo/corridor.net.xml`. |
| MC process gets OOM-killed | Free RAM (close browsers); lower the worker count (`python scripts\mc.py 30 4`). |
| MC hangs near the end on Windows | Do **not** add `max_tasks_per_child` to the pool — balanced workers hit the recycle limit together and deadlock; the committed code uses persistent workers. |
| Worker crash mentioning matplotlib | Plotting must be imported only in the parent; run `figures.py`/`degradation.py` directly, never inside a worker. |
| `busStop ... not downstream` at insertion | A vehicle-length/stop-position edit broke insertion — revert to the committed net and `stops.add.xml` (bus length 12 m, stops at 5–25 m). |
| `mc.py` overwrote your results | It writes `results/mc_results.csv` + `mc_summary.md` each run — back them up first if you're comparing, or just `git checkout` to restore the committed N=30.|

**You have replicated the thesis when:** Steps 4–6 regenerate `calibration.csv`, the figures, and an
`mc_summary.md` matching the committed results, and Step 7's self-test and gate run learn. A teammate who
reaches here has rebuilt the work from the repository alone — not watched it, reproduced it.
