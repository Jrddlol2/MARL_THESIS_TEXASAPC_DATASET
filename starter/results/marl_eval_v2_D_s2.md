MARL evaluation, N = 30 paired seeds. Paired Wilcoxon signed-rank (one-sided), Holm over MARL vs NC/FH/EH, alpha 0.05.

| Cell | Ctrl | Headway CV [95% CI] | Recorded wait (s) [95% CI] | Formula wait (s) | Travel (s) |
|---|---|---|---|---|---|
| Stage A (D+T) | NC | 0.549 [0.513, 0.583] | 391 [379, 404] | 385 | 4398 |
| Stage A (D+T) | FH | 0.386 [0.364, 0.408] | 350 [343, 357] | 348 | 4538 |
| Stage A (D+T) | EH | 0.336 [0.317, 0.357] | 340 [334, 347] | 338 | 4548 |
| Stage A (D+T) | MARL | 0.331 [0.309, 0.354] | 344 [338, 351] | 339 | 4606 |
| Ablation S (D+T+S) | NC | 0.582 [0.546, 0.617] | 407 [392, 421] | 393 | 4503 |
| Ablation S (D+T+S) | FH | 0.417 [0.388, 0.447] | 362 [353, 372] | 354 | 4629 |
| Ablation S (D+T+S) | EH | 0.365 [0.340, 0.392] | 352 [344, 360] | 343 | 4634 |
| Ablation S (D+T+S) | MARL | 0.355 [0.328, 0.385] | 353 [345, 362] | 343 | 4691 |
| Ablation W (observed rain) | NC | 0.551 [0.516, 0.585] | 393 [380, 406] | 386 | 4453 |
| Ablation W (observed rain) | FH | 0.390 [0.368, 0.413] | 350 [343, 358] | 349 | 4593 |
| Ablation W (observed rain) | EH | 0.341 [0.321, 0.361] | 343 [337, 349] | 338 | 4599 |
| Ablation W (observed rain) | MARL | 0.333 [0.312, 0.357] | 345 [339, 352] | 339 | 4655 |
| Ablation B (D+T+B) | NC | 0.572 [0.537, 0.606] | 414 [401, 428] | 401 | 4410 |
| Ablation B (D+T+B) | FH | 0.430 [0.406, 0.455] | 376 [367, 386] | 365 | 4544 |
| Ablation B (D+T+B) | EH | 0.384 [0.363, 0.406] | 365 [356, 374] | 355 | 4555 |
| Ablation B (D+T+B) | MARL | 0.381 [0.361, 0.403] | 368 [360, 378] | 357 | 4641 |
| Stage B (observed rain) | NC | 0.603 [0.568, 0.636] | 431 [417, 447] | 409 | 4571 |
| Stage B (observed rain) | FH | 0.464 [0.432, 0.496] | 393 [380, 407] | 373 | 4696 |
| Stage B (observed rain) | EH | 0.417 [0.390, 0.445] | 380 [370, 389] | 361 | 4698 |
| Stage B (observed rain) | MARL | 0.410 [0.385, 0.437] | 384 [374, 394] | 363 | 4781 |
| Stage B (light rain) | NC | 0.612 [0.578, 0.646] | 437 [420, 455] | 411 | 4748 |
| Stage B (light rain) | FH | 0.474 [0.443, 0.507] | 398 [385, 412] | 375 | 4872 |
| Stage B (light rain) | EH | 0.429 [0.402, 0.459] | 385 [374, 396] | 364 | 4866 |
| Stage B (light rain) | MARL | 0.420 [0.392, 0.449] | 386 [375, 397] | 364 | 4939 |
| Stage B (moderate rain) | NC | 0.613 [0.579, 0.647] | 439 [423, 456] | 412 | 4795 |
| Stage B (moderate rain) | FH | 0.477 [0.446, 0.511] | 401 [387, 416] | 376 | 4919 |
| Stage B (moderate rain) | EH | 0.434 [0.406, 0.463] | 387 [376, 398] | 364 | 4912 |
| Stage B (moderate rain) | MARL | 0.424 [0.397, 0.452] | 388 [376, 400] | 365 | 4980 |
| Stage B (heavy rain) | NC | 0.615 [0.580, 0.649] | 441 [424, 458] | 412 | 4848 |
| Stage B (heavy rain) | FH | 0.479 [0.448, 0.511] | 403 [389, 419] | 376 | 4971 |
| Stage B (heavy rain) | EH | 0.436 [0.408, 0.465] | 389 [378, 401] | 365 | 4961 |
| Stage B (heavy rain) | MARL | 0.426 [0.397, 0.453] | 390 [379, 401] | 365 | 5029 |
| Stage B (extreme rainstorm) | NC | 0.654 [0.619, 0.689] | 486 [470, 504] | 422 | 5911 |
| Stage B (extreme rainstorm) | FH | 0.530 [0.498, 0.564] | 450 [434, 467] | 387 | 6040 |
| Stage B (extreme rainstorm) | EH | 0.514 [0.483, 0.546] | 443 [428, 459] | 382 | 5996 |
| Stage B (extreme rainstorm) | MARL | 0.516 [0.487, 0.546] | 445 [430, 460] | 384 | 6021 |

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
