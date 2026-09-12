"""
=============================================================================
 SHARED HELPERS  --  used by every numbered step in this folder
=============================================================================

Nothing in this file does any data processing. It only holds the plumbing that
all five steps need, so each step script can stay short and readable:

    * where things live on disk          (ROOT, AUDIT_DIR, RAW_*, PROCESSED_DIR)
    * reading the frozen study config    (load_config)
    * checksums                          (sha256_file)
    * safe file writing                  (write_json, write_text)
    * the six cleaning rules             (clean_masks, clean_where)
    * NOAA quirk parsing                 (first_value, parse_flagged_number)

THIS PIPELINE NEVER TOUCHES THE INTERNET.
    Everything is computed from our own archived, checksummed copies of the
    source data. There is no download code anywhere in scripts/pipeline/ --
    `grep -r urllib scripts/pipeline/` returns nothing.

    That is deliberate. The APC dataset is a closed historical archive:
    published 2022-01-14, rows last updated 2022-01-14, covering July-December
    2021. It cannot change. Re-fetching it would prove nothing that the
    recorded SHA-256 does not already prove.

    See the README for how to obtain the source files on a new machine.

WHY SAFE WRITING MATTERS
    Every write goes to a ".part" file first and is renamed only once it has
    finished. If the script is interrupted half-way, the old good file is still
    there and the incomplete one is obviously named. We never end up with a
    half-written audit file that looks valid.
=============================================================================
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


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

# The archival snapshot: all 9,197,694 raw rows, every CapMetro route.
# Not in git (3.7 GB). See the README for how to get it.
RAW_FULL_SNAPSHOT = RAW_CAPMETRO_DIR / "APC_Raw_July_2021_December_2021_full.csv"

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
# READING THE ARCHIVED SNAPSHOT
# -----------------------------------------------------------------------------
def require_file(path: Path, what: str) -> Path:
    """Fail with a useful message instead of a stack trace when data is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"\n\nMissing {what}:\n    {path}\n\n"
            "This pipeline reads our archived copies of the source data and does\n"
            "not download anything. See the 'Getting the data' section of the\n"
            "repository README for how to obtain this file.\n"
        )
    return path




# -----------------------------------------------------------------------------
# THE CLEANING RULES
# -----------------------------------------------------------------------------
def clean_masks(
    frame: "pd.DataFrame", routes: Iterable[str], directions: Iterable[str]
) -> tuple["pd.Series", "pd.Series", "pd.Series", "pd.Series"]:
    """The six cleaning rules, as four CUMULATIVE boolean masks.

    THIS IS THE CANONICAL IMPLEMENTATION. Step 1 uses all four masks to build
    the cleaning funnel; Step 2 uses only the last one. Defining them here once
    means the funnel and the study set can never drift apart.

      1. route_id in (...)              keep only the route(s) we study
      2. route_id = current_route_id    the bus was actually running that route
                                        at that moment -- drops records logged
                                        during a mid-trip reassignment
      3. import_error = '0'             the record imported without error
      4. import_trip_error = '0'        the trip imported without error
      5. bs_id <> '0'                   a real bus stop; 0 means unknown
                                        (garage, deadhead, logon events)
      6. direction_code_id in (...)     keep only the direction(s) we study

    Every rule is a published field test. None is a judgement call, and none
    looks at a passenger count -- so no record is ever dropped for being
    inconvenient.

    Returns (on_route, matching, error_free, clean), each mask a superset of
    the next. Those four are exactly the bars on the cleaning-funnel slide.
    """
    routes, directions = list(routes), list(directions)

    on_route = frame["route_id"].isin(routes)                                    # 1
    matching = on_route & (frame["route_id"] == frame["current_route_id"])       # 2
    error_free = (                                                               # 3, 4
        matching
        & (frame["import_error"] == "0")
        & (frame["import_trip_error"] == "0")
    )
    clean = (                                                                    # 5, 6
        error_free
        & (frame["bs_id"] != "0")
        & frame["direction_code_id"].isin(directions)
    )
    return on_route, matching, error_free, clean


def clean_where(routes: Iterable[str], directions: Iterable[str]) -> str:
    """The same six rules written as an SQL-style predicate, for the record.

    Nothing executes this -- clean_masks() above is what actually runs.
    It exists so the audit files and the manuscript can quote the cleaning rule
    as a single readable line, and so anyone can re-run the identical filter
    against the public API if they ever want to.
    """
    route_values = ",".join(f"'{route}'" for route in routes)
    direction_values = ",".join(f"'{direction}'" for direction in directions)
    return (
        f"route_id in ({route_values}) and route_id=current_route_id "
        "and import_error='0' and import_trip_error='0' and bs_id<>'0' "
        f"and direction_code_id in ({direction_values})"
    )


# -----------------------------------------------------------------------------
# NOAA QUIRK PARSING  (used by step 3)
# -----------------------------------------------------------------------------
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
