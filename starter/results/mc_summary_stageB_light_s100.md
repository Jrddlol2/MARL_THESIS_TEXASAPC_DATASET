H0 = 600 s, 18 buses, 27 stops, N = 30 paired seeds, max hold 120 s, B removes 1 bus(es), surge sigma_d 1.0, weather light (speed loss 0.053), capacity 55, seeds 100-129, traffic stress sigma_s 0.0. Ordinary-day variability fitted from APC (fit_variability.py). Control stops: ['5280', '5857', '5859', '5867', '4046'] (§3.2.2 criteria). Wait = SUMO recorded per-passenger wait (primary); formula = headway model (H/2)(1+CV^2), cross-check.

| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | formula wait | n |
|---|---|---|---|---|--:|--:|
| Stage B (D+T+S+W+B) | NC | 0.592 [0.556, 0.630] | 4799 [4721, 4882] | 459 [429, 493] | 407 | 30 |
| Stage B (D+T+S+W+B) | FH | 0.429 [0.399, 0.459] | 4921 [4851, 4999] | 412 [385, 445] | 365 | 30 |
| Stage B (D+T+S+W+B) | EH | 0.393 [0.364, 0.425] | 4913 [4847, 4986] | 406 [379, 437] | 357 | 30 |

**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**

| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |
|---|---|---|---|---|
| Stage B (D+T+S+W+B) | -28% [-35, -19] | -10% | -34% [-40, -27] | -12% |
