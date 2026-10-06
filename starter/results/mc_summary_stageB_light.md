H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather light (speed loss 0.053), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.666 [0.635, 0.697] | 4966 [4901, 5041] | 457 [442, 473] | 421 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.530 [0.498, 0.562] | 5043 [4983, 5109] | 416 [402, 430] | 383 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.487 [0.460, 0.515] | 5022 [4962, 5087] | 403 [392, 415] | 371 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -20% [-24, -17] | -9% | -27% [-31, -23] | -12% |
