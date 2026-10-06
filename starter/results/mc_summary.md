H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather observed (speed loss 0.000), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check. Weather W = observed ordinary-rain slow-down only.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.609 [0.574, 0.643] | 4590 [4566, 4617] | 410 [395, 425] | 398 | 30 |
| Stage A (D+T) | FH | 0.446 [0.422, 0.471] | 4684 [4662, 4708] | 367 [358, 376] | 358 | 30 |
| Stage A (D+T) | EH | 0.391 [0.369, 0.414] | 4678 [4658, 4699] | 355 [347, 362] | 346 | 30 |
| Ablation S (D+T+S) | NC | 0.634 [0.599, 0.669] | 4719 [4653, 4792] | 425 [410, 441] | 404 | 30 |
| Ablation S (D+T+S) | FH | 0.472 [0.444, 0.500] | 4801 [4742, 4867] | 379 [368, 389] | 362 | 30 |
| Ablation S (D+T+S) | EH | 0.421 [0.393, 0.450] | 4790 [4736, 4851] | 367 [358, 377] | 351 | 30 |
| Ablation W (D+T+W) | NC | 0.612 [0.576, 0.646] | 4647 [4623, 4673] | 413 [399, 428] | 399 | 30 |
| Ablation W (D+T+W) | FH | 0.451 [0.427, 0.475] | 4741 [4718, 4765] | 371 [362, 380] | 358 | 30 |
| Ablation W (D+T+W) | EH | 0.397 [0.375, 0.419] | 4731 [4710, 4752] | 358 [351, 366] | 346 | 30 |
| Ablation B (D+T+B) | NC | 0.634 [0.601, 0.666] | 4605 [4582, 4631] | 431 [416, 446] | 414 | 30 |
| Ablation B (D+T+B) | FH | 0.495 [0.468, 0.522] | 4692 [4670, 4715] | 392 [381, 403] | 376 | 30 |
| Ablation B (D+T+B) | EH | 0.445 [0.423, 0.468] | 4687 [4667, 4708] | 380 [371, 389] | 363 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.658 [0.625, 0.690] | 4790 [4725, 4862] | 449 [434, 466] | 419 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.522 [0.490, 0.554] | 4868 [4809, 4934] | 410 [397, 424] | 381 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.475 [0.449, 0.504] | 4854 [4798, 4917] | 396 [386, 407] | 369 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -27% [-32, -22] | -11% | -36% [-41, -30] | -13% |
| Ablation S (D+T+S) | -25% [-29, -21] | -11% | -34% [-39, -28] | -14% |
| Ablation W (D+T+W) | -26% [-31, -22] | -10% | -35% [-39, -31] | -13% |
| Ablation B (D+T+B) | -22% [-26, -18] | -9% | -30% [-34, -25] | -12% |
| Stage B (D+T+S+W+B) | -21% [-27, -15] | -9% | -28% [-32, -23] | -12% |
