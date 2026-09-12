"""
=============================================================================
 STEP 3 OF 4  --  JOIN WEATHER TO EVERY BUS STOP EVENT
=============================================================================

WHAT THIS STEP ANSWERS
    "Was it raining when this bus stopped here?" -- for all 229,421 events.

THE METHOD
    pandas.merge_asof: for each APC stop event, take the NOAA observation
    CLOSEST IN TIME, and accept it only if it is within 90 minutes.

    merge_asof is the standard tool for exactly this job -- joining two
    time-ordered tables on "nearest time" rather than on an exact key.

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

THE ONE SUBTLE BIT: DST AMBIGUITY
    On 7 November 2021 the hour 01:00-02:00 happened TWICE in Austin. A bare
    APC timestamp inside that hour is genuinely ambiguous.

    We localize twice -- once assuming the first pass through the hour
    (ambiguous=True, i.e. still on daylight time) and once assuming the second
    (ambiguous=False) -- and count the rows where those two give different UTC
    instants. Those are the ambiguous ones. We then use the first pass, and
    report the count, rather than silently guessing.

WHAT THIS STEP DOES *NOT* ESTABLISH
    It reports the pooled median segment time on dry vs rainy events
    (204 s vs 212 s). That difference is DESCRIPTIVE ONLY. Austin rain is
    convective and clusters in the afternoon, so part of the gap is rush hour,
    not rain. A real rain multiplier has to be estimated within segment,
    time-of-day and day-type strata. The warning is written into the output
    file so it cannot be quoted out of context.

INPUTS   data/raw/capmetro/route_801_direction_6_clean.csv   (Step 1)
         data/processed/texas_capmetro/weather_*.csv          (Step 2)

OUTPUTS  data/audit/texas_capmetro/weather_join_audit.json
         data/audit/texas_capmetro/WEATHER_FEASIBILITY_EVIDENCE.md

RUN      python scripts/pipeline/03_join_weather.py
=============================================================================
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR, PROCESSED_DIR, ROOT, UTC,
    ensure_dirs, load_config, require_file, sha256_file, write_json, write_text,
)


def load_apc_events(path: Path, timezone_name: str) -> tuple[pd.DataFrame, int]:
    """Read the study set and put its timestamps on an unambiguous UTC clock.

    The APC file has NO timezone column, so reading these as Austin local time
    is an explicit assumption -- documented as such in the manuscript, not
    presented as fact. It is corroborated by the observed service window in the
    data (roughly 04:00-24:00) matching the published timetable's 5 AM-12:30 AM
    span; a UTC reading would displace it by five to six hours.

    Returns (events, dst_ambiguous_count).
    """
    events = pd.read_csv(
        path, usecols=["apc_date_time", "rev_seconds", "rev_distance"], dtype=str
    )
    naive = pd.to_datetime(events["apc_date_time"], format="%Y%m%d%H%M%S", errors="coerce")

    # See "THE ONE SUBTLE BIT" above: localize both ways, and where the two
    # disagree the timestamp fell inside the repeated fall-back hour.
    first_pass = naive.dt.tz_localize(timezone_name, ambiguous=True, nonexistent="shift_forward")
    second_pass = naive.dt.tz_localize(timezone_name, ambiguous=False, nonexistent="shift_forward")
    dst_ambiguous = int((first_pass != second_pass).sum())

    events["event_time"] = first_pass.dt.tz_convert("UTC")
    for column in ("rev_seconds", "rev_distance"):
        events[column] = pd.to_numeric(events[column], errors="coerce")

    return events, dst_ambiguous


def load_weather(station_key: str) -> pd.DataFrame:
    """Read one station's normalized observations, sorted by time for merge_asof."""
    path = require_file(
        PROCESSED_DIR / f"weather_{station_key}_2021_jul_dec.csv",
        f"the normalized weather table for {station_key} (run 02_prepare_weather.py first)",
    )
    weather = pd.read_csv(path, usecols=["timestamp_utc", "rain_flag"])
    weather["obs_time"] = pd.to_datetime(weather["timestamp_utc"], utc=True)
    return weather[["obs_time", "rain_flag"]].sort_values("obs_time").reset_index(drop=True)


def join_nearest(events: pd.DataFrame, weather: pd.DataFrame, tolerance: pd.Timedelta,
                 suffix: str) -> pd.DataFrame:
    """Attach each event's nearest observation within `tolerance`.

    Unmatched events get NaN, which is how we measure coverage.
    """
    joined = pd.merge_asof(
        events.sort_values("event_time"),
        weather.rename(columns={"obs_time": f"obs_time_{suffix}",
                                "rain_flag": f"rain_{suffix}"}),
        left_on="event_time",
        right_on=f"obs_time_{suffix}",
        direction="nearest",
        tolerance=tolerance,
    )
    joined[f"delta_min_{suffix}"] = (
        (joined["event_time"] - joined[f"obs_time_{suffix}"]).abs().dt.total_seconds() / 60
    )
    return joined


def audit_weather_join(config: dict[str, Any]) -> dict[str, Any]:
    apc_path = require_file(
        ROOT / config["apc"]["raw_output"],
        "the direction-6 study set (run 01_extract_dir6.py first)",
    )
    tolerance_minutes = int(config["weather"]["nearest_join_tolerance_minutes"])
    tolerance = pd.Timedelta(minutes=tolerance_minutes)

    events, dst_ambiguous = load_apc_events(apc_path, config["study"]["timezone"])
    apc_rows = len(events)

    # --- the two joins: primary station, then the sensitivity cross-check ----
    joined = join_nearest(events, load_weather("camp_mabry"), tolerance, "primary")
    joined = join_nearest(joined, load_weather("bergstrom"), tolerance, "secondary")

    matched = joined["rain_primary"].notna()
    primary = joined[matched]

    # --- coverage and how close the matches actually were --------------------
    deltas = primary["delta_min_primary"].to_numpy()
    # NB: the p95 here is the plain order statistic used since the first audit
    # (ceil(0.95 n)-th value), NOT pandas' interpolated quantile.
    p95 = float(np.sort(deltas)[max(0, math.ceil(0.95 * len(deltas)) - 1)]) if len(deltas) else None

    rain = primary["rain_primary"].astype(int)
    both_matched = primary["rain_secondary"].notna()
    agree = int((rain[both_matched] == primary.loc[both_matched, "rain_secondary"]).sum())

    counts = {
        "apc_rows": apc_rows,
        "primary_matched": int(matched.sum()),
        "primary_rain_exposed_rows": int(rain.sum()),
        "secondary_matched": int(both_matched.sum()),
        "station_rain_flag_agreement": agree,
        "station_rain_flag_disagreement": int(both_matched.sum()) - agree,
    }
    if dst_ambiguous:
        counts["dst_ambiguous_apc_rows_fold0_used"] = dst_ambiguous
    if apc_rows - int(matched.sum()):
        counts["primary_unmatched"] = apc_rows - int(matched.sum())

    # --- the descriptive wet/dry comparison (NOT a causal effect) -------------
    # only segments with BOTH positive time and positive distance
    usable = primary[(primary["rev_seconds"] > 0) & (primary["rev_distance"] > 0)]
    wet = usable.loc[usable["rain_primary"] == 1, "rev_seconds"]
    dry = usable.loc[usable["rain_primary"] == 0, "rev_seconds"]

    join_coverage = counts["primary_matched"] / apc_rows if apc_rows else 0
    # The feasibility rule was declared BEFORE seeing the result.
    feasible = join_coverage >= 0.95 and counts["primary_rain_exposed_rows"] >= 1000

    evidence = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "apc_subset_sha256": sha256_file(apc_path),
        "apc_timestamp_interpretation": config["apc"]["timestamp_assumption"],
        "dst_policy": (
            "APC wall-clock timestamps are localized to America/Chicago. Ambiguous fall-back "
            "timestamps use fold=0 and are counted explicitly. NOAA local-standard timestamps "
            "are converted from fixed UTC-06:00 to America/Chicago before matching."
        ),
        "join_method": f"nearest NOAA observation within {tolerance_minutes} minutes",
        "counts": dict(sorted(counts.items())),
        "primary_join_coverage_percent": round(100 * join_coverage, 3),
        "secondary_join_coverage_percent": round(100 * counts["secondary_matched"] / apc_rows, 3)
        if apc_rows else 0,
        "median_absolute_join_delta_minutes": round(float(np.median(deltas)), 3)
        if len(deltas) else None,
        "p95_absolute_join_delta_minutes": round(p95, 3) if p95 is not None else None,
        "descriptive_unadjusted_segment_medians": {
            "dry_positive_time_distance_segments": len(dry),
            "rain_positive_time_distance_segments": len(wet),
            "dry_median_rev_seconds": round(float(dry.median()), 3) if len(dry) else None,
            "rain_median_rev_seconds": round(float(wet.median()), 3) if len(wet) else None,
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

    write_text(AUDIT_DIR / "WEATHER_FEASIBILITY_EVIDENCE.md", "\n".join([
        "# Weather-join feasibility audit",
        "",
        f"- APC rows: {apc_rows:,}",
        f"- Camp Mabry join coverage: {evidence['primary_join_coverage_percent']}%",
        f"- Austin-Bergstrom sensitivity join coverage: {evidence['secondary_join_coverage_percent']}%",
        f"- Rain-exposed APC rows at Camp Mabry: {counts['primary_rain_exposed_rows']:,}",
        f"- DST-ambiguous APC rows (fold=0 used): {dst_ambiguous:,}",
        f"- Ordinary-weather calibration feasible under the declared coverage rule: {'yes' if feasible else 'no'}",
        "",
        "The join is technically feasible if the rule above passes, but feasibility is not evidence of a causal rain effect. Any multiplier must be estimated with segment, time-of-day, and day-type controls. Severe weather remains a labeled synthetic stress test.",
    ]))
    return evidence


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    ensure_dirs()
    evidence = audit_weather_join(load_config())
    counts = evidence["counts"]

    print("\nStep 3 complete.")
    print(f"  APC events joined : {counts['primary_matched']:,} / {counts['apc_rows']:,} "
          f"({evidence['primary_join_coverage_percent']}%)")
    print(f"  rain-exposed      : {counts['primary_rain_exposed_rows']:,}")
    print(f"  median join gap   : {evidence['median_absolute_join_delta_minutes']} min "
          f"(p95 {evidence['p95_absolute_join_delta_minutes']})")
    agree = counts["station_rain_flag_agreement"]
    total = agree + counts["station_rain_flag_disagreement"]
    print(f"  two-station agree : {agree:,} / {total:,} ({100 * agree / total:.1f}%)")
    print(f"  feasible          : {evidence['ordinary_weather_calibration_feasible']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
