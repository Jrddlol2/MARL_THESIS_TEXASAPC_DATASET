# Full-Corridor Upgrade — Progress & Changes (2026-09-02)

**Purpose.** Document (for Overleaf transfer — *no Overleaf files edited*) the scaling of the
SUMO environment, calibration, baseline, and disturbance experiments from the reduced 6-stop
slice to the **full Route 801 direction-code-6 corridor**, plus three modeling upgrades made
along the way. Every number, mechanism, and equation below is grounded in the committed code
under `starter_kit/`. It supersedes the 6-stop results in `PROGRESS_AND_CHANGES_2026-09-01.md`
for the environment/baseline/disturbance sections; the data-cleaning and provenance sections of
that document still stand.

> Scope note kept from the roadmap: this upgrade covers **calibration + baseline + disturbances +
> Monte-Carlo** (all fast, no training). The **MARL training corridor** is *not* fixed here — that
> is decided at the October fail-fast gate by measured wall-clock, and full-corridor baselines are
> reported regardless (Roadmap "Beyond Dec 5").

---

## A. What changed at a glance

| # | Item | Before (6-stop) | After (full corridor) |
|---|------|-----------------|-----------------------|
| 1 | Corridor scope | 6 contiguous stops (~5.7 km) | **26 revenue stops** (full dir-6 route, terminals excluded) |
| 2 | Stop ordering | hand-picked | **`mean_seq`-ordered**, verified monotonic in latitude |
| 3 | Calibration | GEH<5, RMSPE 8.2% | GEH<5 on **100%** of 25 segments, **RMSPE 0.75%** |
| 4 | Dwell model | exogenous LogNormal noise (demand-independent) | **demand-responsive** dwell = door + boarding·(waiting pax) |
| 5 | Demand injection | uniform `[0, T]` at every stop | **service-aligned** window per stop (`CUM_i`) |
| 6 | Wait metric | direct SUMO `waitingTime` | **headway model** `w=(E[H]/2)(1+CV²)`, boardings-weighted |
| 7 | Disturbance draws | sequential RNG (order-dependent) | **pre-drawn fields per seed** → truly paired NC/EH |
| 8 | Fleet size `NBUS` | 8 | 12 (to populate the longer corridor) |
| 9 | Config source | stop lists hardcoded in 3 scripts | single **`corridor.txt`** read by all scripts |

Files touched: `scripts/calibrate_corridor.py`, `scripts/run_baseline.py`,
`scripts/run_disturbances.py`, `scripts/watch.py`, new `scripts/mc.py`, `scripts/figures.py`,
new `corridor.txt`.

---

## B. Corridor definition (SO1.1)

**Selection rule.** The full direction-code-6 stop set (29 rows in `sim_inputs/stops.csv`) is
ordered by `mean_seq` — the *average observed trip position* of each stop from
`sim_inputs/stop_coordinates.csv`. This continuous index cleanly resolves the integer-`seq`
collisions (nine sequence numbers were shared by two stops each). Three stops are excluded:

- **5304** — origin-terminal layover (dwell 781 s), not a revenue stop;
- **5873** — destination-terminal layover (dwell 583 s, `run_s = 0`);
- **6361** — post-terminal anomaly (`mean_seq` 21.44 > the terminal's 21.01, only 0.19 mean
  boardings), which would break the monotone geometry.

The remaining **26 stops** are, in order:
`5280, 5857, 5858, 4540, 467, 5859, 5606, 5861, 6360, 484, 5405, 5357, 5863, 497, 5866, 2738,
2611, 5867, 6372, 4029, 4046, 5870, 5553, 6356, 5871, 5872`.

**Verification.** The latitude of the ordered stops is **strictly monotonically decreasing**
(north→south) with no backtracking — confirming a clean linear corridor. The list lives in one
file, `corridor.txt`, read by every script (calibration, baseline, disturbances, live viewer).

---

## C. Calibration (SO1.1) — full corridor

The corridor is built as a 26-node schematic chain in SUMO. Inter-stop geometric distance `L_i`
comes from the stop coordinates (equirectangular projection about the corridor centroid); each
edge free-flow speed is solved so the simulated segment running time matches the empirical target
`r_i = run_s`:

```
v_i = L_i / r_i        (initial),   then   v_i ← v_i · (M_i / C_i)   (refined)
```

where `M_i` = simulated segment time, `C_i` = observed `run_s`. Two refinement iterations absorb
the systematic acceleration/deceleration overhead. Closeness is scored with the GEH statistic and
RMSPE:

```
GEH_i = sqrt( 2 (M_i − C_i)² / (M_i + C_i) )
RMSPE = sqrt( mean_i ((M_i − C_i)/C_i)² ) · 100%
```

**Result:** all 25 segments **GEH < 5** (max 0.29), **RMSPE 0.75%**. Saved to
`results/calibration.csv`; figure `results/figures/calibration_validation.png`. (The reduced
6-stop pass reported RMSPE 8.2%; the tighter value here reflects the added refinement iteration.)

---

## D. Modeling upgrade 1 — demand-responsive dwell (the bunching mechanism)

**Why.** In the 6-stop model, dwell time was an exogenous LogNormal draw *independent of how many
passengers were waiting*. That has a fatal consequence for a study of bunching: a demand **surge**
changed nothing (the "S surge" scenario was numerically identical to baseline), and headway
irregularity had no physical driver other than injected noise.

**What.** Dwell is now coupled to the passengers actually waiting at the stop (`n`, read live via
`traci.busstop.getPersonCount`):

```
d = max( d0 ,  min( d_max , d0 + β·n ) · ε ),      ε ~ LogNormal(0, σ_d)
d0 = 6 s (door dead time),  β = 4 s/passenger,  d_max = 90 s (cap),  σ_d = 0.25
```

This reproduces the classic **Newell–Potts bunching feedback**: a bus running late accumulates more
waiting passengers → dwells longer → falls further behind, while its follower catches up. Bunching
now *emerges* from demand–headway dynamics rather than being imposed. Applied identically in
`run_baseline.py` and `run_disturbances.py`.

**Effect.** Under ideal demand the fleet stays regular (headway CV ≈ 0.05, NC) — the correct
behavior for a study of *non-ideal* conditions — while every disturbance now perturbs it in a
physically meaningful way, including the surge.

---

## E. Modeling upgrade 2 — service-aligned demand window

**Why.** On a corridor ~4× longer, injecting passengers at every stop over a single window
`[0, T]` is wrong: a bus does not *reach* the far stops until ~3,500 s in, so early-injected
far-stop riders waited for a bus that had not departed, inflating measured wait ~10×.

**What.** Each stop `i` receives its demand over a window shifted by the bus's cumulative travel
time to that stop:

```
window_i = [ CUM_i ,  CUM_i + H0·(N−1) ],     CUM_i = Σ_{k<i} ( r_k + d_k )
```

(`r_k` = segment run time, `d_k` = nominal dwell, `H0` = 300 s headway, `N` = 12 buses). This keeps
per-rider wait at its steady-state value instead of absorbing the startup transient.

---

## F. Modeling upgrade 3 — headway-model wait metric

**Why.** SUMO's direct `waitingTime` remained contaminated under heavy disturbance: weather delays
push bus arrivals past even the aligned demand window, and the effect hits EH harder (holding delays
arrivals further), which *reversed* the EH/NC ordering — an artifact, not a finding.

**What.** Passenger wait is computed from the **simulated bus-arrival headways** via the standard
random-arrival model, boardings-weighted across stops:

```
w = Σ_s  q_s · (E[H_s]/2)(1 + CV_s²)  /  Σ_s q_s ,      CV_s = SD(H_s)/E[H_s]
```

where `H_s` are the simulated inter-arrival headways at stop `s` and `q_s` its mean boardings.
This is exactly the `(H0/2)(1+CV²)` relationship already cited in the methods; it is simulation-
driven (uses the real, bunched headways) and robust to demand-injection timing.

**Cross-check (validates the metric).** Under ideal conditions the direct SUMO wait and the model
wait agree: NC 153 s (direct) vs 155 s (model); EH 151 s vs 156 s. They diverge only where the
direct measure is known to be artifact-contaminated (heavy weather), so the model wait is reported.

---

## G. Disturbance suite & paired Monte-Carlo (SO1.2, SO3)

**Generators** (per segment `i`, per bus): weather `F_W ~ clip(LogNormal(−σ²/2, σ), 0.5, 3)` with
`σ² = ln(1+η²)`, `η = 0.8` (mean 1, heavy-tailed; speed `v_i / F_W`); traffic `F_T ~ U(0.8, 1.2)`
(speed `v_i · F_T`); breakdown = one random bus immobilized `+400 s` at a random stop; surge = a
sustained pulse of 120 extra riders over 3 headways at an upper-corridor stop (overflow propagates
downstream); baseline demand always on.

**Even-Headway control** (Rodriguez et al.): a bus whose forward headway `h < H0` is held
`min(H0 − h, 0.4·H0)` at interior stops; departures are managed with `resume()` so boarding and
holding coexist. No-Control runs the fleet freely.

**Paired design.** All disturbances are **pre-drawn as deterministic fields indexed by (bus, stop)
from a per-seed RNG**, and `--seed` is passed to SUMO. NC and EH at the same seed therefore
experience the *identical* disturbance and demand realization — a genuinely paired comparison. The
Monte-Carlo (`scripts/mc.py`) runs `N = 30` paired replications over six scenarios
(Baseline, Surge, Traffic, Weather, Breakdown, All), reporting bootstrap 95% CIs and the paired
EH-vs-NC % change.

### G.1 Single-seed illustration (one realization; MC supersedes)

| Scenario | NC CV | EH CV | NC wait (s) | EH wait (s) |
|---|---|---|---|---|
| Baseline | 0.046 | 0.023 | 150 | 151 |
| Surge | 0.182 | 0.147 | 155 | 157 |
| Traffic | 0.267 | 0.156 | 157 | 160 |
| Weather | 1.000 | 0.617 | 348 | 272 |
| Breakdown | 0.219 | 0.161 | 164 | 163 |
| All | 1.151 | 0.575 | 344 | 221 |

*Single seeds are volatile for the combined scenarios (a given seed can draw an adverse breakdown
location); the 30-seed CIs below are the reportable result.*

### G.2 Monte-Carlo (N = 30 paired replications, bootstrap 95% CI)

All 30 replications valid in every one of the 12 scenario×controller cells (no failed runs).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] |
|---|---|---|---|---|
| Baseline  | NC | 0.037 [0.034, 0.040] | 4528 [4527, 4529] | 150 [150, 151] |
| Baseline  | EH | 0.020 [0.018, 0.022] | 4551 [4549, 4553] | 151 [151, 151] |
| Surge     | NC | 0.169 [0.163, 0.177] | 4658 [4655, 4660] | 155 [154, 155] |
| Surge     | EH | 0.137 [0.133, 0.141] | 4923 [4914, 4932] | 157 [157, 157] |
| Traffic   | NC | 0.312 [0.292, 0.335] | 5038 [5023, 5053] | 164 [162, 166] |
| Traffic   | EH | 0.154 [0.145, 0.163] | 5280 [5260, 5301] | 161 [160, 162] |
| Weather   | NC | 0.963 [0.902, 1.026] | 6403 [6236, 6570] | 287 [264, 313] |
| Weather   | EH | 0.625 [0.584, 0.668] | 7029 [6825, 7236] | 245 [229, 263] |
| Breakdown | NC | 0.274 [0.220, 0.331] | 4580 [4576, 4586] | 167 [162, 172] |
| Breakdown | EH | 0.210 [0.169, 0.253] | 4743 [4699, 4791] | 165 [162, 170] |
| All       | NC | 0.963 [0.919, 1.004] | 6753 [6593, 6912] | 288 [270, 306] |
| All       | EH | 0.684 [0.633, 0.740] | 7448 [7257, 7648] | 267 [246, 289] |

**Paired EH-vs-NC % change (negative = EH better; same seed = identical disturbance):**

| Scenario | Δ Headway CV % [95% CI] | Δ Wait % [95% CI] |
|---|---|---|
| Baseline  | **−46%** [−51, −42] | +0% [+0, +0] |
| Surge     | **−19%** [−21, −18] | +1% [+1, +1] |
| Traffic   | **−51%** [−55, −46] | −2% [−3, −1] |
| Weather   | **−35%** [−38, −32] | **−15%** [−20, −10] |
| Breakdown | **−23%** [−26, −21] | −1% [−1, −0] |
| All       | **−29%** [−34, −23] | −7% [−14, +0] |

Figures: `results/figures/mc_headway_cv.png`, `results/figures/mc_wait.png`.

**Findings.**
1. **Bunching scales with disturbance severity.** No-Control headway CV rises from 0.037 (ideal)
   to ~0.96 under weather and under the combined scenario — a >25× increase — confirming the
   thesis premise that controllers must be evaluated under *non-ideal* conditions.
2. **Even-Headway significantly reduces bunching in every scenario** (all CV CIs exclude zero;
   −19% to −51% paired reduction), and it also *tightens* the seed-to-seed spread of CV.
3. **EH's passenger-wait benefit grows with disturbance severity.** Negligible under mild
   disturbance (baseline/surge/traffic/breakdown ≈ 0), but a significant **−15%** under weather;
   consistent with `wait = (H0/2)(1+CV²)`, where the CV² term only bites once bunching is severe.
4. **EH pays a travel-time cost** (holding): ≈ +0.5% ideal, rising to ≈ +10% under weather / All.
   So EH trades in-vehicle time for headway regularity, and its wait benefit appears only under
   stress — exactly the imperfect trade-off a learned MARL controller is meant to improve.
5. Weather is the dominant single disturbance; the combined "All" scenario is statistically
   indistinguishable from Weather-alone in NC headway CV (weather saturates the bunching).

*These are heuristic-vs-heuristic preliminary results (NC vs EH). They establish the environment,
the disturbance suite, and the evaluation harness; the MARL-vs-EH comparison (the Dec 5 target)
reuses this exact harness once the agent is trained.*

---

## H. Reproduce

```bash
cd starter_kit
python scripts/calibrate_corridor.py   # builds + calibrates the 26-stop net -> results/calibration.csv
python scripts/run_baseline.py         # NC vs EH, ideal demand (direct vs model wait cross-check)
python scripts/run_disturbances.py     # single-seed D/S/T/W/B + All table
python scripts/mc.py 30                 # 30-seed paired Monte-Carlo -> results/mc_summary.md
python scripts/figures.py              # calibration + MC figures -> results/figures/
python scripts/watch.py EH Weather+Breakdown   # live sumo-gui view of any scenario
```
