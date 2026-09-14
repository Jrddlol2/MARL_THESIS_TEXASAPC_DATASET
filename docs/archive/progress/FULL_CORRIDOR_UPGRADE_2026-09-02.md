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
Monte-Carlo (`scripts/mc.py`) runs `N = 30` paired replications over the five activation-matrix
cells (Stage A, three ablations, Stage B — see §J) for each of the three baselines (NC / FH / EH),
reporting bootstrap 95% CIs and the paired change vs No-Control.

### G.1 Monte-Carlo (N = 30 paired replications, bootstrap 95% CI)

Manuscript activation matrix, three baselines. All 30 replications valid in every one of the 15
scenario×controller cells (no failed runs).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] |
|---|---|---|---|---|
| **Stage A** (D+T) | NC | 0.335 [0.312, 0.358] | 5042 [5031, 5053] | 166 [164, 168] |
|                   | FH | 0.153 [0.145, 0.160] | 5279 [5261, 5297] | 161 [160, 162] |
|                   | EH | 0.172 [0.163, 0.182] | 5201 [5187, 5215] | 159 [157, 160] |
| Abl. S (D+T+S)    | NC | 0.369 [0.350, 0.387] | 5158 [5141, 5176] | 169 [167, 171] |
|                   | FH | 0.231 [0.218, 0.243] | 5595 [5561, 5628] | 166 [165, 168] |
|                   | EH | 0.242 [0.230, 0.255] | 5377 [5358, 5397] | 163 [161, 164] |
| Abl. W (D+T+W)    | NC | 1.013 [0.951, 1.076] | 6457 [6313, 6606] | 306 [289, 323] |
|                   | FH | 0.648 [0.595, 0.709] | 7045 [6849, 7241] | 256 [237, 276] |
|                   | EH | 0.830 [0.742, 0.933] | 6656 [6512, 6800] | 280 [250, 319] |
| Abl. B (D+T+B)    | NC | 0.442 [0.402, 0.483] | 5098 [5084, 5111] | 179 [175, 184] |
|                   | FH | 0.253 [0.229, 0.279] | 5421 [5381, 5464] | 172 [169, 175] |
|                   | EH | 0.289 [0.262, 0.318] | 5297 [5277, 5316] | 169 [166, 172] |
| **Stage B** (all) | NC | 0.955 [0.894, 1.018] | 6813 [6638, 6983] | 283 [264, 302] |
|                   | FH | 0.675 [0.628, 0.725] | 7426 [7243, 7612] | 264 [245, 285] |
|                   | EH | 0.837 [0.788, 0.885] | 6997 [6850, 7148] | 268 [253, 284] |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T)       | **−54%** [−58, −51] | −3% | **−49%** [−53, −45] | −5% |
| Abl. S (D+T+S)      | **−37%** [−42, −33] | −1% | **−34%** [−37, −31] | −4% |
| Abl. W (D+T+W)      | **−36%** [−41, −31] | −16% | **−18%** [−26, −9] | −8% |
| Abl. B (D+T+B)      | **−43%** [−46, −38] | −4% | **−35%** [−39, −30] | −6% |
| Stage B (D+T+S+W+B) | **−29%** [−34, −24] | −7% | **−12%** [−18, −7] | −5% |

Figures: `results/figures/mc_headway_cv.png`, `results/figures/mc_wait.png`.

**Findings.**
1. **Bunching scales with disturbance severity.** No-Control headway CV rises from 0.34 (Stage A,
   D+T) to ~1.0 under weather and ~0.96 under the combined scenario, confirming the thesis premise
   that controllers must be evaluated under *non-ideal* conditions.
2. **Both holding heuristics significantly reduce bunching in every cell** (all CV CIs exclude
   zero), and both *tighten* the seed-to-seed spread of CV — but they are not equal.
3. **Forward-Headway is the more robust heuristic under stress.** FH beats EH on headway CV in
   every cell, and the gap *widens with severity*: under weather FH −36% vs EH −18%, and under the
   combined Stage B FH −29% vs EH −12%. FH also gives the larger wait reduction under weather
   (−16% vs −8%). Mechanistically, two-way EH depends on an *estimated* backward headway (the
   follower's arrival at the previous stop), which becomes a noisy proxy under heavy-tailed weather;
   FH needs only the cleanly-observed forward gap, so it degrades more gracefully.
4. **Both pay a travel-time cost** (holding); FH holds harder → larger CV reduction *and* larger
   travel cost (Stage A: FH +5% travel vs EH +3%). This is the regularity-vs-travel trade-off.
5. **Neither heuristic is uniformly best**, and both leave large residual bunching under weather /
   Stage B (CV still 0.65–0.84). A learned controller that adapts holding to observed conditions —
   rather than applying a fixed one- or two-way rule — is exactly what these gaps motivate.

*Heuristic-vs-heuristic preliminary results (NC / FH / EH), aligned to the manuscript activation
matrix and baselines. They establish the environment, disturbance suite, and evaluation harness;
the MARL comparison (Dec 5 target) drops in as a fourth controller on this same harness.*

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

---

## I. Stop-count reconciliation (26 modeled vs "29 observed stop IDs")

The manuscript scope states *"29 observed stop IDs."* The model uses **26**. A full scan of the raw
asset (9,197,694 rows) resolves the difference conclusively:

| Filter level | Distinct dir-6 stops |
|---|---|
| route + direction only (incl. `bs_id=0` null) | 30 |
| `bs_id ≠ 0` (no error filter) | 29 |
| full clean filter | **29** |
| real stops dropped by the error filters | **0** |

So direction 6 ever touched exactly **29 real stops** over the whole Jul–Dec 2021 window, and cleaning
removed none of them. The corridor model excludes **3** of the 29 as non-revenue:

- **5304** — origin-terminal layover (median dwell 781 s);
- **5873** — destination-terminal layover (median dwell 583 s, `run_s = 0`);
- **6361** — post-terminal sequence anomaly (`mean_seq` 21.44 > the terminal's 21.01; 0.19 mean boardings).

The remaining **26 revenue stops** are the corridor. This is a documented modeling exclusion, not a
data gap — no manuscript change is required beyond noting the two terminals and the anomaly are
represented in the data but not simulated as served segments.

## J. Manuscript activation matrix & the three baselines (SO3 alignment)

The evaluation was re-aligned to the manuscript's fixed activation matrix (§2.5). **Demand (D) and
traffic-speed variation (T) are present in every cell**; the ablations add one disturbance class each:

| Cell | Active disturbances | Role |
|---|---|---|
| **Stage A** | D + T | ideal condition |
| Ablation S | D + T + S | demand-surge only |
| Ablation W | D + T + W | weather only |
| Ablation B | D + T + B | breakdown only |
| **Stage B** | D + T + S + W + B | combined non-ideal |

(The earlier six-scenario set in §G used D-only as its baseline and applied S/W/B without T; those cells
are superseded by the matrix above. "Traffic" ≡ Stage A and "All" ≡ Stage B carried over directly.)

**Three baselines (NC / FH / EH) — and a definition correction.** The manuscript compares against
No-Control, **Forward-Headway**, and **Even-Headway**. The holding rule used in the earlier results was
in fact *forward-headway* control (it holds on the gap to the leader only). The two are now implemented
as distinct controllers:

```
Forward-Headway (FH):  hold = min(H0 − h_fwd, 0.4·H0)      if h_fwd < H0     # one-way: gap to leader
Even-Headway   (EH):   hold = clip( 0.5·(h_bwd − h_fwd), 0, 0.4·H0 )         # two-way: centre between neighbours
```

where `h_fwd` is the observed gap to the leader at the current stop and `h_bwd` is the gap to the
follower (estimated from the follower's arrival at the previous stop; single-lane corridor preserves bus
order, so leader = bus *i−1* and follower = *i+1*). So earlier "EH" figures were really **FH**; the MC
below reports all three of NC/FH/EH.

> **Deferred (labeled, not a blocker):** the weather generator is the *synthetic* heavy-tailed lognormal
> regime the manuscript permits for out-of-support stress — it must be labeled synthetic. The manuscript's
> *primary* weather exposure is an empirical NOAA rain join (Camp Mabry); that join is future work and
> does not gate the preliminary comparison.
