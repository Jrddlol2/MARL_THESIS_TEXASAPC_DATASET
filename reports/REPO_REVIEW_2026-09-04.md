# Repository Review — Judgment, Holes, and Open Questions

**Date:** 2026-09-04
**Reviewer:** Claude Code (run by R. Marquez), for Group B3
**Branch:** `review/repo-audit-2026-09-04` (branched from `dataset/texas-capmetro-801`)
**Scope:** Full pull + read of the repo, run of everything runnable on this machine,
live re-verification of the committed data evidence, and a deliberate hunt for
things a panel can question.

> **How to use this file:** This is a *findings* document, not a task tracker. It is
> intentionally opinionated — it records where the work is genuinely solid, where it is
> thin, and where it will get challenged. Each hole has: what it is → why it matters →
> where to look (file) → the likely defense question → a suggested action. Read Section 4
> first tomorrow; that is where the real work is.

---

## 0. TL;DR (read this if nothing else)

- **The data half is real and reproducible.** I re-queried the live Texas Open Data API
  today and got numbers **byte-identical** to the committed audit from 2026-08-23. The
  route-selection evidence, calibration, and Monte-Carlo result tables are internally
  consistent — no fabrication between the raw CSVs and the summary tables.
- **The MARL half does not exist yet.** The thesis is titled *"An Evaluation of
  Multi-Agent Reinforcement Learning…"* but **no agent has ever been trained**. There is
  no checkpoint, and no MARL row in any results file. Every committed number is a
  **classical baseline** (No-Control / Forward-Headway / Even-Headway). This is a
  proposal, and the code is honest about it — but it is the single biggest thing a panel
  will press on.
- **Under the exact conditions the thesis is about — weather and compound stress — the
  classical controllers barely help** (improvement ≈ −1%, confidence interval crosses
  zero). The whole bet of the thesis is that MARL will do better here, and that bet is
  currently **untested**.
- **The simulated "weather" is a made-up parameter, not fitted to the real NOAA data**
  you already have. The NOAA join proves the data *could* be used; it is not actually
  used to drive the weather disturbance.
- A handful of **stale/inconsistent docs** (stop counts, RMSPE) are easy fixes and worth
  cleaning before anyone reads the repo cold.

---

## 1. What was verified as correct

### 1.1 Live data reproducibility (strong evidence)
I re-ran the route-selection aggregation directly against `data.texas.gov` on 2026-09-04
and compared to the committed `data/audit/texas_capmetro/route_selection_audit.json`
(generated 2026-08-23):

| Metric | Route 801 (live) | Route 803 (live) | Matches committed? |
|---|---:|---:|:--:|
| All route records | 547,616 | 468,689 | ✅ exact |
| Matching current-route | 524,728 | 445,369 | ✅ exact |
| Error-free matching | 480,452 | 403,254 | ✅ exact |

The 2021 APC dataset is a static historical archive, so this stability is expected — but
it means the "why Route 801" argument (20.9% more clean stop-events, 52.3% more
boardings, 22.1% more usable segments than 803) is **fully reproducible from source**.

### 1.2 Internal consistency of committed results
- **Calibration** (`starter/results/calibration.csv`): 25 segments (26-stop corridor),
  **max |GEH| = 0.29, all GEH < 5, RMSPE = 0.75%**. Passes the methods §3.2.3 acceptance
  criterion comfortably.
- **Monte-Carlo** (`starter/results/mc_results.csv` → `mc_summary.md`): 450 data rows =
  5 scenarios × 3 controllers × 30 seeds. Per-cell mean headway CVs recomputed from the
  raw CSV **match the summary table exactly** (e.g. Stage A NC 0.331 / FH 0.237 / EH 0.271).
- **Weather-join feasibility** (`WEATHER_FEASIBILITY_EVIDENCE.md`): 229,421 APC rows,
  100% join coverage to Camp Mabry and Bergstrom, 11,804 rain-exposed rows. The code
  correctly refuses to call the wet/dry median difference a causal effect.

### 1.3 Code that runs and is correct (pure-logic layer)
Ran on Anaconda Python 3.12 (no SUMO/torch needed):
- `envs/reward.py` — reward composition and action decode: correct.
- `envs/obs.py` — 7-feature normalized observation vector: correct.
- `baselines/even_headway.py` — hold logic (0.4·H cap): correct.
- `scripts/figures.py` — regenerated all three figures from committed CSVs without error.

**Architecture judgment:** the design is genuinely good. There is **one** simulation core
(`envs/corridor_sim.py`) exposing `simulate(decide, …)`, and *every* controller — the
baselines and the future MARL policy — is just a different `decide(obs) → (hold, skip)`
function running on identical disturbances and seeds. That makes the eventual
MARL-vs-baseline comparison apples-to-apples by construction. This is the right call and
should be defended as a strength.

---

## 2. What could NOT be run here (environment gaps, not code bugs)

This machine has Anaconda (`pandas, numpy, matplotlib, scipy, requests`) but is **missing
every dependency the simulation/learning half needs**:

| Missing | Blocks |
|---|---|
| **SUMO** (`SUMO_HOME` unset, not on disk) | `corridor_sim`, `mc`, `calibrate_corridor`, `run_baseline`, `run_disturbances`, `marey`, `degradation`, `watch` |
| **PyTorch** | `agents/ddqn.py`, all training/eval |
| **PettingZoo / Gymnasium** | `envs/bus_env.py` |
| **Raw APC/NOAA files** (gitignored) + hardcoded path | `scripts/extract_sim_inputs.py` (path is `C:\Users\jared\Desktop\…` — a teammate's machine) |

None of this is broken code — it is an un-provisioned environment. To run the full repo
here: install SUMO (set `SUMO_HOME`), `pip install torch pettingzoo gymnasium`, download
the raw data from the team Drive into `data/raw/…`, and fix the hardcoded path in
`extract_sim_inputs.py`.

I did **not** run `pipeline.py all` (it mass-downloads ~1M rows to gitignored folders and
still cannot do the SUMO half); the lightweight live check in §1.1 verifies the same
claim without the download.

---

## 3. How the system is implemented (context, brief)

```
real APC data ──► sim_inputs (per-stop dwell, boardings, run-time)
                       │
                       ▼
   corridor_sim.simulate(decide, D,S,T,W,B, …)      ← the ONE environment
                       │  calls decide(obs) → (hold_seconds, skip) at control stops
        ┌──────────────┼───────────────────────────┐
        ▼              ▼                            ▼
   NC / FH / EH   MarlController               (future controllers)
   (baselines)    wraps a shared DDQN
```

- **Corridor:** 26 real Route 801 dir-6 stops, SUMO-calibrated so simulated segment times
  match APC-observed times (GEH < 5). Buses injected at `H0 = 300 s`, 12 buses.
- **Disturbances (the "non-ideal conditions"):** **D**emand (always on), **S**urge,
  **T**raffic (×U(0.8,1.2)), **W**eather (÷ heavy-tailed lognormal, intensity `eta`),
  **B**reakdown (one bus frozen). Toggled per run.
- **A controller is a function.** NC returns 0; EH holds a bus that is too close to its
  leader (0.4·H cap). MARL wraps a **parameter-shared Double-DQN** (CTDE: one shared
  Q-network for all buses, decentralized execution). Observation = 7-vector
  (`obs.py`); action = one of 10 (5 hold-fractions × skip on/off); reward =
  −(headway-irregularity + wait + degenerate-skip). Reward/action/hyperparameters are
  deliberately left as **sweepable candidates**, not committed decisions.

---

## 4. The holes — read this section carefully tomorrow

Grouped roughly by how damaging each is. Each item is a place to *investigate and decide*,
not necessarily a bug.

### H1 — The MARL agent has never been built or run *(critical)*
- **What:** No trained checkpoint exists; no results file contains a MARL row. The entire
  thesis contribution is currently a plan.
- **Why it matters:** The title promises "an evaluation of MARL." Right now there is
  nothing to evaluate. Everything committed is a classical baseline.
- **Where:** `starter/agents/ddqn.py`, `starter/scripts/train_marl.py`,
  `starter/scripts/eval_marl.py` (harnesses exist, never executed);
  `CLAUDE.md` explicitly states "The MARL simulation has NOT been run yet."
- **Likely question:** *"Show me your MARL results."* / *"How do you know MARL helps at
  all?"*
- **Suggested action:** Train even a rough DDQN checkpoint so there is **one** MARL number
  to stand on before defense. A weak-but-real result beats a plan.

### H2 — Reward, action space, and all hyperparameters are undecided *(high)*
- **What:** `reward.py` and `marl_env.py` present the reward terms, weights `w=(w1,w2,w3)`,
  ΔT, and DDQN hyperparameters as candidates to sweep — nothing is fixed.
- **Why it matters:** "What is your reward function?" currently has no committed answer.
- **Where:** `starter/envs/reward.py` (IRR/WAIT/SKIP dictionaries),
  `starter/envs/marl_env.py:Config`.
- **Likely question:** *"Justify your reward design and weights."*
- **Suggested action:** Pick and justify a default reward form + weights, run the EO2.1
  sweep, and record the rationale. Even a small sweep table is defensible.

### H3 — Under weather / compound stress, control barely works *(high — premise risk)*
- **What:** In `mc_summary.md`, the paired improvement vs No-Control collapses exactly
  where it should matter most:
  - Ablation W (D+T+W): FH −6% [CI −12, +1], EH −9% [CI −17, +1] — **CIs include 0**.
  - Stage B (all disturbances): FH −1% [−6,+3], EH −1% [−7,+5] — **essentially no effect**.
- **Why it matters:** The thesis premise is "dynamic scheduling under non-ideal
  conditions." The baselines demonstrate that *classical* control fails there. That is
  fine as motivation — but MARL then has to succeed there, and that is untested (see H1).
- **Where:** `starter/results/mc_summary.md` (paired % change table).
- **Likely question:** *"Your own results show holding doesn't help under weather — why
  will MARL be different?"*
- **Suggested action:** Have a crisp, honest argument ready (MARL can act earlier, use
  richer state, and combine holding with skipping), and ideally back it with an early
  MARL run on the W and Stage B cells.

### H4 — Simulated weather is synthetic, not fitted to the real NOAA data *(high)*
- **What:** The weather disturbance is a chosen lognormal with `eta = 0.8`
  (`corridor_sim.py: ETA = 0.8`). It is **not** estimated from the observed rain
  slowdowns, even though the NOAA↔APC join is complete and available.
- **Why it matters:** You have real weather data and real segment times; a reviewer will
  reasonably ask why the weather effect is invented instead of measured. The repo's own
  gate calls severe weather a "labeled synthetic stress test" — defensible, but only if
  stated plainly and not oversold.
- **Where:** `starter/envs/corridor_sim.py` (`ETA`, `WF` lognormal draw);
  `config/texas_capmetro_801.json` (severe-weather policy); `data/README.md`.
- **Likely question:** *"You have the rain data — why is your weather multiplier a guess?"*
- **Suggested action:** Decide the framing. Either (a) estimate an *ordinary-rain* speed
  factor from the observed wet/dry segments (with segment/time-of-day/day-type controls,
  as the audit warns) and use it to anchor `eta`, and/or (b) keep severe weather explicitly
  synthetic and say so in one clear sentence in methods.

### H5 — Direction code "6" has no compass label *(medium — data provenance)*
- **What:** Direction is a raw code; northbound/southbound, stop names, route shape, and
  scheduled headway are all blocked pending a checksum-verified 2021 GTFS snapshot. All
  archive retrieval attempts returned HTTP 401.
- **Why it matters:** The manuscript cannot yet name the direction or cite a real schedule
  headway (`H0 = 300 s` is a modeling choice, not a sourced value — see H8).
- **Where:** `config/texas_capmetro_801.json` (gtfs gate),
  `data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md`.
- **Likely question:** *"Which direction is this, and where does your headway come from?"*
- **Suggested action:** Keep trying for a 2021 GTFS (Transitland/Mobility Database with an
  account key), or state the code-only limitation explicitly and treat `H0` as a declared
  assumption.

### H6 — APC timestamps assumed Austin wall-clock *(medium)*
- **What:** The time basis is an explicit, unconfirmed assumption; DST handling is coded
  but the basis itself is not CapMetro-confirmed.
- **Where:** `config/texas_capmetro_801.json:timestamp_assumption`;
  `scripts/texas_capmetro_pipeline.py:parse_apc_datetime`.
- **Likely question:** *"How do you know these timestamps are local time?"*
- **Suggested action:** Try to confirm with CapMetro/Socrata metadata; otherwise keep it
  labeled as an assumption (it already is).

### H7 — Modeled quantities can be mistaken for measured *(medium)*
- **What:** Passenger **wait time, capacity, breakdowns, and speed trajectories are NOT in
  the APC file** — they are modeled. Also, two wait estimates **diverge sharply** under
  stress: in Stage B, the headway-model wait is ~280 s while SUMO's per-passenger
  `wait_direct` is ~742 s.
- **Why it matters:** If a table presents wait time without saying which estimator, it
  looks like a measured result. The divergence needs an explanation.
- **Where:** `starter/envs/corridor_sim.py` (`wait_s` vs `wait_direct` comments);
  `starter/results/mc_summary.md` (`wait_dir` column).
- **Likely question:** *"Which wait number is real, and why do they disagree by 2–3×?"*
- **Suggested action:** Pick one primary estimator, explain the divergence (far-stop
  passengers arrive after the injection window under heavy weather), and label every wait
  figure as modeled, not observed.

### H8 — Key sim parameters set in code, not yet sourced *(medium)*
- **What:** `H0 = 300 s`, `NBUS = 12`, and the 5 designated control stops
  (5280/5857/5859/5867/4046) are set in `corridor_sim.py`. The control-stop justification
  lives in a **code comment** citing "§3.2.2 criteria."
- **Why it matters:** The manuscript's stated justification must match the code exactly,
  and `H0`/`NBUS` should trace to a real or clearly-declared value (`CLAUDE.md` marks
  headway as `%TODO-VAL`).
- **Where:** `starter/envs/corridor_sim.py` (`H0, NBUS, CONTROL_STOPS`),
  `starter/envs/marl_env.py:Config.control_stops`.
- **Suggested action:** Make sure methods §3.2.2 and the code agree on the control-stop
  set and criteria, and source or explicitly declare `H0` and fleet size.

### H9 — Stale / inconsistent documentation *(low — but fix before anyone reads cold)*
- **`starter/README.md` says "reduced 6-stop corridor" and "29 stops"**, but the committed
  artifacts are a **26-stop** corridor (`corridor.txt`, 25 calibration segments). The
  README describes an earlier state.
- **RMSPE mismatch by context:** the README's *reduced-corridor first pass* reports RMSPE
  **8.2%**; the committed *26-stop* `calibration.csv` computes **0.75%**. Different runs —
  cite the right one.
- **Self-test vs summary mismatch:** the `corridor_sim.py` `__main__` parity comment
  expects NC~0.335 / FH~0.153 / EH~0.172 (measured at *all interior* control stops), while
  `mc_summary.md` reports FH 0.237 / EH 0.271 (at the *5 designated* stops). Not a bug, but
  anyone running the smoke test and comparing will be confused.
- **Suggested action:** Update `starter/README.md` to the 26-stop reality and the correct
  RMSPE; add one line to the self-test comment clarifying the control-stop difference.

### H10 — Scope / external validity *(expected, name it first)*
- **What:** One corridor, one route, one direction, one half-year (2021).
- **Likely question:** *"Does this generalize?"*
- **Suggested action:** State the scope as a deliberate bounded case study and note it in
  limitations/future work rather than letting the panel raise it.

---

## 5. All suggested actions, consolidated

**Before defense (highest leverage):**
1. Train at least one DDQN checkpoint → produce a single real MARL-vs-baseline number (H1).
2. Commit to and justify a reward form + weights; run the EO2.1 sweep (H2).
3. Prepare the honest "why MARL under weather" argument, ideally with an early W/Stage-B
   MARL run (H3).
4. Decide the weather framing: fit an ordinary-rain factor from real data, or state severe
   weather as explicitly synthetic (H4).

**Repo hygiene (safe, quick, do on this branch):**
5. Fix `starter/README.md` — 26 stops (not 6/29), RMSPE 0.75% (not 8.2% for the full run).
6. Clarify the `corridor_sim.py` self-test comment (control-stop set difference).
7. Pick one primary wait estimator and label all wait figures as modeled (H7).

**Data / provenance (keep pushing, or declare the limit):**
8. Keep pursuing a 2021 GTFS snapshot; until then, keep direction code-only and `H0` as a
   declared assumption (H5, H8).
9. Try to confirm the APC timestamp basis with CapMetro/Socrata (H6).

**Environment (to actually run the sim half):**
10. Install SUMO + `pip install torch pettingzoo gymnasium`; pull raw data from the team
    Drive into `data/raw/…`; fix the hardcoded path in `extract_sim_inputs.py`.

---

## 6. Reproduce this review

```bash
# live route-count verification (stdlib only, needs internet)
python scripts/texas_capmetro_pipeline.py gtfs-status        # offline, exit 0

# pure-logic self-tests (Anaconda: numpy present, no SUMO/torch needed)
python starter/envs/reward.py
cd starter/envs && python obs.py && cd ../..
python starter/baselines/even_headway.py

# regenerate committed figures from committed CSVs (run from starter/)
cd starter && python scripts/figures.py && cd ..
```

**Verification status at time of writing:** data half reproducible and internally
consistent ✅ · simulation/learning half un-runnable on this machine (deps missing) ⚠️ ·
MARL contribution not yet produced ❌.

---

*This document is a review snapshot for the 2026-09-04 investigation session. It records
judgment and open questions; it does not modify the manuscript or the committed results.*
