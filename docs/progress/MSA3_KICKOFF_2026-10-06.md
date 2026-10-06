# MSA 3 kickoff — 2026-10-06

MSA 2 is done. MSA 3 (Nov 23–28) covers **EO 3.1 and EO 3.2**: MARL against the baselines, with
statistics, under ordinary and disturbed conditions. This note records what changed today, why,
and what runs next. The dataset is frozen: nothing below re-processes APC or NOAA data.

## 1. What was wrong, and what we fixed

A plan-vs-manuscript audit (26 Aug manuscript, the code, the RRL) found four problems. None of them
came from how tasks were chosen; they were in the code and the MARL setup.

| # | Problem | Fix | Commit |
|---|---|---|---|
| 1 | **Boarding undercount.** SUMO boards and drops riders in the same second a bus stops, before `getPersonCount` is read, so dwell used too few riders (about 410 boardings and 290 alightings missed per run). | Compare the bus's rider list at its last departure with the list on arrival and add the difference to the dwell count. | `ebf96ca` |
| 2 | **Headway CV** was a per-stop CV averaged over stops; the manuscript (Eq. 3.15) and the RRL (Rodriguez 2023 p.11, Xu 2025 p.7) pool all headways. | `headway_cv` is now pooled; the old value is kept as `headway_cv_stop_mean`. | `ebf96ca` |
| 3 | **Travel time** started when the bus entered SUMO; §3.2.9 says departure from the origin. | `travel_s` now starts when the bus leaves stop 0; old value kept as `travel_s_from_entry`. | `ebf96ca` |
| 4 | **The skip action was never switched on**, although the action space is hold × skip (manuscript p.45). Holding-only MARL ties EH (overnight 09-18: Stage A wait +0.4% to +2.3% above EH). Also, `eval_marl.py` ignored the run's config, so a skip-trained policy would have been evaluated with skip off. | `train_marl.py --skip`; `eval_marl.py` reads `config.json` next to the checkpoint. | `dd2b81a` |

`scripts/test_simulator.py`: all checks pass after the fixes.

## 2. What the fixes changed

**Validation against real buses** (No-Control, held-out weekdays, `results/validation/`):

| | Before fix | After fix | Observed (APC) |
|---|---|---|---|
| Headway CV, stops 1–26 (per-stop mean) | 0.556 | **0.599** | 0.504 |
| Error by stop (RMSE) | 0.069 | 0.113 | — |
| Riders on board, error | 2.07 | **1.88** | — |

Counting every rider makes dwell longer, so the simulator now bunches about 19% more than real
buses. Part of the earlier close match was the undercount. **Kept the fix (decision 2026-10-06):** the
mechanics are now correct, every controller faces the same simulator, and real CapMetro "no control"
still runs to a timetable, which damps bunching. This explanation still needs an RRL source before it
goes into the manuscript.

**Baselines** (development seeds 0–29; test seeds 100–129 re-run separately): see the README §4.
The ranking is unchanged (EH < FH < NC everywhere); all values rose by about 0.06 CV and 15–18 s of wait.

## 3. Statistics (answers the MSA 2 panel)

Procedure (manuscript §3.2.9 pp.53–54): Friedman across NC/FH/EH → paired Wilcoxon signed-rank per
pair → Holm correction → bootstrap 95% CI of the paired difference; degradation = mean(disturbed) /
mean(Stage A) per controller with an unpaired bootstrap CI. Sources: Demšar 2006 JMLR pp.7–8, 12–13;
Patterson et al. 2024 JMLR pp.29–30; Colas et al. 2019 p.8.

- **MSA 2 test corridor (E3):** FH vs EH bunching — no detectable difference (+3.3%, CI −1.7% to +8.5%,
  Holm p = 0.25); EH waits 0.8% (2.5 s) less than FH (p = 0.003); both cut bunching by about 54% vs NC.
- **Route 801, fixed simulator, dev seeds:** EH beats FH and FH beats NC in every cell (Holm p < 0.001).
  Degradation of waiting time: surge ×1.03 and observed rain ×1.01 (both not significant), breakdown
  ×1.05–1.07, Stage B ×1.10–1.12 (significant). Holding helps a little less under stress.

## 4. Running overnight (2026-10-06 → 07)

`starter/scripts/overnight_2026-10-06_skip_sweep.sh` (log `starter/results/overnight_2026-10-06.log`):
the first MARL runs **with skip**, a small EO 2.1 reward-weight sweep, training seed 0, 800 episodes,
evaluated on development seeds only.

| Run | Waiting term | Weights (irregularity, waiting, skip) |
|---|---|---|
| `sk_D_w1-05-1` | in-vehicle priced equally (`both`) | 1, 0.5, 1 |
| `sk_D_w1-05-2` | `both` | 1, 0.5, **2** |
| `sk_D_w1-05-05` | `both` | 1, 0.5, **0.5** |
| `sk_D_w1-1-1` | `both` | 1, **1**, 1 |
| `sk_P5_w1-05-1` | priced, κ = 0.5 | 1, 0.5, 1 |
| `sk_P5_w1-1-1` | priced, κ = 0.5 | 1, 1, 1 |

## 5. Member work (test corridor, verification)

Every member uses one shared build (`shared_build_v2`: all riders counted, pooled CV, capacity 55,
one random stream per source of randomness). Guides were given out on 2026-10-06; the answer keys
are kept outside this repo.

| Member | Task | Due |
|---|---|---|
| Medenilla | Statistics script (Friedman → Wilcoxon → Holm, bootstrap, degradation) | Part 1 Oct 12 |
| Badal | Demand surge: corridor-wide N(1, σd²) clip [1, 10] (Wang & Sun 2023 p.9) + local +10/20/50 riders (p.11) | Nov 2 |
| Lopez | Weather: corridor-wide slowdown 3 / 7.5 / 10 / 25% (FHWA 2006 p.5-17; FHWA Road Weather Management, arterials 10–25%) | Nov 2 |
| Marquez | Breakdown: 1 and 3 buses removed, riders picked up by the next bus (Guedes & Borenstein 2018 pp.1–2) | Nov 2 |

## 6. Timeline to MSA 3

| Week | Critical path (Jared) | Members |
|---|---|---|
| Oct 6–12 | Fixes, baselines re-run, skip on, sweep night 1 | Statistics Part 1 |
| Oct 13–19 | Sweep night 2, pick the reward | Disturbances |
| Oct 20–Nov 2 | Final training (3 seeds), freeze the policy | Disturbances due Nov 2 |
| Nov 3–9 | Final evaluation on test seeds 100–129, once | Statistics on all results |
| Nov 10–22 | Chapter 4, merge the 5_latex_temp changes into the manuscript, deck | Deck + script |

## 7. Still open

- RRL source for "real buses bunch less than the uncontrolled simulator because they run to a timetable".
- GEH is applied to running times, not counts: keep it, with a written reason in the manuscript.
- The manuscript (26 Aug) still shows the η-lognormal weather, the [1, 3] surge clip, the Poisson
  breakdown and a 240 s EH cap; the locked versions are in the local `5_latex_temp` copy.
- Drop the "two enhancements will be tested" sentence (manuscript p.48).

## 8. Weather levels changed (2026-10-06, evening)

The light / moderate / heavy levels (5.3 / 6.3 / 7.4%) came from a Philippine expressway study and the
extreme level (25%) from a Chinese typhoon study whose own table shows only an 8% drop (worst area 14%).
Both are replaced by US sources, page-checked:

| Level | Speed loss | Source |
|---|---|---|
| Observed ordinary rain | ×1.0135 (not significant) | our NOAA × APC join (Austin) |
| Light rain | 3% | FHWA 2006 (Hranac et al., FHWA-HOP-07-073) p.5-17: 2–3.6% |
| Heavy rain | 7.5% | FHWA 2006 p.5-17: 6–9% at about 1.6 cm/h |
| Wet arterial | 10% | FHWA Road Weather Management: arterials 10–25% on wet pavement |
| Extreme, wet arterial | 25% | same, upper end (unchanged value) |

**RL precedent for synthetic weather:** Wang & Sun 2023 (IEEE T-ITS, bus MARL) scale cruising speed by one
factor per episode, randomised in training (p.9); Da et al. 2023 (IEEE CDC, Table I) and 2024 (AAAI) and
Turnau et al. 2025 (MARL, arXiv, p.8 and Table 5) model rain as one set of vehicle settings applied to all
vehicles. None of these take their weather values from measurements; we take ours from FHWA.

The training range (0–25%) and the extreme cell are unchanged. The light, heavy and wet-arterial Stage B
baselines are re-run (dev and test seeds) by `starter/scripts/queue_2026-10-06_weather.sh`, which then
starts the overnight skip sweep.
