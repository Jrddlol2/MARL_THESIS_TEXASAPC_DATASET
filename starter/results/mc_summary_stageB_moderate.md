H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather moderate (speed loss 0.063), capacity 55, seeds 0-29, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.613 [0.578, 0.647] | 4795 [4737, 4863] | 439 [423, 456] | 412 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.477 [0.446, 0.510] | 4919 [4867, 4976] | 401 [387, 415] | 376 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.434 [0.407, 0.462] | 4912 [4863, 4967] | 387 [376, 399] | 364 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -22% [-27, -17] | -9% | -29% [-34, -24] | -12% |
