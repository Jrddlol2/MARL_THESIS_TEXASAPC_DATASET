# Panel Demo Runbook — MARL Dynamic Bus Scheduling (Group B3)

A step-by-step guide to **demonstrate and defend the implementation live**. For each step: what to open
or run, what appears on screen (with the real output), what to say in your own words, and why it is
done that way. Everything here was run on the project machine and the outputs are the actual ones.

**All commands run from the starter-kit directory.** In a fresh clone that is `MARL/starter/`; on the
Desktop working copy it is `THESIS Claude/starter_kit/`. Same code either way. Shell examples use
PowerShell.

**Verified environment:** SUMO 1.27.1, Python 3.12.0, PyTorch 2.12.0 (CPU), matplotlib 3.11.1,
plus `traci, sumolib, numpy, pandas`.

---

## A. Pre-flight checklist (run the night before AND ~10 min before the panel)

```powershell
# 1) SUMO on PATH + SUMO_HOME (adjust the path to your install)
$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
sumo --version              # expect: Eclipse SUMO 1.27.x
# 2) Python deps import cleanly
python -c "import traci, sumolib, numpy, pandas, torch, matplotlib; print('deps ok')"
# 3) The calibrated net and inputs exist (needed by the viewer, baselines, MC)
Test-Path sumo\corridor.net.xml, sim_inputs\stops.csv, sumo\stops.add.xml
# 4) Dry-run the two fastest steps once (should finish in seconds)
python scripts\calibrate_corridor.py
python envs\reward.py
```

If `sumo\corridor.net.xml` is missing, run `python scripts\calibrate_corridor.py` once — it builds and
calibrates the net. If `sumo` isn't found, fix `SUMO_HOME`/PATH before anything else. Have the
`results\figures\*.png` open in a folder as a fallback (Section E).

---

## B. The live demo (ordered fast → visual → substantive)

> Legend: **[SAFE]** reliable and fast · **[RISKY]** may be slow or need a display — have the fallback ready.

### B1 — The data pipeline **[SAFE, ~1 min, no run]**
**① Open** `scripts/extract_sim_inputs.py` in VSCode; also open `sim_inputs/stops.csv`.
**② On screen** the six-rule filter (lines 11–14) and the per-stop reduction (lines 21–25); `stops.csv`
has 26 rows of dwell / running time / distance / boardings.
**③ Say this** "I start from the CapMetro Automatic Passenger Counter records for July–December 2021.
This block keeps only Route 801, direction 6, drops mid-service route reassignments and the import-error
rows, and reduces about nine million events to the 229,421 that define my corridor. I take medians for
dwell, running time and distance because they're robust to layover outliers, and means for boardings
because those are the demand rates I sample. The output is this `stops.csv` — the numbers the simulator
runs on."
**④ Why** stop-event data, not trajectories, so an abstract empirically-parameterised corridor is the
honest model (Rodriguez et al., 2023; Wang & Sun, 2020). I don't stream the 3.5 GB file live — it's a
one-time step; the cleaned subset is cached.

### B2 — Calibration **[SAFE, ~6 s]**
**① Run**
```powershell
python scripts\calibrate_corridor.py
```
**② On screen** (real output):
```
iter 1: <5:100% RMSPE=9.37% GEHmax=1.56
iter 2: <5:100% RMSPE=0.75% GEHmax=0.29
calibration criterion met (RMSPE 0.75%, GEH<5 on 100%) -> sumo/corridor.* is calibrated
wrote results/calibration.csv (RMSPE 0.75%)
```
Then open `results/figures/calibration_validation.png` (points on the identity line).
**③ Say this** "I build the 26-stop corridor in SUMO and solve each edge's speed so the simulated
segment travel times match the empirical medians. Two iterations bring the error down to 0.75 percent,
with GEH below five on every segment — well inside the accepted microsimulation-calibration threshold."
**④ Why** buses are injected at the observed frequency, so counts match by construction; I therefore use
GEH on travel time as a closeness measure with RMSPE binding (FHWA, 2019; UK Highways Agency, 1996).

### B3 — SUMO live: the corridor running **[RISKY — needs a display; the centrepiece]**
**① Run**
```powershell
python scripts\watch.py EH "Weather+Breakdown"
```
**② On screen** the `sumo-gui` window: 12 buses traversing the 26-stop corridor; **control stops drawn
red**, other stops grey; a bus **flashes amber the moment it applies a hold**, red if it breaks down;
under weather the buses **bunch** (gaps collapse). Use the on-screen **Delay (ms)** box to slow it down.
**③ Say this** "This is the calibrated corridor running live. The red stops are my five control stops —
the only places a controller may act. Watch this bus flash amber: that's an Even-Headway hold, spacing
it back from the bus ahead. Under the weather factor you can see the buses start to bunch, which is
exactly the instability the controller fights."
**④ Why** the visual proof that holding = delaying departure at a control stop, and that bunching is an
emergent dynamic, not injected noise. **Fallback:** if the GUI won't open, show the pre-recorded clip /
screenshot in `demo_fallbacks/` and the Marey diagram (B6).

### B4 — Baselines, single seed **[SAFE, ~21 s]**
**① Run**
```powershell
python scripts\run_baseline.py
```
**② On screen** (real output):
```
controller | headway CV | travel (s) | wait direct (s) | wait model (s) | boarded
   NC     |    0.049   |   4523.6  |      151.7      |      150.2     |  465
   FH     |    0.016   |   4546.0  |      153.6      |      150.9     |  465
   EH     |    0.017   |   4539.3  |      151.9      |      150.6     |  465
FH vs NC: headway CV -67% ...   EH vs NC: headway CV -65% ...
```
**③ Say this** "This is a quick single-seed illustration: with only dwell noise, both holding rules cut
headway variability sharply and barely move travel time. The rigorous numbers come from the Monte-Carlo
next — this is just to show the controllers working end to end."
**④ Why** be explicit that this is one seed with dwell-noise only, so the −67 % here is *not* the headline
result; the headline is the N = 30 activation-matrix run.

### B5 — The rigorous results **[SAFE, ~1 min to show; do NOT run the full MC live]**
**① Open** `results/mc_summary.md` (the committed N = 30 table). Optionally run a tiny reproduction:
```powershell
python scripts\mc.py 5 4      # ~4 min; small N, wide CIs — pattern only
```
**② On screen** the table: Stage A (D+T) — **FH −28 % [−35, −21]**, **EH −18 % [−25, −11]** headway-CV
vs No-Control; the ablations keep the gain; **Stage B (D+T+S+W+B) ≈ −1 %** — control collapses.
**③ Say this** "Over thirty matched-seed replications with bootstrap confidence intervals, both fixed
controllers significantly reduce headway irregularity under mild disturbance — the intervals exclude
zero. But under combined weather-plus-breakdown stress they fall back to no-control levels. That
degradation is the whole motivation for a learning controller."
**④ Why** matched seeds isolate the controller; bootstrap CIs give the significance (Efron & Tibshirani,
1993). The full MC is ~15–22 min, so it's pre-computed; the small run only shows the direction.

### B6 — The figures (the story) **[SAFE, seconds]**
```powershell
python scripts\figures.py      # ~4 s  -> calibration_validation, mc_headway_cv, mc_wait
python scripts\marey.py        # ~34 s -> marey_diagram (time-space trajectories; bunching = converging lines)
```
Show `marey_diagram.png` (bunching), `mc_headway_cv.png` (the bars + CIs), `degradation_curve.png`
(advantage shrinks as weather rises). **Say:** "The Marey diagram is time on one axis, position on the
other; lines that converge are buses bunching. The degradation curve shows the control advantage
narrowing as weather intensifies — again pointing to an adaptive policy."

### B7 — The MARL agent **[SAFE to show; full training is offline]**
**① Open** `agents/ddqn.py`, `envs/marl_env.py`, `envs/reward.py`. **Run the self-tests:**
```powershell
python agents\ddqn.py     # ~31 s -> "greedy accuracy ... = 0.92 (chance = 0.10)"
python envs\reward.py     # instant -> on-time -0.075, bunched -0.480, bunched+skip -0.730
```
Show `results/figures/gate1_convergence.png`.
**③ Say this** "Each bus is an agent sharing one Double-DQN network — centralised training, decentralised
execution. The self-test proves the learner works: on a controlled task it reaches 92 percent versus 10
percent chance. The reward self-test shows the shaping — near-zero when the bus is on-headway, strongly
negative when it's bunched. The convergence figure is the fail-fast gate; the full domain-randomised
training runs offline over several hours."
**④ Why** discrete 10-action space → value-based; Double-DQN tempers the overestimation the heavy-tailed
regime would amplify (van Hasselt et al., 2016; Mnih et al., 2015); parameter sharing = fleet-size
invariance (Gupta et al., 2017); event-driven control = semi-MDP (Bradtke & Duff, 1995).

---

## C. Know your codebase (where to point in VSCode)

| File | One line | The lines that matter |
|---|---|---|
| `envs/corridor_sim.py` | The simulation core every controller drives. | 53–57 the FH/EH control laws; 122–138 demand-responsive dwell + the control hook (`decide(obs)`); 84–87 the pre-drawn weather/traffic fields. |
| `agents/ddqn.py` | Parameter-shared Double-DQN. | 92–108 `learn()` — online net selects the next action, target net evaluates it (double-Q). |
| `envs/reward.py` | The three-term reward library. | 25–40 candidate terms (irregularity / waiting / skip); 47–57 `compose()` = −(w1·irr+w2·wait+w3·skip). |
| `envs/marl_env.py` | Config + semi-MDP assembly. | 20–36 `Config` (every knob); 46–59 reward realised at the bus's *next* decision, transition pushed, learn, act. |
| `scripts/mc.py` | Matched-seed Monte-Carlo + CIs. | 43–47 bootstrap CI; 50–57 paired % change; 63 the (scenario × controller × seed) grid. |

Practice: open each file, scroll to those lines, and say what they do in one sentence.

---

## D. Anticipated panel questions (answers you can point to)

**Provenance & integrity**
- *Where did the data come from?* — CapMetro Automatic Passenger Counter records, July–December 2021,
  Route 801 direction 6; a public agency dataset. The simulator consumes `sim_inputs/stops.csv`, derived
  by `scripts/extract_sim_inputs.py`.
- *Why this route/direction?* — it's a high-frequency Rapid corridor with heavy ridership (≈810,309
  boardings over 184 service days in the window); the selection is documented in the route-selection
  audit and the manuscript's scope section.
- *How many records, what did you drop, and why?* — six rules: route = 801, operating route = scheduled
  route (drops reassignments), both import-error flags clear, valid stop id, direction 6. That takes
  ~9.2 M events to 229,421.
- *How do we know it's reproducible / not tampered?* — the cleaned subset carries a SHA-256 checksum, and
  the whole reduction is one script.
- *What does the data NOT give you?* — passenger arrival times, vehicle capacity, breakdowns, or an
  authoritative schedule. Those are simulated or synthetic layers, and I keep them labelled as such.
- *What are the units on distance?* — `rev_distance` is in miles; that's flagged in the code.
- *Where does weather come from?* — currently a **synthetic** lognormal factor; the empirical NOAA
  precipitation join is future work, not claimed as done.

**Tooling**
- *What is SUMO?* — Simulation of Urban MObility, an open-source microscopic traffic simulator (Lopez et
  al., 2018); I drive it from Python through its TraCI control interface. *Why not a commercial tool?* —
  it's open, scriptable, reproducible, and standard in this literature.
- *What is `netconvert` / TraCI?* — `netconvert` builds the road network from node/edge files; TraCI is
  the live API I use to add buses, read stops, hold, and set speeds each simulation step.
- *Why Python / PyTorch / a DDQN you didn't write from scratch?* — standard, inspectable RL stack;
  `agents/ddqn.py` is my own implementation of the update, and its self-test proves it learns.
- *What is a Marey diagram?* — a time–space plot of each bus's trajectory; converging lines = bunching.

**Methodology**
- *Why an abstract corridor and not a full OSM street network?* — the APC gives stop-event points, not
  trajectories, so a street-level network can't be justified from the data; empirically parameterised
  corridors are the norm in bus-holding RL (Rodriguez et al., 2023; Wang & Sun, 2020). Street-level
  microsimulation is stated future work.
- *Why GEH on travel time?* — because injecting at the observed frequency makes counts match by
  construction, so I repurpose GEH as a travel-time closeness measure with RMSPE binding (FHWA, 2019).
- *Why does dwell depend on the queue?* — that coupling is what produces bunching: a late bus collects
  more riders, dwells longer, falls further behind — the Newell–Potts instability (Daganzo, 2009).
- *Why these five control stops?* — derived from the four §3.2.2 criteria (origin; onset of high-demand
  segments; avoid high through-volume; upstream-only for adjacent hubs); I *measured* that five stops
  still cut CV ~a third under ideal demand, so they're sufficient.
- *Why Double-DQN + parameter sharing + CTDE?* — discrete actions → value-based; double estimator tempers
  overestimation under heavy tails (van Hasselt, 2016); one shared net = fleet-size invariance (Gupta,
  2017; Christianos, 2021); each bus contributes its own local transition (CTDE).
- *Why a semi-MDP?* — control is event-driven (only at control-stop arrivals), so an action's reward is
  realised at the bus's next decision (Bradtke & Duff, 1995).
- *Why matched-seed Monte-Carlo with bootstrap CIs?* — same disturbance realisation per seed across
  controllers isolates the control effect; bootstrap gives distribution-free 95% intervals.

**Validity & limits**
- *Is GEH<5 / RMSPE 0.75% actually good?* — yes; GEH<5 is the standard microsimulation acceptance bar,
  and 0.75% travel-time error is far inside it.
- *Is synthetic weather legitimate?* — as a controlled stressor, yes; I don't claim it's real rain, and I
  separate it from the (future) empirical NOAA exposure so a robustness result isn't attributed to an
  undeclared modelling choice.
- *Why only 30 seeds?* — enough for the bootstrap CIs to exclude zero on the Stage-A effects; the
  significant results already have tight intervals.
- *What does Stage-B degradation mean?* — under combined weather+breakdown, fixed holding falls to
  no-control level (≈−1%, CI includes zero). That's the gap the learned controller is meant to close.
- *Why would bunching occur when demand is low (~1.6 boardings per bus visit)?* — Bunching is a feedback
  instability, not a crowding effect: a bus that falls slightly behind faces a larger headway gap, so more
  passengers accumulate in that gap, its dwell lengthens, and it falls further behind (Newell-Potts;
  Daganzo, 2009). The trigger is the sensitivity of dwell to the gap, which holds at any demand level on a
  high-frequency line and compounds over 26 stops. The number that matters is the queue that builds
  between buses -- it scales with the gap, not the ~1.6 per-visit average -- plus traffic, weather, and
  breakdowns that open gaps independently of demand. It is not hypothetical here: on the real calibrated
  demand, No-Control headway CV runs 0.33 (Stage A) to 0.98 (weather), with the Marey trajectories visibly
  converging. I do NOT claim to have observed bunching directly in the APC -- I model a well-established
  instability and reproduce it in the calibrated simulation.
- *Could you just raise demand to force bunching?* — I don't, and don't need to: bunching already emerges
  at the real demand. Inflating the calibrated baseline would forfeit the study's data grounding, so
  heavier demand enters only as a labelled non-ideal stressor -- the demand-surge disturbance (S), and if
  needed a demand-multiplier sensitivity -- kept distinct from the measured baseline.

**Contribution & scope**
- *What's new vs. the cited MARL-holding work?* — a public-data-calibrated corridor plus configurable
  disturbance generators, evaluated under matched seeds, with the three data layers (real / synthetic /
  future-empirical) kept distinct — a reusable, contestable evaluation apparatus, not a private sim.
- *What's done vs. remaining?* — done: calibrated environment (SO1), disturbance suite, baseline
  evaluation (SO3 heuristics), MARL apparatus + gate (SO2). Remaining: reward-coefficient study, full
  training, trained-policy evaluation as the 4th controller, NOAA join.

**If you don't know:** say so honestly — "that's outside what the APC data supports, so I treat it as
future work" beats bluffing. Panels reward candour.

---

## E. Failure fallbacks

| If this breaks | Do this |
|---|---|
| SUMO GUI won't open (B3) | Check `SUMO_HOME`/PATH; else show `demo_fallbacks/watch_*.png` + the Marey diagram. |
| `corridor.net.xml` missing | Run `python scripts\calibrate_corridor.py` once (6 s) — it regenerates it. |
| A run stalls / is slow live | Close it; open the committed `results/…` file or the pre-saved figure instead. |
| "busStop not downstream" / insertion error | You edited vehicle length/stop positions — revert; the committed net + `stops.add.xml` are known-good. |
| MC too slow live | Never run full N=30 live; show `results/mc_summary.md`. |
| matplotlib error in a worker | Figures import matplotlib only in the parent — run `figures.py` directly, not inside a pool. |

Capture these fallbacks **before** the panel: run `watch.py` once and screenshot the GUI (control stops
red, a bus amber) into `docs/progress/demo_fallbacks/`.

---

## F. Two timings

**3-minute version (if that's all you get):** B2 calibration (6 s) → B3 SUMO live (~1 min) → B5 open the
results table → B6 the degradation story. That's the arc: *calibrated corridor → it runs → controllers
help but degrade → hence MARL.*

**Full version:** B1 → B7 in order, ~10–12 minutes of talking with the SAFE runs; keep the RISKY GUI
step early so a failure there doesn't derail the rest.
