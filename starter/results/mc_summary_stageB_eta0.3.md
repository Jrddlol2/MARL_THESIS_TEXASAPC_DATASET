H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 0.3, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.685 [0.648, 0.719] | 4723 [4641, 4820] | 445 [429, 463] | 473 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.574 [0.541, 0.608] | 4844 [4763, 4931] | 411 [396, 426] | 436 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.534 [0.498, 0.571] | 4843 [4765, 4927] | 399 [384, 414] | 423 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -16% [-20, -12] | -8% | -22% [-26, -18] | -10% |
