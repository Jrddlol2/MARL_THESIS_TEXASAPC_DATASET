# New baselines (fixed simulator), development seeds 0-29

Corridor-wide weather, capacity 55. Wait = SUMO recorded per-passenger wait (primary); formula in brackets. Change vs No Control in the same cell.

| Condition | NC CV | FH CV | EH CV | NC wait | FH wait | EH wait | EH vs NC (CV / wait) |
|---|---|---|---|---|---|---|---|
| Stage A (D+T) | 0.549 | 0.386 | 0.336 | 391 (385) | 350 (348) | 340 (338) | -39% / -13% |
| Ablation S (D+T+S) | 0.582 | 0.417 | 0.365 | 407 (393) | 362 (354) | 352 (343) | -37% / -13% |
| Ablation W (D+T+W) | 0.551 | 0.390 | 0.341 | 393 (386) | 350 (349) | 343 (338) | -38% / -13% |
| Ablation B (D+T+B) | 0.572 | 0.430 | 0.384 | 414 (401) | 376 (365) | 365 (355) | -33% / -12% |
| Stage B (D+T+S+W+B) | 0.603 | 0.464 | 0.417 | 431 (409) | 393 (373) | 380 (361) | -31% / -12% |
| Stage B, light | 0.612 | 0.474 | 0.429 | 437 (411) | 398 (375) | 385 (364) | -30% / -12% |
| Stage B, moderate | 0.613 | 0.477 | 0.434 | 439 (412) | 401 (376) | 387 (364) | -29% / -12% |
| Stage B, heavy | 0.615 | 0.479 | 0.436 | 441 (412) | 403 (376) | 389 (365) | -29% / -12% |
| Stage B, extreme | 0.654 | 0.530 | 0.514 | 486 (422) | 450 (387) | 443 (382) | -21% / -9% |
