# Shared test-corridor build v2 (MSA 3)

The one simulator every MSA 3 disturbance study uses. Do not edit `controllers.py` or `simulator/params.py`.

Run the baseline first (about 5-10 min):

    py run_baseline.py            # all cores but one
    py run_baseline.py --jobs 4

It writes `results/baseline_v2_runs.csv`. Expected E3 means (30 seeds):
CV NC 0.218 / FH 0.113 / EH 0.140; wait_s 353.8 / 352.5 / 348.1.

Changes from MSA 2 (v1): every rider counted in dwell; CV pooled over all gaps (manuscript Eq. 3.15,
old value kept as cv_stop_mean); capacity 55 (NTD 2021); one random stream per source (`simulator/seeds.py`).
