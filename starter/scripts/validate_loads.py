"""
=============================================================================
 CHECK: ARE THE SIMULATED BUS LOADS REALISTIC?  (risk register R4)
=============================================================================

WHAT IT DOES
    Runs the simulator (No-Control, dwell + traffic) on a few seeds and records
    how many riders are on board as each bus leaves each stop. Compares that
    with the real APC data: the mean `max_load` recorded at each stop
    (the most riders on board on the segment after that stop).

    Both use the same basis as the simulator's demand: averages per recorded
    stop event (a record exists only when the doors opened).

OUTPUT   results/load_profile_validation.csv
         results/figures/load_profile_validation.{pdf,png}

RUN      python scripts/validate_loads.py [seeds]      (from starter/, ~1 min for 5 seeds)
=============================================================================
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
import corridor_sim as C
import _figstyle as S

if len(sys.argv) > 1:
    NUM_SEEDS = int(sys.argv[1])
else:
    NUM_SEEDS = 5

APC_FILE = os.path.join("..", "data", "raw", "capmetro", "route_801_direction_6_clean.csv")

# ---- real loads from the APC data ---------------------------------------------------------
apc = pd.read_csv(APC_FILE, usecols=["bs_id", "max_load"])
apc["max_load"] = pd.to_numeric(apc["max_load"], errors="coerce")
apc_mean_load = apc.groupby("bs_id")["max_load"].mean()

# ---- simulated loads --------------------------------------------------------------------------
per_seed = []
for seed in range(NUM_SEEDS):
    result = C.simulate(C.BASELINES["NC"], seed=seed, T=True, control_stops=C.CONTROL_STOPS)
    per_seed.append(result["load_leaving"])
    print(f"seed {seed}: rides unfinished = {result['rides_unfinished']}")
simulated = np.nanmean(np.array(per_seed), axis=0)

# ---- table (the last stop is left out: everyone gets off there in the model,
#      while real buses continue to the Southpark Meadows terminal) ------------------------------
rows = []
for i in range(C.NUM_STOPS - 1):
    stop = C.STOPS[i]
    rows.append({
        "index": i,
        "bs_id": stop,
        "apc_mean_max_load": round(float(apc_mean_load.loc[int(stop)]), 2),
        "expected_load_leaving": round(C.EXPECTED_LOAD_LEAVING[i], 2),
        "simulated_load_leaving": round(float(simulated[i]), 2),
    })
table = pd.DataFrame(rows)
table["sim_minus_apc"] = (table["simulated_load_leaving"] - table["apc_mean_max_load"]).round(2)
os.makedirs("results", exist_ok=True)
table.to_csv("results/load_profile_validation.csv", index=False)

error = table["simulated_load_leaving"] - table["apc_mean_max_load"]
rmse = float(np.sqrt(np.mean(error ** 2)))
correlation = float(np.corrcoef(table["simulated_load_leaving"], table["apc_mean_max_load"])[0, 1])
print(table.to_string(index=False))
print(f"\npeak simulated {table['simulated_load_leaving'].max():.1f} vs APC {table['apc_mean_max_load'].max():.1f}; "
      f"RMSE {rmse:.2f} riders; correlation {correlation:.3f}")

# ---- figure -----------------------------------------------------------------------------------------
S.apply()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=S.WIDE)
x = table["index"]
ax.plot(x, table["apc_mean_max_load"], color=S.GREY, marker="o", label="APC mean max_load (observed)")
ax.plot(x, table["simulated_load_leaving"], color=S.BLUE, marker="s", label=f"Simulated, No-Control, {NUM_SEEDS} seeds")
ax.set_xticks(x)
ax.set_xticklabels(table["bs_id"], rotation=90)
ax.set_xlabel("Stop (bs_id), in driving order")
ax.set_ylabel("Riders on board leaving stop")
ax.set_ylim(bottom=0)
ax.legend(loc="upper right")
S.save(fig, "load_profile_validation")
