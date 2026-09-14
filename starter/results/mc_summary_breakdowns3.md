H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 3 bus(es), surge sigma_d 1.0, weather eta 0.8, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Ablation B (D+T+B) | NC | 0.587 [0.549, 0.624] | 4566 [4547, 4584] | 436 [418, 453] | 458 | 30 |
| Ablation B (D+T+B) | FH | 0.457 [0.427, 0.488] | 4731 [4712, 4750] | 398 [386, 411] | 419 | 30 |
| Ablation B (D+T+B) | EH | 0.426 [0.395, 0.456] | 4699 [4680, 4718] | 389 [377, 403] | 409 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.869 [0.830, 0.906] | 5479 [5333, 5636] | 574 [548, 601] | 687 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.792 [0.753, 0.832] | 5612 [5476, 5762] | 540 [514, 567] | 656 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.796 [0.757, 0.835] | 5569 [5426, 5729] | 541 [515, 568] | 648 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Ablation B (D+T+B) | -22% [-28, -16] | -9% | -28% [-35, -19] | -11% |
| Stage B (D+T+S+W+B) | -9% [-13, -5] | -6% | -8% [-12, -5] | -6% |
