"""Stream the 3.5 GB raw APC CSV -> dir-6 clean subset (229,421 rows) -> sim_inputs/stops.csv.
Reproduces the pipeline's six cleaning filters. Point values only (no distributions)."""
import pandas as pd, os
RAW = r"C:\Users\jared\Desktop\THESIS\APC_Raw_July_2021_-_December_2021_20260824.csv"  # <-- set path
OUT = "sim_inputs"; os.makedirs(OUT, exist_ok=True); os.makedirs("data", exist_ok=True)
need = ["route_id","current_route_id","import_error","import_trip_error","bs_id","direction_code_id",
        "actual_sequence","ons","offs","dwell_time","rev_seconds","rev_distance","transit_date_time"]
parts, n_raw = [], 0
for ch in pd.read_csv(RAW, usecols=need, dtype=str, chunksize=1_000_000, na_filter=False):
    n_raw += len(ch)
    m = ((ch["route_id"]=="801") & (ch["route_id"]==ch["current_route_id"]) &
         (ch["import_error"]=="0") & (ch["import_trip_error"]=="0") &
         (ch["bs_id"]!="0") & (ch["direction_code_id"]=="6"))
    parts.append(ch[m])
df = pd.concat(parts, ignore_index=True)
print(f"raw {n_raw:,} -> dir-6 clean {len(df):,} (expect 229,421)")
df.to_csv("data/route_801_direction_6_clean.csv", index=False)      # cache the subset
for c in ["actual_sequence","ons","offs","dwell_time","rev_seconds","rev_distance"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["run_seconds"] = (df["rev_seconds"] - df["dwell_time"]).clip(lower=0)   # segment running time
stops = (df.groupby("bs_id")
           .agg(seq=("actual_sequence","median"), mean_boardings=("ons","mean"),
                mean_alightings=("offs","mean"), dwell_s=("dwell_time","median"),
                run_s=("run_seconds","median"), dist_mi=("rev_distance","median"))  # NOTE: rev_distance is MILES
           .sort_values("seq").round(2))
stops.to_csv(f"{OUT}/stops.csv"); print("wrote sim_inputs/stops.csv", len(stops), "stops")
