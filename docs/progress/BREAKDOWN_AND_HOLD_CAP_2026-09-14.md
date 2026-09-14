# Breakdown as bus removal, and the holding-cap check

> **Superseded (same day, Week 2):** the simulator now uses fitted variability, a 120 s
> holding cap and a corrected backward headway. Current results:
> `WEEK2_SIMULATOR_VS_REALITY_2026-09-14.md`. The numbers below are kept as a record.

**Date:** 2026-09-14 · **Follows:** `WEEK1_SIMULATOR_FIXES_2026-09-14.md` ·
**Code:** `starter/envs/corridor_sim.py`, `starter/scripts/mc.py` ·
**Results:** `starter/results/mc_summary.md` (main), `mc_summary_hold120.md`, `mc_summary_breakdowns3.md`

## 1. Why these two things changed

Both values were checked against the RRL PDFs in `RRW/`.

**Breakdown.** The simulator froze a bus for 400 s. No source supports that number.

| Source | What a breakdown is | Count / duration |
|---|---|---|
| Guedes & Borenstein 2018 (`Guedes2018Rescheduling`) | Serious failure: vehicle towed, trip cut (p. 1, p. 4) | One disruption in the base experiments; 2–3 in the robustness test (p. 12, p. 14) |
| Daganzo 2009 (`Daganzo2009`) | Bus goes out of service; its run is reassigned to the bus behind (p. 8) | — |
| Cao et al. 2022 (`Cao2022Train`) | **Temporary** train stop of random duration (p. 4) | Poisson rate 30%, 10–20 simulation steps |

The manuscript describes removal, which Guedes and Daganzo support. It had cited Cao for
it, but Cao's malfunctions are temporary. **Fixed in `methods.tex` (lines 312 and 472).**

**Holding cap.** 0.4 × scheduled headway comes from Rodriguez et al. 2023 (p. 10), where
the headway was 5 min, so the cap was 120 s. Other RRL caps are also 90–120 s
(Wang & Sun 2023: 90 s, p. 5; Liu et al. 2023: 90 s at a 6-min headway, p. 9; Tang et al.
2024: 120 s, p. 15). None studies a 10-min headway, so our 0.4 × 600 = 240 s is an
extrapolation. Rodriguez also say the cap should follow the agency's policy (p. 6);
CapMetro's is unknown.

## 2. What the code does now

- **B removes a bus.** One bus (departures 2–16) fails on arriving at a random stop (1–25)
  and is taken out of service. Riders bound for that stop get off; everyone else gets off,
  walks onto the stop and waits for the next bus. Drawn from the seed, so every controller
  sees the same breakdown. `simulate(breakdowns=3)` removes three.
- **`max_hold`.** Default 0.4 × H0 = 240 s; `simulate(max_hold=120)` for the check.
  FH and EH read the cap from the observation, so all controllers share it.
- **Forward headway** is now "time since the last bus reached this stop". Without a removal
  this is the same bus as before (buses cannot overtake), so results are unchanged.
- `mc.py` options: `--max-hold`, `--breakdowns`, `--only-breakdown`, `--tag`.

**Checks.** All 270 runs without B are bit-identical to the Week 1 results. Every B run
removed the drawn buses, moved 22–83 riders, stranded 0 and left 0 rides unfinished.

## 3. Results (N = 30 paired seeds, 5 control stops)

### Main table — bus removal, 240 s cap

| Scenario | NC CV | FH CV | EH CV | FH vs NC [95% CI] | EH vs NC [95% CI] |
|---|---|---|---|---|---|
| Stage A (D+T) | 0.159 | 0.121 | 0.123 | −24% [−28, −19] | −23% [−26, −19] |
| + Surge (S) | 0.166 | 0.132 | 0.132 | −21% [−25, −15] | −20% [−25, −16] |
| + Weather (W) | 0.755 | 0.611 | 0.654 | −19% [−22, −16] | −13% [−18, −9] |
| + Breakdown (B) | 0.236 | 0.198 | 0.205 | −16% [−23, −9] | −13% [−21, −4] |
| **Stage B (all)** | **0.752** | **0.622** | **0.661** | **−17% [−21, −14]** | **−12% [−16, −8]** |

Only the two B rows changed (the delay version gave −23%/−20% and −18%/−13%).

### Check 1 — hold cap 120 s instead of 240 s

| Scenario | FH vs NC | EH vs NC |
|---|---|---|
| Stage A | −24% [−29, −18] | −23% [−27, −17] |
| + Weather | −11% [−15, −8] | −10% [−14, −5] |
| + Breakdown | −16% [−23, −8] | −13% [−21, −5] |
| **Stage B** | **−10% [−14, −5]** | **−9% [−13, −3]** |

### Check 2 — three buses removed instead of one

| Scenario | NC CV | FH vs NC | EH vs NC |
|---|---|---|---|
| + Breakdown | 0.315 | −8% [−15, −0] | −7% [−14, +1] |
| Stage B | 0.738 | −15% [−20, −11] | −11% [−14, −7] |

### How long the rules actually hold (240 s cap, 10 seeds)

| | Holds when holding (median) | Decisions at the 240 s cap | Decisions over 120 s |
|---|---|---|---|
| FH, Stage A | 37 s | 0% | 4% |
| FH, Stage B | 222 s | 22% | 30% |
| EH, Stage B | 102 s | 7% | 19% |

## 4. What this means

1. **The cap does not matter under mild disturbance** (Stage A identical at 120 and 240 s),
   but **it drives much of the rule-based benefit under severe disturbance.** With the
   120 s cap used in the RRL, Stage B improvement falls from −17% to −10% (FH) and −12% to
   −9% (EH). Forward-Headway's lead over Even-Headway comes mostly from 3–4 minute holds.
2. **Repeated breakdowns defeat fixed holding.** With three buses removed, the
   breakdown-only benefit falls to −8% (FH, CI touching zero) and −7% (EH, CI crossing
   zero). This is the "holding fails under severe disturbance" pattern, now measured on
   a disturbance the RRL supports.
3. **MARL motivation, restated with evidence:** rule-based holding helps under mild
   disturbance, but under severe or repeated disturbance it either needs long holds
   (up to 4 minutes, beyond any cap in the RRL) or its benefit shrinks toward zero.

## 5. Decisions still needed

- **Which cap is the headline?** 240 s follows Rodriguez's formula; 120 s matches every
  absolute cap in the RRL. Whichever is chosen, report the other as a sensitivity result,
  and use the same cap for MARL (`marl_env.Config.dt` = cap ÷ 0.4).
- **Breakdown count.** The code removes a fixed number of buses; `methods.tex:472` still
  describes a per-timestep Poisson trial with rate λ. Update the text, or switch the code.
- **FH formula.** Code "fills the gap"; `methods.tex:680` gives Daganzo's d + g(H0 − h).
