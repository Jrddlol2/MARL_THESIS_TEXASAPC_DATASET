"""
=============================================================================
 STEP 3 OF 4  --  MATCH WEATHER TO EVERY BUS STOP EVENT
=============================================================================

THE QUESTION
    "Was it raining when this bus stopped here?"  -- for all 229,421 events.

THE METHOD
    For each bus event, find the NOAA reading CLOSEST IN TIME, and accept it
    only if it is within 90 minutes. pandas has a ready-made tool for this
    kind of "nearest time" match: pd.merge_asof.

WHY 90 MINUTES
    The biggest gap between two Camp Mabry readings is 120 minutes, so no bus
    event is ever more than 60 minutes from a reading. 90 minutes is safely
    above that. In practice the typical gap is 12.7 minutes and every event
    gets a match (100% coverage). The 90 is stored in the config file.

THE DAYLIGHT-SAVING HOUR
    On 7 November 2021 the clocks went back, so 01:00-02:00 happened twice in
    Austin. A bus time inside that hour could mean either one. We convert every
    time both ways, count how many rows come out different (the unclear
    ones), use the first meaning, and report the count.

WHAT THIS DOES *NOT* PROVE
    It reports the median segment time on dry vs rainy events (204 s vs 212 s).
    That is only a description. Rain in Austin tends to fall in the afternoon
    rush hour, so part of the difference is traffic, not rain.

INPUT    data/raw/capmetro/route_801_direction_6_clean.csv     (from Step 1)
         data/processed/texas_capmetro/weather_*.csv            (from Step 2)
OUTPUT   data/audit/texas_capmetro/weather_join_audit.json
         data/audit/texas_capmetro/WEATHER_FEASIBILITY_EVIDENCE.md

RUN      python scripts/pipeline/03_join_weather.py        (a few seconds)
=============================================================================
"""

import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common


def load_bus_events(csv_file, timezone_name):
    """Read the bus events and give each one an exact UTC time.

    The bus file has no time zone column, so we ASSUME its times are Austin
    local time. The data supports this: buses run from about 04:00 to 24:00,
    which matches the published 5 AM - 12:30 AM timetable.

    Returns two things: the table, and how many times fell in the repeated hour.
    """
    events = pd.read_csv(csv_file, usecols=["apc_date_time", "rev_seconds", "rev_distance"],
                         dtype=str)

    # "20210701053012" -> 2021-07-01 05:30:12   (no time zone yet)
    local_time = pd.to_datetime(events["apc_date_time"], format="%Y%m%d%H%M%S", errors="coerce")

    # Attach the Austin time zone twice: once assuming the FIRST pass through
    # the repeated hour, once assuming the SECOND. Where they differ, the time
    # was unclear.
    first_meaning = local_time.dt.tz_localize(timezone_name, ambiguous=True,
                                              nonexistent="shift_forward")
    second_meaning = local_time.dt.tz_localize(timezone_name, ambiguous=False,
                                               nonexistent="shift_forward")
    unclear_count = int((first_meaning != second_meaning).sum())

    events["event_time"] = first_meaning.dt.tz_convert("UTC")
    events["rev_seconds"] = pd.to_numeric(events["rev_seconds"], errors="coerce")
    events["rev_distance"] = pd.to_numeric(events["rev_distance"], errors="coerce")

    return events, unclear_count


def load_weather(station_key):
    """Read one station's clean weather table, sorted by time."""
    csv_file = common.require_file(
        common.PROCESSED_DIR / f"weather_{station_key}_2021_jul_dec.csv",
        f"the normalized weather table for {station_key} (run 02_prepare_weather.py first)",
    )
    weather = pd.read_csv(csv_file, usecols=["timestamp_utc", "rain_flag"])
    weather["obs_time"] = pd.to_datetime(weather["timestamp_utc"], utc=True)
    weather = weather[["obs_time", "rain_flag"]]
    weather = weather.sort_values("obs_time").reset_index(drop=True)
    return weather


def match_nearest_reading(events, weather, max_gap, name):
    """Give each bus event the closest weather reading within max_gap.

    New columns added (NAME = "primary" or "secondary"):
        obs_time_NAME    time of the matched reading
        rain_NAME        its rain flag (empty if no reading was close enough)
        delta_min_NAME   minutes between the bus event and the reading
    """
    weather = weather.rename(columns={"obs_time": "obs_time_" + name,
                                      "rain_flag": "rain_" + name})
    matched = pd.merge_asof(
        events.sort_values("event_time"),
        weather,
        left_on="event_time",
        right_on="obs_time_" + name,
        direction="nearest",        # closest reading, before OR after
        tolerance=max_gap,          # but no further away than this
    )
    gap = (matched["event_time"] - matched["obs_time_" + name]).abs()
    matched["delta_min_" + name] = gap.dt.total_seconds() / 60
    return matched


def join_weather(config):
    bus_file = common.require_file(
        common.ROOT / config["apc"]["raw_output"],
        "the direction-6 study set (run 01_extract_dir6.py first)",
    )
    max_gap_minutes = int(config["weather"]["nearest_join_tolerance_minutes"])
    max_gap = pd.Timedelta(minutes=max_gap_minutes)

    events, unclear_count = load_bus_events(bus_file, config["study"]["timezone"])
    total_events = len(events)

    # ---- match to the main station, then to the cross-check station ---------
    joined = match_nearest_reading(events, load_weather("camp_mabry"), max_gap, "primary")
    joined = match_nearest_reading(joined, load_weather("bergstrom"), max_gap, "secondary")

    has_match = joined["rain_primary"].notna()
    matched = joined[has_match]
    matched_count = int(has_match.sum())

    # ---- how close were the matches? -----------------------------------------
    gaps = matched["delta_min_primary"].to_numpy()
    if len(gaps) > 0:
        median_gap = round(float(np.median(gaps)), 3)
        # 95th percentile, taken as the plain sorted value at position ceil(0.95 n)
        sorted_gaps = np.sort(gaps)
        position = max(0, math.ceil(0.95 * len(gaps)) - 1)
        p95_gap = round(float(sorted_gaps[position]), 3)
    else:
        median_gap = None
        p95_gap = None

    # ---- do the two stations agree on rain? ----------------------------------
    rain = matched["rain_primary"].astype(int)
    both_matched = matched["rain_secondary"].notna()
    both_count = int(both_matched.sum())
    agree_count = int((rain[both_matched] == matched.loc[both_matched, "rain_secondary"]).sum())

    counts = {
        "apc_rows": total_events,
        "primary_matched": matched_count,
        "primary_rain_exposed_rows": int(rain.sum()),
        "secondary_matched": both_count,
        "station_rain_flag_agreement": agree_count,
        "station_rain_flag_disagreement": both_count - agree_count,
    }
    if unclear_count > 0:
        counts["dst_ambiguous_apc_rows_fold0_used"] = unclear_count
    if total_events - matched_count > 0:
        counts["primary_unmatched"] = total_events - matched_count

    # ---- dry vs rainy segment times (description only, NOT cause and effect) --
    # use only segments with a positive time AND a positive distance
    usable = matched[(matched["rev_seconds"] > 0) & (matched["rev_distance"] > 0)]
    wet_times = usable.loc[usable["rain_primary"] == 1, "rev_seconds"]
    dry_times = usable.loc[usable["rain_primary"] == 0, "rev_seconds"]

    if len(dry_times) > 0:
        dry_median = round(float(dry_times.median()), 3)
    else:
        dry_median = None
    if len(wet_times) > 0:
        wet_median = round(float(wet_times.median()), 3)
    else:
        wet_median = None

    # ---- the pass/fail rule (decided BEFORE looking at the result) -------------
    if total_events > 0:
        coverage = matched_count / total_events
        secondary_coverage_percent = round(100 * both_count / total_events, 3)
    else:
        coverage = 0
        secondary_coverage_percent = 0
    feasible = coverage >= 0.95 and counts["primary_rain_exposed_rows"] >= 1000

    evidence = {
        "generated_utc": datetime.now(common.UTC).isoformat(),
        "apc_subset_sha256": common.sha256_file(bus_file),
        "apc_timestamp_interpretation": config["apc"]["timestamp_assumption"],
        "dst_policy": (
            "APC wall-clock timestamps are localized to America/Chicago. Ambiguous fall-back "
            "timestamps use fold=0 and are counted explicitly. NOAA local-standard timestamps "
            "are converted from fixed UTC-06:00 to America/Chicago before matching."
        ),
        "join_method": f"nearest NOAA observation within {max_gap_minutes} minutes",
        "counts": counts,
        "primary_join_coverage_percent": round(100 * coverage, 3),
        "secondary_join_coverage_percent": secondary_coverage_percent,
        "median_absolute_join_delta_minutes": median_gap,
        "p95_absolute_join_delta_minutes": p95_gap,
        "descriptive_unadjusted_segment_medians": {
            "dry_positive_time_distance_segments": len(dry_times),
            "rain_positive_time_distance_segments": len(wet_times),
            "dry_median_rev_seconds": dry_median,
            "rain_median_rev_seconds": wet_median,
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
    common.write_json(common.AUDIT_DIR / "weather_join_audit.json", evidence)

    if feasible:
        feasible_word = "yes"
    else:
        feasible_word = "no"
    lines = [
        "# Weather-join feasibility audit",
        "",
        f"- APC rows: {total_events:,}",
        f"- Camp Mabry join coverage: {evidence['primary_join_coverage_percent']}%",
        f"- Austin-Bergstrom sensitivity join coverage: {evidence['secondary_join_coverage_percent']}%",
        f"- Rain-exposed APC rows at Camp Mabry: {counts['primary_rain_exposed_rows']:,}",
        f"- DST-ambiguous APC rows (fold=0 used): {unclear_count:,}",
        f"- Ordinary-weather calibration feasible under the declared coverage rule: {feasible_word}",
        "",
        "The join is technically feasible if the rule above passes, but feasibility is not evidence of a causal rain effect. Any multiplier must be estimated with segment, time-of-day, and day-type controls. Severe weather remains a labeled synthetic stress test.",
    ]
    common.write_text(common.AUDIT_DIR / "WEATHER_FEASIBILITY_EVIDENCE.md", "\n".join(lines))
    return evidence


def main():
    common.ensure_dirs()
    evidence = join_weather(common.load_config())
    counts = evidence["counts"]

    agree = counts["station_rain_flag_agreement"]
    both = agree + counts["station_rain_flag_disagreement"]

    print("\nStep 3 complete.")
    print(f"  APC events joined : {counts['primary_matched']:,} / {counts['apc_rows']:,} "
          f"({evidence['primary_join_coverage_percent']}%)")
    print(f"  rain-exposed      : {counts['primary_rain_exposed_rows']:,}")
    print(f"  median join gap   : {evidence['median_absolute_join_delta_minutes']} min "
          f"(p95 {evidence['p95_absolute_join_delta_minutes']})")
    print(f"  two-station agree : {agree:,} / {both:,} ({100 * agree / both:.1f}%)")
    print(f"  feasible          : {evidence['ordinary_weather_calibration_feasible']}")


if __name__ == "__main__":
    main()
