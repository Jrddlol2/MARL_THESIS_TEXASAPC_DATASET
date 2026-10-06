"""run_baseline.py -- the v2 baseline every disturbance study compares against.

  E1  clean run (no randomness), seed 0, NC / FH / EH
  E3  random riders + 10% travel-time noise, seeds 0-29, NC / FH / EH

Writes results/baseline_v2_runs.csv (same columns as MSA 2) and prints how long it took.
Run from this folder:   py run_baseline.py            (all CPU cores but one)
                        py run_baseline.py --jobs 2   (fewer cores)
"""
import csv
import os
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
if "SUMO_HOME" not in os.environ:
    sys.exit("SUMO_HOME is not set: reinstall SUMO with the SUMO_HOME option ticked")
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
sys.path.append(os.path.join(HERE, "simulator"))

import run as R  # noqa: E402
from controllers import CONTROLLERS  # noqa: E402

COLS = ["experiment", "controller", "setting", "seed", "cv", "cv_stop_mean", "wait_s",
        "hold_total_s", "travel_s", "unfinished"]


def one(task):
    exp, ctrl, seed = task
    if exp == "E1":
        res = R.simulate(CONTROLLERS[ctrl], seed=seed, random_arrivals=False, noise=0.0, label=f"E1{ctrl}")
        setting = "clean"
    else:
        res = R.simulate(CONTROLLERS[ctrl], seed=seed, random_arrivals=True, noise=0.10, label=f"E3{ctrl}")
        setting = "noise10"
    return {"experiment": exp, "controller": ctrl, "setting": setting, "seed": seed,
            **{k: res[k] for k in COLS[4:]}}


def main():
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else max(1, os.cpu_count() - 1)
    tasks = [("E1", c, 0) for c in CONTROLLERS] + [("E3", c, s) for c in CONTROLLERS for s in range(30)]
    t0 = time.time()
    with Pool(jobs) as pool:
        rows = pool.map(one, tasks)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "baseline_v2_runs.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    minutes = (time.time() - t0) / 60
    print(f"{len(rows)} runs on {jobs} cores in {minutes:.1f} min "
          f"({(time.time() - t0) * jobs / len(rows):.1f} s per run per core)")


if __name__ == "__main__":
    main()
