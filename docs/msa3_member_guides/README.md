# MSA 3 member guides (given out 2026-10-06)

Each member has one folder. The guides say **what** to build and **how to check it**. They contain
no solution code. The answer keys are kept outside this repo.

| Folder | Member | Task | Due | Run time (4-core laptop) |
|---|---|---|---|---|
| `1_Medenilla_Statistics/` | Medenilla | Friedman → Wilcoxon → Holm, bootstrap CIs, degradation. Input: `all_controllers_runs.csv` (MSA 2 test corridor) | Part 1: Oct 12 | seconds (no simulation) |
| `2_Badal_Surge/` | Badal | Demand surge: corridor-wide N(1, σd²) clip [1, 10] + local +10/+20/+50 riders | Nov 2 | ~45–60 min |
| `3_Lopez_Weather/` | Lopez | Corridor-wide slowdown 5.3 / 6.3 / 7.4 / 25% | Nov 2 | ~30–45 min |
| `4_Marquez_Breakdown/` | Marquez | 1 and 3 buses removed; riders picked up by the next bus | Nov 2 | ~20–35 min |
| `shared_build_v2/` | Badal, Lopez, Marquez | The one test-corridor simulator everyone uses | — | baseline ~5–10 min |

Run times were measured on 4 cores (about 13 s per run per core). With 2 cores, expect about
twice as long; one run at a time takes about 4 times as long.

## For the three disturbance members

1. Copy `shared_build_v2/` out of the repo into your own working folder. Do not use your MSA 2 code.
2. Run `py run_baseline.py` first. Your E3 means must match the guide (CV NC 0.218 / FH 0.113 /
   EH 0.140; wait 353.8 / 352.5 / 348.1 s). If they don't, stop and message Jared.
3. The numbers changed since MSA 2 because every rider is now counted, so FH now bunches less than
   EH. That is expected.

What changed in v2 and why: [`../progress/MSA3_KICKOFF_2026-10-06.md`](../progress/MSA3_KICKOFF_2026-10-06.md).
Sources for every setting are listed at the end of each guide.
