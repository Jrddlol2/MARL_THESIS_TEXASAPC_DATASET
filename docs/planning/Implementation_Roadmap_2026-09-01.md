# Implementation Roadmap (RE-BASELINED · OPTION A) — Group B3 MARL Bus-Scheduling Thesis
**Semester:** AY 2026–2027, 1st sem · **Re-baselined:** early Sep 2026 · **Reality:** only the dataset is done; MSA 1 is next week.
**Committed target by Dec 5:** a **preliminary MARL-vs-Even-Headway comparison** on the 3 metrics (reduced corridor).
**Case:** CapMetro Rapid Route 801, dir code 6 — 29 stops, 229,421 clean APC events (already acquired & audited).

> **Committed deliverable (Option A).** By **Dec 5** produce a table + figure comparing the **trained MARL controller vs the
> Even-Headway (EH) baseline** on **mean passenger waiting time, headway coefficient of variation, and mean travel time**,
> on the reduced corridor, under ideal conditions. This is the fixed endpoint — everything upstream bends to protect it.
> **What makes this possible from dataset-only:** the comparison only needs a *trained* model, **not a winning one** — a
> best-effort MARL vs EH is a valid preliminary result. So the deliverable survives even if training is mediocre.

> **Three rules that make Option A land:**
> 1. **Reduced-corridor everything.** Build + calibrate + train + compare on a **5–8-stop slice** of Route 801. Full 29 → next sem.
> 2. **Protect the last 3 weeks (Nov 10–28) for the comparison.** The pipeline must *work* by **~Nov 7**, not later.
> 3. **One hard gate (mid-Oct): does the reward move?** Pass it by **Oct 17–20** or trigger the catch-up rule (below). This is the make-or-break date for Option A.

---

## Part 0 — This week (Sep 1–5): get off zero + realistic MSA 1
From dataset-only with MSA 1 in a week, MSA 1 is a **setup gate**, not results.
- **0.1 Dataset → sim-inputs.** Re-run `scripts/texas_capmetro_pipeline.py`; export per-stop demand rates, dwell distribution, per-segment travel-time targets to `sim_inputs/`. — *Done when:* the 3 files exist and trace to the pipeline. *(Jared)*
- **0.2 Toolchain from zero.** SUMO + TraCI; Python env with PettingZoo (AEC) + Gymnasium + one parameter-sharing RL lib (RLlib or SB3); repo branch + board; compute decision (local GPU vs Colab). — *Done when:* a hello-world TraCI + random-agent loop runs. *(Jared + Badal)*
- **0.3 Reduced SUMO skeleton.** Network for a **5–8-stop slice** (not 29). — *Done when:* the slice renders with stops in sequence. *(Lopez)*
- **0.4 MSA 1 pack + IP form (Sep 5).** — *Done when:* Progress Report 1 drafted.

**MSA 1 deliverable (ready Sep 5):** data + `sim_inputs/` confirmed · toolchain live · reduced skeleton started · this plan + owners + risks.

## Suggested owner split (adjust freely)
| Member | Primary | Backup |
|---|---|---|
| **Lopez, Elijah** | SUMO network + calibration (SO1.1) | Generators |
| **Marquez, Rence** | Disturbance generators (SO1.2) + writing lead | Calibration |
| **Badal, Khalil** | MARL architecture + reward + training (SO2) | Integration |
| **Mananguit, Jared** | Integration (MARL↔SUMO) + repo/compute + eval pipeline | MARL training |
| **Medenilla, Jose Anton** | EH baseline + metrics + comparison (SO3) | Writing/viz |

---

## Part 1 — Activities (every step + "Done when")

### SO1 — Simulation environment · *Sep 8 – Oct 3* · target calibrated **reduced** env before MSA 2
**EO 1.1 SUMO build + calibrate (reduced corridor)** — Owner: Lopez
1. Finish the 5–8-stop network; stops from APC `bs_id` order + spacing. — *Done when:* buses traverse the slice.
2. Wire dwell + demand from `sim_inputs/`. — *Done when:* simulated dwell tracks empirical.
3. Extract simulated segment travel times; compute **GEH + RMSE**. — *Done when:* a GEH table prints.
4. Calibrate to **GEH<5 on >85% of modeled segments**. — *Done when:* criterion met + logged. **← SO1 gate (target Oct 3).**
5. Short calibration note. — *Done when:* it's in the repo.

**EO 1.2 Disturbance generators — D now, W kept cheap** — Owner: Marquez
6. **Demand (D)** via TraCI from calibrated rates (needed for every run). — *Done when:* boardings match rates.
7. **Weather (W)** — CV-driven lognormal travel-time factor (Patil et al.); keep it ready for the stretch comparison. — *Done when:* raising η widens the tail.
8. *(Defer S/T/B to next sem unless far ahead.)* Record generator limits. — *Done when:* a one-page note exists.

### SO2 — MARL controller · *Sep 29 – Nov 7* · **pipeline must work by ~Nov 7** · Owner: Badal (+ Jared integration)
9. **Observation** per bus agent (position, fwd/bwd headway, load, queue — methods Table 3.6). — *Done when:* `observe()` returns the spec.
10. **Action** = discrete hold/skip. — *Done when:* a held bus waits via TraCI.
11. **Wrap SUMO as a PettingZoo AEC env.** — *Done when:* passes PettingZoo API tests.
12. **Reward** = penalize headway irregularity + delay. — *Done when:* computable per step + unit-tested on a toy case.
13. **Parameter-shared policy** + algorithm (shared-param PPO/MAPPO or DDQN-family). — *Done when:* training runs without shape errors.
14. **Integrate MARL↔TraCI loop.** — *Done when:* a full episode runs with the policy in-loop. *(Jared)*
15. **Infra:** logging, checkpointing, seeds, capped episode budget. — *Done when:* a run resumes from a checkpoint.
16. **FAIL-FAST GATE — does the reward move?** Small-scale run on the slice. — *Done when:* reward trends up. **← Pass by Oct 17–20. This is the Option-A make-or-break.**
17. **Full training** to the capped budget (**best-effort is acceptable** — see catch-up). — *Done when:* a reward-convergence curve exists + weights saved by **~Nov 7**.

### SO3 — Comparison (THE committed deliverable) · *Oct 20 – Dec 5* · Owner: Medenilla
18. **Build the Even-Headway (EH) baseline** — start Oct 20, in parallel with training. — *Done when:* EH runs in the same env and emits the 3 metrics.
19. **Run the comparison:** trained MARL vs EH, ideal conditions, reduced corridor; Monte-Carlo reps, fixed seeds. — *Done when:* a table of waiting time / headway-CV / travel time for MARL vs EH exists. **← the Dec 5 deliverable (target ready Nov 21).**
20. **Plot + write up as preliminary** (methods Fig 3.4 format); state honestly whether MARL reaches parity/beats EH — either way it's a valid preliminary finding. — *Done when:* a results section + figure are drafted (by Nov 28).
21. *(Stretch, only if ahead)* add the **weather (W)** disturbance to the comparison, and/or the **NC/FH** baselines. — *Done when:* extra rows exist, or are deferred with a note.

### Deliverables & admin · continuous · Owner: Marquez (writing) + Jared (coord)
22. Progress Reports 1/2/3; replace the leftover `results.tex` NeuroSEE template before writing results; Poster + Paper (Dec 5); IP form (Sep 5), Peer Evals (Sep 26 / Oct 24 / Dec 12), NSDB tab current.

---

## Part 2 — Week-by-week Gantt (Option A)
Legend: **█** work · **▒** buffer · **◆** checkpoint · **○** internal target-ready · **▤** stretch

| Activity ↓ / Week → | 9/1 | 9/8 | 9/15 | 9/22 | 9/29 | 10/6 | 10/13 | 10/20 | 10/27 | 11/3 | 11/10 | 11/17 | 11/24 | 12/1 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| P0 Setup + tooling + data | █ | █ | | | | | | | | | | | | |
| SO1.1 SUMO build+calibrate (reduced) | | █ | █ | █ | ○ | | | | | | | | | |
| SO1.2 Generators (D, W) | | | | █ | █ | ○ | | | | | | | | |
| SO2 obs/action/reward + AEC wrap | | | | | █ | █ | █ | | | | | | | |
| SO2 integrate + **fail-fast gate (16)** | | | | | | | █ | █○ | | | | | | |
| SO2 full training (best-effort ok) | | | | | | | | █ | █ | █○ | ▒ | | | |
| SO3 EH baseline (parallel) | | | | | | | | █ | █ | | | | | |
| **SO3 MARL-vs-EH comparison** | | | | | | | | | | | █ | █ | █○ | █ |
| SO3 stretch: +W disturbance / NC-FH | | | | | | | | | | | | | ▤ | ▤ |
| Writing / poster / paper | | | | | | | | | | | | █ | █ | █ |
| **Checkpoints** | | ◆MSA1<br>PR1 | | ◆PE1 | | ◆MSA2<br>PR2 | | ◆PE2 | | | | | ◆MSA3<br>PR3 | ◆Poster<br>Paper |
| **Buffer** | | | ▒ | | | | | | | ▒ | ▒ | | | |

---

## Part 3 — What to show at each gate
| Gate | Internal target | Show |
|---|---|---|
| **MSA 1** (Sep 7–12) | Sep 5 | Data + `sim_inputs/` confirmed; toolchain live; reduced SUMO skeleton started; this plan + risks |
| **MSA 2** (Oct 5–10) | Oct 3 | **Calibrated reduced env (GEH<5)**; D (+W) generator; MARL env (obs/action/reward) wrapping it; **fail-fast gate about to run** |
| **MSA 3** (Nov 23–28) | Nov 21 | **The MARL-vs-EH comparison** (or its first pass) — reward curve + the 3-metric table/figure |
| **Poster + Paper** (Dec 5) | draft Nov 28 | Preliminary MARL-vs-EH comparison written up (+ W disturbance if reached) |

## Part 4 — Course schedule × work due
| Course date | Milestone | Internal target | Have ready |
|---|---|---|---|
| Sep 5 | IP Registry Form | Sep 4 | Form filled |
| **Sep 7–12** | **MSA 1** + PR1 | **Sep 5** | Setup + data + skeleton |
| Sep 26 | Peer Eval 1 | Sep 25 | — |
| **Oct 5–10** | **MSA 2** + PR2 | **Oct 3** | Calibrated reduced env + D/W + MARL env |
| Oct 24 | Peer Eval 2 | Oct 23 | — |
| **Nov 23–28** | **MSA 3** + PR3 | **Nov 21** | MARL-vs-EH comparison (first pass) |
| **Dec 5** | **Poster + Paper** | **Nov 28 / Dec 4** | Comparison written up (preliminary) |
| Dec 7–12 | Reassessment / Deliberation | — | Contingency |
| Dec 12 | Peer Eval 3 + Adviser Eval | Dec 11 | — |

## Part 5 — Risk register (Option A is time-tight — these matter)
| Risk | Lik/Impact | Early signal | Mitigation | Catch-up (protects the Dec 5 comparison) |
|---|---|---|---|---|
| **Fail-fast gate slips past ~Oct 20** | High/High | Reward flat at step 16 | Reward shaping; EH-imitation warm start; shrink action space; smallest possible env | **Freeze the model as-is and still run the MARL-vs-EH comparison with a best-effort/partial model** — report honestly. The deliverable survives. |
| Slow start / plan not followed | High/High | Missed internal target | Reduced corridor; weekly 30-min check vs this Gantt; backup owners | Shift into a buffer week; drop the W-stretch first |
| SUMO calibration misses GEH<5 | Med/High | GEH>5 by Sep 26 | Calibrate the slice only; dwell first, then speed | Accept GEH<5 on the busiest segments; note the rest |
| Training too slow / Colab limits | High/Med | Run > a few hrs; disconnects | Reduced corridor + capped episodes + checkpoints; book GPU early | Fewer episodes / smaller net — a trained-enough model for the comparison |
| MARL↔SUMO integration bugs | Med/High | Env fails PettingZoo tests | Mock env to isolate TraCI timing | Comparison on the reduced env; full env next sem |

**Critical path (protect these dates):** calibrate reduced env by **Oct 3** → MARL env+reward integrated by **Oct 17** → **fail-fast gate passed by Oct 20** → best-effort model + EH baseline by **Nov 7** → comparison table by **Nov 21** → written up by **Nov 28**.

## Part 6 — Next semester (Jan–Apr 2027)
Scale to full 29 stops; full disturbance matrix (D/S/T/W/B) and the real non-ideal robustness story; all baselines (NC/FH/EH); statistical rigor (bootstrap CIs / IQM); finalize Results/Discussion/Conclusion; resolve the two open citation TODOs from the reference audit; final defense.

---

### Bottom line (Option A)
The deliverable is fixed: **a MARL-vs-Even-Headway comparison on the 3 metrics by Dec 5.** It's achievable from dataset-only *if* you (1) keep everything on the 5–8-stop reduced corridor, (2) pass the **fail-fast reward gate by ~Oct 20**, and (3) accept a **best-effort model** for the comparison rather than chasing perfect convergence. Miss the Oct-20 gate and the catch-up still delivers the comparison — just with a weaker MARL, reported honestly. Protect Oct 3 (calib) and Oct 20 (reward moves); the rest follows.
