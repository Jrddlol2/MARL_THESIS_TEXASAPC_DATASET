"""
=============================================================================
 SHARED HELPERS  --  used by every numbered step in this folder
=============================================================================

Nothing in this file does any data processing. It only holds the plumbing that
all five steps need, so that each step script can stay short and readable:

    * where things live on disk          (ROOT, AUDIT_DIR, RAW_* , PROCESSED_DIR)
    * reading the frozen study config    (load_config)
    * checksums                          (sha256_file)
    * safe file writing                  (write_json, write_text)
    * downloading                        (open_url, fetch_json, download_file)
    * paging the Texas Open Data API     (download_soda_csv)
    * the six cleaning rules             (clean_where)
    * tolerant number parsing            (safe_int, safe_float)

WHY SAFE WRITING MATTERS
    Every write goes to a ".part" file first and is renamed only once it has
    finished. If the script is interrupted half-way, the old good file is still
    there and the incomplete one is obviously named. We never end up with a
    half-written audit file that looks valid.

WHY EVERY DOWNLOAD IS CHECKSUMMED
    The whole provenance argument rests on being able to say "this exact file,
    with this exact SHA-256, produced these exact numbers". Each download
    returns a small manifest dict recording url / path / bytes / sha256, and
    the step scripts write those manifests into data/audit/texas_capmetro/.

This file is a direct extraction from scripts/texas_capmetro_pipeline.py.
The logic is unchanged -- only the comments are new.
=============================================================================
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


# -----------------------------------------------------------------------------
# WHERE EVERYTHING LIVES
# -----------------------------------------------------------------------------
# parents[2] because this file sits at  <repo>/scripts/pipeline/common.py
ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT / "config" / "texas_capmetro_801.json"
AUDIT_DIR = ROOT / "data" / "audit" / "texas_capmetro"
RAW_CAPMETRO_DIR = ROOT / "data" / "raw" / "capmetro"
RAW_NOAA_DIR = ROOT / "data" / "raw" / "noaa"
PROCESSED_DIR = ROOT / "data" / "processed" / "texas_capmetro"

# Identify ourselves politely to the public APIs we call.
USER_AGENT = "MARL-thesis-public-data-audit/1.0 (academic reproducibility)"

# The Socrata API caps a single response, so we ask for 50,000 rows at a time
# and page through with $offset until a short page comes back.
PAGE_SIZE = 50_000

UTC = timezone.utc

# NOAA Local Climatological Data timestamps are in LOCAL STANDARD TIME with no
# daylight-saving adjustment -- that is NOAA's documented convention, not a
# guess. We therefore read them as a fixed UTC-06:00 offset and convert from
# there. Getting this wrong would shift every summer observation by one hour.
NOAA_LOCAL_STANDARD_TIME = timezone(timedelta(hours=-6), name="CST")

# NOAA numeric fields sometimes carry a trailing quality letter, e.g. "0.05s".
# This pulls the number back out.
NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")


# -----------------------------------------------------------------------------
# CONFIG AND DIRECTORIES
# -----------------------------------------------------------------------------
def load_config() -> dict[str, Any]:
    """Read config/texas_capmetro_801.json.

    Every tunable value -- routes, direction codes, the study window, the NOAA
    stations, the 90-minute join tolerance -- lives in that file, NOT in code.
    If you need to change what the pipeline does, change the config.
    """
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def ensure_dirs() -> None:
    """Create the output folders if they are not there yet."""
    for path in (AUDIT_DIR, RAW_CAPMETRO_DIR, RAW_NOAA_DIR, PROCESSED_DIR):
        path.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# CHECKSUMS AND SAFE WRITING
# -----------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    """SHA-256 of a file, read 1 MB at a time so a 3.7 GB file fits in memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    """Write an audit file. sort_keys keeps the output stable run-to-run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def write_text(path: Path, content: str) -> None:
    """Write a markdown evidence file, same .part-then-rename safety."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(content.rstrip() + "\n", encoding="utf-8")
    temporary.replace(path)


# -----------------------------------------------------------------------------
# NETWORK
# -----------------------------------------------------------------------------
def open_url(url: str, *, attempts: int = 4, timeout: int = 180):
    """Open a URL, retrying with a growing pause (2s, 4s, 8s) on failure.

    Public data portals occasionally time out. Retrying means a long download
    does not die on one bad moment.
    """
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
    """GET a URL and parse the response as JSON."""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    with open_url(url) as response:
        return json.load(io.TextIOWrapper(response, encoding="utf-8-sig"))


def download_file(url: str, destination: Path, *, force: bool = False) -> dict[str, Any]:
    """Download a whole file, streamed 1 MB at a time.

    If the file is already on disk we reuse it and record
    "reused_existing_file": True, so re-running the pipeline is free and safe.
    Pass force=True to redownload anyway.
    """
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


# -----------------------------------------------------------------------------
# THE TEXAS OPEN DATA (SOCRATA) API
# -----------------------------------------------------------------------------
def soda_url(base: str, params: dict[str, str]) -> str:
    """Build a Socrata query URL from a parameter dict."""
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
    """Download a filtered CSV from the Texas Open Data portal, one page at a time.

    THIS IS THE IMPORTANT DESIGN CHOICE IN THE WHOLE PIPELINE.

    The `where` string is sent to the portal, so the FILTERING HAPPENS ON THEIR
    SERVERS. We never download all 9.2 million raw rows just to throw most of
    them away. What arrives is already clean.

    Because the query is a plain string, it can be quoted verbatim in the
    manuscript and on a slide -- the cleaning rule is auditable text, not a
    sequence of clicks in a spreadsheet.

    Returns a manifest recording the endpoint, the exact query, row count,
    file size and SHA-256.
    """
    select_text = ",".join(select)
    query_definition = {
        "$select": select_text,
        "$where": where,
        "$order": order,
        "$limit": str(PAGE_SIZE),
    }

    # Already downloaded? Reuse it and just re-count / re-checksum.
    if destination.exists() and not force:
        with destination.open("r", encoding="utf-8-sig", newline="") as handle:
            row_count = sum(1 for _ in handle) - 1  # minus the header line
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

            # A short page means we have reached the end.
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


# -----------------------------------------------------------------------------
# THE CLEANING RULE
# -----------------------------------------------------------------------------
def clean_where(routes: Iterable[str], directions: Iterable[str]) -> str:
    """Build the six-part cleaning predicate as a Socrata WHERE clause.

    The six rules, in the order they appear in the string:

      1. route_id in (...)                 keep only the route(s) we study
      2. route_id = current_route_id       the bus was actually running that
                                           route at that moment -- drops records
                                           logged during a mid-trip reassignment
      3. import_error = '0'                the record imported without error
      4. import_trip_error = '0'           the trip imported without error
      5. bs_id <> '0'                      a real bus stop; 0 means unknown
                                           (garage, deadhead, logon events)
      6. direction_code_id in (...)        keep only the direction(s) we study

    Every rule is a published field test. None of them is a judgement call, and
    none of them looks at a passenger count -- so no record is ever dropped for
    being inconvenient.
    """
    route_values = ",".join(f"'{route}'" for route in routes)
    direction_values = ",".join(f"'{direction}'" for direction in directions)
    return (
        f"route_id in ({route_values}) and route_id=current_route_id "
        "and import_error='0' and import_trip_error='0' and bs_id<>'0' "
        f"and direction_code_id in ({direction_values})"
    )


# -----------------------------------------------------------------------------
# THE SAME SIX RULES, APPLIED LOCALLY
# -----------------------------------------------------------------------------
# The archival snapshot: all 9,197,694 raw rows, every CapMetro route.
# This file is NOT needed for the normal (API) path -- the portal does the
# filtering for us there. It is used only by the --local path below.
RAW_FULL_SNAPSHOT = RAW_CAPMETRO_DIR / "APC_Raw_July_2021_December_2021_full.csv"


def passes_clean_rules(
    row: dict[str, str], routes: Iterable[str], directions: Iterable[str]
) -> bool:
    """Python version of clean_where(), rule for rule, in the same order.

    This exists so the offline path applies EXACTLY the same six tests as the
    Socrata query. Keep the two in step: if you change one, change the other.

        clean_where()        -> a string the portal executes
        passes_clean_rules() -> the same logic executed here

    They are checked against each other every time both paths are run: both
    must yield 229,421 rows for direction 6.
    """
    return (
        row["route_id"] in routes                          # 1. the route we study
        and row["route_id"] == row["current_route_id"]     # 2. not mid-reassignment
        and row["import_error"] == "0"                     # 3. record imported cleanly
        and row["import_trip_error"] == "0"                # 4. trip imported cleanly
        and row["bs_id"] != "0"                            # 5. a real bus stop
        and row["direction_code_id"] in directions         # 6. the direction we study
    )


def stream_raw_snapshot(path: Path | None = None):
    """Yield the archival snapshot one row at a time.

    9.2 million rows is far too much to hold in memory, so this is a generator:
    each row is read, handed to the caller, and thrown away. Memory use stays
    flat no matter how big the file is.
    """
    source = path or RAW_FULL_SNAPSHOT
    if not source.exists():
        raise FileNotFoundError(
            f"Archival snapshot not found: {source}\n"
            "The --local path needs the full 3.7 GB export. Use the API path "
            "(omit --local) if you do not have it."
        )
    csv.field_size_limit(10**9)
    with source.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


# -----------------------------------------------------------------------------
# TOLERANT PARSING
# -----------------------------------------------------------------------------
# The Socrata portal types ALL 47 columns as text, so every numeric field has
# to be parsed explicitly. These two helpers return None instead of crashing on
# a blank or malformed value.

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


def first_value(row: dict[str, str], *names: str) -> str:
    """Return the first non-empty value among several possible column names.

    NOAA changes its column capitalisation between files ("DATE" vs "Date"),
    so we try a few spellings rather than assuming one.
    """
    for name in names:
        value = row.get(name)
        if value is not None and value.strip() != "":
            return value.strip()
    return ""


def parse_flagged_number(value: str) -> float | None:
    """Pull a number out of a NOAA value that may carry a quality flag.

    e.g. "0.05s" -> 0.05 ,  "" -> None
    """
    if not value:
        return None
    match = NUMBER_RE.search(value.replace(",", ""))
    return float(match.group()) if match else None
