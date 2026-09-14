H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 0.8, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.556 [0.518, 0.590] | 4391 [4373, 4409] | 387 [375, 400] | 393 | 30 |
| Stage A (D+T) | FH | 0.396 [0.371, 0.420] | 4533 [4518, 4550] | 350 [342, 358] | 356 | 30 |
| Stage A (D+T) | EH | 0.342 [0.322, 0.363] | 4543 [4528, 4559] | 339 [332, 346] | 344 | 30 |
| Ablation S (D+T+S) | NC | 0.596 [0.553, 0.639] | 4549 [4485, 4626] | 399 [384, 414] | 420 | 30 |
| Ablation S (D+T+S) | FH | 0.427 [0.398, 0.456] | 4673 [4612, 4742] | 356 [347, 366] | 379 | 30 |
| Ablation S (D+T+S) | EH | 0.371 [0.345, 0.396] | 4674 [4618, 4743] | 344 [336, 352] | 366 | 30 |
| Ablation W (D+T+W) | NC | 0.865 [0.827, 0.903] | 5048 [4960, 5138] | 520 [497, 544] | 531 | 30 |
| Ablation W (D+T+W) | FH | 0.798 [0.761, 0.834] | 5183 [5093, 5277] | 493 [470, 515] | 497 | 30 |
| Ablation W (D+T+W) | EH | 0.786 [0.748, 0.825] | 5162 [5078, 5247] | 488 [466, 512] | 493 | 30 |
| Ablation B (D+T+B) | NC | 0.564 [0.528, 0.599] | 4397 [4379, 4414] | 402 [387, 417] | 410 | 30 |
| Ablation B (D+T+B) | FH | 0.423 [0.396, 0.452] | 4536 [4520, 4553] | 367 [356, 378] | 376 | 30 |
| Ablation B (D+T+B) | EH | 0.370 [0.346, 0.395] | 4549 [4532, 4566] | 355 [345, 366] | 363 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.876 [0.840, 0.913] | 5243 [5122, 5374] | 540 [516, 563] | 579 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.804 [0.767, 0.843] | 5360 [5245, 5489] | 509 [486, 533] | 543 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.796 [0.756, 0.836] | 5339 [5221, 5464] | 505 [483, 529] | 539 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -29% [-35, -22] | -10% | -38% [-44, -33] | -12% |
| Ablation S (D+T+S) | -28% [-33, -23] | -11% | -38% [-42, -33] | -14% |
| Ablation W (D+T+W) | -8% [-10, -6] | -5% | -9% [-11, -7] | -6% |
| Ablation B (D+T+B) | -25% [-29, -20] | -9% | -34% [-39, -30] | -12% |
| Stage B (D+T+S+W+B) | -8% [-12, -4] | -6% | -9% [-13, -5] | -6% |
