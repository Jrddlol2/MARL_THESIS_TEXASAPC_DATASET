H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather extreme (speed loss 0.250), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.654 [0.620, 0.688] | 5911 [5849, 5979] | 486 [470, 504] | 422 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.530 [0.498, 0.563] | 6040 [5982, 6104] | 450 [433, 467] | 387 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.514 [0.485, 0.545] | 5996 [5941, 6058] | 443 [428, 459] | 382 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -19% [-24, -13] | -8% | -21% [-26, -16] | -9% |
