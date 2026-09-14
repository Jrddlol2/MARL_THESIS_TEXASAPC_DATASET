H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 0.6, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.820 [0.784, 0.855] | 5063 [4955, 5186] | 509 [487, 531] | 545 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.742 [0.707, 0.779] | 5183 [5075, 5299] | 478 [458, 499] | 509 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.725 [0.688, 0.766] | 5169 [5062, 5278] | 472 [451, 494] | 502 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -9% [-13, -6] | -6% | -12% [-16, -7] | -7% |
