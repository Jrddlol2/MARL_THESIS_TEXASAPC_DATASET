MARL evaluation, N = 30 paired seeds. Paired Wilcoxon signed-rank (one-sided), Holm over MARL vs NC/FH/EH, alpha 0.05.

| Cell | Ctrl | Headway CV [95% CI] | Wait (s) [95% CI] | Travel (s) |
|---|---|---|---|---|
| Stage A (D+T) | NC | 0.556 [0.518, 0.591] | 387 [375, 399] | 4391 |
| Stage A (D+T) | FH | 0.396 [0.371, 0.420] | 350 [342, 358] | 4533 |
| Stage A (D+T) | EH | 0.342 [0.322, 0.363] | 339 [332, 346] | 4543 |
| Stage A (D+T) | MARL | 0.340 [0.320, 0.362] | 341 [334, 348] | 4619 |
| Ablation S (D+T+S) | NC | 0.596 [0.552, 0.641] | 399 [383, 413] | 4549 |
| Ablation S (D+T+S) | FH | 0.427 [0.397, 0.458] | 356 [347, 366] | 4673 |
| Ablation S (D+T+S) | EH | 0.371 [0.346, 0.396] | 344 [336, 352] | 4674 |
| Ablation S (D+T+S) | MARL | 0.378 [0.348, 0.410] | 348 [339, 357] | 4756 |
| Ablation W (observed rain) | NC | 0.559 [0.523, 0.594] | 388 [375, 401] | 4445 |
| Ablation W (observed rain) | FH | 0.400 [0.375, 0.423] | 351 [343, 359] | 4588 |
| Ablation W (observed rain) | EH | 0.346 [0.326, 0.368] | 340 [333, 347] | 4596 |
| Ablation W (observed rain) | MARL | 0.343 [0.321, 0.365] | 342 [334, 349] | 4672 |
| Ablation B (D+T+B) | NC | 0.564 [0.527, 0.600] | 402 [388, 417] | 4397 |
| Ablation B (D+T+B) | FH | 0.423 [0.396, 0.451] | 367 [356, 379] | 4536 |
| Ablation B (D+T+B) | EH | 0.370 [0.346, 0.396] | 355 [345, 365] | 4549 |
| Ablation B (D+T+B) | MARL | 0.381 [0.355, 0.409] | 360 [349, 371] | 4633 |
| Stage B (observed rain) | NC | 0.609 [0.565, 0.651] | 415 [398, 432] | 4612 |
| Stage B (observed rain) | FH | 0.458 [0.427, 0.490] | 374 [362, 387] | 4735 |
| Stage B (observed rain) | EH | 0.404 [0.377, 0.432] | 361 [350, 373] | 4736 |
| Stage B (observed rain) | MARL | 0.421 [0.389, 0.456] | 368 [355, 381] | 4817 |
| Stage B (eta 0.3) | NC | 0.685 [0.650, 0.720] | 445 [428, 463] | 4723 |
| Stage B (eta 0.3) | FH | 0.574 [0.540, 0.609] | 411 [395, 426] | 4844 |
| Stage B (eta 0.3) | EH | 0.534 [0.498, 0.572] | 399 [385, 414] | 4843 |
| Stage B (eta 0.3) | MARL | 0.534 [0.497, 0.571] | 401 [386, 417] | 4914 |
| Stage B (eta 0.6) | NC | 0.820 [0.785, 0.857] | 509 [486, 531] | 5063 |
| Stage B (eta 0.6) | FH | 0.742 [0.708, 0.778] | 478 [458, 499] | 5183 |
| Stage B (eta 0.6) | EH | 0.725 [0.688, 0.765] | 472 [452, 494] | 5169 |
| Stage B (eta 0.6) | MARL | 0.720 [0.678, 0.762] | 471 [449, 494] | 5248 |
| Stage B (eta 1.0) | NC | 0.904 [0.866, 0.942] | 557 [532, 582] | 5317 |
| Stage B (eta 1.0) | FH | 0.836 [0.800, 0.874] | 526 [502, 551] | 5442 |
| Stage B (eta 1.0) | EH | 0.832 [0.792, 0.873] | 524 [500, 549] | 5408 |
| Stage B (eta 1.0) | MARL | 0.827 [0.790, 0.868] | 523 [499, 549] | 5514 |
| Stage B (eta 1.3) | NC | 0.929 [0.891, 0.968] | 572 [546, 600] | 5334 |
| Stage B (eta 1.3) | FH | 0.862 [0.825, 0.901] | 541 [517, 566] | 5463 |
| Stage B (eta 1.3) | EH | 0.864 [0.825, 0.904] | 541 [516, 567] | 5427 |
| Stage B (eta 1.3) | MARL | 0.854 [0.815, 0.894] | 537 [512, 563] | 5531 |

**Acceptance criteria**

- **Stage A (i)** wait no worse than EH: MARL 341 s vs EH 339 s, Holm p(MARL worse) = 0.017 -> FAIL
- **Stage A (ii)** headway CV lower than NC: MARL 0.340 vs NC 0.556, Holm p = 0.000 -> PASS
- **Training gate** headway CV below EH: MARL 0.340 vs EH 0.342, Holm p = 0.251 -> PASS
- **Stage B** wait below the best baseline in every Stage B cell -> FAIL
  - Stage B (observed rain): MARL wait 368 s vs best baseline EH 361 s, Holm p = 1.000 -> fail
  - Stage B (eta 0.3): MARL wait 401 s vs best baseline EH 399 s, Holm p = 0.825 -> fail
  - Stage B (eta 0.6): MARL wait 471 s vs best baseline EH 472 s, Holm p = 0.292 -> fail
  - Stage B (eta 1.0): MARL wait 523 s vs best baseline EH 524 s, Holm p = 0.420 -> fail
  - Stage B (eta 1.3): MARL wait 537 s vs best baseline FH 541 s, Holm p = 0.164 -> fail
