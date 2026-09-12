"""
=============================================================================
 STEP 4 OF 5  --  JOIN WEATHER TO EVERY BUS STOP EVENT
=============================================================================

WHAT THIS STEP ANSWERS
    "Was it raining when this bus stopped here?" -- for all 229,421 events.

THE METHOD
    For each APC stop event, find the NOAA observation CLOSEST IN TIME, and
    accept it if it is within 90 minutes.

WHY 90 MINUTES
    It is a coverage guarantee, not a modelling choice.

    The largest gap between consecutive Camp Mabry observations in the study
    window is 120 minutes. So the worst case for any bus event is landing dead
    in the middle of such a gap -- 60 minutes from the nearest observation.
    A 90-minute tolerance clears that bound with 50% headroom.

    It never actually binds: the realised median join gap is 12.7 minutes,
    p95 is 27.9 minutes, and coverage comes out at 100%. If the cap were doing
    real work, coverage would be below 100%.

    The value lives in config/texas_capmetro_801.json as
    weather.nearest_join_tolerance_minutes -- change it there, not here.

TWO THINGS WORTH UNDERSTANDING IN THE CODE BELOW

  1. DST AMBIGUITY (parse_apc_datetime)
     On 7 November 2021 the hour 01:00-02:00 happened TWICE in Austin. A bare
     APC timestamp in that hour is genuinely ambiguous. We detect it by
     building the datetime twice -- once with fold=0 and once with fold=1 --
     and comparing the UTC offsets. If they differ, the timestamp is in the
     repeated hour. We then use fold=0 (the first pass) and COUNT how many
     rows this affected, rather than silently guessing.

  2. BINARY SEARCH (nearest_weather)
     Observations are kept in a time-sorted list, so bisect can jump straight
     to the insertion point and we only ever compare the two neighbours.
     That is O(log n) per event. A naive "check every observation" search
     would be 229,421 x 6,484 = about 1.5 billion comparisons; this is a few
     million and finishes in seconds.

WHAT THIS STEP DOES *NOT* ESTABLISH
    It reports the pooled median segment time on dry vs rainy events
    (204 s vs 212 s). That difference is DESCRIPTIVE ONLY. Austin rain is
    convective and clusters in the afternoon, so part of the gap is rush hour,
    not rain. A real rain multiplier has to be estimated within segment,
    time-of-day and day-type strata. The warning is written into the output
    file so it cannot be quoted out of context.

INPUTS   data/raw/capmetro/route_801_direction_6_clean.csv   (Step 2)
         data/processed/texas_capmetro/weather_*.csv          (Step 3)

OUTPUTS  data/audit/texas_capmetro/weather_join_audit.json
         data/audit/texas_capmetro/WEATHER_FEASIBILITY_EVIDENCE.md

RUN      python scripts/pipeline/04_join_weather.py
=============================================================================
"""

from __future__ import annotations

import argparse
import bisect
import csv
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR,
    PROCESSED_DIR,
    ROOT,
    UTC,
    ensure_dirs,
    load_config,
    safe_float,
    sha256_file,
    write_json,
    write_text,
)


def parse_apc_datetime(value: str, austin: ZoneInfo) -> tuple[datetime, bool]:
    """Read a compact APC timestamp (YYYYMMDDHHMMSS) as an Austin wall-clock time.

    Returns (utc_instant, is_dst_ambiguous).

    The APC file has NO timezone column, so reading these as Austin local time
    is an explicit assumption -- documented as such in the manuscript, not
    presented as fact. It is corroborated by the fact that the observed service
    window in the data (roughly 04:00-24:00) matches the published timetable's
    5 AM - 12:30 AM span; a UTC reading would displace it by five to six hours.
    """
    naive = datetime.strptime(value, "%Y%m%d%H%M%S")
    first = naive.replace(tzinfo=austin, fold=0)
    second = naive.replace(tzinfo=austin, fold=1)
    ambiguous = first.utcoffset() != second.utcoffset()
    return first.astimezone(UTC), ambiguous


def load_weather_index(path: Path) -> tuple[list[float], list[dict[str, str]]]:
    """Load one station's observations into a parallel pair of lists.

    instants[i] is the UTC epoch second of rows[i]. Keeping the times in their
    own sorted list is what makes the binary search below possible.
    """
    rows: list[dict[str, str]] = []
    instants: list[float] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            instants.append(datetime.fromisoformat(row["timestamp_utc"]).timestamp())
            rows.append(row)
    return instants, rows


def nearest_weather(
    target: float, instants: list[float], rows: list[dict[str, str]], tolerance_seconds: int
) -> tuple[dict[str, str] | None, float | None]:
    """Find the observation closest in time to `target`, or None if too far away.

    bisect_left finds where `target` would slot into the sorted list; the
    nearest observation is therefore one of the two entries either side.
    """
    index = bisect.bisect_left(instants, target)
    candidates = [candidate for candidate in (index - 1, index) if 0 <= candidate < len(instants)]
    if not candidates:
        return None, None
    best = min(candidates, key=lambda candidate: abs(instants[candidate] - target))
    delta = abs(instants[best] - target)
    if delta > tolerance_seconds:
        return None, delta
    return rows[best], delta


def audit_weather_join(config: dict[str, Any]) -> dict[str, Any]:
    primary_path = ROOT / config["apc"]["raw_output"]
    if not primary_path.exists():
        raise FileNotFoundError(
            f"Primary APC subset is missing: {primary_path}. Run 02_download_dir6.py first."
        )

    primary_weather_path = PROCESSED_DIR / "weather_camp_mabry_2021_jul_dec.csv"
    secondary_weather_path = PROCESSED_DIR / "weather_bergstrom_2021_jul_dec.csv"
    if not primary_weather_path.exists() or not secondary_weather_path.exists():
        raise FileNotFoundError(
            "Normalized weather files are missing. Run 03_prepare_weather.py first."
        )

    primary_instants, primary_rows = load_weather_index(primary_weather_path)
    secondary_instants, secondary_rows = load_weather_index(secondary_weather_path)

    austin = ZoneInfo(config["study"]["timezone"])
    tolerance_seconds = int(config["weather"]["nearest_join_tolerance_minutes"]) * 60

    counts: dict[str, int] = defaultdict(int)
    join_deltas: list[float] = []
    wet_segment_seconds: list[float] = []
    dry_segment_seconds: list[float] = []

    # ---- one streamed pass over all 229,421 stop events --------------------
    with primary_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            counts["apc_rows"] += 1

            raw_timestamp = row.get("apc_date_time", "")
            try:
                instant, ambiguous = parse_apc_datetime(raw_timestamp, austin)
            except ValueError:
                counts["invalid_apc_timestamp"] += 1
                continue
            if ambiguous:
                counts["dst_ambiguous_apc_rows_fold0_used"] += 1

            target = instant.timestamp()

            # ---- primary station (Camp Mabry) ------------------------------
            primary_weather, delta = nearest_weather(
                target, primary_instants, primary_rows, tolerance_seconds
            )
            if primary_weather is None:
                counts["primary_unmatched"] += 1
                continue
            counts["primary_matched"] += 1
            assert delta is not None
            join_deltas.append(delta / 60)  # seconds -> minutes

            primary_rain = int(primary_weather["rain_flag"])
            counts["primary_rain_exposed_rows"] += primary_rain

            # ---- collect segment times for the descriptive comparison ------
            # only segments with BOTH positive time and positive distance
            seconds = safe_float(row.get("rev_seconds"))
            distance = safe_float(row.get("rev_distance"))
            if seconds is not None and distance is not None and seconds > 0 and distance > 0:
                (wet_segment_seconds if primary_rain else dry_segment_seconds).append(seconds)

            # ---- secondary station (Bergstrom), as a cross-check -----------
            secondary_weather, _ = nearest_weather(
                target, secondary_instants, secondary_rows, tolerance_seconds
            )
            if secondary_weather is not None:
                counts["secondary_matched"] += 1
                secondary_rain = int(secondary_weather["rain_flag"])
                if secondary_rain == primary_rain:
                    counts["station_rain_flag_agreement"] += 1
                else:
                    counts["station_rain_flag_disagreement"] += 1

    # ---- summarise ---------------------------------------------------------
    apc_rows = counts["apc_rows"]
    primary_matched = counts["primary_matched"]
    secondary_matched = counts["secondary_matched"]
    join_coverage = primary_matched / apc_rows if apc_rows else 0
    rain_sample = counts["primary_rain_exposed_rows"]

    # The feasibility rule was declared BEFORE seeing the result.
    feasible = join_coverage >= 0.95 and rain_sample >= 1000

    evidence = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "apc_subset_sha256": sha256_file(primary_path),
        "apc_timestamp_interpretation": config["apc"]["timestamp_assumption"],
        "dst_policy": (
            "APC wall-clock timestamps are localized to America/Chicago. Ambiguous fall-back "
            "timestamps use fold=0 and are counted explicitly. NOAA local-standard timestamps "
            "are converted from fixed UTC-06:00 to America/Chicago before matching."
        ),
        "join_method": f"nearest NOAA observation within {tolerance_seconds // 60} minutes",
        "counts": dict(sorted(counts.items())),
        "primary_join_coverage_percent": round(100 * join_coverage, 3),
        "secondary_join_coverage_percent": round(100 * secondary_matched / apc_rows, 3)
        if apc_rows
        else 0,
        "median_absolute_join_delta_minutes": round(statistics.median(join_deltas), 3)
        if join_deltas
        else None,
        "p95_absolute_join_delta_minutes": round(
            sorted(join_deltas)[max(0, math.ceil(0.95 * len(join_deltas)) - 1)], 3
        )
        if join_deltas
        else None,
        "descriptive_unadjusted_segment_medians": {
            "dry_positive_time_distance_segments": len(dry_segment_seconds),
            "rain_positive_time_distance_segments": len(wet_segment_seconds),
            "dry_median_rev_seconds": round(statistics.median(dry_segment_seconds), 3)
            if dry_segment_seconds
            else None,
            "rain_median_rev_seconds": round(statistics.median(wet_segment_seconds), 3)
            if wet_segment_seconds
            else None,
            "warning": (
                "These pooled medians are descriptive only and must not be interpreted as a "
                "causal weather multiplier; segment, time-of-day, and day-type controls are required."
            ),
        },
        "ordinary_weather_calibration_feasible": feasible,
        "feasibility_rule": "at least 95% APC join coverage and at least 1,000 rain-exposed APC rows",
        "severe_weather_policy": (
            "Observed ordinary rain may calibrate empirical baseline effects after stratified modeling. "
            "Severe/extreme weather outside observed support remains an explicitly synthetic stress test."
        ),
    }
    write_json(AUDIT_DIR / "weather_join_audit.json", evidence)

    lines = [
        "# Weather-join feasibility audit",
        "",
        f"- APC rows: {apc_rows:,}",
        f"- Camp Mabry join coverage: {evidence['primary_join_coverage_percent']}%",
        f"- Austin-Bergstrom sensitivity join coverage: {evidence['secondary_join_coverage_percent']}%",
        f"- Rain-exposed APC rows at Camp Mabry: {rain_sample:,}",
        f"- DST-ambiguous APC rows (fold=0 used): {counts['dst_ambiguous_apc_rows_fold0_used']:,}",
        f"- Ordinary-weather calibration feasible under the declared coverage rule: {'yes' if feasible else 'no'}",
        "",
        "The join is technically feasible if the rule above passes, but feasibility is not evidence of a causal rain effect. Any multiplier must be estimated with segment, time-of-day, and day-type controls. Severe weather remains a labeled synthetic stress test.",
    ]
    write_text(AUDIT_DIR / "WEATHER_FEASIBILITY_EVIDENCE.md", "\n".join(lines))

    return evidence


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    ensure_dirs()
    evidence = audit_weather_join(load_config())
    counts = evidence["counts"]

    print("\nStep 4 complete.")
    print(f"  APC events joined : {counts['primary_matched']:,} / {counts['apc_rows']:,} "
          f"({evidence['primary_join_coverage_percent']}%)")
    print(f"  rain-exposed      : {counts['primary_rain_exposed_rows']:,}")
    print(f"  median join gap   : {evidence['median_absolute_join_delta_minutes']} min "
          f"(p95 {evidence['p95_absolute_join_delta_minutes']})")
    agree = counts["station_rain_flag_agreement"]
    total = agree + counts["station_rain_flag_disagreement"]
    print(f"  two-station agree : {agree:,} / {total:,} ({100*agree/total:.1f}%)")
    print(f"  feasible          : {evidence['ordinary_weather_calibration_feasible']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
