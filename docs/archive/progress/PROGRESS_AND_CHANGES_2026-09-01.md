# Progress & Changes — 2026-09-01 (prepared for Overleaf, NOT yet applied)

> **Purpose.** Document what changed since the current build, grounded and reproducible, with the code and
> equations, so it can be lifted into the manuscript when you decide. **No Overleaf/`.tex` files were edited.**
> Ready-to-paste LaTeX lives in `methods_parameterization.tex`; the figure is `calibration_validation.png`;
> the provenance long-form is `DATA_CLEANING.md`.

---

## A. What changed vs the current build — at a glance
| # | Area | Current build says | This session produced | Manuscript home |
|---|---|---|---|---|
| 1 | Dataset cleaning | §3.2.5 states the counts | **Independently reproduced** the 229,421-event subset from the 3.5 GB raw asset; exact filters + funnel + checksum verified | §3.2.5 (add reproduction note) |
| 2 | `sim_inputs` | — | Per-stop **demand / dwell / segment-time** derived from APC (point values) | §3.2.5 + a small table |
| 3 | SUMO calibration | "microsimulation **calibrated** to GEH<5 (FHWA)" | Reframed to **empirical parameterization** + a fidelity check (honest); GEH<5 kept as validation, not calibration | §3.2.3 — replace wording (see `methods_parameterization.tex`) |
| 4 | Corridor scope | full route implied | **Reduced 6-stop corridor** selected for preliminary results | §3.2 (scope note) |
| 5 | Architecture | two-phase (SUMO→Python) | **Three-phase**: add *deploy trained agents back into SUMO* via TraCI; single shared obs/action env | §3.2 (architecture) |

Everything below is grounded in code that was **run** (not sketched); numbers are reproduced from your real data.

---

## B. Changes in detail

### B.1 — Dataset cleaning, independently reproduced
**What & why.** To make the cleaning reproducible and defensible (an RTC ask), the exact filter was re-run on a fresh copy of the raw asset and shown to reproduce your committed subset.

**Cleaning filter (six rules; SoQL server-side, mirrored in pandas):**
```python
keep = (route_id == '801') & (route_id == current_route_id) & \
       (import_error == '0') & (import_trip_error == '0') & \
       (bs_id != '0') & (direction_code_id == '6')
```
Rules: study route; reported route = active route; both import-error flags clear; drop placeholder stop id 0; direction 6.

**Funnel (Route 801):**
`9,197,694 raw → 547,616 (route 801) → 524,728 (current-route match) → 480,452 (error-free) → 455,654 (clean, dir 4&6) → 229,421 (direction 6)`
**SHA-256** of the dir-6 subset: `8368412e47df32ff8a3c2837048797664315c0e7ae51c44676766b5af7f23e21`.
**Reproduction check (matches the committed manifest exactly):** 229,421 events · 29 distinct stops · 184 service days · median dwell 18.0 s. *Not filtered (reported only): GPS quality, load.* Full detail in `DATA_CLEANING.md`.

### B.2 — `sim_inputs` derivation (per-stop point values)
**Segment running time** — open-to-open time net of the stop's own dwell, so dwell is not double-counted:
$$ t^{\text{run}}_i \;=\; \operatorname{median}\!\big(\texttt{rev\_seconds}_i - \texttt{dwell\_time}_i\big),\qquad t^{\text{run}}_i \ge 0 $$
**Dwell:** $d_i = \operatorname{median}(\texttt{dwell\_time}_i)$.  **Demand:** $\lambda_i = \operatorname{mean}(\texttt{ons}_i)$ boardings per visit.
```python
df["run_seconds"] = (df["rev_seconds"] - df["dwell_time"]).clip(lower=0)
stops = df.groupby("bs_id").agg(seq=("actual_sequence","median"),
          mean_boardings=("ons","mean"), dwell_s=("dwell_time","median"),
          run_s=("run_seconds","median"), dist_mi=("rev_distance","median"))
```
Note: `rev_distance` is in **miles**, not metres (corridor geometry is taken from stop coordinates instead).

### B.3 — Corridor environment: empirical parameterization (Option B)
**What changed & why.** The current build calls the SUMO environment a *microsimulation calibrated to GEH<5*. On a schematic corridor where each edge's speed is set to reproduce the observed time, that match is by construction — so it is honestly **parameterization**, not calibration. We therefore reframe it (still SUMO, still the two/three-phase plan) as *empirical parameterization of an abstract corridor*, which is the standard in the bus-holding RL literature (Wang & Sun; Rodriguez et al. use custom abstract simulators). GEH<5 is retained but reported as an **environment-fidelity check**, not a calibration claim.

**Edge-speed parameterization:** for segment $i$ of length $L_i$ (from stop coordinates),
$$ v_i \;=\; L_i \,/\, t^{\text{run}}_i . $$

**Fidelity metrics** (M = simulated, C = observed/empirical):
$$ \mathrm{GEH} \;=\; \sqrt{\dfrac{2\,(M-C)^2}{M+C}}, \qquad
   \mathrm{RMSPE} \;=\; 100\%\times\sqrt{\dfrac{1}{n}\sum_{i=1}^{n}\!\Big(\dfrac{M_i-C_i}{C_i}\Big)^{2}} . $$

**Result (reduced 6-stop corridor):** every segment GEH < 5, RMSPE = 8.2 % (residual = bus accel/decel at stops).

| Segment | Observed (s) | Simulated (s) | GEH | % err |
|---|--:|--:|--:|--:|
| 5857–5858 | 156 | 166 | 0.83 | +6.8 |
| 5858–4540 | 119 | 129 | 0.90 | +8.4 |
| 4540–467  | 163 | 176 | 1.00 | +8.0 |
| 467–5859  | 106 | 117 | 1.04 | +10.4 |
| 5859–5606 | 193 | 207 | 0.99 | +7.3 |

**Reduced-corridor selection.** The 6 highest-ridership *contiguous* dir-6 stops — `5857, 5858, 4540, 467, 5859, 5606` (55,838 events, ≈5.7 km) — chosen by: contiguous in sequence, maximal summed boardings, terminals excluded. (Scales to the full 29 stops later.)

**Corridor build (schematic SUMO net from real stop geometry):**
```python
# nodes at projected stop coords; one edge per segment at speed v_i = L_i/run_s_i; a busStop per stop
# netconvert nodes+edges -> corridor.net.xml ; buses <stop busStop=".." duration="dwell_s"/>
```
Ready-to-paste manuscript block (subsection + table + figure): **`methods_parameterization.tex`.**

### B.4 — Architecture: three phases with one shared environment
- **Phase 1 — SUMO (parameterize + validate):** the corridor above.
- **Phase 2 — Python (train):** MARL trains in a fast AEC environment whose dynamics come from Phase 1.
- **Phase 3 — SUMO (deploy):** the *trained* policy drives the buses via TraCI for evaluation + visualization.

**Shared env contract (what makes the policy transfer Python↔SUMO):** identical observation and action in both backends.
Observation per bus agent (methods Table 3.6):
$$ o_i = \big[\, p_i,\; h^{\text{fwd}}_i,\; h^{\text{bwd}}_i,\; \ell_i,\; q_i \,\big]
   \;=\; [\text{position},\ \text{forward headway},\ \text{backward headway},\ \text{onboard load},\ \text{local queue}]. $$
Action: discrete $\{\text{proceed},\ \text{hold}\}$ (skip added at SO2). Implemented as one `AECEnv` with a `sumo_cfg` switch (Python backend when `None`, SUMO/TraCI backend when set).

**Even-Headway baseline** (Rodriguez et al., with the 0.4·H cap), holds a bus whose forward headway is below target $H^\*$:
$$ \text{hold} \;=\; \min\!\big(\max(0,\; H^\* - h^{\text{fwd}}),\; 0.4\,H^\*\big). $$
```python
def even_headway_hold(h_fwd, H, cap=0.4):
    return 0.0 if h_fwd >= H else float(min(H - h_fwd, cap*H))
```

---

### B.5 — Baseline evaluation harness (SO3): No-Control vs Even-Headway
**What.** A fleet of 8 buses runs the calibrated corridor at scheduled headway $H_0=300$ s with stochastic dwell (lognormal, CV 0.6) as a stand-in for demand variability that induces bunching. Under **No-Control** buses run freely; under **Even-Headway** each bus whose forward headway falls below $H_0$ is held (Eq. 6, 0.4·H cap). Metrics: headway CV (Eq. 5) and mean corridor travel time.

**Result (reduced corridor, single seed, with passenger demand from APC boarding rates — 111 riders):**
| Controller | Headway CV | Corridor travel (s) | Mean wait (s) | Wait SD (s) |
|---|--:|--:|--:|--:|
| No-Control | 0.151 | 940.5 | 188.9 | 136.9 |
| Even-Headway | 0.111 | 975.8 | 194.1 | 135.1 |

Even-Headway **reduces headway CV by 27 %** (regularizes spacing) at a **+4 % travel-time** cost. The **passenger-waiting benefit is negligible here — and that is the correct result at these bunching levels:** mean wait $\approx (H_0/2)(1+\mathrm{CV}^2)$ (Eq. 8), so with CV ≈ 0.1–0.15 the $\mathrm{CV}^2$ term is tiny and regularizing headways barely moves the mean wait. **EH's waiting payoff appears only under strong bunching**, which the SO1.2 disturbance generators will inject. Figure: `baseline_nc_vs_eh.png`; harness: `starter/scripts/run_baseline.py` (passengers board via SUMO `<personFlow>`; departures controlled with `resume()` so boarding and holding coexist).

**Caveats (state honestly in the paper):** single seed (Monte-Carlo replications pending); the dwell-noise perturbation is a stand-in for the calibrated demand generator (SO1.2), so the *magnitude* of bunching — and hence EH's waiting benefit — is not yet realistic. This harness is the slot the trained MARL policy plugs into for the Stage-A comparison.

### B.6 — Disturbance generators (SO1.2): Weather (W) and Breakdown (B)
**What.** Two generators injected during the SUMO run, so the controllers are tested under the non-ideal conditions the study targets:
- **Weather (W):** each segment traversal is scaled by a heavy-tailed factor $F_W\sim\mathrm{LogNormal}$, $\mathbb{E}[F_W]=1$, $\mathrm{CV}(F_W)=\eta$ (Eq. 7, Patil et al.), applied as bus max-speed $=v_i/F_W$ on that segment.
- **Breakdown (B):** one bus is immobilized at a random mid-corridor stop for $T_{\text{break}}$ s (Cao et al.), creating a large gap that bunches its followers.

**Scenario result ($\eta=0.8$, single seed):**
| Scenario | NC CV | EH CV | EH benefit | NC wait (s) | EH wait (s) |
|---|--:|--:|--:|--:|--:|
| Baseline | 0.123 | 0.096 | −22 % | 191.5 | 189.3 |
| Weather (W) | 0.209 | 0.162 | −22 % | 196.9 | 187.1 |
| Weather + Breakdown (W+B) | 0.300 | 0.276 | −8 % | 205.2 | 202.7 |

**Three findings (paper-relevant):**
1. **Disturbances create the bunching** the study is about: headway CV climbs 0.12 → 0.21 → 0.30 as W then B are added.
2. **EH's passenger-waiting benefit emerges under weather** (NC 196.9 → EH 187.1 s), where at baseline it was flat — confirming the $\mathrm{CV}^2$ relationship (Eq. 8): a waiting benefit appears once bunching is significant.
3. **Under breakdown, EH's benefit collapses to −8 %** — holding cannot fix a *stuck* bus; the breakdown gap dominates. This is a genuine limitation of the fixed rule and **motivates a learned controller (MARL) and/or rescheduling** for the B disturbance.

Figure: `disturbance_scenarios.png`; harness: `starter/scripts/run_disturbances.py`. (D/S/T — Poisson demand, surge, traffic-speed — follow the same injection pattern; not yet added.)

### B.7 — Monte-Carlo replications (30 seeds, 95% bootstrap CI) — *supersedes the single-seed tables in B.5/B.6*
Each (scenario × controller) was run over **30 seeds**. The same seed gives NC and EH the *same* disturbance realization, so EH-vs-NC is a **paired** comparison. CIs are **95% bootstrap** (Efron & Tibshirani). Weather $F_W$ is capped to $[0.5, 3]$ for physical realism (a bus slows but does not stall).

| Scenario | Controller | Headway CV [95% CI] | Mean wait (s) [95% CI] |
|---|---|---|---|
| Baseline | NC | 0.122 [0.109, 0.137] | 190 [188, 192] |
| Baseline | EH | 0.096 [0.087, 0.106] | 189 [187, 192] |
| Weather | NC | 0.498 [0.453, 0.543] | 238 [227, 250] |
| Weather | EH | 0.415 [0.374, 0.458] | 229 [219, 238] |
| W+B | NC | 0.603 [0.556, 0.654] | 261 [249, 276] |
| W+B | EH | 0.529 [0.496, 0.563] | 249 [239, 260] |

**EH vs NC — paired % change in headway CV (all significant at 95%):** Baseline **−19 % [−23, −14]**; Weather **−16 % [−22, −9]**; W+B **−10 % [−15, −5]**.

**Findings, now with statistical support:**
1. **Bunching rises sharply under disturbance** — headway CV 0.12 → 0.50 → 0.60 (baseline → W → W+B), CIs non-overlapping.
2. **EH significantly reduces headway CV in every condition, but the benefit shrinks as conditions worsen** (−19 % → −16 % → −10 %) — the breakdown is where a fixed rule loses grip, which is the gap MARL is meant to close.
3. **EH's passenger-waiting benefit is real only under disturbance** (baseline flat 190↔189; weather 238→229; W+B 261→249) — consistent with Eq. 8.

Figure: `mc_scenarios.png` (error bars = 95% CI). Data: `mc_results2.csv` (180 runs).

## C. Equations collected (for the manuscript)
1. Segment running time: $t^{\text{run}}=\operatorname{median}(\texttt{rev\_seconds}-\texttt{dwell\_time})$.
2. Edge-speed parameterization: $v_i=L_i/t^{\text{run}}_i$.
3. GEH: $\sqrt{2(M-C)^2/(M+C)}$; acceptance GEH < 5 on > 85 % of segments.
4. RMSPE: $100\%\sqrt{\tfrac1n\sum((M_i-C_i)/C_i)^2}$.
5. Headway coefficient of variation (response metric): $\mathrm{CV}_h=\sigma_h/\mu_h$.
6. Even-Headway hold: $\min(\max(0,H^\*-h^{\text{fwd}}),\,0.4H^\*)$.
7. Weather stress (already in methods, Patil et al.): $F_W\sim\mathrm{LogNormal}(\mu_{\ln},\sigma_{\ln})$ with $\mathbb{E}[F_W]=1$, $\mathrm{CV}(F_W)=\eta$, i.e. $\sigma_{\ln}^2=\ln(1+\eta^2)$, $\mu_{\ln}=-\tfrac12\sigma_{\ln}^2$.
8. Mean passenger wait vs headway regularity: $\mathbb{E}[\text{wait}]\approx \tfrac{H_0}{2}\,(1+\mathrm{CV}_h^2)$ — the waiting benefit of reducing $\mathrm{CV}_h$ scales with $\mathrm{CV}_h^2$ (small when bunching is mild; large under strong disturbances).

## D. Code (full scripts in `starter/`)
`starter/scripts/extract_sim_inputs.py` (raw→subset→sim_inputs) · `starter/scripts/calibrate_corridor.py` (build + validate) · `starter/envs/bus_env.py` (shared AEC env, Python + SUMO backends) · `starter/baselines/even_headway.py`. Key fragments are inlined above; the folder holds the runnable versions.

## E. Manuscript integration checklist (apply in Overleaf when ready)
- [ ] **§3.2.3 calibration:** replace the "microsimulation calibrated to GEH<5 (FHWA)" wording with the block in `methods_parameterization.tex`.
- [ ] Add `Figures/calibration_validation.png` and the validation table (both in that `.tex`).
- [ ] **§3.2.5 data processing:** add the reproduction note + funnel + SHA-256 (from `DATA_CLEANING.md`).
- [ ] **§3.2 scope:** note the reduced 6-stop corridor for preliminary results (scales to 29).
- [ ] **§3.2 architecture:** add the third (SUMO deployment) phase + the shared-env contract.
- [ ] **Future work:** street-level OSM microsimulation of the corridor.

## F. Not yet done (open)
Done since last update: W & B generators (B.6) and **Monte-Carlo with 95% CIs (B.7)**. Remaining: the D/S/T generators (Poisson demand, surge, traffic-speed); tuning disturbance magnitudes to data; the full 29-stop corridor; and **MARL training (Oct, needs GPU)** → then the **MARL-vs-Even-Headway** comparison drops straight into this CI'd harness.
