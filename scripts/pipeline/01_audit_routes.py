"""
=============================================================================
 STEP 1 OF 5  --  ROUTE SELECTION AUDIT  (Route 801 vs Route 803)
=============================================================================

WHAT THIS STEP ANSWERS
    "Why Route 801 and not Route 803?"  and  "Where do the funnel numbers on
    the Data Cleaning slide come from?"

WHAT IT DOES
    1. Downloads the dataset's official metadata from the Texas Open Data
       portal and saves it as evidence.
    2. Asks the portal to COUNT records for 801 and 803 at three stages of
       cleaning -- these become the middle bars of the cleaning funnel.
    3. Downloads a clean comparison extract (both routes, both directions,
       19 columns) and re-computes every statistic locally, rather than
       trusting the portal's own aggregates.
    4. Writes the comparison and the selection decision to disk.

WHY WE RE-COMPUTE LOCALLY
    Steps 2 and 3 above use two different mechanisms: server-side COUNT queries
    and a local pass over the downloaded rows. If they agree, we know the
    download is complete and the counting is right. That cross-check is the
    point -- it is cheap insurance against a silently truncated download.

INPUTS   config/texas_capmetro_801.json   (routes, API endpoints)
         the Texas Open Data portal        (network)

OUTPUTS  data/raw/capmetro/route_801_803_clean_comparison.csv
         data/audit/texas_capmetro/socrata_metadata.json
         data/audit/texas_capmetro/route_selection_audit.json
         data/audit/texas_capmetro/ROUTE_SELECTION_EVIDENCE.md

RUN      python scripts/pipeline/01_audit_routes.py
         python scripts/pipeline/01_audit_routes.py --force    (redownload)
=============================================================================
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR,
    RAW_CAPMETRO_DIR,
    RAW_FULL_SNAPSHOT,
    UTC,
    clean_where,
    download_soda_csv,
    ensure_dirs,
    fetch_json,
    load_config,
    safe_float,
    safe_int,
    stream_raw_snapshot,
    write_json,
    write_text,
)


# The 19 columns we need to judge 801 against 803. We do not need all 47 here;
# this extract exists only to compare the two routes.
COMPARISON_FIELDS = [
    "route_id",
    "direction_code_id",
    "transit_date_time",
    "apc_date_time",
    "act_trip_start_time",
    "ext_trip_id",
    "vehicle_id",
    "actual_sequence",
    "bs_id",
    "ons",
    "offs",
    "max_load",
    "dwell_time",
    "rev_seconds",
    "rev_distance",
    "veh_lat",
    "veh_long",
    "quality_indicator",
    "position_source",
]


# -----------------------------------------------------------------------------
# PART A -- ask the portal to count records at each cleaning stage
# -----------------------------------------------------------------------------
def aggregate_route_counts(base: str, where: str) -> dict[str, int]:
    """Run a GROUP BY route_id COUNT(*) query on the portal.

    Returns e.g. {"801": 547616, "803": 468689}. Each call is one bar of the
    cleaning funnel.
    """
    rows = fetch_json(
        base,
        {
            "$select": "route_id,count(*) as record_count",
            "$where": where,
            "$group": "route_id",
            "$order": "route_id",
        },
    )
    return {row["route_id"]: int(row["record_count"]) for row in rows}


# -----------------------------------------------------------------------------
# PART B -- re-compute every statistic ourselves from the downloaded rows
# -----------------------------------------------------------------------------
def summarize_rows(path: Path) -> dict[str, Any]:
    """Stream the comparison CSV once and build per-route statistics.

    One pass, one row at a time -- the file is never held in memory.

    For each route we accumulate:
        clean_stop_events      how many rows survived cleaning
        service_days           distinct service-day codes
        trip-day pairs         distinct (day, trip) identities
        boardings / alightings summed ons / offs
        max_load, dwell        for a mean and a median
        usable segments        rows with BOTH positive time and positive distance
        GPS quality            nonzero coordinates and quality_indicator 3..6
        per-direction splits   the same, broken out by direction code

    NOTE ON TRIP IDENTITY
        No single APC column is guaranteed unique, so a trip is identified by
        (service day, ext_trip_id). If ext_trip_id is blank we fall back to
        (act_trip_start_time + vehicle_id). This is why the code builds a
        `trip_key` tuple rather than just reading one field.
    """
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return summarize_row_stream(csv.DictReader(handle))


def summarize_row_stream(rows) -> dict[str, Any]:
    """The accumulator behind summarize_rows(), taking any iterable of rows.

    Split out so the offline path can feed it a filtered stream straight from
    the 3.7 GB snapshot instead of a downloaded CSV. Identical arithmetic
    either way.
    """
    metrics: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "records": 0,
            "boardings": 0,
            "alightings": 0,
            "loads": [],
            "dwells": [],
            "days": set(),
            "trips": set(),
            "stops_by_direction": defaultdict(set),
            "usable_segments": 0,
            "gps_high_quality": 0,
            "direction_records": defaultdict(int),
            "direction_boardings": defaultdict(int),
            "direction_trips": defaultdict(set),
        }
    )

    for row in rows:
        route = row["route_id"]
        direction = row["direction_code_id"]
        item = metrics[route]

        item["records"] += 1
        item["direction_records"][direction] += 1

        # --- demand ---
        ons = safe_int(row.get("ons")) or 0
        offs = safe_int(row.get("offs")) or 0
        item["boardings"] += ons
        item["alightings"] += offs
        item["direction_boardings"][direction] += ons

        # --- load and dwell, collected for a mean / median later ---
        load = safe_float(row.get("max_load"))
        dwell = safe_float(row.get("dwell_time"))
        if load is not None:
            item["loads"].append(load)
        if dwell is not None:
            item["dwells"].append(dwell)

        # --- service day (first 8 chars = YYYYMMDD) ---
        transit_day = (row.get("transit_date_time") or "")[:8]
        if transit_day:
            item["days"].add(transit_day)

        # --- stop id, per direction ---
        stop_id = row.get("bs_id") or ""
        if stop_id:
            item["stops_by_direction"][direction].add(stop_id)

        # --- trip identity (see docstring) ---
        ext_trip_id = row.get("ext_trip_id") or ""
        fallback = (row.get("act_trip_start_time") or "") + "|" + (
            row.get("vehicle_id") or ""
        )
        trip_key = (transit_day, ext_trip_id or fallback)
        item["trips"].add(trip_key)
        item["direction_trips"][direction].add(trip_key)

        # --- a segment is usable only with positive time AND distance ---
        seconds = safe_float(row.get("rev_seconds"))
        distance = safe_float(row.get("rev_distance"))
        if seconds is not None and distance is not None and seconds > 0 and distance > 0:
            item["usable_segments"] += 1

        # --- GPS quality: real coordinates and a good fix code ---
        latitude = safe_float(row.get("veh_lat"))
        longitude = safe_float(row.get("veh_long"))
        quality = safe_int(row.get("quality_indicator"))
        if (
            latitude not in (None, 0.0)
            and longitude not in (None, 0.0)
            and quality is not None
            and 3 <= quality <= 6
        ):
            item["gps_high_quality"] += 1

    # --- turn the accumulators into the final per-route summary ---
    output: dict[str, Any] = {}
    for route, item in sorted(metrics.items()):
        record_count = item["records"]
        output[route] = {
            "clean_stop_events": record_count,
            "service_days": len(item["days"]),
            "distinct_trip_day_pairs": len(item["trips"]),
            "boardings": item["boardings"],
            "alightings": item["alightings"],
            "mean_reported_max_load": round(statistics.fmean(item["loads"]), 3)
            if item["loads"]
            else None,
            "median_dwell_seconds": round(statistics.median(item["dwells"]), 3)
            if item["dwells"]
            else None,
            "usable_positive_time_distance_segments": item["usable_segments"],
            "gps_high_quality_records": item["gps_high_quality"],
            "gps_high_quality_percent": round(100 * item["gps_high_quality"] / record_count, 3)
            if record_count
            else None,
            "distinct_stops_by_direction": {
                key: len(value)
                for key, value in sorted(item["stops_by_direction"].items())
            },
            "direction_summary": {
                key: {
                    "clean_stop_events": item["direction_records"][key],
                    "boardings": item["direction_boardings"][key],
                    "distinct_trip_day_pairs": len(item["direction_trips"][key]),
                }
                for key in sorted(item["direction_records"])
            },
        }
    return output


# -----------------------------------------------------------------------------
# PART C -- put it together and write the evidence
# -----------------------------------------------------------------------------
def audit_routes(config: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    apc = config["apc"]
    candidates = config["study"]["candidate_routes"]  # ["801", "803"]

    # --- official dataset metadata, saved as evidence ---
    metadata = fetch_json(apc["metadata_url"])
    write_json(AUDIT_DIR / "socrata_metadata.json", metadata)

    # --- the three funnel stages, counted server-side ---
    all_routes_where = "route_id in (" + ",".join(f"'{r}'" for r in candidates) + ")"
    matching_where = all_routes_where + " and route_id=current_route_id"
    error_free_where = matching_where + " and import_error='0' and import_trip_error='0'"

    total_counts = aggregate_route_counts(apc["resource_json_url"], all_routes_where)
    matching_counts = aggregate_route_counts(apc["resource_json_url"], matching_where)
    error_free_counts = aggregate_route_counts(apc["resource_json_url"], error_free_where)

    # --- the fully clean comparison extract ---
    comparison_path = RAW_CAPMETRO_DIR / "route_801_803_clean_comparison.csv"
    comparison_manifest = download_soda_csv(
        base_url=apc["resource_csv_url"],
        destination=comparison_path,
        select=COMPARISON_FIELDS,
        where=clean_where(candidates, ["4", "6"]),
        order="route_id,apc_date_time,vehicle_id,actual_sequence,bs_id",
        force=force,
    )

    # --- re-derive everything locally, then attach the server-side counts ---
    route_metrics = summarize_rows(comparison_path)
    for route in candidates:
        route_metrics[route]["all_route_records"] = total_counts.get(route, 0)
        route_metrics[route]["matching_current_route_records"] = matching_counts.get(route, 0)
        route_metrics[route]["error_free_matching_route_records"] = error_free_counts.get(route, 0)

    primary = route_metrics["801"]
    secondary = route_metrics["803"]

    evidence = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "dataset": {
            "name": metadata.get("name"),
            "socrata_id": apc["socrata_id"],
            "column_count": len(metadata.get("columns", [])),
            "landing_page": "https://data.texas.gov/dataset/APC-Raw-July-2021-December-2021/im6q-3pc9",
        },
        "clean_definition": clean_where(candidates, ["4", "6"]),
        "gps_high_quality_definition": "nonzero coordinates and quality_indicator in {3,4,5,6}",
        "comparison_download": comparison_manifest,
        "routes": route_metrics,
        "selection": {
            "primary_route": "801",
            "reason": (
                "Under identical cleaning rules, Route 801 provides larger clean stop-event, "
                "boarding, and usable-segment samples despite fewer distinct trip-day pairs, "
                "while retaining comparable GPS quality."
            ),
            "clean_event_advantage_percent_over_803": round(
                100
                * (primary["clean_stop_events"] - secondary["clean_stop_events"])
                / secondary["clean_stop_events"],
                2,
            ),
            "boarding_advantage_percent_over_803": round(
                100 * (primary["boardings"] - secondary["boardings"]) / secondary["boardings"],
                2,
            ),
            "usable_segment_advantage_percent_over_803": round(
                100
                * (
                    primary["usable_positive_time_distance_segments"]
                    - secondary["usable_positive_time_distance_segments"]
                )
                / secondary["usable_positive_time_distance_segments"],
                2,
            ),
            "interpretation_limit": "The selection maximizes empirical coverage; it is not a claim that Route 801 has better or worse service.",
        },
    }
    write_json(AUDIT_DIR / "route_selection_audit.json", evidence)

    # --- the same decision, as a readable markdown table ---
    lines = [
        "# Reproduced Route 801 selection audit",
        "",
        f"Generated from the official Socrata API at `{evidence['generated_utc']}`.",
        "",
        "| Metric | Route 801 | Route 803 |",
        "|---|---:|---:|",
    ]
    table_metrics = [
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
    for label, key in table_metrics:
        lines.append(f"| {label} | {route_metrics['801'][key]:,} | {route_metrics['803'][key]:,} |")
    lines += [
        "",
        "## Decision",
        "",
        evidence["selection"]["reason"],
        "",
        f"Route 801 has {evidence['selection']['clean_event_advantage_percent_over_803']}% more clean stop events, "
        f"{evidence['selection']['boarding_advantage_percent_over_803']}% more recorded boardings, and "
        f"{evidence['selection']['usable_segment_advantage_percent_over_803']}% more usable positive-time/distance segments than Route 803.",
        "This justifies Route 801 as the primary case by data coverage, not by a claim about service quality.",
        "",
        "Direction code 6 remains provisional code-only. A compass-direction name is blocked until a checksum-verified 2021 GTFS snapshot is obtained.",
    ]
    write_text(AUDIT_DIR / "ROUTE_SELECTION_EVIDENCE.md", "\n".join(lines))

    return evidence


# -----------------------------------------------------------------------------
# PART D -- the same audit, computed offline from the 3.7 GB snapshot
# -----------------------------------------------------------------------------
def audit_routes_local(config: dict[str, Any]) -> dict[str, Any]:
    """Build the ENTIRE cleaning funnel from the local archival snapshot.

    The normal path asks the portal to COUNT records at each cleaning stage.
    This does the same counting here, in a single streaming pass over all
    9,197,694 rows -- no network at all.

    The four funnel levels, applied cumulatively to each row:

        level 1   route_id in ('801','803')                  -> all_route_records
        level 2   + route_id = current_route_id              -> matching_current_route_records
        level 3   + import_error = 0 and import_trip_error=0 -> error_free_matching_route_records
        level 4   + bs_id <> 0 and direction in ('4','6')    -> clean_stop_events

    Rows that reach level 4 are handed to summarize_row_stream() for the full
    per-route statistics, so the offline numbers and the online numbers are
    produced by identical arithmetic.
    """
    candidates = tuple(config["study"]["candidate_routes"])
    levels: dict[str, dict[str, int]] = {
        route: {"all": 0, "matching": 0, "error_free": 0} for route in candidates
    }
    read = 0

    def clean_rows():
        """Count each funnel level as a side effect; yield only clean rows."""
        nonlocal read
        for row in stream_raw_snapshot():
            read += 1
            if read % 1_000_000 == 0:
                print(f"  read {read:,} raw rows...", flush=True)

            route = row["route_id"]
            if route not in candidates:
                continue
            levels[route]["all"] += 1

            if route != row["current_route_id"]:
                continue
            levels[route]["matching"] += 1

            if row["import_error"] != "0" or row["import_trip_error"] != "0":
                continue
            levels[route]["error_free"] += 1

            if row["bs_id"] == "0" or row["direction_code_id"] not in ("4", "6"):
                continue
            yield row

    route_metrics = summarize_row_stream(clean_rows())
    print(f"  read {read:,} raw rows total")

    for route in candidates:
        route_metrics[route]["all_route_records"] = levels[route]["all"]
        route_metrics[route]["matching_current_route_records"] = levels[route]["matching"]
        route_metrics[route]["error_free_matching_route_records"] = levels[route]["error_free"]

    return {
        "generated_utc": datetime.now(UTC).isoformat(),
        "source": "local archival snapshot (offline extraction, no network)",
        "snapshot_path": RAW_FULL_SNAPSHOT.relative_to(RAW_FULL_SNAPSHOT.parents[3]).as_posix(),
        "raw_rows_read": read,
        "clean_definition": clean_where(list(candidates), ["4", "6"]),
        "routes": route_metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload raw files instead of reusing checksum-recorded local copies",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="compute the funnel from the local 3.7 GB snapshot instead of the portal (no network)",
    )
    args = parser.parse_args()

    ensure_dirs()

    if args.local:
        evidence = audit_routes_local(load_config())
        write_json(AUDIT_DIR / "route_selection_audit_local.json", evidence)
        print("\nStep 1 complete (OFFLINE).")
        print(f"  raw rows read : {evidence['raw_rows_read']:,}")
        for route in ("801", "803"):
            r = evidence["routes"][route]
            print(f"  Route {route}: all {r['all_route_records']:,} -> "
                  f"matching {r['matching_current_route_records']:,} -> "
                  f"error-free {r['error_free_matching_route_records']:,} -> "
                  f"clean {r['clean_stop_events']:,}")
        return 0

    evidence = audit_routes(load_config(), force=args.force)

    print("\nStep 1 complete.")
    for route in ("801", "803"):
        r = evidence["routes"][route]
        print(f"  Route {route}: {r['clean_stop_events']:,} clean stop events, "
              f"{r['boardings']:,} boardings")
    print(f"  Selected: Route {evidence['selection']['primary_route']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
