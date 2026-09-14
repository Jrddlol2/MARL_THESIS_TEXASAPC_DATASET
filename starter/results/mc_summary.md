H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 0.8, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.552 [0.517, 0.587] | 4528 [4509, 4547] | 387 [375, 400] | 393 | 30 |
| Stage A (D+T) | FH | 0.366 [0.342, 0.390] | 4710 [4692, 4728] | 345 [338, 352] | 352 | 30 |
| Stage A (D+T) | EH | 0.338 [0.318, 0.357] | 4666 [4649, 4683] | 338 [332, 345] | 342 | 30 |
| Ablation S (D+T+S) | NC | 0.621 [0.576, 0.668] | 4746 [4657, 4851] | 408 [391, 426] | 462 | 30 |
| Ablation S (D+T+S) | FH | 0.425 [0.394, 0.459] | 4899 [4812, 4992] | 357 [347, 367] | 414 | 30 |
| Ablation S (D+T+S) | EH | 0.395 [0.364, 0.428] | 4845 [4764, 4940] | 349 [340, 359] | 402 | 30 |
| Ablation W (D+T+W) | NC | 0.869 [0.830, 0.909] | 5219 [5127, 5313] | 525 [500, 550] | 536 | 30 |
| Ablation W (D+T+W) | FH | 0.793 [0.752, 0.833] | 5380 [5289, 5473] | 494 [471, 519] | 501 | 30 |
| Ablation W (D+T+W) | EH | 0.788 [0.747, 0.829] | 5318 [5230, 5404] | 491 [469, 516] | 494 | 30 |
| Ablation B (D+T+B) | NC | 0.565 [0.529, 0.600] | 4536 [4516, 4554] | 403 [389, 418] | 413 | 30 |
| Ablation B (D+T+B) | FH | 0.401 [0.374, 0.429] | 4715 [4696, 4733] | 363 [353, 373] | 373 | 30 |
| Ablation B (D+T+B) | EH | 0.370 [0.347, 0.394] | 4674 [4656, 4691] | 355 [346, 365] | 363 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.886 [0.846, 0.926] | 5482 [5342, 5637] | 548 [522, 573] | 633 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.803 [0.764, 0.845] | 5633 [5491, 5782] | 514 [489, 539] | 593 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.808 [0.767, 0.851] | 5565 [5424, 5713] | 514 [490, 540] | 586 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -34% [-39, -28] | -11% | -39% [-44, -33] | -13% |
| Ablation S (D+T+S) | -31% [-36, -26] | -13% | -36% [-42, -30] | -14% |
| Ablation W (D+T+W) | -9% [-13, -5] | -6% | -9% [-14, -5] | -6% |
| Ablation B (D+T+B) | -29% [-33, -25] | -10% | -34% [-38, -30] | -12% |
| Stage B (D+T+S+W+B) | -9% [-14, -5] | -6% | -9% [-13, -5] | -6% |
