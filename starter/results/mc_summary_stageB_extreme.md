H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather extreme (speed loss 0.250), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.708 [0.675, 0.742] | 6119 [6052, 6191] | 510 [494, 526] | 432 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.583 [0.552, 0.616] | 6208 [6142, 6281] | 473 [458, 490] | 394 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.570 [0.540, 0.602] | 6152 [6089, 6223] | 467 [452, 482] | 390 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -18% [-22, -13] | -7% | -20% [-24, -14] | -9% |
