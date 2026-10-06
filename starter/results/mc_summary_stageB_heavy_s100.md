H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather heavy (speed loss 0.074), capacity 55, seeds 100-129, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.594 [0.559, 0.630] | 4897 [4820, 4978] | 463 [432, 497] | 407 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.432 [0.403, 0.462] | 5020 [4950, 5099] | 415 [387, 446] | 365 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.398 [0.369, 0.428] | 5009 [4940, 5081] | 408 [381, 439] | 358 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -27% [-33, -21] | -10% | -33% [-39, -26] | -12% |
