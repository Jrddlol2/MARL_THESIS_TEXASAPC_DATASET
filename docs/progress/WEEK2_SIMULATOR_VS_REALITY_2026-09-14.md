# Week 2 — checking the simulator against reality

**Date:** 2026-09-14 · **Covers:** plan items 5–9 (finishes EO 1.1, feeds EO 1.2); risks R2, R3, R7, R9, R11 ·
**Code:** `starter/scripts/fit_variability.py`, `starter/envs/corridor_sim.py`,
`starter/scripts/build_real_net.py`, `starter/scripts/validate_simulator.py` ·
**Fitted values:** `starter/sim_inputs/fitted/` · **Checks:** `starter/results/validation/`

## 0. Two problems found on the way (both fixed)

1. **Even-Headway never saw the bus behind.** The backward headway `hb` was only measured
   once the follower reached the previous stop. At a 10-minute headway it never had, so
   `hb` was the fallback 600 s in **all 255 of 255** decisions checked. Even-Headway was
   really "half of Forward-Headway", and the MARL agent's backward-headway input was a
   constant. This was in the original code. **Fix:** estimate the follower's arrival from
   its last stop plus the typical running time — what an AVL feed provides (manuscript
   §3, "headways would come from AVL"). `hb` now ranges 257–927 s.
2. **Faster-than-typical traffic draws were ignored.** The simulator lowered a bus's
   maximum speed to slow it, but a bus can never beat the edge speed limit, so every
   "faster" draw did nothing. **Fix:** a SUMO speed factor, which works both ways. SUMO's
   own hidden speed randomness is switched off (`speedDev="0"`).

## 1. Item 5 — variability fitted from data (weekday 07:00–18:00, calibration days)

| Quantity | Before (assumed) | Now (fitted) | How |
|---|---|---|---|
| Dwell time | 6 s + 4 s per boarding | **8.1 s + 5.0 s per boarding + 2.7 s per alighting**, cap 94 s (95th pct) | Weighted fit to the median dwell of each (boardings, alightings) cell, 57,242 events |
| Dwell noise | lognormal CV 0.25 | **log-sd 0.50** | From neighbouring buses (below) |
| Running time per stop pair | all-day median of `rev_seconds − dwell` | **median stop-to-stop time, only when the next record is the next stop** | Removes skipped-stop records (R9); corridor total 4,001 s vs 4,513 s before (−11%) |
| Running-time variation | uniform 0.8–1.2 (log-sd ≈ 0.12) | **per segment, median log-sd 0.20** (0.10–0.35) | From neighbouring buses, dry events only |
| Dispatch (trip start) | perfect, every 600 s | **per-bus sd 165 s** (robust 108 s) | Gaps between neighbours at stop 5280, scaled so the first-stop CV matches the calibration days (0.348) |
| Demand per stop | one all-day mean, fixed count | **weekday 07–18 mean per stop; count varies day to day (variance = 3.8 × mean)** | Negative binomial; random arrival times |
| Tech Ridge riders on board | 6.15 (all day) | **7.31** (weekday 07–18) | |

**Why "from neighbouring buses".** Bunching comes from the difference between one bus and
the next. A late afternoon slows every bus together and does not bunch them. Fitting the
spread of all events (log-sd 0.25 for running time; 280 s for dispatch) made the
simulator bunch too much (No-Control CV 0.89 vs 0.50 observed). So each spread is fitted
from pairs of buses scheduled one headway apart on the same day: spread of the
difference ÷ √2 (27,610 pairs).

**By time of day and day type.** `sim_inputs/fitted/stop_params.csv` holds AM (07–10),
MID (10–15) and PM (15–18) values; `CORRIDOR_PERIOD=AM|MID|PM` runs that period.
Weekday running time: AM 3,846 s, MID 4,008 s, PM 4,218 s. Weekend demand is
recorded in `day_type_summary.csv` (Saturday 110, Sunday 83 vs weekday 141 boardings/hour)
but not simulated, because the 10-minute headway applies to weekdays only.

## 2. Item 6 — bunching, measured the same way

Observed: headway CV per stop per **test** day, weekday 07–18, using only gaps between
buses **scheduled one headway apart** (so a trip that was never recorded does not look
like a 20-minute gap). Simulated: No-Control, ordinary day (D+T), 30 seeds.

| | Observed | Simulated |
|---|---|---|
| First stop (5280) | 0.352 | **0.357** |
| Mean, stops 1–26 | 0.504 | **0.552** (+10%) |
| Stop-by-stop RMSE | — | 0.065 |
| Stop-by-stop correlation | — | 0.87 |
| Loads leaving each stop vs APC `max_load` | — | RMSE 1.0 rider, r = 0.985 |

![](../../starter/results/figures/headway_cv_validation.png)

Bunching grows along the corridor in both (observed 0.35 → 0.56). The simulator grows a
little faster in the second half (ends at 0.66). The earlier "0.62 observed vs 0.34
simulated" was not like-for-like (different stops, hours and gap definition); on the same
definition the gap is now +0.05.

**Proposed SO1 criterion:** No-Control mean headway CV within ±15% of the observed value on
held-out days. Met (+10%).

## 3. Item 7 — calibration tested on unseen days

Weekday service days in date order: 1st, 3rd, 5th … calibrate (65 days); 2nd, 4th …
test (64 days).

| | Calibration days | Test days (never used) |
|---|---|---|
| RMSPE | 0.90% | 3.08% |
| GEH < 5 | 26 / 26 | 26 / 26 (max GEH 0.90) |

The largest test-day error is the shortest segment (2738→2611: 64 s simulated vs 57 s,
+12%). The calibration rule (RMSPE < 2%) is set for fitting; held-out RMSPE is 3.1%.

## 4. Item 8 — ordinary rain effect

Median running time with rain vs without, within the same segment × day type × hour band
(before 07, 07–10, 10–15, 15–18, after 18), in 170 strata with ≥ 10 rain and ≥ 30 dry
events (6,120 rain-exposed runs). Pooled with rain-count weights; 95% CI by resampling
service days.

**Ordinary rain slows running time by 1.35% (95% CI −0.8% to +2.5%) — not significant.**
The earlier pooled 204 s vs 212 s (+4%) was mostly rush-hour timing, as the pipeline's
warning said. In the simulator, W = observed rain multiplier (1.0135) × the labelled
synthetic lognormal stress (η). So the weather layer is now data-based for ordinary rain
and synthetic only for severe weather.

## 5. Item 9 — adjustable disturbance strengths (EO 1.2)

| Disturbance | Model | Strength setting | Default | Source |
|---|---|---|---|---|
| D demand | Negative-binomial counts, random arrivals; dwell noise | fitted | fitted | APC |
| T travel time | Per-segment lognormal running-time factor; dispatch deviation | `traffic_stress_sd` σs (extra, clipped 0.8–1.2) | fitted; σs = 0 | APC; Wang & Sun 2023 Eq. 23 |
| S surge | All boarding demand × f_d, f_d ~ N(1, σd²) clipped to [1, 10] | `surge_sd` σd | 1 (2 and 3 available, not yet run) | Wang & Sun 2023 Eq. 22, p. 9 |
| W weather | Rain multiplier × lognormal (mean 1, CV η), clipped 0.5–3 | `eta` η | 0.8 | APC rain (ordinary); Patil et al. (severe, synthetic) |
| B breakdown | Bus removed at a random stop; riders transfer | `breakdowns` n_B | 1 (check: 3) | Guedes & Borenstein 2018; Daganzo 2009 |
| Holding cap | All controllers | `max_hold` | 120 s (check: 240 s) | Rodriguez et al. 2023; Tang et al. 2024; Wang & Sun 2023; Liu et al. 2023 |

All are arguments of `simulate()` and options of `mc.py` (`--surge-sd`, `--eta`,
`--traffic-sd`, `--breakdowns`, `--max-hold`). The manuscript table
(`methods.tex`, parameter table) was updated to these values.

## 6. Baselines re-run on the fitted simulator

N = 30 paired seeds, 5 control stops, **hold cap 120 s**, one bus removed in B.
`starter/results/mc_summary.md` (headline), `mc_summary_hold240.md`, `mc_summary_breakdowns3.md`.

| Scenario | NC CV | FH vs NC [95% CI] | EH vs NC [95% CI] |
|---|---|---|---|
| Stage A (D+T, ordinary day) | 0.552 | −34% [−39, −28] | **−39% [−44, −33]** |
| + Surge (S) | 0.621 | −31% [−36, −26] | −36% [−42, −30] |
| + Weather (W) | 0.869 | −9% [−13, −5] | −9% [−14, −5] |
| + Breakdown (B) | 0.565 | −29% [−33, −25] | −34% [−38, −30] |
| **Stage B (all)** | **0.886** | **−9% [−14, −5]** | **−9% [−13, −5]** |

**Checks**

| Scenario | Cap 240 s: FH / EH | 3 buses removed: FH / EH |
|---|---|---|
| Stage A | −41% / −45% | — |
| + Weather | −14% / −12% | — |
| + Breakdown | −35% / −41% | −22% / −28% |
| Stage B | −14% / −12% | −9% / −8% |

![](../../starter/results/figures/degradation_curve.png)

**What changed, and what it means**

1. **Even-Headway now beats Forward-Headway on ordinary days** (−39% vs −34%). Before the
   backward-headway fix it could not see the bus behind, so it could not.
2. **Fixed holding works well on an ordinary day and loses about three-quarters of its effect
   under severe disturbance** (−34/−39% → −9%). Weather drives it: the degradation curve
   shows both rules converging on No-Control as η grows.
3. **The cap and the breakdown count do not change the conclusion.** A 240 s cap lifts Stage B
   only to −14/−12%; three removals leave Stage B at −9/−8%.
4. **MARL motivation, restated on a validated simulator:** rule-based holding is effective on
   ordinary days but recovers only ~9% of bunching under combined severe disturbance (residual
   CV 0.80). The target for SO2 is the gap between −9% and the ordinary-day −35 to −39%.

Magnitudes changed a lot from Week 1 (Stage A NC 0.159 → 0.552) because the ordinary-day
variability is now measured instead of assumed; the simulator was previously far too calm
(R2).

## 7. What is still soft

- The simulator's bunching is 10% above observed, mostly in the second half of the corridor.
- Dispatch spread is scaled to one number (first-stop CV) from 413 neighbour pairs at stop
  5280 (43% of trips log that stop).
- Buses stop at every stop (dwell ≥ ~8 s); real buses skip stops with no demand. Stop
  skipping by demand (and the controller's skip action, R5) is not modelled.
- Holding by real operators (if any) is inside the observed CV; the simulator's No-Control
  has none.
- Severe weather and breakdowns remain synthetic by necessity.
