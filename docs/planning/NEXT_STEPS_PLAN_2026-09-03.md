# Next-Steps Plan — MARL Build (SO2) · 2026-09-03

Pause point. This is the handoff for the next session: where we are, what the grounding audit found,
the locked design, the manuscript spec to implement, and the ordered plan. Run the grounding audit
(`docs/planning/MARL_Manuscript_Grounding_Audit_Prompt.md`) before each phase.

## Where we are (done & pushed)
- **SO1 environment** — full 26-stop dir-6 corridor calibrated (RMSPE 0.75%, GEH<5 on 100% of 25
  segments); D/S/T/W/B disturbance suite; demand-responsive dwell.
- **SO3 baselines** — NC / FH / EH, N=30 paired Monte-Carlo, manuscript activation matrix
  (Stage A = D+T; ablations D+T+{S,W,B}; Stage B = all). Finding: both heuristics cut bunching, FH
  more robust than EH under stress.
- **Foundation** — `starter/envs/corridor_sim.py`: one reusable `simulate(decide, control_stops, …)`
  that baselines *and* the MARL policy will both drive (a controller = a `decide(obs)->(hold,skip)`
  function). Parity-verified against the committed baselines.
- **Grounding audit** run against the manuscript (this doc's must-fix list).

## Grounding-audit must-fix (fold into Phase 0)
1. **Wait metric (Deviation).** We currently report `wait = (H0/2)(1+CV²)` (headway model), not the
   per-passenger *simulated* wait the manuscript's metric implies. Switch to a robust **direct**
   simulated wait — inject demand so it's disturbance-robust (per-stop arrival tied to when buses
   serve the stop, or measure steady-state only), then report SUMO's recorded wait; keep the headway
   model as a cross-check.
2. **Control stops (Deviation).** FH/EH currently hold at *all* 24 interior stops; the manuscript
   restricts control actions to a *designated subset*. Derive the subset from the four criteria, then
   re-run FH/EH on it so every controller (incl. future MARL) plays by identical rules.
3. **GEH wording (Partial, presentation).** Code applies GEH to travel times; §3.2.3 words it as GEH
   on counts (limitation *c* says travel-time RMSE is primary). Reconcile the calibration reporting.

## Locked design decisions (from earlier discussion)
- Parameter-shared **DDQN under CTDE**, **custom PyTorch** (manuscript says "fully custom").
- **10-action** space (α∈{0,.1,.2,.3,.4} × binary skip); **gate on holding-only** first, enable skip
  after learning is confirmed.
- **Control-stop subset** via the four criteria (not evenly spaced); baselines re-run on the same set.
- Obs = the manuscript's **7-component** vector (Table 3.6).
- No GPU needed; **SUMO is the CPU bottleneck** → run 4–6 parallel envs (Ryzen 5 5625U / 16 GB is
  sufficient and beats free Colab for this).

## Manuscript spec to implement (Chapter 3)
- **Observation (7):** control-stop index · forward headway `h⁻` · estimated backward headway `ĥ⁺` ·
  onboard passenger count · waiting-passenger count · weather flag `w` (encoded) · breakdown flag `b`
  (binary). *(corridor_sim's obs dict currently has 5 — add `w`, `b`.)*
- **Action (10):** holding strength α × maximum holding duration **ΔT** (extract ΔT value from Ch.3);
  binary stop-skip = bypass the *next* stop; skip disallowed at the origin terminal and not on two
  consecutive trips.
- **Reward:** three additive penalty terms — (i) headway irregularity, (ii) passenger waiting time,
  (iii) degenerate-skip penalty; event-discounted return `Σ e^{-βt_k} r`. Component structure is
  fixed by the manuscript; **coefficients are the EO2.1 tuning deliverable** (tune at implementation).
- **Algorithm:** shared DDQN; each bus stores its *own* local transition + per-agent reward in one
  shared replay buffer; decentralized execution.
- **Control-stop criteria (§3.2.2):** origin terminal always; onset of high-demand segments; avoid
  high through-volume stops; no adjacent control hubs (upstream only).
- **Training:** domain-randomize S/W/B (D+T always on); episode = one operating day.

## Phased plan (ordered)

**Phase 0 — spec + must-fixes (no training).** Start here next session.
- Extract remaining Ch.3 numbers: ΔT, exact reward term forms, discount β, any stated DDQN
  hyperparameters.
- Derive the control-stop list from the four criteria using per-stop boardings / alightings /
  through-volume (through-volume ≈ onboard load carried past a stop).
- Fix the wait metric → robust direct simulated wait.
- Reconcile GEH reporting with §3.2.3.
- Re-run **NC/FH/EH, N=30**, on the derived control stops with the clean wait metric — this
  supersedes the current baseline table and becomes the fixed comparison target.

**Phase 1 — env + DDQN (code, minimal compute).**
- Finish `corridor_sim` obs (add `w`, `b`), reward (3 terms), and skip mechanics (bypass next stop +
  the two guard rules).
- Thin Gym/PettingZoo wrapper: expose decision events, collect `(o,a,r,o′)` per bus.
- Custom PyTorch DDQN: shared MLP, double-Q targets, target net, replay buffer, ε-greedy decay.
- Parallel-env runner for throughput.

**Phase 2 — fail-fast gate (~tens of minutes).**
- Train briefly on Stage A, **holding-only**; require the agent to beat NC and approach FH on
  headway CV. If not → fix reward/obs *before* spending more time. Measure seconds/episode here to
  size Phase 3 and settle the training-corridor scope.

**Phase 3 — full training (hours → overnight; laptop OK w/ parallel envs).**
- Domain-randomized training; enable skipping; checkpoint regularly.

**Phase 4 — the comparison (~1 h) = Dec 5 deliverable.**
- Evaluate the trained MARL as a *fourth* controller on Stage A / ablations / Stage B vs NC/FH/EH,
  same metrics, same seeds.

## Deferred (labeled, non-blocking)
- Empirical **NOAA Camp Mabry** rain join (the synthetic lognormal stays for out-of-support stress).
- Sync `starter/scripts/watch.py` (live viewer) to the current dwell model + NC/FH/EH.

## Critical path to Dec 5
Phase 0 (fixes + control stops + baselines) → Phase 1 (env+DDQN) → **Phase 2 gate** (the key
go/no-go) → Phase 3 (train) → Phase 4 (compare). Phases 0–2 carry almost no compute and de-risk the
whole thing; Phase 3 is the only long pole.
