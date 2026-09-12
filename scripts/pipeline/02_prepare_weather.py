"""
=============================================================================
 STEP 2 OF 4  --  NORMALISE THE NOAA WEATHER OBSERVATIONS
=============================================================================

WHAT THIS STEP ANSWERS
    The APC file has no weather column. Weather has to come from outside, and
    it has to be put on the same clock as the bus data before anything can be
    matched. This step does that; Step 3 does the matching.

THE TWO STATIONS
    Camp Mabry      USW00013958   PRIMARY      sits beside the corridor
    Austin-Bergstrom USW00013904  SENSITIVITY  southeast of the city

    Two stations, not one, so the join has a cross-check. Step 4 compares
    their rain flags and reports how often they agree -- which is how we
    quantify the fact that rain in Austin is spatially patchy.

THE HARD PART: TIME ZONES
    This is the single most error-prone thing in the whole data pipeline, and
    it is worth understanding.

    NOAA Local Climatological Data timestamps are in LOCAL STANDARD TIME with
    NO daylight-saving adjustment. That is NOAA's documented convention. So a
    NOAA reading stamped "15:00" in July is really 16:00 on an Austin clock.

    If we ignored that, every summer observation would be off by one hour --
    which would smear rain onto dry bus events and vice versa for roughly half
    the study window, silently.

    So we:
        1. read each NOAA timestamp as a fixed UTC-06:00 instant,
        2. convert that instant to America/Chicago,
        3. store BOTH the UTC instant and the Austin local time.

    Step 3 matches on the UTC instant, which is unambiguous.

WHAT COUNTS AS RAIN
    rain_flag is 1 if ANY of these hold:
        * the precipitation value is greater than zero
        * the precipitation field is "T" (trace)
        * the present-weather code contains RA (rain), DZ (drizzle) or TS
          (thunderstorm)
    This is deliberately inclusive: we are building an EXPOSURE variable, not
    a rainfall measurement.

DEDUPLICATION
    NOAA sometimes reports more than once for the same instant (a routine
    hourly report plus an off-cycle special report). We keep ONE row per
    instant -- the one with the most fields populated, scored below -- so the
    nearest-observation search in Step 3 has no ties to break.

    No network: it reads the NOAA files we already hold. See common.py for why,
    and the README's "Getting the data" section for how to obtain them.

INPUTS   data/raw/noaa/LCD_USW00013958_2021.csv   archived NOAA file, Camp Mabry
         data/raw/noaa/LCD_USW00013904_2021.csv   archived NOAA file, Bergstrom
         config/texas_capmetro_801.json           station ids and source URLs

OUTPUTS
         data/processed/texas_capmetro/weather_camp_mabry_2021_jul_dec.csv
         data/processed/texas_capmetro/weather_bergstrom_2021_jul_dec.csv
         data/audit/texas_capmetro/weather_source_audit.json

RUN      python scripts/pipeline/02_prepare_weather.py
=============================================================================
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR,
    NOAA_LOCAL_STANDARD_TIME,
    PROCESSED_DIR,
    RAW_NOAA_DIR,
    ROOT,
    UTC,
    require_file,
    ensure_dirs,
    first_value,
    load_config,
    parse_flagged_number,
    sha256_file,
    write_json,
)


def normalize_weather_station(
    station_key: str, station: dict[str, Any], raw_path: Path
) -> tuple[Path, dict[str, Any]]:
    """Turn one raw NOAA LCD file into a clean, time-corrected observation table."""
    start_date = date(2021, 7, 1)
    end_date = date(2021, 12, 31)
    austin = ZoneInfo("America/Chicago")

    # keyed by UTC instant so duplicates collapse automatically
    by_timestamp: dict[datetime, dict[str, Any]] = {}

    with raw_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            # --- 1. parse the timestamp -------------------------------------
            date_value = first_value(row, "DATE", "Date")
            if not date_value:
                continue
            try:
                naive = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
            except ValueError:
                continue

            if naive.tzinfo is not None:
                # already carries an offset -- trust it
                noaa_instant = naive.astimezone(UTC)
            else:
                # the normal case: local standard time, no DST -> fixed UTC-06:00
                noaa_instant = naive.replace(tzinfo=NOAA_LOCAL_STANDARD_TIME).astimezone(UTC)

            local = noaa_instant.astimezone(austin)

            # --- 2. keep only the study window ------------------------------
            if not (start_date <= local.date() <= end_date):
                continue

            # --- 3. pull out the measurements -------------------------------
            precipitation_raw = first_value(row, "HourlyPrecipitation")
            weather_code = first_value(row, "HourlyPresentWeatherType", "HourlyWeatherType")
            temperature = parse_flagged_number(first_value(row, "HourlyDryBulbTemperature"))
            humidity = parse_flagged_number(first_value(row, "HourlyRelativeHumidity"))
            wind = parse_flagged_number(first_value(row, "HourlyWindSpeed"))
            visibility = parse_flagged_number(first_value(row, "HourlyVisibility"))
            precipitation = parse_flagged_number(precipitation_raw)

            # Skip administrative rows that carry no actual measurement.
            has_hourly_measurement = any(
                value is not None
                for value in (temperature, humidity, wind, visibility, precipitation)
            ) or bool(weather_code)
            if not has_hourly_measurement:
                continue

            # --- 4. decide the rain flag ------------------------------------
            upper_weather = weather_code.upper()
            trace = precipitation_raw.upper().startswith("T")
            rain_flag = bool(
                trace
                or (precipitation is not None and precipitation > 0)
                or any(code in upper_weather for code in ("RA", "DZ", "TS"))
            )

            normalized = {
                "station_key": station_key,
                "station_id": station["station_id"],
                "timestamp_utc": noaa_instant.isoformat(),
                "timestamp_austin": local.isoformat(),
                "source_timestamp_local_standard": date_value,
                "report_type": first_value(row, "REPORT_TYPE", "ReportType"),
                "precipitation": precipitation,
                "precipitation_raw": precipitation_raw,
                "rain_flag": int(rain_flag),
                "present_weather": weather_code,
                "visibility": visibility,
                "temperature": temperature,
                "relative_humidity": humidity,
                "wind_speed": wind,
            }

            # --- 5. keep the most complete row for this instant -------------
            # score = how many measurement fields are actually populated
            score = sum(
                value not in (None, "")
                for key, value in normalized.items()
                if key
                not in {
                    "station_key",
                    "station_id",
                    "timestamp_utc",
                    "timestamp_austin",
                    "source_timestamp_local_standard",
                }
            )
            previous = by_timestamp.get(noaa_instant)
            if previous is None or score > previous["_score"]:
                normalized["_score"] = score
                by_timestamp[noaa_instant] = normalized

    # --- write out, sorted by time (Step 4 relies on this order) -------------
    rows = []
    for timestamp in sorted(by_timestamp):
        row = dict(by_timestamp[timestamp])
        row.pop("_score", None)  # drop the internal scoring field
        rows.append(row)

    output_path = PROCESSED_DIR / f"weather_{station_key}_2021_jul_dec.csv"
    fieldnames = list(rows[0]) if rows else ["station_key", "timestamp_utc"]
    temporary = output_path.with_suffix(output_path.suffix + ".part")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output_path)

    audit = {
        "station_key": station_key,
        "name": station["name"],
        "station_id": station["station_id"],
        "records": len(rows),
        "first_timestamp_austin": rows[0]["timestamp_austin"] if rows else None,
        "last_timestamp_austin": rows[-1]["timestamp_austin"] if rows else None,
        "rain_flag_records": sum(int(row["rain_flag"]) for row in rows),
        "records_with_precipitation_value": sum(
            row["precipitation"] is not None for row in rows
        ),
        "records_with_visibility": sum(row["visibility"] is not None for row in rows),
        "processed_path": output_path.relative_to(ROOT).as_posix(),
        "processed_sha256": sha256_file(output_path),
    }
    return output_path, audit


def prepare_weather(config: dict[str, Any]) -> dict[str, Any]:
    weather = config["weather"]
    downloads: dict[str, Any] = {}
    stations: dict[str, Any] = {}

    for key, config_key in (("camp_mabry", "primary_station"), ("bergstrom", "secondary_station")):
        station = weather[config_key]
        # the archived file is named after the last segment of the source URL
        raw_path = RAW_NOAA_DIR / station["url"].rsplit("/", 1)[-1]
        require_file(raw_path, f"the NOAA raw file for {station['name']}")
        downloads[key] = {
            "source_url": station["url"],
            "path": raw_path.relative_to(ROOT).as_posix(),
            "bytes": raw_path.stat().st_size,
            "sha256": sha256_file(raw_path),
        }
        _, stations[key] = normalize_weather_station(key, station, raw_path)

    evidence = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "product": weather["product"],
        "citation_doi": weather["citation_doi"],
        "source_time_basis": weather["time_basis"],
        "normalization": (
            "Interpret NOAA timestamps as fixed UTC-06:00 local standard time, then convert "
            "to America/Chicago. This shifts summer observations to daylight time while preserving "
            "their physical instants."
        ),
        "downloads": downloads,
        "stations": stations,
    }
    write_json(AUDIT_DIR / "weather_source_audit.json", evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    ensure_dirs()
    evidence = prepare_weather(load_config())

    print("\nStep 2 complete.")
    for key, station in evidence["stations"].items():
        print(f"  {station['name']:<36} {station['records']:>6,} observations, "
              f"{station['rain_flag_records']:>4,} rain-flagged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
