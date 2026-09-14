"""
=============================================================================
 STEP 2 OF 4  --  CLEAN UP THE NOAA WEATHER OBSERVATIONS
=============================================================================

WHY THIS STEP EXISTS
    The bus data has no weather column. Weather comes from NOAA weather
    stations, and it must be put on the same clock as the bus data before the
    two can be matched. This step fixes the clock; Step 3 does the matching.

THE TWO STATIONS
    Camp Mabry        USW00013958   main station, beside the corridor
    Austin-Bergstrom  USW00013904   second station, used as a cross-check

THE TRICKY PART: TIME ZONES
    NOAA writes times in LOCAL STANDARD TIME and never uses daylight saving.
    So in July, a NOAA time of "15:00" is really 16:00 on an Austin clock.
    If we ignored this, every summer reading would be one hour off.

    So for every reading we:
        1. treat the NOAA time as "UTC minus 6 hours",
        2. convert it to Austin time (America/Chicago),
        3. save BOTH the UTC time and the Austin time.

WHAT COUNTS AS RAIN  (rain_flag = 1 if ANY of these is true)
    * the precipitation amount is more than zero
    * the precipitation field is "T" (a trace of rain)
    * the weather code contains RA (rain), DZ (drizzle) or TS (thunderstorm)

DUPLICATES
    NOAA sometimes sends two reports for the same minute. We keep the one with
    the most filled-in fields.

INPUT    data/raw/noaa/LCD_USW00013958_2021.csv   (Camp Mabry)
         data/raw/noaa/LCD_USW00013904_2021.csv   (Bergstrom)
OUTPUT   data/processed/texas_capmetro/weather_camp_mabry_2021_jul_dec.csv
         data/processed/texas_capmetro/weather_bergstrom_2021_jul_dec.csv
         data/audit/texas_capmetro/weather_source_audit.json

RUN      python scripts/pipeline/02_prepare_weather.py     (a few seconds)
=============================================================================
"""

import csv
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

STUDY_START = date(2021, 7, 1)
STUDY_END = date(2021, 12, 31)
AUSTIN = ZoneInfo("America/Chicago")

# Columns that describe WHERE/WHEN a reading is from, not a measurement.
# They are ignored when we score how complete a reading is.
LABEL_COLUMNS = ["station_key", "station_id", "timestamp_utc", "timestamp_austin",
                 "source_timestamp_local_standard"]


def clean_one_station(station_key, station, raw_file):
    """Read one raw NOAA file and write a clean, time-corrected table.

    Returns a small summary (the "audit") of what was written.
    """
    # One entry per UTC time. If a time appears twice, we keep the better row.
    best_row_at_time = {}
    score_at_time = {}

    with open(raw_file, "r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):

            # ---- 1. read the time ------------------------------------------
            date_text = common.first_value(row, "DATE", "Date")
            if date_text == "":
                continue                                    # no time: skip row
            try:
                reading_time = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
            except ValueError:
                continue                                    # unreadable time: skip row

            if reading_time.tzinfo is not None:
                # The time already says its own time zone, so trust it.
                time_utc = reading_time.astimezone(common.UTC)
            else:
                # Normal case: NOAA local standard time = UTC-06:00, all year.
                time_utc = reading_time.replace(tzinfo=common.NOAA_LOCAL_STANDARD_TIME)
                time_utc = time_utc.astimezone(common.UTC)

            time_austin = time_utc.astimezone(AUSTIN)

            # ---- 2. keep only July-December 2021 ---------------------------
            if time_austin.date() < STUDY_START or time_austin.date() > STUDY_END:
                continue

            # ---- 3. read the measurements ----------------------------------
            precipitation_text = common.first_value(row, "HourlyPrecipitation")
            weather_code = common.first_value(row, "HourlyPresentWeatherType", "HourlyWeatherType")
            temperature = common.parse_flagged_number(common.first_value(row, "HourlyDryBulbTemperature"))
            humidity = common.parse_flagged_number(common.first_value(row, "HourlyRelativeHumidity"))
            wind = common.parse_flagged_number(common.first_value(row, "HourlyWindSpeed"))
            visibility = common.parse_flagged_number(common.first_value(row, "HourlyVisibility"))
            precipitation = common.parse_flagged_number(precipitation_text)

            # Skip office/admin rows that contain no measurement at all.
            has_a_measurement = False
            for value in [temperature, humidity, wind, visibility, precipitation]:
                if value is not None:
                    has_a_measurement = True
            if weather_code != "":
                has_a_measurement = True
            if not has_a_measurement:
                continue

            # ---- 4. decide whether it was raining --------------------------
            is_trace = precipitation_text.upper().startswith("T")
            has_rain_amount = precipitation is not None and precipitation > 0
            has_rain_code = False
            for code in ["RA", "DZ", "TS"]:
                if code in weather_code.upper():
                    has_rain_code = True

            if is_trace or has_rain_amount or has_rain_code:
                rain_flag = 1
            else:
                rain_flag = 0

            clean_row = {
                "station_key": station_key,
                "station_id": station["station_id"],
                "timestamp_utc": time_utc.isoformat(),
                "timestamp_austin": time_austin.isoformat(),
                "source_timestamp_local_standard": date_text,
                "report_type": common.first_value(row, "REPORT_TYPE", "ReportType"),
                "precipitation": precipitation,
                "precipitation_raw": precipitation_text,
                "rain_flag": rain_flag,
                "present_weather": weather_code,
                "visibility": visibility,
                "temperature": temperature,
                "relative_humidity": humidity,
                "wind_speed": wind,
            }

            # ---- 5. if this time was already seen, keep the fuller row ------
            score = 0
            for column, value in clean_row.items():
                if column in LABEL_COLUMNS:
                    continue
                if value is not None and value != "":
                    score = score + 1

            if time_utc not in best_row_at_time or score > score_at_time[time_utc]:
                best_row_at_time[time_utc] = clean_row
                score_at_time[time_utc] = score

    # ---- write the rows out, oldest first --------------------------------------
    rows = []
    for time_utc in sorted(best_row_at_time):
        rows.append(best_row_at_time[time_utc])

    output_file = common.PROCESSED_DIR / f"weather_{station_key}_2021_jul_dec.csv"
    if len(rows) > 0:
        column_names = list(rows[0].keys())
    else:
        column_names = ["station_key", "timestamp_utc"]

    temporary_file = output_file.with_suffix(output_file.suffix + ".part")
    with open(temporary_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(rows)
    temporary_file.replace(output_file)

    # ---- summary numbers for the audit file ------------------------------------
    rain_rows = 0
    rows_with_precipitation = 0
    rows_with_visibility = 0
    for row in rows:
        rain_rows = rain_rows + row["rain_flag"]
        if row["precipitation"] is not None:
            rows_with_precipitation = rows_with_precipitation + 1
        if row["visibility"] is not None:
            rows_with_visibility = rows_with_visibility + 1

    if len(rows) > 0:
        first_time = rows[0]["timestamp_austin"]
        last_time = rows[-1]["timestamp_austin"]
    else:
        first_time = None
        last_time = None

    audit = {
        "station_key": station_key,
        "name": station["name"],
        "station_id": station["station_id"],
        "records": len(rows),
        "first_timestamp_austin": first_time,
        "last_timestamp_austin": last_time,
        "rain_flag_records": rain_rows,
        "records_with_precipitation_value": rows_with_precipitation,
        "records_with_visibility": rows_with_visibility,
        "processed_path": output_file.relative_to(common.ROOT).as_posix(),
        "processed_sha256": common.sha256_file(output_file),
    }
    return audit


def prepare_weather(config):
    """Clean both stations and write weather_source_audit.json."""
    weather = config["weather"]
    downloads = {}
    stations = {}

    # (short name used in file names, name of the station block in the config)
    for station_key, config_key in [("camp_mabry", "primary_station"),
                                    ("bergstrom", "secondary_station")]:
        station = weather[config_key]

        # Our saved raw file has the same name as the last part of the NOAA URL.
        raw_file = common.RAW_NOAA_DIR / station["url"].split("/")[-1]
        common.require_file(raw_file, f"the NOAA raw file for {station['name']}")

        downloads[station_key] = {
            "source_url": station["url"],
            "path": raw_file.relative_to(common.ROOT).as_posix(),
            "bytes": raw_file.stat().st_size,
            "sha256": common.sha256_file(raw_file),
        }
        stations[station_key] = clean_one_station(station_key, station, raw_file)

    evidence = {
        "generated_utc": datetime.now(common.UTC).isoformat(),
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
    common.write_json(common.AUDIT_DIR / "weather_source_audit.json", evidence)
    return evidence


def main():
    common.ensure_dirs()
    evidence = prepare_weather(common.load_config())

    print("\nStep 2 complete.")
    for station in evidence["stations"].values():
        print(f"  {station['name']:<36} {station['records']:>6,} observations, "
              f"{station['rain_flag_records']:>4,} rain-flagged")


if __name__ == "__main__":
    main()
