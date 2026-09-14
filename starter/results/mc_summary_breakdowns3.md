H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 3 bus(es), surge sigma_d 1.0, weather eta 0.8, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = headway model; wait_dir = SUMO per-passenger (cross-check).

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |
|---|---|---|---|---|--:|--:|
| Ablation B (D+T+B) | NC | 0.578 [0.541, 0.616] | 4413 [4395, 4430] | 431 [414, 448] | 457 | 30 |
| Ablation B (D+T+B) | FH | 0.462 [0.431, 0.492] | 4544 [4528, 4560] | 398 [385, 412] | 418 | 30 |
| Ablation B (D+T+B) | EH | 0.415 [0.384, 0.446] | 4559 [4543, 4575] | 386 [374, 399] | 404 | 30 |
| Stage B (D+T+S+W+B) | NC | 0.856 [0.820, 0.891] | 5222 [5097, 5355] | 564 [539, 589] | 629 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.788 [0.753, 0.824] | 5338 [5219, 5467] | 534 [509, 559] | 594 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.778 [0.740, 0.817] | 5324 [5208, 5452] | 530 [505, 556] | 590 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Ablation B (D+T+B) | -20% [-26, -13] | -8% | -28% [-34, -22] | -10% |
| Stage B (D+T+S+W+B) | -8% [-11, -5] | -5% | -9% [-13, -5] | -6% |
