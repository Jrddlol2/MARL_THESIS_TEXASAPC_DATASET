"""
=============================================================================
 EVIDENCE  --  WHY ROUTE 801 AND NOT ROUTE 803?
=============================================================================

WHAT THIS ANSWERS
    1. "Why did you pick Route 801 instead of Route 803?"
    2. "Where do the numbers on the cleaning-funnel slide come from?"

    This is evidence, not a processing step: nothing else reads its output.

WHAT IT DOES
    Part A  reads all 9,197,694 raw rows (in chunks), applies the six cleaning
            rules, and counts how many rows of each route survive each stage.
    Part B  takes the fully clean rows and computes statistics per route
            (boardings, service days, dwell time, GPS quality, ...).
    Part C  writes a JSON file and a readable markdown table.

THE FOUR FUNNEL STAGES
    stage 1   route is 801 or 803                         all_route_records
    stage 2   + route_id = current_route_id               matching_current_route_records
    stage 3   + import_error = 0 and import_trip_error=0  error_free_matching_route_records
    stage 4   + bs_id <> 0 and direction is 4 or 6        clean_stop_events

INPUT    data/raw/capmetro/APC_Raw_July_2021_December_2021_full.csv
         data/audit/texas_capmetro/socrata_metadata.json   (saved portal info)
OUTPUT   data/audit/texas_capmetro/route_selection_audit.json
         data/audit/texas_capmetro/ROUTE_SELECTION_EVIDENCE.md

RUN      python scripts/pipeline/audit_route_selection.py   (about 45 seconds)
=============================================================================
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

# We only need 19 of the 47 columns. Reading fewer columns is faster.
NEEDED_COLUMNS = [
    "route_id", "current_route_id", "import_error", "import_trip_error",
    "bs_id", "direction_code_id", "transit_date_time", "act_trip_start_time",
    "ext_trip_id", "vehicle_id", "ons", "offs", "max_load", "dwell_time",
    "rev_seconds", "rev_distance", "veh_lat", "veh_long", "quality_indicator",
]

ROWS_PER_CHUNK = 1_000_000

# Rows of the markdown table: (label shown in the table, key in the statistics)
TABLE_ROWS = [
    ("All route records", "all_route_records"),
    ("Matching current-route records", "matching_current_route_records"),
    ("Error-free matching-route records", "error_free_matching_route_records"),
    ("Clean stop events (directions 4 and 6)", "clean_stop_events"),
    ("Service-day codes", "service_days"),
    ("Distinct trip-day pairs", "distinct_trip_day_pairs"),
    ("Boardings", "boardings"),
    ("Mean reported max load", "mean_reported_max_load"),
    ("Median dwell (s)", "median_dwell_seconds"),
    ("Positive time-and-distance segments", "usable_positive_time_distance_segments"),
    ("High-quality GPS (%)", "gps_high_quality_percent"),
]


# -----------------------------------------------------------------------------
# PART A -- read the raw file, count the funnel, keep the clean rows
# -----------------------------------------------------------------------------
def read_and_count(candidate_routes):
    """Returns (clean rows as one table, funnel counts per route, rows read)."""
    common.require_file(common.RAW_FULL_SNAPSHOT, "the raw APC snapshot")

    # funnel[route]["all" / "matching" / "error_free"] = number of rows
    funnel = {}
    for route in candidate_routes:
        funnel[route] = {"all": 0, "matching": 0, "error_free": 0}

    clean_pieces = []
    rows_read = 0

    chunks = pd.read_csv(common.RAW_FULL_SNAPSHOT, usecols=NEEDED_COLUMNS, dtype=str,
                         na_filter=False, chunksize=ROWS_PER_CHUNK)

    for chunk in chunks:
        rows_read = rows_read + len(chunk)

        # The six cleaning rules, as four stages (see common.py).
        on_route, matching, error_free, clean = common.clean_masks(chunk, candidate_routes, ["4", "6"])

        # Count how many rows of each route pass each stage.
        # (mask & is_this_route) is True only for rows passing the stage AND on that route.
        for route in candidate_routes:
            is_this_route = chunk["route_id"] == route
            funnel[route]["all"] += int((on_route & is_this_route).sum())
            funnel[route]["matching"] += int((matching & is_this_route).sum())
            funnel[route]["error_free"] += int((error_free & is_this_route).sum())

        clean_pieces.append(chunk[clean])
        print(f"  read {rows_read:,} raw rows...", flush=True)

    clean_rows = pd.concat(clean_pieces, ignore_index=True)
    print(f"  read {rows_read:,} raw rows total, kept {len(clean_rows):,} clean")
    return clean_rows, funnel, rows_read


# -----------------------------------------------------------------------------
# PART B -- statistics per route
# -----------------------------------------------------------------------------
def route_statistics(clean_rows):
    """Compute every reported number, separately for each route."""
    table = clean_rows.copy()

    # Everything was read as text, so turn the number columns into numbers.
    # Anything that is not a valid number becomes NaN (empty) and is skipped.
    for column in ["ons", "offs", "max_load", "dwell_time", "rev_seconds",
                   "rev_distance", "veh_lat", "veh_long", "quality_indicator"]:
        table[column] = pd.to_numeric(table[column], errors="coerce")

    # Service day = first 8 characters of the timestamp, e.g. "20210701".
    table["service_day"] = table["transit_date_time"].str[:8]

    # A trip is "service day + ext_trip_id". If ext_trip_id is blank, use
    # "trip start time + vehicle id" instead.
    backup_trip_id = table["act_trip_start_time"] + "|" + table["vehicle_id"]
    trip_id = table["ext_trip_id"].where(table["ext_trip_id"] != "", backup_trip_id)
    table["trip_key"] = table["service_day"] + "|" + trip_id

    # A segment is usable only if BOTH its time and its distance are positive.
    table["usable_segment"] = (table["rev_seconds"] > 0) & (table["rev_distance"] > 0)

    # Good GPS = real (non-zero) coordinates and a quality code from 3 to 6.
    table["good_gps"] = (
        table["veh_lat"].notna() & (table["veh_lat"] != 0)
        & table["veh_long"].notna() & (table["veh_long"] != 0)
        & table["quality_indicator"].between(3, 6)
    )

    statistics = {}
    for route, rows in table.groupby("route_id", sort=True):
        good_gps_count = int(rows["good_gps"].sum())

        stops_per_direction = {}
        per_direction = {}
        for direction, group in rows.groupby("direction_code_id", sort=True):
            stops_per_direction[direction] = int(group["bs_id"].nunique())
            per_direction[direction] = {
                "clean_stop_events": len(group),
                "boardings": int(group["ons"].fillna(0).sum()),
                "distinct_trip_day_pairs": int(group["trip_key"].nunique()),
            }

        statistics[route] = {
            "clean_stop_events": len(rows),
            "service_days": int(rows["service_day"].nunique()),
            "distinct_trip_day_pairs": int(rows["trip_key"].nunique()),
            "boardings": int(rows["ons"].fillna(0).sum()),
            "alightings": int(rows["offs"].fillna(0).sum()),
            "mean_reported_max_load": round(float(rows["max_load"].mean()), 3),
            "median_dwell_seconds": round(float(rows["dwell_time"].median()), 3),
            "usable_positive_time_distance_segments": int(rows["usable_segment"].sum()),
            "gps_high_quality_records": good_gps_count,
            "gps_high_quality_percent": round(100 * good_gps_count / len(rows), 3),
            "distinct_stops_by_direction": stops_per_direction,
            "direction_summary": per_direction,
        }
    return statistics


# -----------------------------------------------------------------------------
# PART C -- write the evidence files
# -----------------------------------------------------------------------------
def percent_more(route_801, route_803, key):
    """How much bigger Route 801's number is than Route 803's, in percent."""
    return round(100 * (route_801[key] - route_803[key]) / route_803[key], 2)


def build_evidence(config, routes, source):
    candidate_routes = list(config["study"]["candidate_routes"])

    # Dataset name and column count come from the saved portal metadata.
    metadata_file = common.AUDIT_DIR / "socrata_metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    else:
        metadata = {}

    route_801 = routes["801"]
    route_803 = routes["803"]

    return {
        "generated_utc": datetime.now(common.UTC).isoformat(),
        "dataset": {
            "name": metadata.get("name"),
            "socrata_id": config["apc"]["socrata_id"],
            "column_count": len(metadata.get("columns", [])),
            "landing_page": "https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9",
        },
        "clean_definition": common.clean_where(candidate_routes, ["4", "6"]),
        "gps_high_quality_definition": "nonzero coordinates and quality_indicator in {3,4,5,6}",
        "source": source,
        "routes": routes,
        "selection": {
            "primary_route": "801",
            "reason": (
                "Under identical cleaning rules, Route 801 provides larger clean stop-event, "
                "boarding, and usable-segment samples despite fewer distinct trip-day pairs, "
                "while retaining comparable GPS quality."
            ),
            "clean_event_advantage_percent_over_803":
                percent_more(route_801, route_803, "clean_stop_events"),
            "boarding_advantage_percent_over_803":
                percent_more(route_801, route_803, "boardings"),
            "usable_segment_advantage_percent_over_803":
                percent_more(route_801, route_803, "usable_positive_time_distance_segments"),
            "interpretation_limit": "The selection maximizes empirical coverage; it is not a claim that Route 801 has better or worse service.",
        },
    }


def write_evidence_markdown(evidence):
    """Write the same decision as a table a person can read."""
    routes = evidence["routes"]
    selection = evidence["selection"]

    lines = []
    lines.append("# Reproduced Route 801 selection audit")
    lines.append("")
    lines.append(f"Generated at `{evidence['generated_utc']}` by {evidence['source']['method']}.")
    lines.append("")
    lines.append("| Metric | Route 801 | Route 803 |")
    lines.append("|---|---:|---:|")
    for label, key in TABLE_ROWS:
        lines.append(f"| {label} | {routes['801'][key]:,} | {routes['803'][key]:,} |")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(selection["reason"])
    lines.append("")
    lines.append(
        f"Route 801 has {selection['clean_event_advantage_percent_over_803']}% more clean stop events, "
        f"{selection['boarding_advantage_percent_over_803']}% more recorded boardings, and "
        f"{selection['usable_segment_advantage_percent_over_803']}% more usable positive-time/distance segments than Route 803."
    )
    lines.append("This justifies Route 801 as the primary case by data coverage, not by a claim about service quality.")
    lines.append("")
    lines.append("Direction code 6 remains provisional code-only. A compass-direction name is blocked until a checksum-verified 2021 GTFS snapshot is obtained.")

    common.write_text(common.AUDIT_DIR / "ROUTE_SELECTION_EVIDENCE.md", "\n".join(lines))


def main():
    common.ensure_dirs()
    config = common.load_config()
    candidate_routes = list(config["study"]["candidate_routes"])

    print(f"Reading {common.RAW_FULL_SNAPSHOT.name} (no network).")
    clean_rows, funnel, rows_read = read_and_count(candidate_routes)

    routes = route_statistics(clean_rows)
    for route in candidate_routes:
        routes[route]["all_route_records"] = funnel[route]["all"]
        routes[route]["matching_current_route_records"] = funnel[route]["matching"]
        routes[route]["error_free_matching_route_records"] = funnel[route]["error_free"]

    source = {
        "method": "local extraction from the archived snapshot (no network)",
        "path": common.RAW_FULL_SNAPSHOT.relative_to(common.ROOT).as_posix(),
        "raw_rows_read": rows_read,
        "sha256": common.sha256_file(common.RAW_FULL_SNAPSHOT),
    }

    evidence = build_evidence(config, routes, source)
    common.write_json(common.AUDIT_DIR / "route_selection_audit.json", evidence)
    write_evidence_markdown(evidence)

    print("\nRoute selection audit complete.")
    for route in candidate_routes:
        r = evidence["routes"][route]
        print(f"  Route {route}: all {r['all_route_records']:,} -> "
              f"matching {r['matching_current_route_records']:,} -> "
              f"error-free {r['error_free_matching_route_records']:,} -> "
              f"clean {r['clean_stop_events']:,}")
    print(f"  Selected: Route {evidence['selection']['primary_route']}")


if __name__ == "__main__":
    main()
