# Code walkthrough — the simulator (`starter/envs/`, `starter/agents/`)

Block-by-block explanation of the simulation core: the corridor loop every experiment
drives, the MARL glue, the observation vector and the reward library.

Generated with [`docs/prompts/Code_Walkthrough_Prompt.md`](../prompts/Code_Walkthrough_Prompt.md).
**Line numbers are current as of 2026-09-14** (Week 1 simulator fixes: H0 = 600 s,
18 buses, passenger destinations, Tech Ridge riders, fixed bus order).

## File index

| File | Lines | What breaks if you delete it |
|---|---|---|
| `envs/corridor_sim.py` | 791 | **Everything.** Every baseline, MARL run and the live viewer call `simulate()` |
| `envs/reward.py` | 68 | The agent has no score. Also holds `Q_REF`, which `obs.py` imports |
| `envs/obs.py` | 39 | The agent has no input |
| `envs/marl_env.py` | 63 | The network can't be used as a controller |
| `agents/ddqn.py` | 131 | No learning |
| `scripts/watch.py` | 84 | The live SUMO-GUI demo (a thin wrapper around `simulate(gui=True)`) |
| `scripts/validate_loads.py` | 89 | The load-profile check against APC `max_load` |
| `baselines/even_headway.py` | 13 | Nothing — `corridor_sim` has its own rules |
| `envs/bus_env.py` | 77 | **Nothing. No importers** (PettingZoo skeleton, superseded) |

## What changed on 2026-09-14 (and why)

| Change | Why | Where |
|---|---|---|
| `H0` 300 → **600 s** | The 2021 timetable runs every 10 min, weekdays 7 AM–6 PM | L157 |
| 12 → **18 buses** | ~87-min trip ÷ 10-min headway ≈ 9 buses on the corridor at once (observed peak median 10); twice that lets the middle buses run with a full corridor ahead and behind | L164–165 |
| Riders get off at **their own stop** | Everyone rode to the last stop, so loads were ~3× too high | L250–336 |
| Buses start with **Tech Ridge riders** | Stop 5304 has the most boardings (6.15) but is not simulated | L149, L343–359 |
| Buses handled in **fixed order** b0, b1, … | Looping over a `set()` made results depend on Python's hash seed (same seed gave CV 0.192 / 0.193 / 0.212) | L510 |
| Weather/traffic slowdown uses **this bus's** draw | It used a variable left over from whichever bus arrived last | L626–628 |
| `D=False` now **turns off** dwell noise | It had no effect | L549–550 |
| `gui=True` option | The live viewer now runs this exact code | L461–465 |

---

# `envs/corridor_sim.py` — the heart

**One loop that any controller drives.** A controller is a function
`decide(obs) -> (hold_seconds, skip)`. NC, FH, EH and the MARL policy are different
`decide` functions on an identical environment — the comparison is fair by construction.

## PART 1 · L76–149 — load the corridor

```
L80   STOPS          the 27 modelled stops from corridor.txt, in driving order
L91   EDGES          "e0", "e1", ... — road piece i leaves stop i
L99-101 all_stops (every dir-6 stop) and stop_data (re-ordered to corridor order)
      WATCH .loc[STOP_IDS] raises KeyError if corridor.txt names a stop missing
            from the CSVs. This is how a bad corridor edit fails.
L104-105 TECH_RIDGE 5304, SOUTHPARK_MEADOWS 5873 — the two terminals: not stops in
      the sim, but their riders are (start on board / get off at the last stop)
L108-132 NET = "real" (default): SEGMENT_LENGTH = along-road distance from
      route_shape_stops.csv. "schematic": straight-line distance.
L134-147 RUN_TIME, SEGMENT_SPEED (= length / observed run time), BASE_DWELL (>= 8 s),
      DEMAND (mean boardings), ALIGHTINGS (mean alightings)
L149  START_LOAD = Tech Ridge mean boardings (6.15)
```

## PART 2 · L153–213 — settings

```
L157  H0 = 600.0                  scheduled headway (2021 timetable)
L164-165 NUM_BUSES = 2 x 9 = 18   see the table above
L167  DWELL_NOISE_CV = 0.25       lognormal — ASSUMED, not fitted (risk R3)
L168  MAX_HOLD_FRACTION = 0.4     max hold 240 s, applies to every controller
L169  LONG_STOP = 600             placeholder stop length; we release buses ourselves
L170  BREAKDOWN_SECONDS = 400     now 0.67 x H0 (was 1.33 x H0)
L171  WEATHER_CV = 0.8            LABELLED SYNTHETIC weather
L173-176 FIXED_DWELL 6 s, 4 s per boarding, 90 s cap, capacity 60 — asserted, not fitted
L177  SUMO_SECONDS_PER_PERSON 0.5 SUMO's default boarding time per person
L181  TIME_TO_REACH[i]            scheduled time to reach stop i (passenger timing only)
L191  CONTROL_STOPS = [0,1,5,17,20]  bus stops 5280, 5857, 5859, 5867, 4046
      WHY   from the four §3.2.2 criteria, NOT evenly spaced
      WATCH positional indices into corridor.txt — inserting a stop shifts them
L198-213 vtype file written atomically (write-then-rename) so parallel workers
      never read half a file; width=6 is visual only
```

## PART 3 · L217–246 — baseline controllers

```
L219  forward_headway_hold(hf) = 0 if hf >= H0 else min(H0 - hf, 0.4 H0)
      sees only the gap AHEAD
L227  even_headway_hold(hf, hb) = clip(0.5 (hb - hf), 0, 0.4 H0)
      sees both neighbours
L234-246 no_control / forward_headway / even_headway, and BASELINES = {NC, FH, EH}
```

## PART 4 · L250–386 — passengers

```
L259-274 ALIGHT_FRACTION per stop
      fraction = APC alightings / expected riders on board; last stop = 1
      WHY   then expected alightings per stop equal the APC mean, and the expected
            load along the corridor follows the APC data (peak ~18.5 vs APC
            mean max_load 17.1 at stop 5357)
      WATCH APC means are per recorded stop event (doors opened), not per trip —
            same basis as DEMAND, so the model is internally consistent (risk R9)

L277  destination_shares(i)   chance of getting off at each later stop
L288  split_whole_riders()    whole numbers that add up exactly (largest remainder)
L306  spread_destinations()   mixes destinations evenly over time
L324  riders_at_stop()        one <person> per rider, arrivals evenly spaced
      WATCH do NOT switch back to one <personFlow> per destination: SUMO starts
            every flow's first rider at the flow's begin time, which bunches
            arrivals (it doubled SUMO's recorded wait and inflated CV 0.11 -> 0.21)

L339-382 write_scenario_file()
      L343-359 the 18 buses, each followed by its Tech Ridge riders with
               depart="triggered" — SUMO puts them inside the bus when it starts
      WATCH triggered riders need the bus defined in a FILE; traci.vehicle.add()
            is too late ("Unknown vehicle in triggered departure")
      L361-368 waiting riders: 18 x mean boardings per stop, spread over the
               time the buses pass
      L370-373 S: 120 surge riders over 900 s (now ~1.5 headways — relatively
               MORE severe than at H0 = 300; not yet aligned to the manuscript's
               f_d scaling)
```

## PART 5 · L390–726 — `simulate()`

### L430–449 — draw all randomness up front

```
L423  random = np.random.default_rng(1000 + seed)
L432  dwell_noise    (D)   lognormal, one per bus x stop
L437-439 weather_factor (W) lognormal with MEAN 1, clipped to [0.5, 3]
L442  traffic_factor (T)   uniform 0.8-1.2
L445-449 breakdown bus and stop (B)
      WHY   drawn before the run, in a fixed order, so every controller sees the
            identical disturbance for a given seed — that is what makes the
            Monte-Carlo comparison PAIRED
```

### L451–479 — start SUMO

```
L454-457 per-run port and file names (parallel-safe), write the scenario file
L460-469 command: sumo (or sumo-gui + --start --delay + view settings)
      --tripinfo-output.write-unfinished  so riders who never got off are counted
      --seed, --step-length 1, -e 36000
```

### L496–646 — the main loop (one pass = one simulated second)

```
L507  stop when all 18 buses have entered and left
L510  for bus in BUS_NAMES         <-- FIXED ORDER. Never loop over a set here.
L517-529 new bus: register all 27 stops with the placeholder duration

L534-607 (1) JUST ARRIVED at stop i   (is_stopped and not was_stopped)
      L545-550 dwell = min(90, 6 + 4 x waiting), x noise if D
               WHY  the feedback that CREATES bunching: a late bus finds more
                    people, dwells longer, falls further behind
      L554-555 doors_time = 0.5 s x (getting off + boarding) + 1
               WHY  SUMO needs that long to move riders; without it a rider
                    could miss their stop. Rarely binds (dwell is >= 6 s).
      L559     control stop and not the lead bus (bus 0 has no leader)
      L562     hf = time since the bus ahead arrived HERE
      L568     hb = estimated from the PREVIOUS stop (the follower hasn't
               arrived here yet) — the manuscript's "estimated backward headway"
      L584-587 obs dict (11 keys) -> decide(obs)
               WATCH `skip` is returned but NOT USED — risk R5, still open
      L589     hold clipped to [0, 240 s] for every controller
      L591-596 breakdown adds 400 s once
      L603     stop_duration = max(6, dwell, doors_time) + hold + breakdown

L609-633 (2) WAITED LONG ENOUGH: record the load leaving, resume, then set the
      speed for the next road piece: SEGMENT_SPEED / (weather / traffic), floor 2 m/s
L635-638 (3) JUST DROVE OFF: aim at the next stop
```

### L648–726 — results

```
L650-655 headway_cv: per stop, std(gaps) / mean(gaps); averaged over stops 1..26
         (the origin is excluded — its headways are the launch schedule)
L657     travel_s: first-stop to last-stop time per bus
L664-671 wait_s: boardings-weighted (mean gap / 2)(1 + CV^2) — PRIMARY wait,
         a model (random-arrival formula), not a measurement
L676-687 wait_direct: SUMO's recorded wait per rider (Tech Ridge riders excluded);
         rides_unfinished: boarded but never got off (should be 0)
L696-701 load_leaving: mean riders on board leaving each stop
L712-724 trace=True: per-bus (arrival time, stop index) for Marey diagrams
```

## PART 6 · L730–778 — helpers

```
L732  count_riders_getting_off()  riders whose ride ends at this stop
L744  base_colour()               grey for NC, blue otherwise (GUI)
L751  write_coloured_stops()      copies the stop file with colours; positions
                                  unchanged, so a GUI run gives identical numbers
L765  zoom_to_corridor()          fit the corridor in the window
```

## Verified behaviour (2026-09-14)

| Check | Result |
|---|---|
| Same seed, Python hash seeds 0 / 5 / 7 | Identical results |
| `gui=True` path vs headless (FH, seed 1, D+T+B) | Identical CV and travel time; 35 amber holds, 1 red breakdown |
| Riders who boarded but never got off | 0 |
| SUMO recorded wait vs headway-formula wait (FH, seed 1, D+T) | 300 s vs 306 s |
| Simulated load leaving each stop vs expected | Within 0.3 riders at every stop |

## Findings — `corridor_sim.py`

| | |
|---|---|
| **Skip still not implemented** (R5) | L587 receives `skip` and ignores it. `marl_env.Config.skip_enabled = False` masks it today. Implement before enabling skip in training |
| Lead bus never acts | L559 (`bus_number > 0`). Correct, but 17 of 18 buses are controllable |
| Surge severity grew relative to headway | L370–373: 120 riders over 900 s is now 1.5 headways, not 3. Manuscript defines S as a scaling factor `f_d` — align in MSA 2 |
| Breakdown is a delay, not a removal | L591–596. Manuscript §3 describes removing a bus for the rest of the day |
| Dwell and traffic variability assumed | L167, L442 (risk R3) |

---

# `envs/obs.py` — what a bus sees

Turns the 11-key obs dict into the manuscript's 7-vector (Table 3.6), each near [0, 1]:
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
L17   decode_action(a, H0=600, dt=600) -> (alpha x dt, skip)
      holds are now {0, 60, 120, 180, 240} s (were {0, 30, 60, 90, 120})
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
L26   H0 = 600.0, dt = 600.0, skip_enabled = False
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
| **High** | Skip action discarded | `corridor_sim.py:587` | Open (R5) |
| High | Results depended on Python hash seed | `corridor_sim.py:510` | **Fixed 2026-09-14** |
| High | `H0 = 300`, should be 600 | `corridor_sim.py:157` + 7 other sites | **Fixed 2026-09-14** |
| High | All riders rode to the last stop | `corridor_sim.py:250–386` | **Fixed 2026-09-14** |
| Medium | Weather/traffic draw taken from the wrong bus | `corridor_sim.py:626–628` | **Fixed 2026-09-14** |
| Medium | `D=False` had no effect | `corridor_sim.py:549` | **Fixed 2026-09-14** |
| Medium | Surge relatively harsher at H0 = 600; breakdown is a delay not a removal | `corridor_sim.py:370`, `:591` | Open (align to manuscript) |
| Medium | `wait_queue` and `wait_hold` penalise opposite behaviours | `reward.py:32–35` | By design — choose in EO2.1 |
| Medium | `CONTROL_STOPS` are positional indices | `corridor_sim.py:191` | Watch when editing corridor.txt |
| Low | `bus_env.py` has no importers; `baselines/even_headway.py` duplicates the rule | both | Open |
| Low | `Q_REF` never tuned | `reward.py:14` | Open |
