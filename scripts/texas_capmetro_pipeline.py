#!/usr/bin/env python3
"""Reproduce the CapMetro Route 801 evidence package from public sources.

Only compact audit outputs and manifests are intended for Git. Raw downloads
and processed inputs are written beneath ignored data directories.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import math
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "texas_capmetro_801.json"
AUDIT_DIR = ROOT / "data" / "audit" / "texas_capmetro"
RAW_CAPMETRO_DIR = ROOT / "data" / "raw" / "capmetro"
RAW_NOAA_DIR = ROOT / "data" / "raw" / "noaa"
PROCESSED_DIR = ROOT / "data" / "processed" / "texas_capmetro"
USER_AGENT = "MARL-thesis-public-data-audit/1.0 (academic reproducibility)"
PAGE_SIZE = 50_000
UTC = timezone.utc
NOAA_LOCAL_STANDARD_TIME = timezone(timedelta(hours=-6), name="CST")
NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def ensure_dirs() -> None:
    for path in (AUDIT_DIR, RAW_CAPMETRO_DIR, RAW_NOAA_DIR, PROCESSED_DIR):
        path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(content.rstrip() + "\n", encoding="utf-8")
    temporary.replace(path)


def open_url(url: str, *, attempts: int = 4, timeout: int = 180):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts:
                raise
            time.sleep(min(2**attempt, 8))
    raise RuntimeError("unreachable")


def fetch_json(url: str, params: dict[str, str] | None = None) -> Any:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    with open_url(url) as response:
        return json.load(io.TextIOWrapper(response, encoding="utf-8-sig"))


def download_file(url: str, destination: Path, *, force: bool = False) -> dict[str, Any]:
    if destination.exists() and not force:
        return {
            "url": url,
            "path": destination.relative_to(ROOT).as_posix(),
            "bytes": destination.stat().st_size,
            "sha256": sha256_file(destination),
            "reused_existing_file": True,
        }
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    with open_url(url) as response, temporary.open("wb") as output:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            output.write(block)
    temporary.replace(destination)
    return {
        "url": url,
        "path": destination.relative_to(ROOT).as_posix(),
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "reused_existing_file": False,
    }


def soda_url(base: str, params: dict[str, str]) -> str:
    return base + "?" + urllib.parse.urlencode(params)


def download_soda_csv(
    *,
    base_url: str,
    destination: Path,
    select: Iterable[str],
    where: str,
    order: str,
    force: bool = False,
) -> dict[str, Any]:
    select_text = ",".join(select)
    query_definition = {
        "$select": select_text,
        "$where": where,
        "$order": order,
        "$limit": str(PAGE_SIZE),
    }
    if destination.exists() and not force:
        with destination.open("r", encoding="utf-8-sig", newline="") as handle:
            row_count = sum(1 for _ in handle) - 1
        return {
            "endpoint": base_url,
            "query": query_definition,
            "path": destination.relative_to(ROOT).as_posix(),
            "rows": max(row_count, 0),
            "bytes": destination.stat().st_size,
            "sha256": sha256_file(destination),
            "reused_existing_file": True,
        }

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    total_rows = 0
    fieldnames: list[str] | None = None
    with temporary.open("w", encoding="utf-8", newline="") as output:
        writer: csv.DictWriter[str] | None = None
        offset = 0
        while True:
            params = dict(query_definition)
            params["$offset"] = str(offset)
            url = soda_url(base_url, params)
            with open_url(url) as response:
                text_stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
                reader = csv.DictReader(text_stream)
                page_rows = list(reader)
                if fieldnames is None:
                    fieldnames = reader.fieldnames or list(select)
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                assert writer is not None
                writer.writerows(page_rows)
            page_count = len(page_rows)
            total_rows += page_count
            print(f"Downloaded {total_rows:,} rows -> {destination.name}", flush=True)
            if page_count < PAGE_SIZE:
                break
            offset += PAGE_SIZE
    temporary.replace(destination)
    return {
        "endpoint": base_url,
        "query": query_definition,
        "path": destination.relative_to(ROOT).as_posix(),
        "rows": total_rows,
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "reused_existing_file": False,
    }


def clean_where(routes: Iterable[str], directions: Iterable[str]) -> str:
    route_values = ",".join(f"'{route}'" for route in routes)
    direction_values = ",".join(f"'{direction}'" for direction in directions)
    return (
        f"route_id in ({route_values}) and route_id=current_route_id "
        "and import_error='0' and import_trip_error='0' and bs_id<>'0' "
        f"and direction_code_id in ({direction_values})"
    )


def safe_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def safe_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def summarize_rows(path: Path) -> dict[str, Any]:
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
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            route = row["route_id"]
            direction = row["direction_code_id"]
            item = metrics[route]
            item["records"] += 1
            item["direction_records"][direction] += 1
            ons = safe_int(row.get("ons")) or 0
            offs = safe_int(row.get("offs")) or 0
            item["boardings"] += ons
            item["alightings"] += offs
            item["direction_boardings"][direction] += ons
            load = safe_float(row.get("max_load"))
            dwell = safe_float(row.get("dwell_time"))
            if load is not None:
                item["loads"].append(load)
            if dwell is not None:
                item["dwells"].append(dwell)
            transit_day = (row.get("transit_date_time") or "")[:8]
            if transit_day:
                item["days"].add(transit_day)
            stop_id = row.get("bs_id") or ""
            if stop_id:
                item["stops_by_direction"][direction].add(stop_id)
            ext_trip_id = row.get("ext_trip_id") or ""
            fallback = (row.get("act_trip_start_time") or "") + "|" + (
                row.get("vehicle_id") or ""
            )
            trip_key = (transit_day, ext_trip_id or fallback)
            item["trips"].add(trip_key)
            item["direction_trips"][direction].add(trip_key)
            seconds = safe_float(row.get("rev_seconds"))
            distance = safe_float(row.get("rev_distance"))
            if seconds is not None and distance is not None and seconds > 0 and distance > 0:
                item["usable_segments"] += 1
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


def aggregate_route_counts(base: str, where: str) -> dict[str, int]:
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


def audit_routes(config: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    apc = config["apc"]
    candidates = config["study"]["candidate_routes"]
    metadata = fetch_json(apc["metadata_url"])
    write_json(AUDIT_DIR / "socrata_metadata.json", metadata)
    all_routes_where = "route_id in (" + ",".join(f"'{r}'" for r in candidates) + ")"
    matching_where = all_routes_where + " and route_id=current_route_id"
    error_free_where = matching_where + " and import_error='0' and import_trip_error='0'"
    total_counts = aggregate_route_counts(apc["resource_json_url"], all_routes_where)
    matching_counts = aggregate_route_counts(apc["resource_json_url"], matching_where)
    error_free_counts = aggregate_route_counts(apc["resource_json_url"], error_free_where)

    comparison_fields = [
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
    comparison_path = RAW_CAPMETRO_DIR / "route_801_803_clean_comparison.csv"
    comparison_manifest = download_soda_csv(
        base_url=apc["resource_csv_url"],
        destination=comparison_path,
        select=comparison_fields,
        where=clean_where(candidates, ["4", "6"]),
        order="route_id,apc_date_time,vehicle_id,actual_sequence,bs_id",
        force=force,
    )
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


def download_primary_subset(config: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    apc = config["apc"]
    metadata_path = AUDIT_DIR / "socrata_metadata.json"
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.exists()
        else fetch_json(apc["metadata_url"])
    )
    fields = [column["fieldName"] for column in metadata["columns"]]
    destination = ROOT / apc["raw_output"]
    manifest = download_soda_csv(
        base_url=apc["resource_csv_url"],
        destination=destination,
        select=fields,
        where=clean_where(["801"], ["6"]),
        order="apc_date_time,vehicle_id,actual_sequence,bs_id",
        force=force,
    )
    manifest.update(
        {
            "generated_utc": datetime.now(UTC).isoformat(),
            "route_id": "801",
            "direction_code": "6",
            "direction_label": None,
            "direction_label_gate": "2021-compatible GTFS not yet verified",
            "column_count": len(fields),
        }
    )
    write_json(AUDIT_DIR / "primary_subset_manifest.json", manifest)
    return manifest


def first_value(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name)
        if value is not None and value.strip() != "":
            return value.strip()
    return ""


def parse_flagged_number(value: str) -> float | None:
    if not value:
        return None
    match = NUMBER_RE.search(value.replace(",", ""))
    return float(match.group()) if match else None


def normalize_weather_station(
    station_key: str, station: dict[str, Any], raw_path: Path
) -> tuple[Path, dict[str, Any]]:
    start_date = date(2021, 7, 1)
    end_date = date(2021, 12, 31)
    austin = ZoneInfo("America/Chicago")
    by_timestamp: dict[datetime, dict[str, Any]] = {}
    with raw_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            date_value = first_value(row, "DATE", "Date")
            if not date_value:
                continue
            try:
                naive = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
            except ValueError:
                continue
            if naive.tzinfo is not None:
                noaa_instant = naive.astimezone(UTC)
            else:
                noaa_instant = naive.replace(tzinfo=NOAA_LOCAL_STANDARD_TIME).astimezone(UTC)
            local = noaa_instant.astimezone(austin)
            if not (start_date <= local.date() <= end_date):
                continue
            precipitation_raw = first_value(row, "HourlyPrecipitation")
            weather_code = first_value(row, "HourlyPresentWeatherType", "HourlyWeatherType")
            temperature = parse_flagged_number(first_value(row, "HourlyDryBulbTemperature"))
            humidity = parse_flagged_number(first_value(row, "HourlyRelativeHumidity"))
            wind = parse_flagged_number(first_value(row, "HourlyWindSpeed"))
            visibility = parse_flagged_number(first_value(row, "HourlyVisibility"))
            precipitation = parse_flagged_number(precipitation_raw)
            has_hourly_measurement = any(
                value is not None
                for value in (temperature, humidity, wind, visibility, precipitation)
            ) or bool(weather_code)
            if not has_hourly_measurement:
                continue
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

    rows = []
    for timestamp in sorted(by_timestamp):
        row = dict(by_timestamp[timestamp])
        row.pop("_score", None)
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


def prepare_weather(config: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    weather = config["weather"]
    downloads: dict[str, Any] = {}
    stations: dict[str, Any] = {}
    for key, config_key in (("camp_mabry", "primary_station"), ("bergstrom", "secondary_station")):
        station = weather[config_key]
        raw_path = RAW_NOAA_DIR / Path(urllib.parse.urlparse(station["url"]).path).name
        downloads[key] = download_file(station["url"], raw_path, force=force)
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


def parse_apc_datetime(value: str, austin: ZoneInfo) -> tuple[datetime, bool]:
    naive = datetime.strptime(value, "%Y%m%d%H%M%S")
    first = naive.replace(tzinfo=austin, fold=0)
    second = naive.replace(tzinfo=austin, fold=1)
    ambiguous = first.utcoffset() != second.utcoffset()
    return first.astimezone(UTC), ambiguous


def load_weather_index(path: Path) -> tuple[list[float], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    instants: list[float] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            instant = datetime.fromisoformat(row["timestamp_utc"]).timestamp()
            instants.append(instant)
            rows.append(row)
    return instants, rows


def nearest_weather(
    target: float, instants: list[float], rows: list[dict[str, str]], tolerance_seconds: int
) -> tuple[dict[str, str] | None, float | None]:
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
            f"Primary APC subset is missing: {primary_path}. Run download-primary first."
        )
    primary_weather_path = PROCESSED_DIR / "weather_camp_mabry_2021_jul_dec.csv"
    secondary_weather_path = PROCESSED_DIR / "weather_bergstrom_2021_jul_dec.csv"
    if not primary_weather_path.exists() or not secondary_weather_path.exists():
        raise FileNotFoundError("Normalized weather files are missing. Run weather first.")

    primary_instants, primary_rows = load_weather_index(primary_weather_path)
    secondary_instants, secondary_rows = load_weather_index(secondary_weather_path)
    austin = ZoneInfo(config["study"]["timezone"])
    tolerance_seconds = int(config["weather"]["nearest_join_tolerance_minutes"]) * 60
    counts = defaultdict(int)
    join_deltas: list[float] = []
    wet_segment_seconds: list[float] = []
    dry_segment_seconds: list[float] = []
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
            primary_weather, delta = nearest_weather(
                target, primary_instants, primary_rows, tolerance_seconds
            )
            if primary_weather is None:
                counts["primary_unmatched"] += 1
                continue
            counts["primary_matched"] += 1
            assert delta is not None
            join_deltas.append(delta / 60)
            primary_rain = int(primary_weather["rain_flag"])
            counts["primary_rain_exposed_rows"] += primary_rain
            seconds = safe_float(row.get("rev_seconds"))
            distance = safe_float(row.get("rev_distance"))
            if seconds is not None and distance is not None and seconds > 0 and distance > 0:
                (wet_segment_seconds if primary_rain else dry_segment_seconds).append(seconds)
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

    apc_rows = counts["apc_rows"]
    primary_matched = counts["primary_matched"]
    secondary_matched = counts["secondary_matched"]
    join_coverage = primary_matched / apc_rows if apc_rows else 0
    rain_sample = counts["primary_rain_exposed_rows"]
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
        "secondary_join_coverage_percent": round(
            100 * secondary_matched / apc_rows, 3
        )
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


def write_gtfs_gate(config: dict[str, Any]) -> None:
    gtfs = config["gtfs"]
    write_json(
        AUDIT_DIR / "gtfs_retrieval_attempts.json",
        {
            "generated_utc": datetime.now(UTC).isoformat(),
            "required_service_window": gtfs["required_service_window"],
            "status": gtfs["status"],
            "attempts": gtfs["retrieval_attempts"],
            "gate": gtfs["gate"],
        },
    )
    attempt_lines = "\n".join(
        f"- **{attempt['source']}:** {attempt['result']}"
        for attempt in gtfs["retrieval_attempts"]
    )
    content = f"""# Historical GTFS acquisition gate

Status: **open - a 2021-compatible snapshot has not yet been checksum-verified.**

Required service window: `{gtfs['required_service_window'][0]}` through
`{gtfs['required_service_window'][1]}`.

The current official feed is publicly available at
`{gtfs['current_official_feed']}`, but it is not valid evidence for a 2021 route
mapping. Candidate historical sources are {gtfs['candidate_archive']}.

## Retrieval attempts

{attempt_lines}

Until the gate closes, the manuscript and code must:

- refer to APC direction `6` by code only;
- avoid assigning northbound/southbound labels from the current schedule;
- avoid claiming historical stop names, route shapes, or scheduled headways; and
- keep schedule-derived parameters as `%TODO-DATA`.

This is a source-availability limitation, not a failed weather/APC feasibility
check. The APC records themselves contain stop IDs and stop-event coordinates,
so segment-level empirical work can proceed while authoritative 2021 schedule
semantics remain gated.
"""
    write_text(AUDIT_DIR / "GTFS_ACQUISITION_STATUS.md", content)


def run_all(config: dict[str, Any], *, force: bool = False) -> None:
    audit_routes(config, force=force)
    download_primary_subset(config, force=force)
    prepare_weather(config, force=force)
    audit_weather_join(config)
    write_gtfs_gate(config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("all", "audit-routes", "download-primary", "weather", "join-weather", "gtfs-status"),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload raw files instead of reusing checksum-recorded local copies",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ensure_dirs()
    config = load_config()
    if args.command == "all":
        run_all(config, force=args.force)
    elif args.command == "audit-routes":
        audit_routes(config, force=args.force)
    elif args.command == "download-primary":
        download_primary_subset(config, force=args.force)
    elif args.command == "weather":
        prepare_weather(config, force=args.force)
    elif args.command == "join-weather":
        audit_weather_join(config)
    elif args.command == "gtfs-status":
        write_gtfs_gate(config)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted; any incomplete download remains a .part file.", file=sys.stderr)
        raise SystemExit(130)
