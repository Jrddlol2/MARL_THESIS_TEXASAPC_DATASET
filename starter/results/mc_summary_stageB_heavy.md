H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather heavy (speed loss 0.074), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.668 [0.638, 0.698] | 5065 [4999, 5138] | 460 [444, 476] | 422 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.537 [0.506, 0.569] | 5141 [5080, 5208] | 421 [407, 435] | 384 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.494 [0.467, 0.524] | 5118 [5059, 5183] | 409 [397, 421] | 373 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -20% [-24, -15] | -9% | -26% [-30, -21] | -11% |
