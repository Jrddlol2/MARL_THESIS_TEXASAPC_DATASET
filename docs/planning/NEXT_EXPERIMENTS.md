# Next experiments — queued, not yet run

Written 2026-09-16, after the four-run reward sweep (A–D). Everything here is decided but deferred.
Nothing in this list has been started.

## Where the sweep left us

| Run | Reward | Stage A CV | Stage A wait | Severe-weather wait (η 0.6 / 1.0 / 1.3) |
|---|---|---|---|---|
| Even-Headway | — | 0.342 | 339 s | 472 / 524 / 541 s |
| A `dr1` | schedule adherence | 0.362 | 345 s | 477 / 523 / 537 |
| B `dr2_even` | evenness | 0.345 | 342 s | **467 / 515 / 529** (all significant) |
| C `dr3_both` | both gaps vs schedule | 0.412 | 351 s | 489 / 536 / 552 |
| **D `dr4_even_hold`** | evenness + in-vehicle cost | **0.340** | 341 s | 471 / 523 / 537 |

Two winners on two metrics: **D** is best on spacing and clears the project gate; **B** is best on
waiting under severe weather and is the only run whose advantage there is statistically significant.

Criteria still unmet: Stage A (i) — waiting 2 s worse than Even-Headway (p = 0.017); Stage B — waiting
below the best baseline in *every* cell (B passes 3 of 5, D passes none significantly but is never
significantly worse).

## 1. The λ sweep between B and D  (highest value, ~8 h wall clock)

D prices a second of in-vehicle delay the same as a second of waiting at a stop. B does not price it at
all. Somewhere between them should be a policy with B's severe-weather waiting and D's ordinary-day
spacing.

```
waiting penalty = (1 − λ) · (riders waiting × gap endured) + λ · (riders on board × seconds held)
```

λ = 0 is B, λ = 0.5 is D, so run **λ = 0.25 and λ = 0.75**, two runs in parallel, 800 episodes each.
Requires a small change in `reward.py` to expose λ (today `wait_both` is hard-coded at equal pricing).

**Report as a frontier:** mean waiting on one axis, in-vehicle travel on the other, the four MARL points
and the three baselines on the same axes. Even-Headway is a single point; a learned controller offers a
curve, which is a contribution rules cannot match.

**Rule:** choose λ on the validation seeds (90000+), never on seeds 0–29.

## 2. Repeat seeds for B and D  (~8 h, two at a time)

Every configuration so far is one training run. The failures are 2–7 second margins, which single-run
noise could account for. Two extra seeds each for B and D; report mean ± range. If the spread covers the
margins, the honest claim becomes "statistically indistinguishable from the best rule", which is a fine
result and more defensible than a 2 s win or loss.

## 3. Evaluate the skip action  (~4 h + design decisions)

Structural rather than tuning: in severe weather a skipped stop recovers a gap that holding cannot
close. Already implemented and covered by `test_simulator.py`, never evaluated; the third reward term
(stranded riders, w₃ = 1.0) has never been active.

Before running it, decide two things:

- **Fairness reporting.** Skipping improves the mean by moving cost onto skipped passengers. Report the
  90th-percentile wait and `riders_overcarried`, not just the mean. Both are already recorded.
- **A like-for-like baseline.** Even-Headway cannot skip. Either give the baselines a simple skip rule
  (skip when full, or when the gap ahead is under half the headway) or report both settings and say
  which comparison is which.

## 4. The Stage A (i) criterion itself  (Jared's call, no run needed)

"No statistically significant degradation" has no tolerance band, so with 30 paired seeds on identical
disturbances any difference eventually registers — 341 s vs 339 s fails at p = 0.017. Standard
non-inferiority testing declares a margin first (2%, about 7 s here), under which D passes.

If a margin is adopted, it must be reported as **added after seeing the result**, with both versions
shown. Deciding this is a manuscript matter, not a code one.

## 5. Transfer to Route 803  (stretch, ~2 days + 5 h compute)

The real generalisation test, and the data is already in the repo (196,048 clean events in direction 4,
180,753 in direction 6, 28 stops). Direction 4 of Route 801 is a weaker check — same timetable, same
fleet, only 3 stop IDs shared with direction 6, reversed demand.

**Design:** build and validate 803's own corridor (its own calibration, its own control stops by the
§3.2.2 criteria, its own headway sourced or derived), then four arms on identical seeds —
baselines, the 801 policy zero-shot, the same policy fine-tuned ~200 episodes, and a from-scratch
policy. Report percentages against each corridor's own baselines, so corridor difficulty does not
masquerade as transfer loss.

**Outcome readings:** zero-shot ≈ from-scratch means the policy learned bunching, not this corridor (the
strong result); zero-shot beats the baselines but trails from-scratch means the method transfers and the
policy needs adaptation; zero-shot failing while from-scratch succeeds points at what the observation is
missing.

## Order I would run them

1. λ sweep + seed repeats together (four runs, two at a time, ~8 h) — decides whether the criteria can
   be met at all, and produces the frontier figure either way.
2. Skip action, once the fairness and baseline questions are settled.
3. Route 803, as the stretch goal — headline if it lands, future work if it does not.
