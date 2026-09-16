# Week 3 — the manuscript's evaluation matrix, and the first real training run

2026-09-16. Everything here is reproducible from `starter/results/` and `starter/experiments/dr1/`.

## 1. The baseline results were incomplete, and one of them was wrong

`methods.tex` defines nine evaluation conditions. We had five, and the weather ones used the wrong
weather: the manuscript's weather-only condition is **observed ordinary rain**, but ours used the
synthetic stress at η = 0.8. The missing 540 runs are now done (30 seeds × 3 controllers × 6 cells).

| Condition | No Control | Forward-Headway | Even-Headway |
|---|---|---|---|
| Stage A (ordinary day) | 0.556 | 0.396 (−29%) | 0.342 (−38%) |
| + surge | 0.596 | 0.427 (−28%) | 0.371 (−38%) |
| + weather, **observed rain** | 0.559 | 0.400 (−28%) | 0.346 (−38%) |
| + breakdown | 0.564 | 0.423 (−25%) | 0.370 (−34%) |
| **Stage B, observed rain** | 0.609 | 0.458 (−25%) | **0.404 (−34%)** |

**Stage B as synthetic weather stress rises** (`stageB_weather_sweep.png`):

| η | 0 (observed rain) | 0.3 | 0.6 | 0.8 | 1.0 | 1.3 |
|---|---|---|---|---|---|---|
| Even-Headway vs No Control | −34% | −22% | −12% | −9% | −8% | −7% |

**What changed in the story.** We used to say fixed holding "loses most of its effect under combined
disturbance". That is only true under strong synthetic weather. Under everything the data actually
supports — surge, a breakdown and real rain together — Even-Headway still cuts bunching by a third.
The case for MARL now rests on the high-stress region (η ≥ 0.6), which is labelled synthetic
throughout, as the manuscript already requires.

## 2. Training now follows the manuscript

The manuscript's training row says demand and traffic are always on while surge, weather and breakdown
are randomized. Our gate run trained on ordinary days only, which would have produced an agent that
never saw the conditions it has to win in.

- Each episode: surge, weather and breakdown each on with probability 0.5; when weather is on its
  strength is drawn uniformly between 0 (observed rain) and 1.3.
- The draw depends only on the episode number, so `--resume` repeats the same sequence exactly.
- The manuscript's two stabilizers are now implemented: rewards clipped at −5 (measured: under η = 1.3
  a random policy sees rewards down to −11, but 95% are above −4.4) and slow target-network updates
  (Polyak, τ = 0.005).
- The event-based discount is in: each transition is discounted by e^(−β·Δt) over the seconds between
  that bus's decisions, β set so one scheduled headway discounts by 0.99.
- Checkpoints every 50 episodes with exact resume, and `checkpoint_best.pt` chosen on a mixed
  validation set (Stage A, Stage B observed rain, Stage B η 0.6) on seeds 90000+, never the test seeds.

**Verified before launching:** a run stopped at 2 episodes and resumed reproduces an uninterrupted
4-episode run exactly, log and final network; the disturbance draws come out 48%/48%/52% on.

## 3. The pass mark, fixed before the run

- **Project gate (Jared's choice):** in Stage A, the greedy policy's mean headway CV over seeds 0–29
  must be below Even-Headway's 0.342.
- **The manuscript's criteria:** Stage A — mean wait not significantly worse than Even-Headway, and
  bunching significantly below No Control; Stage B — mean wait below the best baseline in every
  Stage B cell.
- **Statistics, also fixed beforehand:** paired Wilcoxon signed-rank by seed, Holm correction across
  the three baseline comparisons, α = 0.05, 30 paired seeds. `scripts/eval_marl.py` prints the verdicts.

## 4. Run A — the schedule-adherence reward

`experiments/dr1/`, 800 episodes in 3 h 44 min. The reward penalised how far the gap *ahead* sat from
the 600 s timetable. Its frozen policy was then evaluated on all nine conditions, 30 seeds each, on the
same seeds as the baselines (`results/marl_eval_dr1.md`).

**Bunching (headway CV)**

| Condition | No Control | Forward-Headway | Even-Headway | MARL |
|---|---|---|---|---|
| Stage A | 0.556 | 0.396 | **0.342** | 0.362 |
| + surge | 0.596 | 0.427 | **0.371** | 0.399 |
| + weather (observed rain) | 0.559 | 0.400 | **0.346** | 0.363 |
| + breakdown | 0.564 | 0.423 | **0.370** | 0.396 |
| Stage B, observed rain | 0.609 | 0.458 | **0.404** | 0.437 |
| Stage B η 0.3 | 0.685 | 0.574 | **0.534** | 0.563 |
| Stage B η 0.6 | 0.820 | 0.742 | **0.725** | 0.729 |
| Stage B η 1.0 | 0.904 | 0.836 | 0.832 | **0.823** |
| Stage B η 1.3 | 0.929 | 0.862 | 0.864 | **0.849** |

**What it shows.** The learned policy beats No-Control everywhere and beats Forward-Headway in every
single condition (2–9% lower bunching). Against Even-Headway it is 5–8% worse on ordinary days, level
at η 0.6, and ahead at η 1.0 and 1.3 — the severe-weather regime where the fixed rules stop coping.
The crossover the thesis argues for is visible; it just happens later than hoped.

**Against the pre-registered criteria, three of four fail**

| Criterion | Result |
|---|---|
| Stage A (ii): bunching below No-Control | **PASS** (0.362 vs 0.556, p < 0.001) |
| Stage A (i): waiting no worse than Even-Headway | FAIL — 345 s vs 339 s, significantly worse |
| Project gate: bunching below Even-Headway | FAIL — 0.362 vs 0.342 |
| Stage B: waiting below the best baseline in every cell | FAIL — closest at η 1.3, 537 s vs 541 s, p = 0.09 |

**Why it fails, in one number.** In-vehicle travel time is 4,671 s against Even-Headway's 4,543 s: the
agent holds about two minutes more per trip. Chasing the timetable buys spacing at the riders' expense,
which is what loses the waiting-time test. The during-training evaluations (3 seeds) read about 0.44 in
Stage A and were pessimistic; the 30-seed evaluation gives 0.362. Only the 30-seed numbers should be
quoted.

**Kept on record:** `experiments/dr1/config.json`, `metrics.csv`, `checkpoint_best.pt`,
`checkpoint.pt`, `results/marl_eval_dr1.{csv,md}`, figures `dr1_curve`, `dr1_convergence`,
`marl_dr1_headway_cv`, `marl_dr1_wait`.

## 4b. Run B — the evenness reward (running)

`experiments/dr2_even/`, identical in every respect except the irregularity term, which now penalises
the difference between the gap ahead and the gap behind — the quantity headway CV measures, and the one
Even-Headway optimises. Results to follow.

## 5. Also done this week

- **Manuscript aligned with the implementation** (`methods.tex`, `problem.tex`): training runs in SUMO,
  RMSPE instead of RMSE, GEH stated as a closeness statistic on running times, the interleaved
  calibration split with its reason, and five parameter-table rows filled in (27 modelled stops, 18
  dispatched trips, 5 control stops, H0 = 600 s cited to the archived timetable, the event discount).
- **GTFS gate closed** as "not publicly archived" rather than pending; direction 6 is labelled
  southbound as corroboration from the current feed, and that is how it is described everywhere.
- **Date-order split check:** held-out error 6.83% against 3.08%, with GEH < 5 on every segment either
  way — consistent with ridership rising 31% from July to October, not with a worse model
  (`results/validation/SPLIT_ROBUSTNESS.md`).
- **Results chapter drafted** from the measured outputs; the MARL section is a placeholder holding the
  criteria above. The old NeuroSEE template text is gone.
- **Cleaned datasets published** in `data/shared/` with `scripts/unpack_shared_data.py`, so anyone can
  clone and run the simulator without the 3.7 GB raw file.

## 6. Still open

- Bunching runs about 10% high in the second half of the corridor (timepoint holding, untestable with
  the APC schedule field).
- `discussion.tex` and `futurework.tex` are still template text from another thesis.
- The slides still quote the old numbers.
