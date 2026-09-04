# MARL Experiment Harness — Plan & Options (2026-09-03)

Plan for Phase 1: a **modular, config-driven** MARL harness where every design decision is a knob, so
you experiment first and commit nothing until the evidence (the fail-fast gate) tells you what works.
Isolated from the locked Phase-0 baseline. Nothing here is a decision — it is the menu.

## Design principle
- **Isolated:** MARL lives in new files + writes to `experiments/<run>/`; the committed baseline
  (`corridor_sim`, `mc.py`, the N=30 table) is never touched.
- **Config-driven:** one `Config` dataclass holds all knobs (reward form + weights, obs variant, ΔT,
  hyperparameters, episodes, domain-randomization, curriculum). To experiment you copy a config and
  change one field — no code edits.
- **Evidence-gated:** each run logs a learning curve + the fail-fast gate metric; you compare runs and
  only then pick the config that goes in the manuscript.

## Components & build order
1. `envs/marl_env.py` — wraps `corridor_sim`'s decision events into `(obs, action, reward)` and
   assembles each bus's transition `(o, a, r, o′)` (semi-MDP: reward realized over the segment to the
   bus's next decision). Reuses the calibrated corridor, disturbances, control stops.
2. `envs/reward.py` — a **library** of candidate reward terms (below); the config selects forms + weights.
3. `envs/obs.py` — featurizes corridor_sim's obs dict into the manuscript 7-vector (config selects variant).
4. `scripts/train_marl.py` — config-driven training loop (shared DDQN, domain randomization, checkpoints,
   metrics) → `experiments/<run>/`.
5. `scripts/eval_marl.py` — load a checkpoint, evaluate as the 4th controller on the same Stage A /
   ablations / Stage B cells vs NC/FH/EH.
6. **Fail-fast gate** — a thin `train_marl.py` preset: short Stage-A holding-only run; must beat NC and
   approach FH on headway CV, else fix reward/obs before spending more.

---

## THE OPTIONS (what you'll experiment with)

### 1. Reward — irregularity term (drives headway CV down)
| Opt | Form | Character |
|---|---|---|
| **1a (default)** | `((h_fwd − H₀)/H₀)²` | anchors to the scheduled headway H₀; simplest; direct CV target |
| 1b | `((h_fwd − h_bwd)/H₀)²` | even-spacing (two-way, Daganzo); self-regulates around whatever headway emerges — may suit weather better, where H₀ is unrealistic for all buses |
| 1c | `½[((h_fwd−H₀)/H₀)² + ((h_bwd−H₀)/H₀)²]` | both neighbors vs schedule |

### 2. Reward — waiting term (passenger wait / anti-over-holding)
| Opt | Form | Character |
|---|---|---|
| 2a | `(hold_time/H₀)·(load/cap)` | penalizes holding ∝ onboard riders delayed (in-vehicle focus) |
| **2b (default)** | `(queue·h_fwd)/(Q_ref·H₀)` | penalizes at-stop wait ∝ waiting riders × how long — closest to the manuscript's "waiting time at served stops" |
| 2c | headway-model wait increment at the stop | ties reward to the reported metric |

### 3. Reward — skip-degeneracy penalty
| Opt | Form | Character |
|---|---|---|
| **3a (default)** | `skip·(queue/Q_ref)` | demand-aware: skipping a busy stop hurts, an empty one is cheap |
| 3b | `skip·c` (flat) | simple constant discouragement |

Overall: `r = −w₁·(irregularity) − w₂·(waiting) − w₃·(skip)`; start `w = (1.0, 0.5, 1.0)`, sweep at the
gate. **Coefficient tuning is literally the EO2.1 deliverable**, so this sweep IS the thesis contribution.

### 4. Observation
| Opt | Vector | Note |
|---|---|---|
| **4a (default)** | manuscript 7: [stop idx, h_fwd, h_bwd, load, queue, weather flag w, breakdown flag b] | Table 3.6 exactly |
| 4b | 7 + neighboring-trip info | the DDQN-HA enhancement the manuscript flags for testing |
| — | flag encoding: `w` binary (weather on) vs intensity (realized speed factor); `b` binary (incident ahead) | sub-knob |

### 5. Action / holding
| Knob | Options | Default |
|---|---|---|
| ΔT (max hold) | H₀=300 s (max hold 120 s, matches baseline cap) · larger (more authority) · smaller | **H₀ = 300 s** |
| Skip | enabled · holding-only | **holding-only for the gate**, enable after it learns |

### 6. DDQN hyperparameters (sensible defaults; sweep only if the gate struggles)
| Knob | Default | Sweep range |
|---|---|---|
| learning rate | 1e-3 | 3e-4 … 3e-3 |
| discount γ | 0.99 | 0.95 … 0.995 |
| ε decay | over ~30k steps | shorter/longer |
| replay buffer | 100k | 50k … 200k |
| net | [128,128] | [64,64] … [256,256] |
| target update | every 500 steps | 250 … 1000 |

### 7. Training / curriculum
| Knob | Options | Default |
|---|---|---|
| disturbance exposure | full domain-randomization from start · **curriculum** (Stage A → add S/W/B) | curriculum (more stable) |
| episode budget | e.g. 2k / 5k / 10k episodes | start 2k for the gate |
| fleet / horizon | as baseline (12 buses, 1 day) · shorter (faster episodes) | as baseline; shorten only if training too slow |
| parallel envs | 1 … 6 (the mc.py lever) | 4–6 for experience throughput |

---

## Experiment workflow
1. Build the harness (commits **no** decisions — just makes them knobs).
2. Run the **fail-fast gate** on the default config (1a/2b/3a, holding-only, Stage A). Does it beat NC / reach FH?
3. If yes → sweep the interesting knobs (reward form 1a vs 1b, weights, curriculum) and compare gate metrics.
4. Enable skip, train under full domain randomization to the episode budget.
5. Pick the winning config; **only that** goes into `eval_marl.py` for the final MARL-vs-NC/FH/EH table and the manuscript.

## What gets committed
The harness code (isolated, config-driven) goes to the repo; experiment runs live in `experiments/`
(git-ignored or kept, your call). No reward/obs/hyperparameter choice is written into the manuscript
until the sweep picks it.
