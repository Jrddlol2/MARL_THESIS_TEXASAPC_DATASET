# Code walkthrough — the simulator (`starter/envs/`, `starter/agents/`)

Block-by-block explanation of the simulation core: the corridor loop every experiment
drives, the MARL glue, the observation vector and the reward library.

Generated with [`docs/prompts/Code_Walkthrough_Prompt.md`](../prompts/Code_Walkthrough_Prompt.md).
**Line numbers are current as of 2026-09-14, after the breakdown-removal change**
(Week 1 fixes + bus removal + `max_hold` option).

## File index

| File | Lines | What breaks if you delete it |
|---|---|---|
| `envs/corridor_sim.py` | 866 | **Everything.** Every baseline, MARL run and the live viewer call `simulate()` |
| `envs/reward.py` | 68 | The agent has no score. Also holds `Q_REF`, which `obs.py` imports |
| `envs/obs.py` | 39 | The agent has no input |
| `envs/marl_env.py` | 63 | The network can't be used as a controller |
| `agents/ddqn.py` | 131 | No learning |
| `scripts/watch.py` | 84 | The live SUMO-GUI demo (a thin wrapper around `simulate(gui=True)`) |
| `scripts/mc.py` | 147 | The 30-seed baseline tables (options `--max-hold`, `--breakdowns`, `--only-breakdown`, `--tag`) |
| `scripts/validate_loads.py` | 89 | The load-profile check against APC `max_load` |
| `baselines/even_headway.py` | 13 | Nothing — `corridor_sim` has its own rules |
| `envs/bus_env.py` | 77 | **Nothing. No importers** (PettingZoo skeleton, superseded) |

## What changed on 2026-09-14 (and why)

| Change | Why | Where |
|---|---|---|
| `H0` 300 → **600 s** | The 2021 timetable runs every 10 min, weekdays 7 AM–6 PM | L160 |
| 12 → **18 buses** | ~87-min trip ÷ 10-min headway ≈ 9 buses on the corridor at once (observed peak median 10); twice that lets the middle buses run with a full corridor ahead and behind | L162–168 |
| Riders get off at **their own stop** | Everyone rode to the last stop, so loads were ~3× too high | L256–392 |
| Buses start with **Tech Ridge riders** | Stop 5304 has the most boardings (6.15) but is not simulated | L152, L351–365 |
| Buses handled in **fixed order** b0, b1, … | Looping over a `set()` made results depend on Python's hash seed (same seed gave CV 0.192 / 0.193 / 0.212) | L531 |
| Weather/traffic slowdown uses **this bus's** draw | It used a variable left over from whichever bus arrived last | L656–658 |
| `D=False` now **turns off** dwell noise | It had no effect | L585–586 |
| `gui=True` option | The live viewer now runs this exact code | L480–484 |
| **Breakdown = bus removed** (was a 400 s delay) | Grounded in Guedes & Borenstein 2018 (towed, trip cut) and Daganzo 2009 (out of service); the 400 s delay had no source | L461–469, L561–566, L788–816 |
| `hf` = time since the **last bus at this stop** | Still the bus ahead when no bus is removed (buses cannot overtake); correct after a removal | L568–572, L598 |
| `max_hold` option (default 0.4 × H0 = 240 s) | 0.4 × H is Rodriguez et al. 2023; other RRL caps are 90–120 s, so a 120 s check is run | L171–174, L433–434, L628 |

---

# `envs/corridor_sim.py` — the heart

**One loop that any controller drives.** A controller is a function
`decide(obs) -> (hold_seconds, skip)`. NC, FH, EH and the MARL policy are different
`decide` functions on an identical environment — the comparison is fair by construction.

## PART 1 · L79–152 — load the corridor

```
L83   STOPS          the 27 modelled stops from corridor.txt, in driving order
L94   EDGES          "e0", "e1", ... — road piece i leaves stop i
L100-102 all_stops (every dir-6 stop) and stop_data (re-ordered to corridor order)
      WATCH .loc[STOP_IDS] raises KeyError if corridor.txt names a stop missing
            from the CSVs. This is how a bad corridor edit fails.
L107-108 TECH_RIDGE 5304, SOUTHPARK_MEADOWS 5873 — the two terminals: not stops in
      the sim, but their riders are (start on board / get off at the last stop)
L111-135 NET = "real" (default): SEGMENT_LENGTH = along-road distance from
      route_shape_stops.csv. "schematic": straight-line distance.
L137-150 RUN_TIME, SEGMENT_SPEED (= length / observed run time), BASE_DWELL (>= 8 s),
      DEMAND (mean boardings), ALIGHTINGS (mean alightings)
L152  START_LOAD = Tech Ridge mean boardings (6.15)
```

## PART 2 · L156–219 — settings

```
L160  H0 = 600.0                  scheduled headway (2021 timetable)
L167-168 NUM_BUSES = 2 x 9 = 18   see the table above
L170  DWELL_NOISE_CV = 0.25       lognormal — ASSUMED, not fitted (risk R3)
L174  MAX_HOLD_FRACTION = 0.4     default max hold 240 s, for every controller
      WHY   0.4 x scheduled headway is Rodriguez et al. (2023, p. 10)
      WATCH their headway was 5 min (cap 120 s); RRL absolute caps are 90-120 s and
            none tests a 10-min headway. Under Stage B, FH hits the cap on ~25% of
            decisions, so the cap matters. simulate(max_hold=120) is the check.
L175  LONG_STOP = 600             placeholder stop length; we release buses ourselves
L176  NUM_BREAKDOWNS = 1          buses removed per run when B is on
L177  WEATHER_CV = 0.8            LABELLED SYNTHETIC weather
L179-182 FIXED_DWELL 6 s, 4 s per boarding, 90 s cap, capacity 60 — asserted, not fitted
L183  SUMO_SECONDS_PER_PERSON 0.5 SUMO's default boarding time per person
L187  TIME_TO_REACH[i]            scheduled time to reach stop i (passenger timing only)
L197  CONTROL_STOPS = [0,1,5,17,20]  bus stops 5280, 5857, 5859, 5867, 4046
      WHY   from the four §3.2.2 criteria, NOT evenly spaced
      WATCH positional indices into corridor.txt — inserting a stop shifts them
L204-219 vtype file written atomically (write-then-rename) so parallel workers
      never read half a file; width=6 is visual only
```

## PART 3 · L223–252 — baseline controllers

```
L225  forward_headway_hold(hf, max_hold) = 0 if hf >= H0 else min(H0 - hf, max_hold)
      sees only the gap AHEAD
      NOTE  the manuscript (methods.tex:680) writes FH as Daganzo's d + g(H0 - h);
            the code is the simpler "fill the gap" rule — align before MSA 2
L233  even_headway_hold(hf, hb, max_hold) = clip(0.5 (hb - hf), 0, max_hold)
      sees both neighbours (Rodriguez et al. 2023, Eq. 11)
L240-252 no_control / forward_headway / even_headway read obs["max_hold"];
      BASELINES = {NC, FH, EH}
```

## PART 4 · L256–392 — passengers

```
L265-280 ALIGHT_FRACTION per stop
      fraction = APC alightings / expected riders on board; last stop = 1
      WHY   then expected alightings per stop equal the APC mean, and the expected
            load along the corridor follows the APC data (peak ~18.5 vs APC
            mean max_load 17.1 at stop 5357)
      WATCH APC means are per recorded stop event (doors opened), not per trip —
            same basis as DEMAND, so the model is internally consistent (risk R9)

L283  destination_shares(i)   chance of getting off at each later stop
L294  split_whole_riders()    whole numbers that add up exactly (largest remainder)
L312  spread_destinations()   mixes destinations evenly over time
L330  riders_at_stop()        one <person> per rider, arrivals evenly spaced
      WATCH do NOT switch back to one <personFlow> per destination: SUMO starts
            every flow's first rider at the flow's begin time, which bunches
            arrivals (it doubled SUMO's recorded wait and inflated CV 0.11 -> 0.21)

L345-388 write_scenario_file()
      L351-365 the 18 buses, each followed by its Tech Ridge riders with
               depart="triggered" — SUMO puts them inside the bus when it starts
      WATCH triggered riders need the bus defined in a FILE; traci.vehicle.add()
            is too late ("Unknown vehicle in triggered departure")
      L367-374 waiting riders: 18 x mean boardings per stop, spread over the
               time the buses pass
      L376-379 S: 120 surge riders over 900 s (now ~1.5 headways — relatively
               MORE severe than at H0 = 300; not yet aligned to the manuscript's
               f_d scaling)
```

## PART 5 · L396–770 — `simulate()`

### L433–469 — options and all randomness drawn up front

```
L433-434 max_hold defaults to 0.4 x H0 = 240 s
L436  random = np.random.default_rng(1000 + seed)
L445  dwell_noise    (D)   lognormal, one per bus x stop
L450-452 weather_factor (W) lognormal with MEAN 1, clipped to [0.5, 3]
L455  traffic_factor (T)   uniform 0.8-1.2
L461-469 breakdown_at {bus number: stop index} (B)
      one bus from departures 2..16, at a stop 1..25; more if breakdowns > 1
      WHY   drawn before the run, in a fixed order, so every controller sees the
            identical disturbance for a given seed — that is what makes the
            Monte-Carlo comparison PAIRED. The first draw happens even when B is
            off, so turning B on does not change the D/T/W draws.
```

### L470–496 — start SUMO

```
L473-476 per-run port and file names (parallel-safe), write the scenario file
L478-488 command: sumo (or sumo-gui + --start --delay + view settings)
      --tripinfo-output.write-unfinished  so riders who never got off are counted
      --seed, --step-length 1, -e 36000
```

### L517–670 — the main loop (one pass = one simulated second)

```
L528  stop when all 18 buses have entered and left (removed buses count as left)
L531  for bus in BUS_NAMES         <-- FIXED ORDER. Never loop over a set here.
L538-550 new bus: register all 27 stops with the placeholder duration

L556-637 (1) JUST ARRIVED at stop i   (is_stopped and not was_stopped)
      L561-566 B: if this bus breaks down here -> remove_broken_bus(), record it,
               and skip everything else (it does not serve the stop)
      L568-573 remember the last arrival at this stop (the bus ahead), then record
      L581-586 dwell = min(90, 6 + 4 x waiting), x noise if D
               WHY  the feedback that CREATES bunching: a late bus finds more
                    people, dwells longer, falls further behind
      L590-591 doors_time = 0.5 s x (getting off + boarding) + 1
               WHY  SUMO needs that long to move riders; without it a rider
                    could miss their stop. Rarely binds (dwell is >= 6 s).
      L595     control stop and not the lead bus (bus 0 has no leader)
      L598     hf = time since the last bus arrived HERE
      L603-609 hb = estimated from the PREVIOUS stop, using the next bus still in
               service (skips removed buses) — the manuscript's "estimated
               backward headway"
      L623-626 obs dict (12 keys, incl. max_hold) -> decide(obs)
               WATCH `skip` is returned but NOT USED — risk R5, still open
      L628     hold clipped to [0, max_hold] for every controller
      L633     stop_duration = max(6, dwell, doors_time) + hold

L639-663 (2) WAITED LONG ENOUGH: record the load leaving, resume, then set the
      speed for the next road piece: SEGMENT_SPEED / (weather / traffic), floor 2 m/s
L665-668 (3) JUST DROVE OFF: aim at the next stop
```

### L678–770 — results

```
L681-685 headway_cv: per stop, std(gaps) / mean(gaps); averaged over stops 1..26
         (the origin is excluded — its headways are the launch schedule).
         A removed bus leaves a ~2 x H0 gap downstream, which raises the CV.
L687-690 travel_s: first-stop to last-stop time per bus (removed buses excluded)
L694-701 wait_s: boardings-weighted (mean gap / 2)(1 + CV^2) — PRIMARY wait,
         a model (random-arrival formula), not a measurement
L704-728 wait_direct: SUMO's recorded wait per rider (Tech Ridge riders and rides
         on a removed bus excluded; moved riders' second wait counted);
         rides_unfinished (boarded, never got off) and riders_stranded (moved,
         never picked up) should both be 0
L737-742 load_leaving: mean riders on board leaving each stop
L744-754 result dict, incl. buses_removed, riders_moved, riders_stranded
L756-769 trace=True: per-bus (arrival time, stop index) for Marey diagrams
```

## PART 6 · L774–853 — helpers

```
L776  count_riders_getting_off()  riders whose ride ends at this stop
L788  remove_broken_bus()         B: note riders' destinations, remove the bus,
                                  re-add each rider (not bound for this stop) as a
                                  new person who walks 1 m onto the stop and waits
                                  for the next "801" to their own stop
      WATCH SUMO drops a removed bus's riders (teleports them); the re-added
            "moved_..." person is how they keep waiting. A plain waiting stage
            does NOT register them at the stop — the short walk does.
L819  base_colour()               grey for NC, blue otherwise (GUI)
L826  write_coloured_stops()      copies the stop file with colours; positions
                                  unchanged, so a GUI run gives identical numbers
L840  zoom_to_corridor()          fit the corridor in the window
```

## Verified behaviour (2026-09-14)

| Check | Result |
|---|---|
| Same seed, Python hash seeds 0 / 5 / 7 | Identical results |
| `gui=True` path vs headless (FH, seed 1) | Identical CV and travel time |
| Riders who boarded but never got off | 0 |
| SUMO recorded wait vs headway-formula wait (FH, seed 1, D+T) | 300 s vs 306 s |
| Simulated load leaving each stop vs expected | Within 0.3 riders at every stop |
| After the removal change: 18 runs without B (3 scenarios × 3 controllers × 2 seeds) | Bit-identical to the committed Week 1 results |
| B runs (1 and 3 breakdowns, cap 240 and 120) | Buses removed as drawn; 22–83 riders moved; 0 stranded; 0 unfinished |

## Findings — `corridor_sim.py`

| | |
|---|---|
| **Skip still not implemented** (R5) | L626 receives `skip` and ignores it. `marl_env.Config.skip_enabled = False` masks it today. Implement before enabling skip in training |
| Lead bus never acts | L595 (`bus_number > 0`). Correct, but 17 of 18 buses are controllable |
| Surge severity grew relative to headway | L376–379: 120 riders over 900 s is now 1.5 headways, not 3. Manuscript defines S as a scaling factor `f_d` — align in MSA 2 |
| Breakdown count is fixed, not Poisson | L461–469 removes a fixed number of buses (1, or 3 as a check). `methods.tex:472` still describes a per-timestep Bernoulli trial with rate λ — update the text or the code |
| FH formula differs from the manuscript | L225 vs `methods.tex:680` (Daganzo's d + g(H0 − h)) |
| Dwell and traffic variability assumed | L170, L455 (risk R3) |

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
| **High** | Skip action discarded | `corridor_sim.py:626` | Open (R5) |
| High | Results depended on Python hash seed | `corridor_sim.py:531` | **Fixed 2026-09-14** |
| High | `H0 = 300`, should be 600 | `corridor_sim.py:160` + 7 other sites | **Fixed 2026-09-14** |
| High | All riders rode to the last stop | `corridor_sim.py:256–392` | **Fixed 2026-09-14** |
| Medium | Weather/traffic draw taken from the wrong bus | `corridor_sim.py:656–658` | **Fixed 2026-09-14** |
| Medium | `D=False` had no effect | `corridor_sim.py:585` | **Fixed 2026-09-14** |
| Medium | Breakdown was a 400 s delay with no RRL source | `corridor_sim.py:461–469`, `:788` | **Fixed 2026-09-14** — bus removed (Guedes & Borenstein 2018; Daganzo 2009) |
| Medium | Breakdown count fixed (1, or 3) vs manuscript's per-timestep Poisson | `corridor_sim.py:461–469`, `methods.tex:472` | Open (align text or code) |
| Medium | Surge relatively harsher at H0 = 600 | `corridor_sim.py:376` | Open (align to manuscript) |
| Medium | FH formula differs from the manuscript (Daganzo d + g(H0 − h)) | `corridor_sim.py:225`, `methods.tex:680` | Open |
| Medium | `wait_queue` and `wait_hold` penalise opposite behaviours | `reward.py:32–35` | By design — choose in EO2.1 |
| Medium | `CONTROL_STOPS` are positional indices | `corridor_sim.py:197` | Watch when editing corridor.txt |
| Low | `bus_env.py` has no importers; `baselines/even_headway.py` duplicates the rule | both | Open |
| Low | `Q_REF` never tuned | `reward.py:14` | Open |
