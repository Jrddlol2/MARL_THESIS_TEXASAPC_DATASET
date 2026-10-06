H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather moderate (speed loss 0.063), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.666 [0.636, 0.698] | 5013 [4947, 5087] | 458 [443, 475] | 421 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.533 [0.501, 0.566] | 5088 [5026, 5157] | 418 [403, 433] | 384 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.491 [0.464, 0.520] | 5066 [5007, 5131] | 405 [394, 417] | 372 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -20% [-24, -16] | -9% | -26% [-30, -22] | -12% |
