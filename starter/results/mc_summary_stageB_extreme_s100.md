H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather extreme (speed loss 0.250), capacity 55, seeds 100-129, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.632 [0.599, 0.668] | 5964 [5882, 6049] | 517 [480, 558] | 416 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.481 [0.454, 0.509] | 6085 [6006, 6170] | 473 [437, 518] | 374 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.470 [0.444, 0.496] | 6044 [5971, 6122] | 465 [431, 506] | 371 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -24% [-29, -18] | -8% | -26% [-31, -20] | -10% |
