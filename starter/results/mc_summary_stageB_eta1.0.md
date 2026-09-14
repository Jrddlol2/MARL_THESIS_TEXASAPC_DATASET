H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 1.0, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.904 [0.867, 0.941] | 5317 [5189, 5453] | 557 [532, 582] | 600 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.836 [0.799, 0.875] | 5442 [5318, 5575] | 526 [502, 551] | 563 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.832 [0.794, 0.872] | 5408 [5284, 5538] | 524 [500, 549] | 560 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -8% [-12, -3] | -5% | -8% [-13, -3] | -6% |
