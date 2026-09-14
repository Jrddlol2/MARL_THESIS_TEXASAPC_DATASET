H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 240 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 0.8, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.552 [0.516, 0.586] | 4528 [4509, 4547] | 387 [375, 400] | 393 | 30 |
| Stage A (D+T) | FH | 0.324 [0.301, 0.349] | 4791 [4769, 4813] | 338 [332, 345] | 346 | 30 |
| Stage A (D+T) | EH | 0.304 [0.285, 0.323] | 4691 [4675, 4706] | 332 [326, 338] | 337 | 30 |
| Ablation S (D+T+S) | NC | 0.621 [0.576, 0.668] | 4746 [4657, 4848] | 408 [392, 425] | 462 | 30 |
| Ablation S (D+T+S) | FH | 0.369 [0.340, 0.402] | 4989 [4901, 5084] | 347 [338, 357] | 406 | 30 |
| Ablation S (D+T+S) | EH | 0.353 [0.325, 0.385] | 4870 [4790, 4964] | 341 [333, 350] | 395 | 30 |
| Ablation W (D+T+W) | NC | 0.869 [0.828, 0.909] | 5219 [5123, 5311] | 525 [500, 550] | 536 | 30 |
| Ablation W (D+T+W) | FH | 0.746 [0.709, 0.785] | 5533 [5434, 5636] | 479 [456, 502] | 485 | 30 |
| Ablation W (D+T+W) | EH | 0.761 [0.723, 0.800] | 5376 [5293, 5457] | 482 [460, 505] | 482 | 30 |
| Ablation B (D+T+B) | NC | 0.565 [0.529, 0.600] | 4536 [4516, 4554] | 403 [389, 418] | 413 | 30 |
| Ablation B (D+T+B) | FH | 0.368 [0.339, 0.399] | 4794 [4770, 4819] | 357 [348, 368] | 370 | 30 |
| Ablation B (D+T+B) | EH | 0.335 [0.313, 0.357] | 4701 [4684, 4718] | 348 [340, 357] | 356 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.886 [0.846, 0.927] | 5482 [5338, 5639] | 548 [523, 573] | 633 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.760 [0.723, 0.799] | 5773 [5623, 5927] | 498 [474, 523] | 579 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.779 [0.738, 0.822] | 5613 [5479, 5752] | 503 [480, 528] | 573 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -41% [-46, -36] | -13% | -45% [-49, -41] | -14% |
| Ablation S (D+T+S) | -41% [-46, -34] | -15% | -43% [-48, -37] | -17% |
| Ablation W (D+T+W) | -14% [-18, -10] | -9% | -12% [-15, -10] | -8% |
| Ablation B (D+T+B) | -35% [-40, -29] | -11% | -41% [-45, -37] | -14% |
| Stage B (D+T+S+W+B) | -14% [-18, -10] | -9% | -12% [-16, -8] | -8% |
