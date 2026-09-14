# Risk register for the MSA 2 work

**Date:** 2026-09-13 · **Status:** internal, not presented at MSA 1 (the risks slide was hidden) ·
**Read this before:** re-running baselines, validating the simulator, building EO 1.2, or training the MARL agent.

Each risk says what is wrong, where it is in the code, why it matters, what to do, and how we will know it is
fixed. Ordered by **when it bites**: the first ones block the next steps.

State of the simulator when this was written: 27 stops, real road geometry (`envs/corridor_sim.py` defaults to
`sumo/corridor_real.net.xml`), calibration RMSPE 0.44%, GEH < 5 on 26/26 segments (`results/calibration_real.csv`).

---

## Tier 1 — could change the conclusions

### R1. Baseline results were run at the wrong headway
- **What:** `H0 = 300 s` (`envs/corridor_sim.py:50`, also `envs/marl_env.py:26`). The 2021 timetable runs every
  10 min on weekdays, 7 AM–6 PM (`data/raw/capmetro/schedule_2021/`).
- **Why it matters:** the holding cap (`0.4 × H0`), the 400 s breakdown and headway-normalised observations all
  scale with H0. At 300 s, disturbances are about twice as severe relative to the headway. The finding that
  motivates MARL ("fixed holding fails under severe disturbance", Stage B) came from these runs and may change.
- **Do:** set H0 = 600 s at every site listed in `GTFS_FINDINGS_CHANGE_LIST_2026-09-12.md`; reconcile `NBUS` with
  the ~84–90 min run time; re-run the N = 30 baselines (`scripts/mc.py`).
- **Done when:** the Stage A/B table is regenerated at 600 s and the Stage B conclusion is re-stated from it.

### R2. The simulator is validated on travel time, not on bunching
- **What:** calibration checks segment travel times only. The thesis metric is headway regularity. Observed
  weekday 07:00–18:00 headway CV is 0.62 (n = 131 days, measured at the trip origin); the simulator's no-control
  CV is about 0.34 (at the control stops, short horizon). **These are not measured the same way.**
- **Why it matters:** if the simulator bunches much less (or more) than real buses, the size of any MARL
  improvement does not transfer.
- **Do:** compute simulated and observed headway CV at the same stops, hours and day type; add this as an SO1
  validation criterion.
- **Done when:** a like-for-like table of observed vs simulated headway CV exists, with the gap explained or closed.

### R3. Variability is assumed, not measured
- **What:** dwell noise is lognormal with CV 0.25 (`CVD`, `corridor_sim.py:50`, used at `:100`); traffic is a
  uniform factor 0.8–1.2 (`:103`); demand is one mean per stop for the whole day (`DEM`, `:49`). The methods
  chapter promises per stop × time-of-day × day-type distributions (Stage 2); `scripts/extract_sim_inputs.py`
  notes this as a limitation.
- **Why it matters:** bunching is driven by exactly this variability. It is also the lever that closes R2.
- **Do:** fit dwell and running-time distributions and demand rates by time of day and day type from the clean
  APC data; replace the assumed values.
- **Done when:** every stochastic parameter in `corridor_sim.py` cites a fitted value or is labelled synthetic.

### R4. Simulated passengers only alight at the last stop
- **What:** every passenger flow rides to `STOPS[-1]` (`corridor_sim.py:84`, surge at `:88`). Onboard load
  therefore rises to about 40 by the end of the corridor. A rough estimate from mean boardings and alightings
  gives a real peak near 12 (around stop 5357); that estimate uses per-door-opening means, not per-trip loads.
- **Why it matters:** onboard load is one of the seven MARL observations, and with no alighting the passenger
  surge (+120) may push buses toward the 60-person capacity. The agent would learn from loads that never occur.
- **Do:** give each passenger a destination drawn from the APC alighting shares downstream of the boarding stop.
- **Done when:** the simulated mean load profile along the corridor is plotted against the APC-derived one.

## Tier 2 — blocks MARL work

### R5. The stop-skip action is not connected
- **What:** `hold, _skip = decide(obs)` discards skip (`corridor_sim.py:150`). `marl_env.Config.skip_enabled`
  defaults to False, so nothing breaks today.
- **Why it matters:** actions 5–9 of the 10-action space behave like 0–4. Once skip is enabled, "skip has no
  effect" will look like a reward-tuning problem.
- **Do:** implement skipping in the simulator (bus passes the stop without dwelling; waiting passengers stay)
  before enabling it in training.
- **Done when:** a unit test shows a skipped stop gets no dwell and keeps its queue.

### R6. The test training run plateaued and saved no model
- **What:** `experiments/gate1/metrics.csv`: 286 of 800 episodes; greedy evaluation headway CV 0.244, 0.255,
  0.235, 0.234, 0.251, 0.251, 0.228 at episodes 40–280 (flat). No checkpoint file. Evaluation used seeds 90000+
  (N = 5), not the baselines' seeds 0–29, so it cannot share a table with them.
- **Why it matters:** the agent stopped improving after ~40 episodes; the prime suspect is R1 (largest hold
  120 s against a 400 s breakdown).
- **Do:** fix R1 first; save checkpoints during training; evaluate on seeds 0–29 so results pair with the baselines.
- **Done when:** a full run with checkpoints and a paired evaluation exists.

## Tier 3 — limitations to state, not blockers

### R7. Calibration is in-sample
- Speeds were tuned and evaluated on the same data. **Do:** split service days by alternating dates (a calendar
  split mixes in season and rain; October is the wettest month, 134.5 mm), calibrate on one set, test on the other.

### R8. Origin-stop demand is not simulated
- Tech Ridge (5304) is excluded as a layover point, but it has the most boardings (6.15 per stop event). **Do:**
  start each bus with 5304's boardings on board.

### R9. Segment times come from door-opening records
- APC logs a stop only when doors open; stop coverage ranges from 37.8% (2738) to 93.4% (5304). A record's
  "time to next location" can span a skipped stop. Medians limit the bias. **Do:** estimate running times from
  consecutive served stops only, and compare.

### R10. No signals or mixed traffic
- Both networks are a single bus lane; intersection delay is represented only by the calibrated speeds and the
  traffic factor. **Do:** state as a scope limitation.

### R11. Severe weather and breakdowns are synthetic
- Ordinary rain is observed (11,804 stop events); severe weather and breakdowns are not. The weather factor is a
  labelled synthetic lognormal. **Do:** estimate the ordinary-rain effect with segment, time-of-day and day-type
  controls (`weather_join_audit.json` warns the pooled 204 s vs 212 s is descriptive only); keep severe cases
  labelled synthetic.

### R12. One Austin route stands in for EDSA
- Results describe controller behaviour on Route 801, southbound, 2021. **Do:** state as a limitation; keep
  simulator parameters adjustable.

### R13. Data housekeeping (low impact)
- **Distance units:** `rev_distance` units are undocumented; evidence says miles (Pleasant Hill → Slaughter
  Station logs 1.68; the road is 1.67 miles). No result uses the field.
- **Timestamps:** APC times are read as Austin local time; only 169 of 229,421 stop events fall between 01:00
  and 04:00, matching the timetable's ~5 AM start.
- **Trip count:** ~95 southbound weekday trips scheduled vs a median of 72 in the clean data. Unresolved whether
  cleaning or cancellations explain it; the peak headway histogram shows no second mode at ~20 min.

---

## Suggested order

1. R1 (headway) → re-run baselines.
2. R4 (alighting) and R8 (origin demand) — cheap, change loads before any training.
3. R3 (fitted variability) → R2 (headway-CV validation) → R7 (held-out days).
4. R5 (skip) → R6 (training with checkpoints, paired seeds).
5. R11 rain effect in parallel with 3.

---

## Status update — 2026-09-14 (Week 1)

Details: `docs/progress/WEEK1_SIMULATOR_FIXES_2026-09-14.md`.

- **R1 — DONE.** H0 = 600 s at all eight sites; fleet = 18 buses (≈ 9 on the corridor at once from
  an ~87-min trip, observed peak median 10). N = 30 baselines re-run. **The Stage B conclusion does
  not hold as stated:** FH −18% [−21, −15], EH −13% [−15, −10] — both significant. Restated: holding
  still helps under combined disturbance but leaves residual CV 0.63 (≈ 5× Stage A) and its benefit
  shrinks as disturbance grows.
- **R4 — DONE.** Riders get off at stops drawn from APC alighting shares. Simulated load vs APC mean
  `max_load`: correlation 0.981, RMSE 1.47 riders (`starter/results/load_profile_validation.csv`).
- **R8 — DONE.** Each bus starts with Tech Ridge's riders (6.15 per bus on average).
- **New, fixed:** results depended on Python's hash seed (loop over a `set`); weather/traffic
  slowdown read another bus's draw; `D=False` had no effect.
- **R2 — more urgent:** simulated No-Control Stage A CV is 0.159 vs observed 0.62 (not yet like-for-like).
- **R6 — next:** retrain from scratch at H0 = 600 (holds up to 240 s), with checkpoints and seeds 0–29.
- **New open items:** surge (120 riders / 900 s) is now 1.5 headways, relatively harsher; breakdown
  is a 400-s delay, not a bus removal as the manuscript describes.

### Update — 2026-09-14 (later): breakdown and holding cap

- **Breakdown now removes a bus** (Guedes & Borenstein 2018; Daganzo 2009); the 400 s delay had no
  source, and `methods.tex` wrongly cited Cao et al. for removal (fixed). New Stage B: FH −17%, EH −12%.
- **New risk R14 — the holding cap drives the Stage B result.** 0.4 × 600 = 240 s is double every
  absolute cap in the RRL (90–120 s). At a 120 s cap, Stage B benefit falls to FH −10%, EH −9%.
  Under Stage B, FH holds at the 240 s cap on 22% of decisions. **Decide the headline cap** and
  report the other as sensitivity; give MARL the same cap.
- **New risk R15 — breakdown count.** Code removes a fixed number (1; 3 as a check), manuscript
  describes a per-timestep Poisson trial. With 3 removals the breakdown-only benefit is FH −8%
  [−15, −0], EH −7% [−14, +1].
- Details: `docs/progress/BREAKDOWN_AND_HOLD_CAP_2026-09-14.md`.

### Update — 2026-09-14 (Week 2)

Details: `docs/progress/WEEK2_SIMULATOR_VS_REALITY_2026-09-14.md`.

- **R3 — DONE.** Demand, dwell, running time and their spreads fitted from APC (weekday 07–18,
  calibration days); by period AM/MID/PM available.
- **R2 — DONE (criterion proposed).** Like-for-like observed headway CV 0.504 (test days) vs
  simulated No-Control 0.552 (+10%); first stop 0.352 vs 0.357; by-stop r = 0.87.
- **R7 — DONE.** Calibration on alternate days: RMSPE 0.90%; held-out days RMSPE 3.08%, GEH < 5 26/26.
- **R9 — DONE for running time.** Targets now use only records whose next record is the next stop
  (old targets ~11% too slow). Demand-driven stop skipping by real buses is still not modelled.
- **R11 — ordinary rain estimated:** +1.35% [−0.8, +2.5], not significant; severe weather stays synthetic.
- **New, fixed:** Even-Headway's backward headway was always the 600 s fallback (never saw the bus
  behind), and "faster" traffic draws had no effect.
- **R14 decided:** 120 s headline cap, 240 s sensitivity (Stage B FH −9% vs −14%).
- **R15 decided:** fixed breakdown count n_B = 1 (3 as a check), methods.tex updated.
- **Headline result:** fixed holding −34/−39% on ordinary days → −9% under Stage B.
