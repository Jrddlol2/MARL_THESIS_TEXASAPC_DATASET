# Calibration/validation split: interleaved vs chronological

The study splits weekday service days **alternately**: day 1 calibrates, day 2 tests, day 3 calibrates,
and so on (65 calibration / 64 test days). `methods.tex` originally specified a chronological split
(early days calibrate, later days test). Both were run on the same pipeline; only the split differs.

| Split | Calibration days | Held-out days | Calibration RMSPE | Held-out RMSPE | GEH < 5 |
|---|---|---|---|---|---|
| Interleaved (the study) | 65, spread over Jul-Dec | 64, spread over Jul-Dec | 0.90% | **3.08%** | 26/26 both sets |
| Chronological | 65, Jun 30 - Sep 27 | 64, Sep 28 - Dec 30 | 0.95% | **6.83%** | 26/26 both sets |

**Why the difference is not a worse model.** Recorded weekday boardings (07:00-18:00) are 1,736 per day
in July and 2,282 in October, a 31% rise, and the median segment running time barely moves (167-174 s).
A chronological split therefore fits the quiet summer months and tests on the busy autumn ones, so part
of the 6.8% is the corridor changing, not the simulator being wrong. Every segment still meets the
GEH < 5 acceptance criterion under both splits.

**Reproduce**

```bash
cd starter
python scripts/fit_variability.py --split chronological   # writes sim_inputs/fitted/
python scripts/build_real_net.py                          # recalibrates and reports both sets
```

Run it in a scratch copy of the repo: both scripts overwrite the fitted inputs and the SUMO network
that every other result depends on. The saved output of the chronological run is
`calibration_chronological_split.csv` in this folder; the study's own calibration stays in
`results/calibration_real.csv`.
