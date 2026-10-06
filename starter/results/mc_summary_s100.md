H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather observed (speed loss 0.000), capacity 55, seeds 100-129, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check. Weather W = observed ordinary-rain slow-down only.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage A (D+T) | NC | 0.522 [0.490, 0.557] | 4381 [4362, 4401] | 381 [370, 394] | 375 | 30 |
| Stage A (D+T) | FH | 0.341 [0.317, 0.366] | 4525 [4507, 4543] | 341 [334, 348] | 337 | 30 |
| Stage A (D+T) | EH | 0.296 [0.276, 0.316] | 4533 [4515, 4550] | 334 [328, 340] | 329 | 30 |
| Ablation S (D+T+S) | NC | 0.566 [0.533, 0.601] | 4555 [4484, 4634] | 417 [398, 439] | 386 | 30 |
| Ablation S (D+T+S) | FH | 0.377 [0.353, 0.405] | 4680 [4612, 4753] | 368 [350, 389] | 343 | 30 |
| Ablation S (D+T+S) | EH | 0.329 [0.308, 0.352] | 4679 [4616, 4747] | 358 [342, 378] | 334 | 30 |
| Ablation W (D+T+W) | NC | 0.524 [0.493, 0.559] | 4436 [4417, 4457] | 382 [371, 393] | 376 | 30 |
| Ablation W (D+T+W) | FH | 0.333 [0.302, 0.367] | 4568 [4544, 4590] | 341 [330, 354] | 337 | 13 |
| Ablation W (D+T+W) | EH | nan [nan, nan] | nan [nan, nan] | nan [nan, nan] | nan | 0 |
| Ablation B (D+T+B) | NC | nan [nan, nan] | nan [nan, nan] | nan [nan, nan] | nan | 0 |
| Ablation B (D+T+B) | FH | nan [nan, nan] | nan [nan, nan] | nan [nan, nan] | nan | 0 |
| Ablation B (D+T+B) | EH | nan [nan, nan] | nan [nan, nan] | nan [nan, nan] | nan | 0 |
| Stage B (D+T+S+W+B) | NC | nan [nan, nan] | nan [nan, nan] | nan [nan, nan] | nan | 0 |
| Stage B (D+T+S+W+B) | FH | 0.535 [0.479, 0.590] | 4942 [4816, 5067] | 432 [416, 448] | 388 | 2 |
| Stage B (D+T+S+W+B) | EH | nan [nan, nan] | nan [nan, nan] | nan [nan, nan] | nan | 0 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage A (D+T) | -35% [-40, -29] | -11% | -43% [-48, -39] | -12% |
| Ablation S (D+T+S) | -33% [-38, -27] | -12% | -42% [-47, -36] | -14% |
| Ablation W (D+T+W) | -35% [-40, -30] | -9% | +nan% [+nan, +nan] | +nan% |
| Ablation B (D+T+B) | +nan% [+nan, +nan] | +nan% | +nan% [+nan, +nan] | +nan% |
| Stage B (D+T+S+W+B) | +nan% [+nan, +nan] | +nan% | +nan% [+nan, +nan] | +nan% |
