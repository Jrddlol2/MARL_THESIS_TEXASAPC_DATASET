"""
=============================================================================
 BRIDGE  --  turn 229,421 cleaned stop events into 29 per-stop averages
=============================================================================

This is where the DATA half of the project meets the SIMULATION half.

    scripts/pipeline/   produced the cleaned study set
            |
            v
    THIS SCRIPT         collapses it to one row per stop
            |
            v
    starter/            builds and calibrates the SUMO corridor from those rows

WHAT IT PRODUCES
    starter/sim_inputs/stops.csv -- 29 rows, one per stop:

        seq              median observed position along the corridor
        mean_boardings   average passengers boarding per bus visit
        mean_alightings  average passengers alighting per bus visit
        dwell_s          median seconds stopped at the stop
        run_s            median seconds running to the NEXT stop
        dist_mi          median distance to the next stop

    Those six numbers per stop are the entire empirical basis of the simulator.

THE ONE CALCULATION THAT MATTERS
        run_seconds = rev_seconds - dwell_time

    rev_seconds is recorded door-open to door-open, so it ALREADY contains that
    stop's dwell. Dwell is modelled separately in the simulator, so subtracting
    prevents counting it twice. This is the number calibration targets.

WHY THE CLEANING RULES APPEAR AGAIN HERE
    This script re-applies the same six rules as scripts/pipeline, rather than
    reading that pipeline's output, ON PURPOSE. Two independent implementations
    landing on the same 229,421 rows is a cross-check: if they ever disagree,
    something is wrong and we want to know.

    The pipeline's version is the canonical one for anything quoted in the
    manuscript (see scripts/pipeline/common.py :: clean_masks).

LIMITATION -- POINT VALUES ONLY
    This produces ONE number per stop. methods.tex Stage 2 describes per-(stop,
    time-of-day, day-type) DISTRIBUTIONS with mu, sigma and CV. Those are MSA2
    work; this is the mean/median simplification used so far.

RUN  (from anywhere -- paths are repo-relative)
     python starter/scripts/extract_sim_inputs.py
=============================================================================
"""

from pathlib import Path

import pandas as pd

# Repo-relative so this runs on any machine. parents[2] because this file sits
# at <repo>/starter/scripts/extract_sim_inputs.py
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "capmetro" / "APC_Raw_July_2021_December_2021_full.csv"
OUT_DIR = ROOT / "starter" / "sim_inputs"

# The 13 columns this script needs, out of the 47 in the raw file.
NEEDED = [
    "route_id", "current_route_id", "import_error", "import_trip_error",
    "bs_id", "direction_code_id", "actual_sequence", "ons", "offs",
    "dwell_time", "rev_seconds", "rev_distance", "transit_date_time",
]

if not RAW.exists():
    raise SystemExit(
        f"\nMissing the raw APC snapshot:\n    {RAW}\n\n"
        "See the 'Getting the data' section of the repository README.\n"
    )

OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- read the 3.7 GB file a million rows at a time, keeping the clean ones ---
# dtype=str: read everything as text.  na_filter=False: blanks stay "" (not NaN).
clean_pieces = []
raw_row_count = 0
for chunk in pd.read_csv(RAW, usecols=NEEDED, dtype=str, chunksize=1_000_000,
                         na_filter=False):
    raw_row_count = raw_row_count + len(chunk)
    keep = (
        (chunk["route_id"] == "801")                           # 1. the route
        & (chunk["route_id"] == chunk["current_route_id"])     # 2. not reassigned
        & (chunk["import_error"] == "0")                       # 3. record ok
        & (chunk["import_trip_error"] == "0")                  # 4. trip ok
        & (chunk["bs_id"] != "0")                              # 5. a real stop
        & (chunk["direction_code_id"] == "6")                  # 6. the direction
    )
    clean_pieces.append(chunk[keep])

# glue the clean pieces back into one table
df = pd.concat(clean_pieces, ignore_index=True)
print(f"raw {raw_row_count:,} -> dir-6 clean {len(df):,} (expect 229,421)")

# ---- parse the numeric columns (the source types everything as text) --------
for column in ["actual_sequence", "ons", "offs", "dwell_time",
               "rev_seconds", "rev_distance"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# rev_seconds is open-to-open, so net out this stop's dwell (see header)
df["run_seconds"] = (df["rev_seconds"] - df["dwell_time"]).clip(lower=0)

# ---- one row per stop -------------------------------------------------------
# groupby("bs_id") puts all rows of the same stop together; agg() then makes one
# summary number per column, written as   new_name=(source_column, "how").
# median for times and distance (not pulled by extreme values), mean for demand.
stops = (
    df.groupby("bs_id")
      .agg(
          seq=("actual_sequence", "median"),
          mean_boardings=("ons", "mean"),
          mean_alightings=("offs", "mean"),
          dwell_s=("dwell_time", "median"),
          run_s=("run_seconds", "median"),
          dist_mi=("rev_distance", "median"),   # NOTE: rev_distance is MILES
      )
      .sort_values("seq")
      .round(2)
)

stops.to_csv(OUT_DIR / "stops.csv")
print(f"wrote {OUT_DIR / 'stops.csv'} -- {len(stops)} stops")
