H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather observed (speed loss 0.000), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check). Weather W = observed ordinary-rain slow-down only.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.549 [0.512, 0.582] | 4398 [4378, 4422] | 385 [373, 398] | 391 | 30 |
| Stage A (D+T) | FH | 0.386 [0.364, 0.408] | 4538 [4520, 4558] | 348 [340, 356] | 350 | 30 |
| Stage A (D+T) | EH | 0.336 [0.317, 0.357] | 4548 [4532, 4566] | 338 [331, 345] | 340 | 30 |
| Ablation S (D+T+S) | NC | 0.582 [0.547, 0.618] | 4503 [4445, 4566] | 393 [380, 407] | 407 | 30 |
| Ablation S (D+T+S) | FH | 0.417 [0.388, 0.446] | 4629 [4579, 4684] | 354 [345, 363] | 362 | 30 |
| Ablation S (D+T+S) | EH | 0.365 [0.339, 0.392] | 4634 [4587, 4686] | 343 [335, 351] | 352 | 30 |
| Ablation W (D+T+W) | NC | 0.551 [0.516, 0.587] | 4453 [4433, 4475] | 386 [373, 397] | 393 | 30 |
| Ablation W (D+T+W) | FH | 0.390 [0.369, 0.413] | 4593 [4575, 4614] | 349 [341, 356] | 350 | 30 |
| Ablation W (D+T+W) | EH | 0.341 [0.322, 0.361] | 4599 [4583, 4617] | 338 [332, 345] | 343 | 30 |
| Ablation B (D+T+B) | NC | 0.572 [0.537, 0.605] | 4410 [4390, 4432] | 401 [389, 414] | 414 | 30 |
| Ablation B (D+T+B) | FH | 0.430 [0.405, 0.455] | 4544 [4526, 4563] | 365 [357, 374] | 376 | 30 |
| Ablation B (D+T+B) | EH | 0.384 [0.364, 0.405] | 4555 [4539, 4574] | 355 [347, 363] | 365 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.603 [0.570, 0.638] | 4571 [4514, 4634] | 409 [396, 423] | 431 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.464 [0.433, 0.497] | 4696 [4645, 4751] | 373 [362, 384] | 393 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.417 [0.390, 0.445] | 4698 [4649, 4751] | 361 [352, 371] | 380 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -30% [-34, -25] | -10% | -39% [-44, -33] | -12% |
| Ablation S (D+T+S) | -28% [-33, -24] | -10% | -37% [-42, -32] | -13% |
| Ablation W (D+T+W) | -29% [-32, -26] | -10% | -38% [-42, -33] | -12% |
| Ablation B (D+T+B) | -25% [-29, -20] | -9% | -33% [-37, -29] | -12% |
| Stage B (D+T+S+W+B) | -23% [-29, -18] | -9% | -31% [-37, -25] | -12% |
