H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather moderate (speed loss 0.063), capacity 55, seeds 100-129, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.592 [0.557, 0.629] | 4845 [4767, 4926] | 461 [431, 494] | 406 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.431 [0.402, 0.461] | 4968 [4896, 5046] | 415 [387, 445] | 365 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.395 [0.367, 0.426] | 4959 [4889, 5032] | 407 [381, 439] | 357 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -27% [-33, -20] | -10% | -33% [-39, -27] | -12% |
