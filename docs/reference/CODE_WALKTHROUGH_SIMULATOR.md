# Code walkthrough — the simulator (`starter/envs/`, `starter/agents/`)

Block-by-block explanation of the simulation core: the corridor loop every experiment
drives, the MARL glue, the observation vector and the reward library.

Generated with [`docs/prompts/Code_Walkthrough_Prompt.md`](../prompts/Code_Walkthrough_Prompt.md).
**Line numbers are current as of 2026-09-14, after the Week 2 follow-ups** (stops served on
demand, per-trip demand, skip action, Daganzo Forward-Headway).

## File index

| File | Lines | What breaks if you delete it |
|---|---|---|
| `envs/corridor_sim.py` | 1126 | **Everything.** Every baseline, MARL run and the live viewer call `simulate()` |
| `scripts/fit_variability.py` | 475 | The fitted inputs in `sim_inputs/fitted/` |
| `scripts/build_real_net.py` | 323 | The calibrated network and `results/calibration_real.csv` |
| `scripts/validate_simulator.py` | 156 | Bunching, load and stop-service checks against real buses |
| `scripts/test_simulator.py` | 113 | The pass/fail checks of FH, EH, skip and stop serving |
| `scripts/mc.py` | 154 | The 30-seed baseline tables and every sensitivity option |
| `envs/reward.py` | 68 | The agent has no score. Also holds `Q_REF`, which `obs.py` imports |
| `envs/obs.py` | 39 | The agent has no input |
| `envs/marl_env.py` | 64 | The network can't be used as a controller |
| `agents/ddqn.py` | 131 | No learning |
| `scripts/watch.py` | 84 | The live SUMO-GUI demo (a thin wrapper around `simulate(gui=True)`) |
| `baselines/even_headway.py` | 13 | Nothing — `corridor_sim` has its own rules |
| `envs/bus_env.py` | 77 | **Nothing. No importers** (PettingZoo skeleton, superseded) |

## What changed on 2026-09-14 (and why)

| Change | Why | Where |
|---|---|---|
| `H0` 300 → **600 s**; 18 buses | 2021 timetable; ~9 buses on the route at once | L175, L182–184 |
| Riders get off at their own stop; buses start with Tech Ridge riders | Loads were ~3× too high; stop 5304 not simulated | L326–480 |
| Fixed bus order | Results depended on Python's hash seed | L664 |
| Breakdown **removes the bus** | Guedes & Borenstein 2018; Daganzo 2009 | L571–580, L749–753, L1051 |
| Hold cap **120 s** (240 s = check) | RRL absolute caps are 90–120 s | L205–209 |
| **All ordinary-day values fitted** from APC | Week 2 item 5 | L123–167, L186–203 |
| **Demand per trip**, not per recorded stop | APC only records a stop when the doors open (served on 39–88% of trips) | L151–155, L167 |
| **Stops served on demand** | Real buses pass stops with nobody waiting or getting off | L688–732 |
| **Skip action** (when `skip_enabled`) | Manuscript action space; was ignored (R5) | L815–821, L688–715, L740–746 |
| **Forward-Headway = Daganzo** | Manuscript's FH is d + (α + b)(H0 − h) | L211–217, L254–265, L293–300 |
| **Backward headway estimated like AVL** | It was always the 600 s fallback | L793, L968 |
| **Speed factor** instead of max speed | "Faster" traffic draws were silently ignored | L991 |
| Surge = Wang & Sun demand factor | Was 120 extra riders at one stop | L562–566 |
| Dispatch deviation + running order | Real trips start early/late; buses can swap | L552, L582–591 |

---

# `envs/corridor_sim.py` — the heart

**One loop that any controller drives.** A controller is a function
`decide(obs) -> (hold_seconds, skip)`. NC, FH, EH and the MARL policy are different
`decide` functions on an identical environment — the comparison is fair by construction.

## PART 1 · L96–167 — load the corridor and the fitted parameters

```
L100  STOPS          the 27 modelled stops from corridor.txt, in driving order
L111  EDGES          "e0", "e1", ... — road piece i leaves stop i
L123  PERIOD         CORRIDOR_PERIOD env var: ALL (weekday 07-18, default), AM, MID, PM
L127-131 fitted stop_params.csv, model_params.json, dispatch_deviation.csv
      WATCH the network is calibrated to the ALL rows; other periods scale running
            time by RUN_SCALE instead of recalibrating
L135-139 SEGMENT_LENGTH = along-road distance between stops
L141-164 RUN_TIME, RUN_SCALE, RUN_LOG_SD (spread from neighbouring buses),
      BASE_DWELL, and DEMAND / ALIGHTINGS PER TRIP (L151-155)
      WHY   APC records a stop only when the doors open; per-record means overstate
            what an average bus sees at a stop half the buses pass
L167  START_LOAD = Tech Ridge boardings per trip (6.93 for ALL)
```

## PART 2 · L171–287 — settings

```
L175  H0 = 600.0                  scheduled headway (2021 timetable)
L182-184 NUM_BUSES = 18; START_OFFSET = 1800 s so early starters have room
L187-191 dwell model (fitted): 8.1 s + 5.0 s/boarding + 2.7 s/alighting,
      noise log-sd 0.50, cap 94 s (95th percentile)
L194  DEMAND_DISPERSION = 3.8     day-to-day demand variance / mean
L197-198 RAIN_MULTIPLIER 1.0135 (observed, n.s.) and WEATHER_CV 0.8 (synthetic eta)
L201  SURGE_SD = 1                Wang & Sun sigma_d
L203  TRAFFIC_STRESS_SD = 0       Wang & Sun sigma_s, off in the main runs
L209  MAX_HOLD_SECONDS = 120      Rodriguez et al. 0.4 H at a 5-min headway
L210  NUM_BREAKDOWNS = 1          Guedes & Borenstein single-disruption design
L216-217 DAGANZO_ALPHA 0.2, DAGANZO_SLACK 25 s   (Daganzo 2009 worked example, p. 7)
L219-220 SKIP_DECISION_DISTANCE 80 m, STOP_END_POSITION 25 m
L223-230 LANE_LENGTH read once from the net file
L238  TIME_TO_REACH[i]            typical time to reach stop i (passengers + hb estimate)
L247  CONTROL_STOPS = [0,1,5,17,20]  5280, 5857, 5859, 5867, 4046 (§3.2.2 criteria)
L250  ALWAYS_SERVED = first, last and control stops
L254-265 DAGANZO_B[i] = sum over stops up to the next control stop of
      (boardings per trip / H0) x 5.0 s  -- Daganzo's b, his Eq. 3
L283-287 vtype: speedDev="0" so SUMO adds no hidden speed randomness
```

## PART 3 · L291–322 — baseline controllers

```
L293  forward_headway_hold(hf, stop, max_hold)
      = clip(25 + (0.2 + b[stop]) x (H0 - hf), 0, max_hold)          Daganzo 2009
      on headway: holds 25 s; 5 min too early: ~107 s; very late: 0
L303  even_headway_hold(hf, hb, max_hold) = clip(0.5 (hb - hf), 0, max_hold)
L310-322 NC / FH / EH read obs; BASELINES = {NC, FH, EH}
```

## PART 4 · L326–480 — passengers

```
L335-350 ALIGHT_FRACTION per stop, so expected alightings = APC per-trip mean
L353  destination_shares()  L364 split_whole_riders()  L382 spread_destinations()
L400  passenger_count()     D on: negative binomial; D off: the mean, rounded
L418  riders_at_stop()      D on: random arrival times; D off: evenly spaced
L438-475 write_scenario_file(): buses at their departure times + Tech Ridge riders
      (depart="triggered"); waiting riders; S multiplies all demand
```

## PART 5 · L483–962 — `simulate()`

### L535–591 — all randomness drawn up front (paired across controllers)

```
L542  dwell_noise (D)        L545-546 run_factor (T)       L548-550 traffic_stress (T)
L552  dispatch_draw (T)      L554-560 weather_stress (W)   L562-566 surge_factor (S)
L571-580 breakdown_at (B)
L582-591 departures and running_order
```

### L593–621 — start SUMO

### L650–850 — the main loop (one pass = one simulated second)

```
L661  stop when all 18 buses have entered and left
L664  for bus in BUS_NAMES      <-- FIXED ORDER
L688-715 (0) APPROACHING stop i (within 80 m): stop or drive past?
      must serve: first/last/control stops, and this bus's breakdown stop
      drive past if nobody waiting AND nobody on board getting off,
      or if the controller ordered a skip (then note riders carried past)
      L711 traci.vehicle.replaceStop(bus, 0, "")  removes the upcoming stop
      L696-699 far away? do not look again until it could be within 80 m (speed)
L717-732 (0b) DRIVING PAST: when the bus passes the stop, record the passage time
      (it counts for headways and the hb estimate) and set the next segment's speed
L734-826 (1) JUST ARRIVED at a served stop i
      L740-746 riders carried past a skipped stop get off here
      L749-753 B: breakdown here -> remove_broken_bus()
      L756-766 remember the last arrival here (the bus ahead), record this one
      L769-778 dwell = 8.1 + 5.0 x waiting + 2.7 x getting off, x noise if D, cap 94 s
      L787     control stop, and not the front bus of the fleet
      L790     hf = time since the last bus arrived or passed here
      L793     hb = estimate_backward_headway()
      L808-813 obs -> decide(obs); hold clipped to [0, max_hold]
      L815-821 SKIP: if skip_enabled, order a skip of the NEXT stop -- not at the
               origin, not the last stop, not if the bus ahead skipped that stop
L828-842 (2) WAITED LONG ENOUGH: record load, resume, set_segment_speed()
L844-847 (3) JUST DROVE OFF: aim at the next stop
```

### L857–962 — results

```
headway_cv (stops 1..26) and headway_cv_by_stop; travel_s; wait_s (model) and
wait_direct (SUMO); load_leaving; rides_unfinished; buses_removed, riders_moved,
riders_stranded; surge_factor; stop_served_share; controller_skips;
riders_overcarried; trace (Marey)
```

## PART 6 · L966–1113 — helpers

```
L968  estimate_backward_headway()  follower's last stop + typical time (AVL-style)
L991  set_segment_speed()          RUN_SCALE x T x W, as a SUMO speed factor
L1006 bus_ahead()                  the leader in running order (for the skip rule)
L1016 riders_bound_for()           riders whose stop is this one
L1028 served_share_list()
L1039 count_riders_getting_off()
L1051 remove_broken_bus()          riders re-added as "moved_..." persons
L1082 base_colour()  L1089 write_coloured_stops()  L1103 zoom_to_corridor()
```

## Verified behaviour (2026-09-14)

| Check | Result |
|---|---|
| `scripts/test_simulator.py` (13 checks: Daganzo FH, EH uses hb, skip rules, stop serving) | All pass |
| Same seed across Python sessions | Identical |
| No-Control headway CV vs observed test days (30 seeds) | 0.556 vs 0.504; first stop 0.357 vs 0.352; by-stop r = 0.87 |
| Share of trips serving each stop (stops not always served) | 0.69 vs 0.64 observed, r = 0.96 |
| Loads vs APC `max_load` | about 2 riders below (APC records only door-open visits), r = 0.99 |
| Calibration: calibration days / held-out test days | RMSPE 0.90% / 3.08%; GEH < 5 on 26/26 both |
| Riders unfinished / stranded | 0 / 0 |

## Findings — `corridor_sim.py`

| | |
|---|---|
| Bunching still ~10% high in the second half | Simulated CV reaches 0.67 vs 0.56 observed at the last stops; stop serving and per-trip demand did not close it. Real operator control could explain it but the APC schedule fields cannot show it |
| Control stops always served | Real buses serve them on 47–90% of trips; needed so a controller can act |
| Lead bus never acts | L787 (`position_of > 0`) |

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
| **High** | Even-Headway (and the MARL `hb` input) never saw the bus behind: `hb` was always 600 s | `corridor_sim.py:793`, `:968` | **Fixed 2026-09-14** (AVL-style estimate) |
| **High** | Skip action discarded | `corridor_sim.py:815–821` | **Fixed 2026-09-14** (tested in `test_simulator.py`) |
| High | Results depended on Python hash seed | `corridor_sim.py:664` | **Fixed 2026-09-14** |
| High | `H0 = 300`, should be 600 | `corridor_sim.py:175` + 7 other sites | **Fixed 2026-09-14** |
| High | All riders rode to the last stop | `corridor_sim.py:326–480` | **Fixed 2026-09-14** |
| High | Variability assumed, not measured (R3) | `corridor_sim.py:123–203` | **Fixed 2026-09-14** (fitted, `fit_variability.py`) |
| Medium | Calibration targets included skipped-stop records (R9), ~11% too slow | `build_real_net.py` | **Fixed 2026-09-14** |
| Medium | "Faster" traffic draws had no effect | `corridor_sim.py:991` | **Fixed 2026-09-14** |
| Medium | Weather/traffic draw taken from the wrong bus; `D=False` had no effect | — | **Fixed 2026-09-14** |
| Medium | Breakdown was an unsourced 400 s delay | `corridor_sim.py:1051` | **Fixed 2026-09-14** (removal) |
| Medium | FH formula differed from the manuscript (Daganzo) | `corridor_sim.py:293` | **Fixed 2026-09-14** |
| Medium | Buses stopped at every stop; demand counted per recorded stop | `corridor_sim.py:688–732`, `:151–155` | **Fixed 2026-09-14** (served share r = 0.96 vs APC) |
| Medium | Bunching ~10% above observed in the second half | validation | Open (not tuned) |
| Medium | `wait_queue` and `wait_hold` penalise opposite behaviours | `reward.py:32–35` | By design — choose in EO2.1 |
| Medium | `CONTROL_STOPS` are positional indices | `corridor_sim.py:247` | Watch when editing corridor.txt |
| Low | `bus_env.py` has no importers; `baselines/even_headway.py` duplicates the rule | both | Open |
| Low | `Q_REF` never tuned | `reward.py:14` | Open |
