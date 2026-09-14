H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 1.3, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.929 [0.890, 0.967] | 5334 [5197, 5477] | 572 [546, 600] | 616 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.862 [0.825, 0.899] | 5463 [5331, 5605] | 541 [516, 567] | 577 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.864 [0.823, 0.905] | 5427 [5292, 5561] | 541 [517, 567] | 576 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -7% [-13, -2] | -5% | -7% [-13, -2] | -5% |
