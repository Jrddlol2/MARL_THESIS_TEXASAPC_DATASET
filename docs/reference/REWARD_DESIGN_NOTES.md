# Reward design: what we tried, what it cost, what it taught us

A record of how the MARL reward was set up, what each change did to the result, and the mistakes worth
not repeating. Numbers are from the 30-seed evaluations in `starter/results/marl_eval_*.md`.

## The structure is fixed by the manuscript

The reward is a weighted sum of three penalties, all negative:

```
reward = −( w1 · irregularity + w2 · waiting + w3 · skip penalty )
```

`methods.tex` fixes those three components and leaves the exact expressions and weights as the
implementation deliverable (EO 2.1). Each term therefore exists as several candidate functions in
[`starter/envs/reward.py`](../../starter/envs/reward.py), selected by `Config`.

A reward is paid at the bus's **next** control-stop decision, scored on the state its previous action
produced, and discounted by e^(−β·Δt) over the elapsed seconds (event-based discount).

## The candidates

| Term | Option | What it penalises |
|---|---|---|
| Irregularity | `dev` | gap ahead vs the 600 s timetable |
| | `even` | gap ahead vs gap behind |
| | `both` | both gaps vs the timetable |
| Waiting | `queue` | riders waiting at the stop × the gap they waited through |
| | `hold` | holding time × how full the bus is (in-vehicle delay) |
| Skip | `stranded` | riders left behind when a stop is skipped |
| | `flat` | a fixed penalty per skip |

## What the runs showed

All runs: 800 episodes, identical disturbances, seeds and network; only the reward differs.

| Run | Reward | Stage A CV | Stage A wait | Stage A travel |
|---|---|---|---|---|
| Even-Headway (best rule) | — | **0.342** | **339 s** | 4543 s |
| A `dr1` | `dev` + `queue` | 0.362 | 345 s | 4671 s |
| B `dr2_even` | `even` + `queue` | 0.345 | 342 s | 4597 s |

**Lesson 1 — score the agent on what you measure it by.** Run A was paid for matching the timetable
while being judged on how even the gaps were. Those differ whenever the whole fleet runs early or late.
Switching that one term (run B) moved Stage A bunching from 0.362 to 0.345, and B beat A in all nine
evaluation conditions on both metrics.

**Lesson 2 — an unpriced cost gets spent.** Neither run charged the agent for holding riders already on
board, so it held: A spent 128 s more per trip than Even-Headway, B still spends 54 s more. That extra
holding is exactly why both fail the "waiting no worse than Even-Headway" criterion by a few seconds,
despite competitive spacing. The travel-time column showed this from run A onward; it was not read
against the waiting-time failure until run B.

**Lesson 3 — the two waiting candidates were written as either/or.** `queue` and `hold` are alternative
forms in the library, so picking one silently drops the other half of "passenger service delay". The
manuscript's term covers both; the implementation forced a choice. Run D adds a combined form.

**Lesson 4 — change one thing per run.** A and B differ in a single term, which is why the 0.017
improvement is attributable. It is tempting to fix everything at once after a disappointing run; then
nothing is learned.

**Lesson 5 — during-training evaluation is too noisy to steer by.** The 3-seed evaluations put run A at
about 0.44 in Stage A; its 30-seed evaluation gave 0.362. Per-seed standard deviation is 0.058, so a
3-seed mean carries ±0.066 at 95% confidence, against ±0.021 for 30 seeds. Use the small evaluations to
pick checkpoints, never to compare configurations.

## Still untested

- Weight sweep: `w = (1.0, 0.5, 1.0)` was never varied.
- `Q_REF = 20`, the queue normalisation, was never tuned.
- Learning rate 1e-3; both runs oscillate ±0.03 after exploration ends, which may be a stability signal.
- Checkpoint selection uses 3 seeds per validation cell, so part of the saved policy's advantage is luck.
- The skip action is off in every run so far, so the third term has never been active.
