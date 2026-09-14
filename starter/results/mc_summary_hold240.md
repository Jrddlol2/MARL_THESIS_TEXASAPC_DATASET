H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 240 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 0.8, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.556 [0.519, 0.590] | 4391 [4374, 4408] | 387 [375, 400] | 393 | 30 |
| Stage A (D+T) | FH | 0.389 [0.364, 0.414] | 4536 [4520, 4552] | 349 [341, 357] | 355 | 30 |
| Stage A (D+T) | EH | 0.306 [0.287, 0.326] | 4573 [4558, 4589] | 333 [327, 339] | 336 | 30 |
| Ablation S (D+T+S) | NC | 0.596 [0.552, 0.639] | 4549 [4484, 4625] | 399 [384, 414] | 420 | 30 |
| Ablation S (D+T+S) | FH | 0.421 [0.391, 0.450] | 4676 [4616, 4744] | 355 [345, 364] | 377 | 30 |
| Ablation S (D+T+S) | EH | 0.329 [0.306, 0.353] | 4702 [4647, 4770] | 336 [329, 344] | 357 | 30 |
| Ablation W (D+T+W) | NC | 0.865 [0.826, 0.902] | 5048 [4954, 5139] | 520 [496, 545] | 531 | 30 |
| Ablation W (D+T+W) | FH | 0.791 [0.755, 0.826] | 5202 [5110, 5297] | 490 [468, 512] | 494 | 30 |
| Ablation W (D+T+W) | EH | 0.758 [0.723, 0.796] | 5221 [5141, 5299] | 478 [458, 500] | 478 | 30 |
| Ablation B (D+T+B) | NC | 0.564 [0.528, 0.599] | 4397 [4379, 4414] | 402 [388, 417] | 410 | 30 |
| Ablation B (D+T+B) | FH | 0.418 [0.391, 0.447] | 4539 [4522, 4556] | 366 [355, 377] | 375 | 30 |
| Ablation B (D+T+B) | EH | 0.334 [0.312, 0.359] | 4582 [4564, 4599] | 348 [339, 358] | 355 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.876 [0.840, 0.912] | 5243 [5120, 5372] | 540 [516, 564] | 579 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.797 [0.761, 0.835] | 5377 [5259, 5498] | 506 [482, 528] | 538 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.767 [0.730, 0.807] | 5391 [5281, 5507] | 495 [473, 518] | 524 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -30% [-35, -25] | -10% | -45% [-50, -39] | -14% |
| Ablation S (D+T+S) | -29% [-35, -23] | -11% | -45% [-50, -39] | -16% |
| Ablation W (D+T+W) | -9% [-10, -7] | -6% | -12% [-15, -10] | -8% |
| Ablation B (D+T+B) | -26% [-31, -21] | -9% | -41% [-45, -36] | -13% |
| Stage B (D+T+S+W+B) | -9% [-12, -6] | -6% | -12% [-17, -8] | -8% |
