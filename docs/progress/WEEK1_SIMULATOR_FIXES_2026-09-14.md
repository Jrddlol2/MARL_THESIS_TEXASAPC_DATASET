# Week 1 — making the simulator trustworthy

**Date:** 2026-09-14 · **Covers:** risk register R1, R4, R8 and code-review issues K1–K5 ·
**Code:** `starter/envs/corridor_sim.py` · **Results:** `starter/results/mc_summary.md`

## 1. What changed

| # | Change | Why | Evidence it works |
|---|---|---|---|
| 1 | Headway `H0` 300 → **600 s** in all 8 places the GTFS change list names | 2021 timetable: every 10 min, weekdays 7 AM–6 PM | `grep` finds no 300-s headway left in active code |
| 1b | Fleet 12 → **18 buses** | Trip ≈ 87 min simulated (No-Control, Stage A; 89.5 min observed) ÷ 10-min headway ≈ **9 buses on the corridor at once** (observed weekday peak: median 10). Dispatching 2 × 9 lets the middle buses run with a full corridor ahead and behind | Derivation in `corridor_sim.py:159–165` |
| 2 | Riders **get off at their own stop** | Everyone rode to the last stop, so loads rose to ~40 | Load profile below |
| 3 | Buses **start with Tech Ridge riders** (6.15 per bus on average) | Stop 5304 has the most boardings but is not simulated | Included in the load profile (stop 5280 starts at 7.1 vs APC 7.3) |
| K1 | Buses handled in a **fixed order** | Looping over a Python `set` made results depend on the hash seed: same seed gave CV 0.192 / 0.193 / 0.212 | Same seed now identical under hash seeds 0, 5, 7 |
| K2 | Weather/traffic slowdown uses **this bus's** draw | Used a variable left over from the last bus to arrive | Code at `corridor_sim.py:626–628` |
| K3 | `D=False` **turns off** dwell noise | It had no effect | Code at `corridor_sim.py:549–550` |
| K4 | `watch.py` now **runs the real simulator** with the window on | Its "EH" mode was really forward-headway and its dwell model differed | GUI path gives identical CV and travel time to a normal run |
| K5 | Both code walkthroughs regenerated | Line numbers were stale | `docs/reference/CODE_WALKTHROUGH_*.md` |

Riders now arrive **one at a time, evenly spaced** (one SUMO `<person>` each). A first
attempt used one `<personFlow>` per destination; SUMO starts each flow's first rider at the
same moment, which bunched arrivals, doubled SUMO's recorded wait (595 s vs 294 s) and
inflated headway CV (0.21 vs 0.11). Caught before the Monte-Carlo run and fixed.

**Where riders get off.** At each stop, the share of riders on board who get off is
`APC mean alightings ÷ expected riders on board`; at the last modelled stop everyone gets
off (this absorbs the Southpark Meadows terminal's alightings). This makes the expected
alightings at every stop equal the APC mean.

**Not changed:** the data pipeline, the corridor geometry, calibration (RMSPE 0.44%,
GEH < 5 on 26/26 — independent of H0), the control stops, the dwell and disturbance models.

## 2. Checks

| Check | Result |
|---|---|
| Riders who boarded but never got off (5 seeds) | **0** |
| Simulated load leaving each stop vs APC mean `max_load` (26 stops) | Correlation **0.981**, RMSE **1.47 riders**, peak 18.4 vs 17.2 (`results/load_profile_validation.csv`, figure `load_profile_validation.png`) |
| SUMO's recorded wait vs the headway-formula wait (Stage A) | 299 s vs 307 s |
| Same seed across Python sessions | Identical |
| GUI run vs headless run | Identical |
| MARL self-tests (`reward.py`, `obs.py`) at H0 = 600 | Pass; holds are now {0, 60, 120, 180, 240} s |

The simulated load runs about 1.5 riders above APC through the middle of the corridor.
APC `max_load` and the boarding/alighting means are all averages over recorded stop events
(doors opened), not per trip — risk R9 — so a small gap is expected.

## 3. The 30-seed baselines, re-run

> **Superseded for the two breakdown rows (same day):** breakdown is now a bus removal,
> not a 400 s delay. New B rows: + Breakdown FH −16%, EH −13%; Stage B FH −17%, EH −12%.
> See `BREAKDOWN_AND_HOLD_CAP_2026-09-14.md`. All other rows are unchanged.

N = 30 paired seeds per cell, 5 control stops, 450 runs, 23 min on 10 workers.
Old results (H0 = 300, 12 buses) are kept in `starter/results/archive_H0_300/`.

| Scenario | NC CV | FH CV | EH CV | FH vs NC [95% CI] | EH vs NC [95% CI] |
|---|---|---|---|---|---|
| Stage A (D+T) | 0.159 | 0.121 | 0.123 | −24% [−28, −19] | −23% [−26, −19] |
| + Surge (S) | 0.166 | 0.132 | 0.132 | −21% [−25, −15] | −20% [−25, −16] |
| + Weather (W) | 0.755 | 0.611 | 0.654 | −19% [−22, −16] | −13% [−18, −9] |
| + Breakdown (B) | 0.219 | 0.169 | 0.174 | −23% [−27, −18] | −20% [−23, −18] |
| **Stage B (all)** | **0.771** | **0.631** | **0.674** | **−18% [−21, −15]** | **−13% [−15, −10]** |

For comparison, the old Stage B row (H0 = 300): FH −1% [−6, +3], EH −1% [−7, +5].

## 4. Does "fixed holding fails under severe disturbance" still hold?

**No — not as stated.** At the old headway, both heuristics' Stage B confidence intervals
crossed zero, so we could say fixed holding stopped working. At the correct headway, both
cut bunching significantly under every disturbance, including Stage B.

What the new table does support:

1. **Fixed holding leaves most of the severe-disturbance bunching in place.** Under Stage B
   the best heuristic still has CV 0.631, about **five times** its Stage A level (0.121), and
   removes only 18% of No-Control's bunching.
2. **Its relative benefit shrinks as disturbance grows**: FH −24% (Stage A) → −18% (Stage B);
   EH −23% → −13%. Weather drives almost all of the degradation.
3. **Forward-Headway beats Even-Headway, and the gap opens under weather** (−19% vs −13%) —
   the same pattern as the earlier runs.
4. Travel time rises with holding (FH +242 s in Stage B), wait improves only under weather
   (FH −9% to −10%).

**Suggested restatement of the MARL motivation:** *rule-based holding still helps under
severe, combined disturbance, but it leaves most of the added bunching in place (residual
CV 0.63, five times the mild-disturbance level) and its benefit shrinks as disturbance
grows. The question is whether an adaptive controller can recover more of that gap.* This
is a weaker "fails" claim but a clean, measurable target for SO2/SO3.

**Why it changed (not separately attributed):** four things moved at once — the headway
doubled (so the 240-s maximum hold is larger and the 400-s breakdown is relatively half as
severe), the K2 fix, realistic loads, and 18 buses. We did not run them one at a time.

## 5. Caveats to carry forward

- **R2 is now more visible:** No-Control Stage A CV is 0.159 against an observed weekday
  CV of 0.62. They are still not measured the same way (observed = trip origin over 11 h),
  but the simulator likely under-represents ordinary variability (R3). Close this before
  quoting absolute CVs.
- **Surge is relatively harsher now:** 120 riders over 900 s is 1.5 headways, not 3. The
  manuscript defines S as a scaling factor `f_d`.
- **Breakdown is a 400-s delay,** not the manuscript's removal of a bus.
- **Skip (R5)** is still not implemented.
- `scripts/run_baseline.py`, `run_disturbances.py` and `verify_real_net.py` are legacy: H0
  updated, rest of their model not. They are not used for results.

## 6. Regenerated

`starter/results/mc_results.csv`, `mc_summary.md`, figures `mc_headway_cv`, `mc_wait`,
`marey_diagram`, `degradation_curve`, `load_profile_validation`,
`calibration_validation` (unchanged content, re-drawn).

**Not regenerated:** `experiments/gate1/` and its figures — they record the old H0 = 300
training run. Retrain from scratch next (holds are now up to 240 s).
