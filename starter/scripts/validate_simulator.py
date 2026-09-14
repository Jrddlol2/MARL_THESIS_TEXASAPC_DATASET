"""
=============================================================================
 CHECK: DOES THE SIMULATOR BUNCH LIKE REAL BUSES?   (Week 2, item 6)
=============================================================================

WHAT IT DOES
    Calibration only checks running time. This checks BUNCHING -- the thing
    the thesis measures -- on an ordinary weekday with no controller:

      observed   headway CV at every stop, weekday 07:00-18:00, on the held-out
                 TEST days, using only gaps between buses scheduled one headway
                 apart (from scripts/fit_variability.py)
      simulated  No-Control, ordinary day (D + T), same stops, many seeds

    Both are "per day, per stop" CVs, averaged.

    It also repeats the load check (riders on board vs APC max_load, weekday
    07:00-18:00), and checks how often buses serve each stop (APC writes a
    record only when the doors open) against the simulator's stop-or-pass rule.

OUTPUT   results/validation/headway_cv_sim_vs_observed.csv
         results/validation/load_profile_sim_vs_observed.csv
         results/validation/stop_service_sim_vs_observed.csv
         results/figures/headway_cv_validation.{pdf,png}

RUN      python scripts/validate_simulator.py [seeds] [jobs]    (from starter/)
=============================================================================
"""

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
import corridor_sim as C

if len(sys.argv) > 1:
    NUM_SEEDS = int(sys.argv[1])
else:
    NUM_SEEDS = 30
if len(sys.argv) > 2:
    JOBS = int(sys.argv[2])
else:
    JOBS = 10

APC_FILE = os.path.join("..", "data", "raw", "capmetro", "route_801_direction_6_clean.csv")


def run_one(seed):
    result = C.simulate(C.BASELINES["NC"], seed=seed, T=True, control_stops=C.CONTROL_STOPS)
    return seed, result["headway_cv_by_stop"], result["load_leaving"], result["rides_unfinished"], result["stop_served_share"]


def main():
    os.makedirs("results/validation", exist_ok=True)

    # ---- simulated ------------------------------------------------------------
    cv_rows = []
    load_rows = []
    served_rows = []
    with ProcessPoolExecutor(max_workers=JOBS) as pool:
        for seed, cv_by_stop, load_leaving, unfinished, served in pool.map(run_one, range(NUM_SEEDS)):
            cv_rows.append(cv_by_stop)
            load_rows.append(load_leaving)
            served_rows.append(served)
            if unfinished:
                print(f"  seed {seed}: {unfinished} unfinished rides")
    simulated_cv = np.nanmean(np.array(cv_rows), axis=0)
    simulated_load = np.nanmean(np.array(load_rows), axis=0)
    simulated_served = np.nanmean(np.array(served_rows), axis=0)

    # ---- observed headway CV ------------------------------------------------------
    observed = pd.read_csv("results/validation/observed_headway_cv.csv")
    observed_by_stop = observed.groupby("stop_index")["cv"].mean()

    table = pd.DataFrame({
        "stop_index": range(C.NUM_STOPS),
        "bs_id": C.STOPS,
        "observed_cv": [round(float(observed_by_stop.get(i, np.nan)), 3) for i in range(C.NUM_STOPS)],
        "simulated_cv": np.round(simulated_cv, 3),
    })
    table["difference"] = (table["simulated_cv"] - table["observed_cv"]).round(3)
    table.to_csv("results/validation/headway_cv_sim_vs_observed.csv", index=False)

    interior = table[table["stop_index"] >= 1]
    summary = {
        "seeds": NUM_SEEDS,
        "observed_mean_cv_stops_1_26": round(float(interior["observed_cv"].mean()), 3),
        "simulated_mean_cv_stops_1_26": round(float(interior["simulated_cv"].mean()), 3),
        "observed_cv_first_stop": float(table.loc[0, "observed_cv"]),
        "simulated_cv_first_stop": float(table.loc[0, "simulated_cv"]),
        "rmse_by_stop": round(float(np.sqrt(np.mean(interior["difference"] ** 2))), 3),
        "correlation_by_stop": round(float(np.corrcoef(interior["observed_cv"], interior["simulated_cv"])[0, 1]), 3),
    }

    # ---- loads, weekday 07-18 --------------------------------------------------------
    apc = pd.read_csv(APC_FILE, usecols=["bs_id", "max_load", "day_type_vs", "open_date_time"], dtype=str)
    apc["hour"] = apc["open_date_time"].str[8:10].astype(int)
    apc = apc[(apc["day_type_vs"] == "1") & (apc["hour"] >= 7) & (apc["hour"] < 18)]
    apc["max_load"] = pd.to_numeric(apc["max_load"], errors="coerce")
    apc_load = apc.groupby(apc["bs_id"].astype(int))["max_load"].mean()
    loads = pd.DataFrame({
        "stop_index": range(C.NUM_STOPS - 1),
        "bs_id": C.STOPS[:-1],
        "apc_mean_max_load": [round(float(apc_load.loc[int(s)]), 2) for s in C.STOPS[:-1]],
        "simulated_load_leaving": np.round(simulated_load[:-1], 2),
    })
    loads.to_csv("results/validation/load_profile_sim_vs_observed.csv", index=False)
    error = loads["simulated_load_leaving"] - loads["apc_mean_max_load"]
    summary["load_rmse_riders"] = round(float(np.sqrt(np.mean(error ** 2))), 2)
    summary["load_correlation"] = round(float(np.corrcoef(loads["simulated_load_leaving"], loads["apc_mean_max_load"])[0, 1]), 3)

    # ---- how often each stop is served (test days) -----------------------------------------
    fitted = pd.read_csv("sim_inputs/fitted/stop_params.csv")
    fitted = fitted[fitted["period"] == "ALL"].set_index("bs_id")
    service = pd.DataFrame({
        "stop_index": range(C.NUM_STOPS),
        "bs_id": C.STOPS,
        "always_served_in_simulator": [i in C.ALWAYS_SERVED for i in range(C.NUM_STOPS)],
        "observed_served_share": [float(fitted.loc[int(s), "served_share_test"]) for s in C.STOPS],
        "simulated_served_share": np.round(simulated_served, 3),
    })
    service.to_csv("results/validation/stop_service_sim_vs_observed.csv", index=False)
    free = service[~service["always_served_in_simulator"]]
    summary["served_share_observed_mean_free_stops"] = round(float(free["observed_served_share"].mean()), 3)
    summary["served_share_simulated_mean_free_stops"] = round(float(free["simulated_served_share"].mean()), 3)
    summary["served_share_correlation_free_stops"] = round(float(np.corrcoef(free["observed_served_share"], free["simulated_served_share"])[0, 1]), 3)
    print(service.to_string(index=False))

    with open("results/validation/simulator_validation_summary.json", "w") as file:
        json.dump(summary, file, indent=2)
    print(table.to_string(index=False))
    print(json.dumps(summary, indent=2))

    # ---- figure ------------------------------------------------------------------------
    import _figstyle as S
    S.apply()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=S.WIDE)
    ax.plot(table["stop_index"], table["observed_cv"], color=S.GREY, marker="o", label="Observed (test days, weekday 07-18)")
    ax.plot(table["stop_index"], table["simulated_cv"], color=S.BLUE, marker="s", label=f"Simulated No-Control, D+T ({NUM_SEEDS} seeds)")
    ax.set_xticks(table["stop_index"])
    ax.set_xticklabels(table["bs_id"], rotation=90)
    ax.set_xlabel("Stop (bs_id), in driving order")
    ax.set_ylabel("Headway CV")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left")
    S.save(fig, "headway_cv_validation")


if __name__ == "__main__":
    main()
