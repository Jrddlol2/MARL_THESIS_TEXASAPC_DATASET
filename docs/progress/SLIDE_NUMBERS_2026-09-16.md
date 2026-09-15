# Numbers to update on the deck (2026-09-16)

Every slide number that has changed since the MSA1 deck, with its source file. Nothing here is a
design decision — it is a find-and-replace list for whoever edits the slides.

## Calibration

| On the slide now | Use instead | Source |
|---|---|---|
| RMSPE **0.44%**, GEH < 5 on 26/26 | **0.90%** on calibration days, **3.08%** on held-out days, GEH < 5 on 26/26 in both | `results/calibration_real.csv` |
| (nothing about a held-out test) | Add it: the corridor is now tested on 64 service days it was never fitted on | `results/calibration_real.csv` |
| "stops once GEH < 5 and RMSPE < 2%" | unchanged, but our run stops at **0.90%** | `scripts/build_real_net.py` |

The 0.44% figure came from the 13 September calibration, before demand, dwell and running-time
variability were fitted from the APC data. The higher number is not a regression: it is measured
against per-trip demand and a stricter running-time definition.

Unchanged and still correct: 27 modelled stops of 29 observed, 26 segments, 30.3 km, direction 6 =
southbound, 10-minute weekday headway.

## Does the simulator behave like real buses? (new slide material)

| Check | Real buses | Simulator |
|---|---|---|
| Bunching (headway CV), corridor | 0.504 | 0.556 |
| Bunching at the first stop | 0.352 | 0.357 |
| Bunching stop by stop | — | r = 0.87 |
| Share of trips that stop at a quiet stop | 64% | 69% (r = 0.96) |
| Riders on board along the route | — | r = 0.99, about 2 riders low |

Source: `results/validation/`. Figure: `headway_cv_validation.png`, `stop_service_validation.png`,
`load_profile_validation.png`.

## Baseline results (replace any earlier table)

| Condition | No Control | Forward-Headway | Even-Headway |
|---|---|---|---|
| Ordinary day | 0.556 | 0.396 (−29%) | 0.342 (−38%) |
| + surge | 0.596 | 0.427 (−28%) | 0.371 (−38%) |
| + weather (observed rain) | 0.559 | 0.400 (−28%) | 0.346 (−38%) |
| + breakdown | 0.564 | 0.423 (−25%) | 0.370 (−34%) |
| Everything, observed rain | 0.609 | 0.458 (−25%) | 0.404 (−34%) |

Source: `results/mc_summary.md`, `mc_summary_observed_rain.md`. 30 paired runs per cell.

**The point to make on the slide:** under everything the data supports, the simple holding rules still
work — Even-Headway cuts bunching by about a third. They only fail once weather stress is pushed beyond
the observed range, and that is where the learned controller has to earn its place:

| Synthetic weather stress η | 0 (observed rain) | 0.3 | 0.6 | 1.0 | 1.3 |
|---|---|---|---|---|---|
| Even-Headway vs No Control | −34% | −22% | −12% | −8% | −7% |

Figure: `stageB_weather_sweep.png`. Always say "labelled synthetic" for η > 0 — it is not a rainfall
category.

## Simulator settings that changed

| On the slide now | Use instead |
|---|---|
| Headway 5 minutes / 300 s | **10 minutes (600 s)**, from the archived 2021 timetable |
| Breakdown = a 400 s delay | **A bus is removed from service**; its riders get off and wait |
| Holding cap 240 s | **120 s**, with 240 s reported as a sensitivity check |
| 12 buses | **18 dispatched trips**, about 9 buses on the corridor at once |

## MARL status

Do **not** show `gate1_convergence.png` or `gate1_curve.png`: they are from the old simulator. The
current training run is `experiments/dr1/` and its curve will be `dr1_curve.png`.

The pass mark was written down before the run: in Stage A the learned policy must have lower bunching
than Even-Headway (0.342), and the manuscript's own criteria are that waiting time is no worse than
Even-Headway with bunching below No Control, and that in every severe-weather cell waiting time is below
the best baseline.
