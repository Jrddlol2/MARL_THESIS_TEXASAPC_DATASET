# Phase 0 — Control-Stop Derivation & Audit Fixes (2026-09-03)

Closes the three grounding-audit must-fixes before the MARL build, and derives the designated control
stops from the manuscript's §3.2.2 criteria. Documentation for Overleaf transfer — no Overleaf files
edited. Companion to `FULL_CORRIDOR_UPGRADE_2026-09-02.md`.

## A. Control-stop selection (§3.2.2 criteria, applied to the data)

The manuscript leaves the **control-stop count** and set "to be finalized (design) using Section 3.2.2
criteria after calibration" (Table, §3.2). The four criteria (after Rodriguez et al. and Wang & Sun's
minimal-intervention principle) are applied to the per-stop demand and through-volume profile of the
26-stop corridor.

**Through-volume** at stop *i* = onboard riders that do **not** alight = `L_in(i) − alight(i)`, where
`L_in(i) = Σ_{k<i}(board_k − alight_k)` is the load arriving at *i*. Holding at a high-through-volume
stop penalises many in-transit riders, so those stops are avoided (criterion 3).

Thresholds (documented, data-driven): **high-demand = boardings above the corridor mean (1.52)**;
**high through-volume = above the 75th percentile (8.5)**.

| Criterion | Applied | Result (stop index) |
|---|---|---|
| 1. Origin terminal always | corridor origin | **0** (5280) |
| 2. Onset of each high-demand segment | above-mean segments {1‑2‑3}, {5‑6}, {9}, {17}, {20} → onsets | 1, 5, 9, 17, 20 |
| 3. Avoid high through-volume | idx 9 (484) through-volume 10.29 (> 8.5) | **drop 9** |
| 4. No adjacent hubs (upstream only) | surviving onsets {1,5,17,20} — none adjacent | no change |

**Designated control stops (5):** indices **{0, 1, 5, 17, 20}** = bs_ids
**5280, 5857, 5859, 5867, 4046**. Note criterion 2 places control at 5857 (idx 1), *upstream* of the
dominant demand hub 4540 (idx 3), so the agent acts before that demand propagates.

**Sufficiency check** (D+T, 3 seeds): restricting holding to these 5 stops, Forward-Headway still
reduces headway CV by **−33%** and Even-Headway by **−30%** vs No-Control (cf. −54% / −49% when
holding at all 24 interior stops). Control authority is retained and the FH/EH separation persists, so
5 control stops is sufficient; the reduced ceiling vs all-stops holding is the expected, correct
consequence of minimal intervention.

**Fair comparison.** All controllers (NC / FH / EH, and later MARL) now act at exactly these 5 stops
— implemented via `simulate(decide, control_stops=CONTROL_STOPS)` in `envs/corridor_sim.py`. This
supersedes the earlier baseline table that held at all interior stops.

## B. Wait metric (audit must-fix #1) — reconciled, both measures reported

The reported passenger wait `wait_s` is the **expected wait under random passenger arrivals given the
realized (disturbed, bunched) bus headways**:

```
w = (E[H]/2)(1 + CV²),  boardings-weighted over stops
```

This is the standard Welding/Osuna–Newell result: for uniformly-arriving passengers, the mean wait is
exactly `Σ h_j² / (2 Σ h_j)` per stop, i.e. `(E[H]/2)(1+CV²)`. It is a **simulation-derived** quantity
(it uses the realized bus arrivals, which carry the bunching and disturbance dynamics) and it is the
correct expectation under the manuscript's own premise that passenger arrival times are unobserved and
therefore modelled as random (limitation *a*). It is robust to demand-injection timing.

As a cross-check, `wait_direct` — SUMO's per-passenger recorded waiting time — is now also reported.
The two agree under mild conditions (Stage A: within ~2 s); `wait_direct` inflates only under heavy
weather, where buses reach far stops after the demand-injection window (a known artifact of a fixed
injection horizon on a long corridor, not a controller effect). Reporting both makes the wait figure
transparent and defensible.

## C. GEH reporting (audit must-fix #3) — reconciled

§3.2.3 words calibration validation as GEH on stop-event / departure **counts**. Because buses are
injected at the observed frequency, count-GEH is satisfied by construction and uninformative; the
binding calibration metric is **segment travel-time RMSPE** (0.75%), consistent with limitation *c*
("travel-time RMSE is primary until [distance] units are verified"). The calibration reporting
(`results/calibration.csv`, `figures/calibration_validation.png`) should therefore state that GEH is
applied to segment **travel times** as a closeness statistic with RMSPE binding — matching the code
(`calibrate_corridor.py`) — rather than to counts. This is a wording reconciliation; the calibration
itself (all 25 segments GEH < 5, RMSPE 0.75%) stands.

## D. Baseline results at the designated control stops — **PENDING (N=30 re-run in progress)**

> The N=30 paired Monte-Carlo (NC/FH/EH × Stage A / ablations / Stage B) restricted to the 5 control
> stops is running; this section and the figures will be filled from `results/mc_summary.md`. These
> become the fixed comparison target the MARL is evaluated against.
