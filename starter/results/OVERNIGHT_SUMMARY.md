# Overnight results (development seeds 0-29; test seeds 100-129 untouched)

Recorded per-passenger wait is primary. Gap = MARL wait vs Even Headway.

| Run | Cell | MARL CV | EH CV | MARL wait (s) | EH wait (s) | Gap % | MARL trip (s) | EH trip (s) |
|---|---|---|---|---|---|---|---|---|
| v2_B_s0 | A | 0.330 | 0.336 | 346 | 340 | +1.72 | 4660 | 4548 |
| v2_B_s0 | B_obs | 0.416 | 0.417 | 385 | 380 | +1.48 | 4819 | 4698 |
| v2_B_s0 | B_heavy | 0.426 | 0.436 | 391 | 389 | +0.38 | 5064 | 4961 |
| v2_B_s0 | B_extreme | 0.516 | 0.514 | 446 | 443 | +0.57 | 6025 | 5996 |
| v2_B_s1 | A | 0.327 | 0.336 | 348 | 340 | +2.25 | 4724 | 4548 |
| v2_B_s1 | B_obs | 0.401 | 0.417 | 380 | 380 | +0.24 | 4823 | 4698 |
| v2_B_s1 | B_heavy | 0.420 | 0.436 | 389 | 389 | -0.10 | 5070 | 4961 |
| v2_B_s1 | B_extreme | 0.497 | 0.514 | 453 | 443 | +2.31 | 6065 | 5996 |
| v2_B_s2 | A | 0.333 | 0.336 | 343 | 340 | +0.67 | 4572 | 4548 |
| v2_B_s2 | B_obs | 0.414 | 0.417 | 383 | 380 | +1.02 | 4751 | 4698 |
| v2_B_s2 | B_heavy | 0.438 | 0.436 | 393 | 389 | +1.01 | 5002 | 4961 |
| v2_B_s2 | B_extreme | 0.542 | 0.514 | 452 | 443 | +2.07 | 6020 | 5996 |
| v2_D_s0 | A | 0.325 | 0.336 | 345 | 340 | +1.25 | 4670 | 4548 |
| v2_D_s0 | B_obs | 0.401 | 0.417 | 380 | 380 | +0.20 | 4814 | 4698 |
| v2_D_s0 | B_heavy | 0.419 | 0.436 | 390 | 389 | +0.23 | 5066 | 4961 |
| v2_D_s0 | B_extreme | 0.502 | 0.514 | 445 | 443 | +0.34 | 6038 | 5996 |
| v2_D_s1 | A | 0.345 | 0.336 | 344 | 340 | +0.92 | 4542 | 4548 |
| v2_D_s1 | B_obs | 0.432 | 0.417 | 388 | 380 | +2.28 | 4716 | 4698 |
| v2_D_s1 | B_heavy | 0.452 | 0.436 | 398 | 389 | +2.14 | 4977 | 4961 |
| v2_D_s1 | B_extreme | 0.529 | 0.514 | 460 | 443 | +3.83 | 6024 | 5996 |
| v2_D_s2 | A | 0.331 | 0.336 | 344 | 340 | +1.14 | 4606 | 4548 |
| v2_D_s2 | B_obs | 0.410 | 0.417 | 384 | 380 | +1.05 | 4781 | 4698 |
| v2_D_s2 | B_heavy | 0.426 | 0.436 | 390 | 389 | +0.06 | 5029 | 4961 |
| v2_D_s2 | B_extreme | 0.516 | 0.514 | 445 | 443 | +0.36 | 6021 | 5996 |
| v2_K111_s0 | A | 0.329 | 0.336 | 343 | 340 | +0.77 | 4615 | 4548 |
| v2_K111_s0 | B_obs | 0.412 | 0.417 | 382 | 380 | +0.65 | 4772 | 4698 |
| v2_K111_s0 | B_heavy | 0.430 | 0.436 | 392 | 389 | +0.71 | 5027 | 4961 |
| v2_K111_s0 | B_extreme | 0.512 | 0.514 | 445 | 443 | +0.44 | 6032 | 5996 |
| v2_K500_s0 | A | 0.322 | 0.336 | 342 | 340 | +0.39 | 4622 | 4548 |
| v2_K500_s0 | B_obs | 0.410 | 0.417 | 382 | 380 | +0.55 | 4785 | 4698 |
| v2_K500_s0 | B_heavy | 0.436 | 0.436 | 394 | 389 | +1.09 | 5037 | 4961 |
| v2_K500_s0 | B_extreme | 0.540 | 0.514 | 453 | 443 | +2.30 | 6037 | 5996 |

## Mean over training seeds

| Config | Cell | Seeds | MARL CV (min-max) | Wait gap % (min-max) |
|---|---|---|---|---|
| v2_B | A | 3 | 0.330 (0.327-0.333) | +1.55 (+0.67 to +2.25) |
| v2_B | B_extreme | 3 | 0.519 (0.497-0.542) | +1.65 (+0.57 to +2.31) |
| v2_B | B_heavy | 3 | 0.428 (0.420-0.438) | +0.43 (-0.10 to +1.01) |
| v2_B | B_obs | 3 | 0.411 (0.401-0.416) | +0.92 (+0.24 to +1.48) |
| v2_D | A | 3 | 0.333 (0.325-0.345) | +1.11 (+0.92 to +1.25) |
| v2_D | B_extreme | 3 | 0.515 (0.502-0.529) | +1.51 (+0.34 to +3.83) |
| v2_D | B_heavy | 3 | 0.432 (0.419-0.452) | +0.81 (+0.06 to +2.14) |
| v2_D | B_obs | 3 | 0.414 (0.401-0.432) | +1.17 (+0.20 to +2.28) |
| v2_K111 | A | 1 | 0.329 (0.329-0.329) | +0.77 (+0.77 to +0.77) |
| v2_K111 | B_extreme | 1 | 0.512 (0.512-0.512) | +0.44 (+0.44 to +0.44) |
| v2_K111 | B_heavy | 1 | 0.430 (0.430-0.430) | +0.71 (+0.71 to +0.71) |
| v2_K111 | B_obs | 1 | 0.412 (0.412-0.412) | +0.65 (+0.65 to +0.65) |
| v2_K500 | A | 1 | 0.322 (0.322-0.322) | +0.39 (+0.39 to +0.39) |
| v2_K500 | B_extreme | 1 | 0.540 (0.540-0.540) | +2.30 (+2.30 to +2.30) |
| v2_K500 | B_heavy | 1 | 0.436 (0.436-0.436) | +1.09 (+1.09 to +1.09) |
| v2_K500 | B_obs | 1 | 0.410 (0.410-0.410) | +0.55 (+0.55 to +0.55) |

## Acceptance verdicts

### v2_B_s0
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 346.3 s vs EH 340.4 s (+1.72%), p(non-inferior) = 0.540 -> FAIL   [original no-margin test: Holm p(MARL worse) = 0.008 -> fail]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 339.8 s vs EH 337.8 s (+0.58%), p(non-inferior) = 0.000 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.031 -> fail]
- **Stage A (ii)** headway CV lower than NC: MARL 0.330 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.330 vs EH 0.336, Holm p = 0.095 -> PASS
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 385 s vs best baseline EH 380 s, Holm p = 0.993 -> fail
  - Stage B (light rain): MARL 388 s vs best baseline EH 385 s, Holm p = 0.981 -> fail
  - Stage B (moderate rain): MARL 390 s vs best baseline EH 387 s, Holm p = 0.956 -> fail
  - Stage B (heavy rain): MARL 391 s vs best baseline EH 389 s, Holm p = 0.855 -> fail
  - Stage B (extreme rainstorm): MARL 446 s vs best baseline EH 443 s, Holm p = 0.831 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 364 s vs best baseline EH 361 s, Holm p = 0.983 -> fail
  - Stage B (light rain): MARL 365 s vs best baseline EH 364 s, Holm p = 0.860 -> fail
  - Stage B (moderate rain): MARL 366 s vs best baseline EH 364 s, Holm p = 0.831 -> fail
  - Stage B (heavy rain): MARL 365 s vs best baseline EH 365 s, Holm p = 0.701 -> fail
  - Stage B (extreme rainstorm): MARL 384 s vs best baseline EH 382 s, Holm p = 0.915 -> fail
### v2_B_s1
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 348.1 s vs EH 340.4 s (+2.25%), p(non-inferior) = 0.761 -> FAIL   [original no-margin test: Holm p(MARL worse) = 0.000 -> fail]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 341.2 s vs EH 337.8 s (+1.01%), p(non-inferior) = 0.029 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.003 -> fail]
- **Stage A (ii)** headway CV lower than NC: MARL 0.327 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.327 vs EH 0.336, Holm p = 0.040 -> PASS (significant)
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 380 s vs best baseline EH 380 s, Holm p = 0.508 -> fail
  - Stage B (light rain): MARL 386 s vs best baseline EH 385 s, Holm p = 0.774 -> fail
  - Stage B (moderate rain): MARL 389 s vs best baseline EH 387 s, Holm p = 0.729 -> fail
  - Stage B (heavy rain): MARL 389 s vs best baseline EH 389 s, Holm p = 0.524 -> fail
  - Stage B (extreme rainstorm): MARL 453 s vs best baseline EH 443 s, Holm p = 0.836 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 361 s vs best baseline EH 361 s, Holm p = 0.596 -> fail
  - Stage B (light rain): MARL 363 s vs best baseline EH 364 s, Holm p = 0.468 -> fail
  - Stage B (moderate rain): MARL 364 s vs best baseline EH 364 s, Holm p = 0.428 -> fail
  - Stage B (heavy rain): MARL 364 s vs best baseline EH 365 s, Holm p = 0.258 -> fail
  - Stage B (extreme rainstorm): MARL 379 s vs best baseline EH 382 s, Holm p = 0.007 -> pass
### v2_B_s2
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 342.7 s vs EH 340.4 s (+0.67%), p(non-inferior) = 0.026 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.210 -> pass]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 338.1 s vs EH 337.8 s (+0.09%), p(non-inferior) = 0.000 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.297 -> pass]
- **Stage A (ii)** headway CV lower than NC: MARL 0.333 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.333 vs EH 0.336, Holm p = 0.460 -> PASS
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 383 s vs best baseline EH 380 s, Holm p = 0.927 -> fail
  - Stage B (light rain): MARL 388 s vs best baseline EH 385 s, Holm p = 0.960 -> fail
  - Stage B (moderate rain): MARL 392 s vs best baseline EH 387 s, Holm p = 0.997 -> fail
  - Stage B (heavy rain): MARL 393 s vs best baseline EH 389 s, Holm p = 0.971 -> fail
  - Stage B (extreme rainstorm): MARL 452 s vs best baseline EH 443 s, Holm p = 1.000 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 363 s vs best baseline EH 361 s, Holm p = 0.897 -> fail
  - Stage B (light rain): MARL 365 s vs best baseline EH 364 s, Holm p = 0.971 -> fail
  - Stage B (moderate rain): MARL 366 s vs best baseline EH 364 s, Holm p = 0.943 -> fail
  - Stage B (heavy rain): MARL 367 s vs best baseline EH 365 s, Holm p = 0.971 -> fail
  - Stage B (extreme rainstorm): MARL 392 s vs best baseline EH 382 s, Holm p = 1.000 -> fail
### v2_D_s0
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 344.7 s vs EH 340.4 s (+1.25%), p(non-inferior) = 0.169 -> FAIL   [original no-margin test: Holm p(MARL worse) = 0.061 -> pass]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 339.3 s vs EH 337.8 s (+0.46%), p(non-inferior) = 0.000 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.286 -> pass]
- **Stage A (ii)** headway CV lower than NC: MARL 0.325 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.325 vs EH 0.336, Holm p = 0.019 -> PASS (significant)
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 380 s vs best baseline EH 380 s, Holm p = 0.580 -> fail
  - Stage B (light rain): MARL 387 s vs best baseline EH 385 s, Holm p = 0.901 -> fail
  - Stage B (moderate rain): MARL 389 s vs best baseline EH 387 s, Holm p = 0.701 -> fail
  - Stage B (heavy rain): MARL 390 s vs best baseline EH 389 s, Holm p = 0.657 -> fail
  - Stage B (extreme rainstorm): MARL 445 s vs best baseline EH 443 s, Holm p = 0.815 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 361 s vs best baseline EH 361 s, Holm p = 0.540 -> fail
  - Stage B (light rain): MARL 364 s vs best baseline EH 364 s, Holm p = 0.742 -> fail
  - Stage B (moderate rain): MARL 364 s vs best baseline EH 364 s, Holm p = 0.572 -> fail
  - Stage B (heavy rain): MARL 364 s vs best baseline EH 365 s, Holm p = 0.532 -> fail
  - Stage B (extreme rainstorm): MARL 380 s vs best baseline EH 382 s, Holm p = 0.044 -> pass
### v2_D_s1
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 343.6 s vs EH 340.4 s (+0.92%), p(non-inferior) = 0.035 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.010 -> fail]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 339.1 s vs EH 337.8 s (+0.40%), p(non-inferior) = 0.000 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.007 -> fail]
- **Stage A (ii)** headway CV lower than NC: MARL 0.345 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.345 vs EH 0.336, Holm p = 0.997 -> FAIL
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 388 s vs best baseline EH 380 s, Holm p = 1.000 -> fail
  - Stage B (light rain): MARL 393 s vs best baseline EH 385 s, Holm p = 1.000 -> fail
  - Stage B (moderate rain): MARL 395 s vs best baseline EH 387 s, Holm p = 1.000 -> fail
  - Stage B (heavy rain): MARL 398 s vs best baseline EH 389 s, Holm p = 1.000 -> fail
  - Stage B (extreme rainstorm): MARL 460 s vs best baseline EH 443 s, Holm p = 1.000 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 366 s vs best baseline EH 361 s, Holm p = 1.000 -> fail
  - Stage B (light rain): MARL 369 s vs best baseline EH 364 s, Holm p = 1.000 -> fail
  - Stage B (moderate rain): MARL 370 s vs best baseline EH 364 s, Holm p = 1.000 -> fail
  - Stage B (heavy rain): MARL 371 s vs best baseline EH 365 s, Holm p = 1.000 -> fail
  - Stage B (extreme rainstorm): MARL 388 s vs best baseline EH 382 s, Holm p = 1.000 -> fail
### v2_D_s2
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 344.3 s vs EH 340.4 s (+1.14%), p(non-inferior) = 0.292 -> FAIL   [original no-margin test: Holm p(MARL worse) = 0.042 -> fail]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 338.8 s vs EH 337.8 s (+0.31%), p(non-inferior) = 0.000 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.219 -> pass]
- **Stage A (ii)** headway CV lower than NC: MARL 0.331 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.331 vs EH 0.336, Holm p = 0.214 -> PASS
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 384 s vs best baseline EH 380 s, Holm p = 0.967 -> fail
  - Stage B (light rain): MARL 386 s vs best baseline EH 385 s, Holm p = 0.831 -> fail
  - Stage B (moderate rain): MARL 388 s vs best baseline EH 387 s, Holm p = 0.665 -> fail
  - Stage B (heavy rain): MARL 390 s vs best baseline EH 389 s, Holm p = 0.708 -> fail
  - Stage B (extreme rainstorm): MARL 445 s vs best baseline EH 443 s, Holm p = 0.825 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 363 s vs best baseline EH 361 s, Holm p = 0.963 -> fail
  - Stage B (light rain): MARL 364 s vs best baseline EH 364 s, Holm p = 0.831 -> fail
  - Stage B (moderate rain): MARL 365 s vs best baseline EH 364 s, Holm p = 0.735 -> fail
  - Stage B (heavy rain): MARL 365 s vs best baseline EH 365 s, Holm p = 0.680 -> fail
  - Stage B (extreme rainstorm): MARL 384 s vs best baseline EH 382 s, Holm p = 0.954 -> fail
### v2_K111_s0
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 343.1 s vs EH 340.4 s (+0.77%), p(non-inferior) = 0.118 -> FAIL   [original no-margin test: Holm p(MARL worse) = 0.091 -> pass]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 338.4 s vs EH 337.8 s (+0.18%), p(non-inferior) = 0.000 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.794 -> pass]
- **Stage A (ii)** headway CV lower than NC: MARL 0.329 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.329 vs EH 0.336, Holm p = 0.024 -> PASS (significant)
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 382 s vs best baseline EH 380 s, Holm p = 0.890 -> fail
  - Stage B (light rain): MARL 388 s vs best baseline EH 385 s, Holm p = 0.984 -> fail
  - Stage B (moderate rain): MARL 391 s vs best baseline EH 387 s, Holm p = 0.950 -> fail
  - Stage B (heavy rain): MARL 392 s vs best baseline EH 389 s, Holm p = 0.878 -> fail
  - Stage B (extreme rainstorm): MARL 445 s vs best baseline EH 443 s, Holm p = 0.851 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 363 s vs best baseline EH 361 s, Holm p = 0.924 -> fail
  - Stage B (light rain): MARL 364 s vs best baseline EH 364 s, Holm p = 0.657 -> fail
  - Stage B (moderate rain): MARL 365 s vs best baseline EH 364 s, Holm p = 0.701 -> fail
  - Stage B (heavy rain): MARL 366 s vs best baseline EH 365 s, Holm p = 0.492 -> fail
  - Stage B (extreme rainstorm): MARL 383 s vs best baseline EH 382 s, Holm p = 0.596 -> fail
### v2_K500_s0
**Acceptance criteria**

- **Stage A (i), recorded wait (PRIMARY)** within 1.5% of EH: MARL 341.8 s vs EH 340.4 s (+0.39%), p(non-inferior) = 0.010 -> PASS   [original no-margin test: Holm p(MARL worse) = 0.735 -> pass]
- **Stage A (i), formula wait (cross-check)** within 1.5% of EH: MARL 337.0 s vs EH 337.8 s (-0.23%), p(non-inferior) = 0.000 -> PASS   [original no-margin test: Holm p(MARL worse) = 1.000 -> pass]
- **Stage A (ii)** headway CV lower than NC: MARL 0.322 vs NC 0.549, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.322 vs EH 0.336, Holm p = 0.000 -> PASS (significant)
- **Stage B, recorded wait (PRIMARY)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 382 s vs best baseline EH 380 s, Holm p = 0.860 -> fail
  - Stage B (light rain): MARL 388 s vs best baseline EH 385 s, Holm p = 0.986 -> fail
  - Stage B (moderate rain): MARL 391 s vs best baseline EH 387 s, Holm p = 0.990 -> fail
  - Stage B (heavy rain): MARL 394 s vs best baseline EH 389 s, Holm p = 0.991 -> fail
  - Stage B (extreme rainstorm): MARL 453 s vs best baseline EH 443 s, Holm p = 1.000 -> fail
- **Stage B, formula wait (cross-check)** below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL 362 s vs best baseline EH 361 s, Holm p = 0.715 -> fail
  - Stage B (light rain): MARL 364 s vs best baseline EH 364 s, Holm p = 0.882 -> fail
  - Stage B (moderate rain): MARL 366 s vs best baseline EH 364 s, Holm p = 0.915 -> fail
  - Stage B (heavy rain): MARL 366 s vs best baseline EH 365 s, Holm p = 0.930 -> fail
  - Stage B (extreme rainstorm): MARL 391 s vs best baseline EH 382 s, Holm p = 1.000 -> fail
