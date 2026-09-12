"""
=============================================================================
 STEP 1 OF 5  --  ROUTE SELECTION AUDIT  (Route 801 vs Route 803)
=============================================================================

WHAT THIS STEP ANSWERS
    "Why Route 801 and not Route 803?"  and  "Where do the funnel numbers on
    the Data Cleaning slide come from?"

WHAT IT DOES
    Reads our archived snapshot in chunks -- all 9,197,694 rows -- applying the
    six cleaning rules and counting how many records survive each one. The rows
    that survive all six become one DataFrame, which pandas then groups by
    route to produce every statistic.

    No network. See common.py for why.

THE FOUR FUNNEL LEVELS, applied cumulatively to each row:

    level 1   route is 801 or 803                        -> all_route_records
    level 2   + route_id = current_route_id              -> matching_current_route_records
    level 3   + import_error = 0 and import_trip_error=0 -> error_free_matching_route_records
    level 4   + bs_id <> 0 and direction in ('4','6')    -> clean_stop_events

    Those four numbers are the bars on the cleaning-funnel slide.

WHY CHUNKS
    The raw file is 3.7 GB -- far too big to load at once. pandas reads it a
    million rows at a time; we filter each chunk and keep only the survivors.
    The clean set is about 832,000 rows, which fits in memory comfortably.

INPUTS   data/raw/capmetro/APC_Raw_..._full.csv          the archived snapshot
         data/audit/texas_capmetro/socrata_metadata.json archived portal metadata
         config/texas_capmetro_801.json

OUTPUTS  data/audit/texas_capmetro/route_selection_audit.json
         data/audit/texas_capmetro/ROUTE_SELECTION_EVIDENCE.md

RUN      python scripts/pipeline/01_audit_routes.py
=============================================================================
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR, RAW_FULL_SNAPSHOT, ROOT, UTC,
    clean_masks, clean_where, ensure_dirs, load_config, require_file, sha256_file,
    write_json, write_text,
)


# Only these columns are needed for the route comparison. Reading 19 of 47
# columns instead of all of them roughly halves the time and memory.
NEEDED_COLUMNS = [
    "route_id", "current_route_id", "import_error", "import_trip_error",
    "bs_id", "direction_code_id", "transit_date_time", "act_trip_start_time",
    "ext_trip_id", "vehicle_id", "ons", "offs", "max_load", "dwell_time",
    "rev_seconds", "rev_distance", "veh_lat", "veh_long", "quality_indicator",
]

CHUNK_SIZE = 1_000_000

# The rows of the evidence table, in order: (label shown, key in the stats dict)
ROWS = [
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
# PART A -- read the snapshot, count the funnel, keep the clean rows
# -----------------------------------------------------------------------------
def load_clean_rows(candidates: list[str]) -> tuple[pd.DataFrame, dict, int]:
    """Stream the snapshot in chunks. Returns (clean_df, funnel_levels, rows_read)."""
    require_file(RAW_FULL_SNAPSHOT, "the raw APC snapshot")

    levels = {r: {"all": 0, "matching": 0, "error_free": 0} for r in candidates}
    kept_chunks: list[pd.DataFrame] = []
    rows_read = 0

    reader = pd.read_csv(
        RAW_FULL_SNAPSHOT,
        usecols=NEEDED_COLUMNS,
        dtype=str,          # the source types every column as text; we parse later
        na_filter=False,    # keep blanks as "" rather than NaN, so the string
        chunksize=CHUNK_SIZE,  # comparisons below behave predictably
    )

    for chunk in reader:
        rows_read += len(chunk)

        # the six cleaning rules, as four cumulative masks (see common.py)
        on_route, matching, error_free, clean = clean_masks(chunk, candidates, ["4", "6"])

        # tally each funnel level per route
        for level_name, mask in (("all", on_route), ("matching", matching),
                                 ("error_free", error_free)):
            counts = chunk.loc[mask, "route_id"].value_counts()
            for route in candidates:
                levels[route][level_name] += int(counts.get(route, 0))

        kept_chunks.append(chunk[clean])
        print(f"  read {rows_read:,} raw rows...", flush=True)

    clean_df = pd.concat(kept_chunks, ignore_index=True)
    print(f"  read {rows_read:,} raw rows total, kept {len(clean_df):,} clean")
    return clean_df, levels, rows_read


# -----------------------------------------------------------------------------
# PART B -- turn the clean rows into per-route statistics
# -----------------------------------------------------------------------------
def summarize(clean_df: pd.DataFrame) -> dict[str, Any]:
    """Group the clean rows by route and compute every reported statistic."""
    df = clean_df.copy()

    # The source types everything as text, so parse the numeric columns
    # explicitly. Unparseable values become NaN and are skipped by mean/median.
    for column in ["ons", "offs", "max_load", "dwell_time",
                   "rev_seconds", "rev_distance", "veh_lat", "veh_long",
                   "quality_indicator"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # --- derived columns, computed once for the whole frame ----------------
    # service day = the first 8 characters, YYYYMMDD
    df["service_day"] = df["transit_date_time"].str[:8]

    # No single APC column is a reliable trip key, so a trip is identified by
    # (service day, ext_trip_id), falling back to start time + vehicle when
    # ext_trip_id is blank.
    fallback = df["act_trip_start_time"] + "|" + df["vehicle_id"]
    trip_id = df["ext_trip_id"].where(df["ext_trip_id"] != "", fallback)
    df["trip_key"] = df["service_day"] + "|" + trip_id

    # a segment is usable only with BOTH positive time and positive distance
    df["usable_segment"] = (df["rev_seconds"] > 0) & (df["rev_distance"] > 0)

    # good GPS = real coordinates and a fix-quality code of 3 to 6
    df["good_gps"] = (
        df["veh_lat"].notna() & (df["veh_lat"] != 0)
        & df["veh_long"].notna() & (df["veh_long"] != 0)
        & df["quality_indicator"].between(3, 6)
    )

    output: dict[str, Any] = {}
    for route, rows in df.groupby("route_id", sort=True):
        record_count = len(rows)
        good_gps = int(rows["good_gps"].sum())

        output[route] = {
            "clean_stop_events": record_count,
            "service_days": int(rows["service_day"].nunique()),
            "distinct_trip_day_pairs": int(rows["trip_key"].nunique()),
            "boardings": int(rows["ons"].fillna(0).sum()),
            "alightings": int(rows["offs"].fillna(0).sum()),
            "mean_reported_max_load": round(float(rows["max_load"].mean()), 3),
            "median_dwell_seconds": round(float(rows["dwell_time"].median()), 3),
            "usable_positive_time_distance_segments": int(rows["usable_segment"].sum()),
            "gps_high_quality_records": good_gps,
            "gps_high_quality_percent": round(100 * good_gps / record_count, 3),
            "distinct_stops_by_direction": {
                direction: int(group["bs_id"].nunique())
                for direction, group in rows.groupby("direction_code_id", sort=True)
            },
            "direction_summary": {
                direction: {
                    "clean_stop_events": len(group),
                    "boardings": int(group["ons"].fillna(0).sum()),
                    "distinct_trip_day_pairs": int(group["trip_key"].nunique()),
                }
                for direction, group in rows.groupby("direction_code_id", sort=True)
            },
        }
    return output


# -----------------------------------------------------------------------------
# PART C -- write the evidence
# -----------------------------------------------------------------------------
def percent_advantage(primary: dict, secondary: dict, key: str) -> float:
    """How much bigger route 801's value is than route 803's, as a percentage."""
    return round(100 * (primary[key] - secondary[key]) / secondary[key], 2)


def build_evidence(
    config: dict[str, Any], routes: dict[str, Any], source: dict[str, Any]
) -> dict[str, Any]:
    candidates = list(config["study"]["candidate_routes"])

    # Dataset facts come from the archived portal metadata already on disk.
    metadata_path = AUDIT_DIR / "socrata_metadata.json"
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.exists() else {}
    )

    primary, secondary = routes["801"], routes["803"]

    return {
        "generated_utc": datetime.now(UTC).isoformat(),
        "dataset": {
            "name": metadata.get("name"),
            "socrata_id": config["apc"]["socrata_id"],
            "column_count": len(metadata.get("columns", [])),
            "landing_page": "https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9",
        },
        "clean_definition": clean_where(candidates, ["4", "6"]),
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
                percent_advantage(primary, secondary, "clean_stop_events"),
            "boarding_advantage_percent_over_803":
                percent_advantage(primary, secondary, "boardings"),
            "usable_segment_advantage_percent_over_803":
                percent_advantage(primary, secondary, "usable_positive_time_distance_segments"),
            "interpretation_limit": "The selection maximizes empirical coverage; it is not a claim that Route 801 has better or worse service.",
        },
    }


def write_evidence_markdown(evidence: dict[str, Any]) -> None:
    """The same decision, as a table a human can read."""
    routes = evidence["routes"]
    # Built by hand rather than DataFrame.to_markdown(), which needs the
    # optional `tabulate` package and formats the table differently.
    table = ["| Metric | Route 801 | Route 803 |", "|---|---:|---:|"]
    table += [
        f"| {label} | {routes['801'][key]:,} | {routes['803'][key]:,} |"
        for label, key in ROWS
    ]

    sel = evidence["selection"]
    write_text(
        AUDIT_DIR / "ROUTE_SELECTION_EVIDENCE.md",
        "\n".join([
            "# Reproduced Route 801 selection audit",
            "",
            f"Generated at `{evidence['generated_utc']}` by {evidence['source']['method']}.",
            "",
            *table,
            "",
            "## Decision",
            "",
            sel["reason"],
            "",
            f"Route 801 has {sel['clean_event_advantage_percent_over_803']}% more clean stop events, "
            f"{sel['boarding_advantage_percent_over_803']}% more recorded boardings, and "
            f"{sel['usable_segment_advantage_percent_over_803']}% more usable positive-time/distance segments than Route 803.",
            "This justifies Route 801 as the primary case by data coverage, not by a claim about service quality.",
            "",
            "Direction code 6 remains provisional code-only. A compass-direction name is blocked until a checksum-verified 2021 GTFS snapshot is obtained.",
        ]),
    )



def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    ensure_dirs()
    config = load_config()
    candidates = list(config["study"]["candidate_routes"])

    print(f"Reading {RAW_FULL_SNAPSHOT.name} (no network).")
    clean_df, levels, rows_read = load_clean_rows(candidates)

    routes = summarize(clean_df)
    for route in candidates:
        routes[route]["all_route_records"] = levels[route]["all"]
        routes[route]["matching_current_route_records"] = levels[route]["matching"]
        routes[route]["error_free_matching_route_records"] = levels[route]["error_free"]

    source = {
        "method": "local extraction from the archived snapshot (no network)",
        "path": RAW_FULL_SNAPSHOT.relative_to(ROOT).as_posix(),
        "raw_rows_read": rows_read,
        "sha256": sha256_file(RAW_FULL_SNAPSHOT),
    }

    evidence = build_evidence(config, routes, source)
    write_json(AUDIT_DIR / "route_selection_audit.json", evidence)
    write_evidence_markdown(evidence)

    print("\nStep 1 complete.")
    for route in candidates:
        r = evidence["routes"][route]
        print(f"  Route {route}: all {r['all_route_records']:,} -> "
              f"matching {r['matching_current_route_records']:,} -> "
              f"error-free {r['error_free_matching_route_records']:,} -> "
              f"clean {r['clean_stop_events']:,}")
    print(f"  Selected: Route {evidence['selection']['primary_route']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
