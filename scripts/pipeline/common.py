"""
=============================================================================
 SHARED HELPERS  --  used by every step in this folder
=============================================================================

This file does NO data processing. It only holds small tools that every step
needs, so that each step script can stay short:

    * where files live on disk        (ROOT, AUDIT_DIR, RAW_..., PROCESSED_DIR)
    * reading the study settings      (load_config)
    * file fingerprints               (sha256_file)
    * safe file writing               (write_json, write_text)
    * the six cleaning rules          (clean_masks, clean_where)
    * reading messy NOAA values       (first_value, parse_flagged_number)

NO INTERNET
    Nothing in scripts/pipeline/ downloads anything. Every step reads our own
    saved copies of the data. The APC dataset is a closed 2021 archive, so the
    SHA-256 fingerprint we record already proves we used the right file.

SAFE WRITING
    Every file is first written as "name.part" and renamed only when finished.
    If the script crashes half-way, you never get a half-written file that
    looks complete.
=============================================================================
"""

import hashlib
import json
import re
from datetime import timedelta, timezone
from pathlib import Path


# -----------------------------------------------------------------------------
# WHERE EVERYTHING LIVES
# -----------------------------------------------------------------------------
# This file is <repo>/scripts/pipeline/common.py, so the repo folder is
# two levels above the folder this file is in.
ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_PATH = ROOT / "config" / "texas_capmetro_801.json"
AUDIT_DIR = ROOT / "data" / "audit" / "texas_capmetro"
RAW_CAPMETRO_DIR = ROOT / "data" / "raw" / "capmetro"
RAW_NOAA_DIR = ROOT / "data" / "raw" / "noaa"
PROCESSED_DIR = ROOT / "data" / "processed" / "texas_capmetro"

# The full raw file: 9,197,694 rows, every CapMetro route, 3.7 GB.
# It is too big for git. See the repository README for how to get it.
RAW_FULL_SNAPSHOT = RAW_CAPMETRO_DIR / "APC_Raw_July_2021_December_2021_full.csv"

UTC = timezone.utc

# NOAA writes its times in LOCAL STANDARD TIME and never switches to daylight
# saving time. So every NOAA time is "UTC minus 6 hours", all year round.
NOAA_LOCAL_STANDARD_TIME = timezone(timedelta(hours=-6), name="CST")

# NOAA numbers sometimes have a letter stuck on the end, e.g. "0.05s".
# This pattern finds the number part: an optional sign, digits, optional decimals.
NUMBER_PATTERN = re.compile(r"[-+]?\d+(?:\.\d+)?")


# -----------------------------------------------------------------------------
# SETTINGS AND FOLDERS
# -----------------------------------------------------------------------------
def load_config():
    """Read config/texas_capmetro_801.json and return it as a dictionary.

    Every setting (route, direction codes, study dates, weather stations, the
    90-minute join limit) lives in that file, not in the code.
    """
    text = CONFIG_PATH.read_text(encoding="utf-8")
    return json.loads(text)


def ensure_dirs():
    """Create the output folders if they do not exist yet."""
    for folder in [AUDIT_DIR, RAW_CAPMETRO_DIR, RAW_NOAA_DIR, PROCESSED_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# FINGERPRINTS AND SAFE WRITING
# -----------------------------------------------------------------------------
def sha256_file(path):
    """Return the SHA-256 fingerprint of a file.

    The file is read 1 MB at a time, so even the 3.7 GB file fits in memory.
    If even one byte of the file changes, the fingerprint changes completely.
    """
    digest = hashlib.sha256()
    one_megabyte = 1024 * 1024
    with open(path, "rb") as file:
        while True:
            block = file.read(one_megabyte)
            if not block:          # an empty block means we reached the end
                break
            digest.update(block)
    return digest.hexdigest()


def write_json(path, data):
    """Save a dictionary as a JSON file (keys sorted, so reruns look identical)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)        # rename .part -> real name only when done


def write_text(path, content):
    """Save a text (markdown) file, using the same .part-then-rename safety."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(content.rstrip() + "\n", encoding="utf-8")
    temporary.replace(path)


def require_file(path, what):
    """Stop with a clear message (not a long error) if an input file is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"\n\nMissing {what}:\n    {path}\n\n"
            "This pipeline reads our saved copies of the data and does not\n"
            "download anything. See 'Getting the data' in the repository README.\n"
        )
    return path


# -----------------------------------------------------------------------------
# THE SIX CLEANING RULES
# -----------------------------------------------------------------------------
def clean_masks(table, routes, directions):
    """Apply the six cleaning rules to a table of APC rows.

    A "mask" is a column of True/False values, one per row: True = keep the row.

      Rule 1  route_id is one of the routes we study
      Rule 2  route_id equals current_route_id   (the bus was really on that
              route at that moment, not in the middle of a reassignment)
      Rule 3  import_error is "0"                (the record loaded fine)
      Rule 4  import_trip_error is "0"           (the trip loaded fine)
      Rule 5  bs_id is not "0"                   (a real bus stop; 0 = unknown)
      Rule 6  direction_code_id is one we study

    None of the rules looks at passenger counts, so no row is ever removed just
    because its numbers look strange.

    The rules are applied one on top of the other, and we return all four
    stages because they are exactly the four bars of the cleaning funnel:
        on_route    passes rule 1
        matching    passes rules 1-2
        error_free  passes rules 1-4
        clean       passes rules 1-6   (this is the final study set)

    THIS IS THE OFFICIAL VERSION of the cleaning rules. Every step uses it.
    """
    routes = list(routes)
    directions = list(directions)

    # Rule 1
    on_route = table["route_id"].isin(routes)

    # Rule 2
    matching = on_route & (table["route_id"] == table["current_route_id"])

    # Rules 3 and 4
    error_free = matching & (table["import_error"] == "0") & (table["import_trip_error"] == "0")

    # Rules 5 and 6
    clean = error_free & (table["bs_id"] != "0") & table["direction_code_id"].isin(directions)

    return on_route, matching, error_free, clean


def clean_where(routes, directions):
    """The same six rules written as one readable SQL-style sentence.

    Nothing runs this text -- clean_masks() above is what actually filters.
    It is saved into the audit files so the rule can be quoted in one line.
    Example output for route 801, direction 6:
        route_id in ('801') and route_id=current_route_id and import_error='0'
        and import_trip_error='0' and bs_id<>'0' and direction_code_id in ('6')
    """
    quoted_routes = []
    for route in routes:
        quoted_routes.append("'" + route + "'")

    quoted_directions = []
    for direction in directions:
        quoted_directions.append("'" + direction + "'")

    return (
        "route_id in (" + ",".join(quoted_routes) + ") and route_id=current_route_id "
        "and import_error='0' and import_trip_error='0' and bs_id<>'0' "
        "and direction_code_id in (" + ",".join(quoted_directions) + ")"
    )


# -----------------------------------------------------------------------------
# READING MESSY NOAA VALUES  (used by step 2)
# -----------------------------------------------------------------------------
def first_value(row, *column_names):
    """Return the first non-empty value among several possible column names.

    NOAA sometimes spells a column "DATE" and sometimes "Date", so we try
    each spelling in turn. Returns "" if none of them has a value.
    """
    for name in column_names:
        value = row.get(name)
        if value is not None and value.strip() != "":
            return value.strip()
    return ""


def parse_flagged_number(value):
    """Turn a NOAA value into a number, ignoring any quality letter.

        "0.05s" -> 0.05        "72" -> 72.0        "" -> None
    """
    if not value:
        return None
    match = NUMBER_PATTERN.search(value.replace(",", ""))
    if match is None:
        return None
    return float(match.group())
