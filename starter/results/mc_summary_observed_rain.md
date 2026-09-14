H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather eta 0.0, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check). Weather W = observed ordinary-rain slow-down only (eta 0).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Ablation W (D+T+W) | NC | 0.559 [0.522, 0.593] | 4445 [4428, 4464] | 388 [376, 400] | 395 | 30 |
| Ablation W (D+T+W) | FH | 0.400 [0.375, 0.423] | 4588 [4573, 4605] | 351 [343, 359] | 358 | 30 |
| Ablation W (D+T+W) | EH | 0.346 [0.326, 0.368] | 4596 [4580, 4612] | 340 [333, 347] | 344 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.609 [0.567, 0.653] | 4612 [4549, 4689] | 415 [399, 432] | 444 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.458 [0.425, 0.490] | 4735 [4673, 4809] | 374 [362, 387] | 403 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.404 [0.376, 0.433] | 4736 [4676, 4806] | 361 [351, 373] | 388 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Ablation W (D+T+W) | -28% [-34, -22] | -10% | -38% [-43, -32] | -12% |
| Stage B (D+T+S+W+B) | -25% [-29, -21] | -10% | -34% [-38, -29] | -13% |
