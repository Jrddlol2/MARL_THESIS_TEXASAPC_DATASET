H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 0.4 x H0, B removes 3 bus(es). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Ablation B (D+T+B) | NC | 0.315 [0.296, 0.337] | 5263 [5253, 5274] | 357 [350, 365] | 368 | 30 |
| Ablation B (D+T+B) | FH | 0.290 [0.269, 0.312] | 5361 [5351, 5372] | 355 [348, 362] | 368 | 30 |
| Ablation B (D+T+B) | EH | 0.294 [0.273, 0.317] | 5314 [5304, 5325] | 355 [348, 362] | 366 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.738 [0.697, 0.782] | 6377 [6304, 6459] | 498 [481, 516] | 565 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.624 [0.586, 0.663] | 6600 [6522, 6682] | 460 [443, 478] | 537 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.659 [0.619, 0.700] | 6498 [6427, 6572] | 470 [454, 488] | 540 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Ablation B (D+T+B) | -8% [-15, -0] | -1% | -7% [-14, +1] | -1% |
| Stage B (D+T+S+W+B) | -15% [-20, -11] | -8% | -11% [-14, -7] | -5% |
