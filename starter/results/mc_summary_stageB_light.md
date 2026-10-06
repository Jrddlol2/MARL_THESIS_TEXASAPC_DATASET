H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather light (speed loss 0.053), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.612 [0.577, 0.645] | 4748 [4688, 4814] | 437 [421, 454] | 411 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.474 [0.443, 0.507] | 4872 [4820, 4929] | 398 [384, 412] | 375 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.429 [0.402, 0.458] | 4866 [4816, 4922] | 385 [374, 396] | 364 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -23% [-28, -17] | -9% | -30% [-35, -25] | -12% |
