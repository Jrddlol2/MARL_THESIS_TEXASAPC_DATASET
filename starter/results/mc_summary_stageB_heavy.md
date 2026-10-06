H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather heavy (speed loss 0.074), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.615 [0.580, 0.649] | 4848 [4787, 4916] | 441 [424, 458] | 412 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.479 [0.448, 0.511] | 4971 [4919, 5029] | 403 [389, 418] | 376 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.436 [0.408, 0.464] | 4961 [4910, 5018] | 389 [378, 401] | 365 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -22% [-26, -18] | -8% | -29% [-34, -24] | -12% |
