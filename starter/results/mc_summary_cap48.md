H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather observed (speed loss 0.000), capacity 48, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check. Weather W = observed ordinary-rain slow-down only.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.549 [0.512, 0.583] | 4398 [4378, 4421] | 391 [379, 404] | 385 | 30 |
| Stage A (D+T) | FH | 0.386 [0.364, 0.409] | 4538 [4520, 4558] | 350 [343, 357] | 348 | 30 |
| Stage A (D+T) | EH | 0.336 [0.317, 0.356] | 4548 [4532, 4565] | 340 [335, 347] | 338 | 30 |
| Ablation S (D+T+S) | NC | 0.582 [0.546, 0.618] | 4503 [4444, 4567] | 407 [393, 422] | 393 | 30 |
| Ablation S (D+T+S) | FH | 0.417 [0.388, 0.446] | 4629 [4579, 4682] | 362 [352, 372] | 354 | 30 |
| Ablation S (D+T+S) | EH | 0.365 [0.339, 0.393] | 4634 [4587, 4685] | 352 [344, 360] | 343 | 30 |
| Ablation W (D+T+W) | NC | 0.551 [0.515, 0.586] | 4453 [4433, 4475] | 393 [381, 406] | 386 | 30 |
| Ablation W (D+T+W) | FH | 0.390 [0.368, 0.413] | 4593 [4575, 4614] | 350 [343, 358] | 349 | 30 |
| Ablation W (D+T+W) | EH | 0.341 [0.322, 0.362] | 4599 [4583, 4617] | 343 [337, 348] | 338 | 30 |
| Ablation B (D+T+B) | NC | 0.572 [0.538, 0.605] | 4410 [4390, 4432] | 414 [401, 428] | 401 | 30 |
| Ablation B (D+T+B) | FH | 0.430 [0.406, 0.456] | 4544 [4526, 4563] | 376 [367, 386] | 365 | 30 |
| Ablation B (D+T+B) | EH | 0.384 [0.363, 0.405] | 4555 [4538, 4574] | 365 [356, 374] | 355 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.603 [0.569, 0.637] | 4571 [4512, 4634] | 431 [416, 447] | 409 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.464 [0.433, 0.495] | 4696 [4646, 4756] | 393 [381, 407] | 373 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.417 [0.390, 0.444] | 4698 [4650, 4751] | 380 [370, 390] | 361 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -30% [-34, -25] | -11% | -39% [-43, -34] | -13% |
| Ablation S (D+T+S) | -28% [-34, -23] | -11% | -37% [-42, -33] | -13% |
| Ablation W (D+T+W) | -29% [-32, -26] | -11% | -38% [-42, -35] | -13% |
| Ablation B (D+T+B) | -25% [-28, -22] | -9% | -33% [-36, -29] | -12% |
| Stage B (D+T+S+W+B) | -23% [-29, -16] | -9% | -31% [-35, -27] | -12% |
