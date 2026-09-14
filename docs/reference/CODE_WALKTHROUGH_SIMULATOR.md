# Code walkthrough — the simulator (`starter/envs/`, `starter/agents/`)

Block-by-block explanation of the simulation core: the corridor loop every experiment
drives, the MARL glue, the observation vector and the reward library.

Generated with [`docs/prompts/Code_Walkthrough_Prompt.md`](../prompts/Code_Walkthrough_Prompt.md).
**Line numbers are current as of 2026-09-14, after Week 2** (fitted variability,
backward-headway fix, 120 s hold cap, bus removal).

## File index

| File | Lines | What breaks if you delete it |
|---|---|---|
| `envs/corridor_sim.py` | 956 | **Everything.** Every baseline, MARL run and the live viewer call `simulate()` |
| `scripts/fit_variability.py` | 447 | The fitted inputs in `sim_inputs/fitted/` (demand, dwell, running time, spreads, dispatch, rain, observed CV) |
| `scripts/build_real_net.py` | 323 | The calibrated network and `results/calibration_real.csv` (calibration + held-out days) |
| `scripts/validate_simulator.py` | 134 | The bunching and load checks against real buses |
| `scripts/mc.py` | 154 | The 30-seed baseline tables and every sensitivity option |
| `envs/reward.py` | 68 | The agent has no score. Also holds `Q_REF`, which `obs.py` imports |
| `envs/obs.py` | 39 | The agent has no input |
| `envs/marl_env.py` | 63 | The network can't be used as a controller |
| `agents/ddqn.py` | 131 | No learning |
| `scripts/watch.py` | 84 | The live SUMO-GUI demo (a thin wrapper around `simulate(gui=True)`) |
| `baselines/even_headway.py` | 13 | Nothing — `corridor_sim` has its own rules |
| `envs/bus_env.py` | 77 | **Nothing. No importers** (PettingZoo skeleton, superseded) |

## What changed on 2026-09-14 (and why)

| Change | Why | Where |
|---|---|---|
| `H0` 300 → **600 s**; 18 buses | 2021 timetable; ~9 buses on the route at once | L162, L169–171 |
| Riders get off at their own stop; buses start with Tech Ridge riders | Loads were ~3× too high; stop 5304 not simulated | L274–424 |
| Fixed bus order | Results depended on Python's hash seed | L599 |
| Breakdown **removes the bus** | Guedes & Borenstein 2018; Daganzo 2009 | L515–524, L629–633, L881–909 |
| Hold cap **120 s** (240 s = check) | RRL absolute caps are 90–120 s | L191–196 |
| **All ordinary-day values fitted** from APC | Week 2 item 5 | L111–154, L173–190 |
| **Backward headway estimated like AVL** | It was always the 600 s fallback — Even-Headway never saw the bus behind | L673, L846–866 |
| **Speed factor** instead of max speed | "Faster" traffic draws were silently ignored | L713–725 |
| Surge = Wang & Sun demand factor | Was 120 extra riders at one stop | L506–510, L386–424 |
| Dispatch deviation + running order | Real trips start early/late; buses can swap | L496, L526–535 |

---

# `envs/corridor_sim.py` — the heart

**One loop that any controller drives.** A controller is a function
`decide(obs) -> (hold_seconds, skip)`. NC, FH, EH and the MARL policy are different
`decide` functions on an identical environment — the comparison is fair by construction.

## PART 1 · L84–154 — load the corridor and the fitted parameters

```
L88   STOPS          the 27 modelled stops from corridor.txt, in driving order
L99   EDGES          "e0", "e1", ... — road piece i leaves stop i
L111  PERIOD         CORRIDOR_PERIOD env var: ALL (weekday 07-18, default), AM, MID, PM
L115-119 fitted stop_params.csv, model_params.json, dispatch_deviation.csv
      WHY   every ordinary-weekday number comes from scripts/fit_variability.py
      WATCH the network is calibrated to the ALL rows; other periods scale running
            time by RUN_SCALE instead of recalibrating
L123-127 SEGMENT_LENGTH = along-road distance between stops
L129-151 RUN_TIME (period median), RUN_SCALE (period / calibrated), RUN_LOG_SD
      (spread from neighbouring buses), BASE_DWELL, DEMAND, ALIGHTINGS
L154  START_LOAD = Tech Ridge mean boardings in the period (7.31 for ALL)
```

## PART 2 · L158–237 — settings

```
L162  H0 = 600.0                  scheduled headway (2021 timetable)
L169-171 NUM_BUSES = 18; START_OFFSET = 1800 s so early starters have room
L174-178 dwell model (fitted): 8.1 s + 5.0 s/boarding + 2.7 s/alighting,
      noise log-sd 0.50, cap 94 s (95th percentile)
L181  DEMAND_DISPERSION = 3.8     day-to-day demand variance / mean
L184-185 RAIN_MULTIPLIER 1.0135 (observed, n.s.) and WEATHER_CV 0.8 (synthetic eta)
L188  SURGE_SD = 1                Wang & Sun sigma_d
L190  TRAFFIC_STRESS_SD = 0       Wang & Sun sigma_s, off in the main runs
L196  MAX_HOLD_SECONDS = 120      Rodriguez et al. 0.4 H at a 5-min headway
L197  NUM_BREAKDOWNS = 1          Guedes & Borenstein single-disruption design
L205  TIME_TO_REACH[i]            typical time to reach stop i (passengers + hb estimate)
L214  CONTROL_STOPS = [0,1,5,17,20]  5280, 5857, 5859, 5867, 4046 (§3.2.2 criteria)
      WATCH positional indices into corridor.txt
L233-237 vtype: speedDev="0" so SUMO adds no hidden speed randomness
```

## PART 3 · L241–270 — baseline controllers

```
L243  forward_headway_hold(hf, max_hold) = 0 if hf >= H0 else min(H0 - hf, max_hold)
      NOTE  the manuscript (methods.tex, FH section) writes Daganzo's d + g(H0 - h)
L251  even_headway_hold(hf, hb, max_hold) = clip(0.5 (hb - hf), 0, max_hold)
L258-270 NC / FH / EH read obs["max_hold"]; BASELINES = {NC, FH, EH}
```

## PART 4 · L274–427 — passengers

```
L283-298 ALIGHT_FRACTION per stop, so expected alightings = APC mean
L301  destination_shares()  L312 split_whole_riders()  L330 spread_destinations()
L348  passenger_count()     D on: negative binomial with the fitted dispersion;
                            D off: the mean, rounded
L366  riders_at_stop()      D on: random arrival times; D off: evenly spaced
      WATCH do NOT use one <personFlow> per destination (bunches arrivals)
L386-424 write_scenario_file(): 18 buses at their (dispatch-adjusted) departure times,
      each followed by its Tech Ridge riders (depart="triggered"); waiting riders
      from one headway before the first bus to the last bus; S multiplies all demand
      WATCH triggered riders need the bus defined in the FILE, not via traci
```

## PART 5 · L431–840 — `simulate()`

### L479–535 — all randomness drawn up front (paired across controllers)

```
L486  dwell_noise    (D)  lognormal, median 1
L489-490 run_factor  (T)  exp(N(0, RUN_LOG_SD[segment])), clipped 0.5-2.5
L492-494 traffic_stress (T, optional)  clip(N(1, sigma_s), 0.8, 1.2), 1 when sigma_s = 0
L496  dispatch_draw  (T)  bootstrap from the fitted deviations
L498-504 weather_stress (W) lognormal mean 1, CV eta, clipped 0.5-3
L506-510 surge_factor (S) clip(N(1, sigma_d), 1, 10)
L515-524 breakdown_at (B) {bus: stop}
      WHY   every draw happens in a fixed order whether or not the disturbance is on,
            so switching one on does not change the others
L526-535 departures and running_order (buses can swap if dispatch deviations are large)
```

### L537–565 — start SUMO

```
L540-543 per-run port and file names (parallel-safe); write the scenario
L546-557 command: sumo (or sumo-gui); --tripinfo-output.write-unfinished
```

### L585–737 — the main loop (one pass = one simulated second)

```
L596  stop when all 18 buses have entered and left
L599  for bus in BUS_NAMES      <-- FIXED ORDER
L623-698 (1) JUST ARRIVED at stop i
      L629-633 B: breakdown here -> remove_broken_bus(), skip the rest
      L635-646 remember the last arrival here (the bus ahead), record this one
      L651-658 dwell = 8.1 + 5.0 x waiting + 2.7 x getting off, x noise if D, cap 94 s
      L662     doors_time: SUMO needs 0.5 s per rider on/off
      L667     control stop, and not the front bus of the fleet
      L670-672 hf = time since the last bus arrived HERE
      L673     hb = estimate_backward_headway(): follower's last stop + typical time
      L688-693 obs (12 keys) -> decide(obs); hold clipped to [0, max_hold]
               WATCH `skip` is returned but NOT USED — risk R5
      L698     stop_duration = max(dwell, doors_time) + hold
L700-725 (2) WAITED LONG ENOUGH: record load, resume, then the next segment's time
      factor = RUN_SCALE x run_factor x traffic_stress (T) x rain x weather (W),
      applied as a speed factor (1 / time factor) so it can speed up OR slow down
L727-730 (3) JUST DROVE OFF: aim at the next stop
```

### L740–840 — results

```
L743-753 headway_cv_by_stop (all 27) and headway_cv (mean of stops 1..26)
L755-759 travel_s (removed buses excluded)
L762-771 wait_s = boardings-weighted (mean gap / 2)(1 + CV^2)
L772-796 wait_direct (SUMO-recorded, Tech Ridge and removed-bus rides excluded);
         rides_unfinished and riders_stranded should both be 0
L805-810 load_leaving
L812-824 result dict, incl. buses_removed, riders_moved, riders_stranded, surge_factor
L826-839 trace=True: per-bus (arrival time, stop index) for Marey diagrams
```

## PART 6 · L844–945 — helpers

```
L846  estimate_backward_headway()  follower = next bus in RUNNING order still in
      service; expected arrival = its last stop time + (TIME_TO_REACH[i] -
      TIME_TO_REACH[j]); not started yet -> departure + TIME_TO_REACH[i];
      no follower -> H0. Never negative.
L869  count_riders_getting_off()
L881  remove_broken_bus()  riders re-added as "moved_..." persons who walk 1 m onto
      the stop (a plain waiting stage does NOT register them at the stop)
L912  base_colour()   L919 write_coloured_stops()   L933 zoom_to_corridor()
```

## Verified behaviour (2026-09-14)

| Check | Result |
|---|---|
| Same seed across Python sessions | Identical |
| Backward headway (EH, 3 seeds, 255 decisions) | 257–927 s (was 600 s in 255 / 255) |
| No-Control headway CV vs observed test days (30 seeds) | 0.552 vs 0.504; first stop 0.357 vs 0.352; by-stop r = 0.87 |
| Loads vs APC `max_load`, weekday 07–18 | RMSE 1.0 rider, r = 0.985 |
| Calibration: calibration days / held-out test days | RMSPE 0.90% / 3.08%; GEH < 5 on 26/26 both |
| Riders unfinished / stranded | 0 / 0 |

## Findings — `corridor_sim.py`

| | |
|---|---|
| **Skip still not implemented** (R5) | L691 receives `skip` and ignores it |
| Buses stop at every stop | Real buses skip stops with no demand (APC coverage 38–93%); not modelled |
| Bunching slightly high in the second half | Simulated CV reaches 0.66 vs 0.56 observed at the last stops |
| FH formula differs from the manuscript | L243 vs Daganzo's d + g(H0 − h) |
| Lead bus never acts | L667 (`position_of > 0`) |

---

# `envs/obs.py` — what a bus sees

Turns the obs dict (12 keys; `max_hold` is not used) into the manuscript's 7-vector (Table 3.6), each near [0, 1]:
`idx/(n-1)`, `hf/H0`, `hb/H0`, `load/cap`, `queue/Q_REF`, `(w-0.5)/2.5`, `b`.

```
WATCH L25-26 divide by H0. With H0 = 600 the inputs differ from gate1 (H0 = 300),
      so any earlier weights cannot be reused. Retrain from scratch.
WATCH L16 imports Q_REF from reward.py (obs depends on the reward module).
```

---

# `envs/reward.py` — how the agent is scored

A **menu of candidate terms**; `Config` picks which (the EO2.1 deliverable).

```
L17   decode_action(a, H0=600, dt=300) -> (alpha x dt, skip)
      holds are {0, 30, 60, 90, 120} s (dt = 300 s, matching the 120 s cap)
L25-30 irregularity: irr_dev / irr_even / irr_both
L32-35 wait: wait_queue (rewards holding to even gaps) vs wait_hold (punishes
      holding) — they pull in OPPOSITE directions
L37-40 skip: skip_stranded / skip_flat — unreachable until R5 is fixed
L47   compose() = -(w1 irr + w2 wait + w3 skip), computed at the bus's NEXT
      decision (semi-MDP)
```

Finding: `Q_REF = 20.0` (L14) has never been tuned.

---

# `envs/marl_env.py` — the glue

```
L26   H0 = 600.0, dt = 300.0 (holds 0-120 s), skip_enabled = False
L33   control_stops = (0, 1, 5, 17, 20)
L46-59 MarlController.__call__(obs) IS the decide() function: reward the bus's
      previous action from this state, store the transition, learn, act
L61-63 finalize() — drop each bus's last action at episode end
      WATCH forget it between episodes and transitions leak across episodes
```

---

# Consolidated findings

| Severity | Finding | Where | Status |
|---|---|---|---|
| **High** | Even-Headway (and the MARL `hb` input) never saw the bus behind: `hb` was always 600 s | `corridor_sim.py:673`, `:846` | **Fixed 2026-09-14** (AVL-style estimate) |
| **High** | Skip action discarded | `corridor_sim.py:691` | Open (R5) |
| High | Results depended on Python hash seed | `corridor_sim.py:599` | **Fixed 2026-09-14** |
| High | `H0 = 300`, should be 600 | `corridor_sim.py:162` + 7 other sites | **Fixed 2026-09-14** |
| High | All riders rode to the last stop | `corridor_sim.py:274–424` | **Fixed 2026-09-14** |
| High | Variability assumed, not measured (R3) | `corridor_sim.py:111–190` | **Fixed 2026-09-14** (fitted, `fit_variability.py`) |
| Medium | Calibration targets included skipped-stop records (R9), ~11% too slow | `build_real_net.py` | **Fixed 2026-09-14** |
| Medium | "Faster" traffic draws had no effect | `corridor_sim.py:713–725` | **Fixed 2026-09-14** |
| Medium | Weather/traffic draw taken from the wrong bus; `D=False` had no effect | — | **Fixed 2026-09-14** |
| Medium | Breakdown was an unsourced 400 s delay | `corridor_sim.py:881` | **Fixed 2026-09-14** (removal) |
| Medium | FH formula differs from the manuscript (Daganzo) | `corridor_sim.py:243` | Open |
| Medium | Buses stop at every stop; real buses skip empty stops | — | Open |
| Medium | `wait_queue` and `wait_hold` penalise opposite behaviours | `reward.py:32–35` | By design — choose in EO2.1 |
| Medium | `CONTROL_STOPS` are positional indices | `corridor_sim.py:214` | Watch when editing corridor.txt |
| Low | `bus_env.py` has no importers; `baselines/even_headway.py` duplicates the rule | both | Open |
| Low | `Q_REF` never tuned | `reward.py:14` | Open |
