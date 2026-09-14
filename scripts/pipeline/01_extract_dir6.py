"""
=============================================================================
 STEP 1 OF 4  --  EXTRACT THE DIRECTION-6 STUDY SET
=============================================================================

WHAT IT MAKES
    route_801_direction_6_clean.csv  --  229,421 rows, all 47 columns.
    This is the FINAL STUDY SET that every later step uses.

WHAT IT DOES
    Reads the 3.7 GB raw file one million rows at a time, and keeps only the
    rows that pass the six cleaning rules for Route 801, direction 6.

WHY KEEP ALL 47 COLUMNS
    The simulator only needs about 13, but keeping every column makes this
    file a complete record of what we studied.

WHY DIRECTION 6
    Headway (the gap between buses) only makes sense between buses going the
    same way, so we study one direction. Direction 6 has more clean records
    (229,421 vs 226,233) and more boardings (420,201 vs 390,108) than
    direction 4 on the same 29 stops. The compass name of "6" (north/south)
    is not assigned here -- see Step 4.

INPUT    data/raw/capmetro/APC_Raw_July_2021_December_2021_full.csv
OUTPUT   data/raw/capmetro/route_801_direction_6_clean.csv
         data/audit/texas_capmetro/primary_subset_manifest.json

RUN      python scripts/pipeline/01_extract_dir6.py        (about 1 minute)
=============================================================================
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Let Python find common.py, which sits in the same folder as this script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

ROWS_PER_CHUNK = 1_000_000


def extract_study_set(config):
    """Copy every clean Route 801 / direction 6 row into a new, smaller CSV."""
    common.require_file(common.RAW_FULL_SNAPSHOT, "the raw APC snapshot")

    output_file = common.ROOT / config["apc"]["raw_output"]
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write to "....part" first; rename at the very end (see common.py).
    temporary_file = output_file.with_suffix(output_file.suffix + ".part")

    rows_read = 0
    rows_kept = 0
    column_names = []
    is_first_chunk = True

    # dtype=str        -> read every column as text, exactly as the source stores it
    # na_filter=False  -> keep blank cells as "" (not NaN) so text comparisons work
    # chunksize        -> give us the file in pieces instead of all at once
    chunks = pd.read_csv(common.RAW_FULL_SNAPSHOT, dtype=str, na_filter=False,
                         chunksize=ROWS_PER_CHUNK)

    for chunk in chunks:
        rows_read = rows_read + len(chunk)
        column_names = list(chunk.columns)

        # Apply the six cleaning rules. We only need the last result, "clean".
        on_route, matching, error_free, clean = common.clean_masks(chunk, ["801"], ["6"])
        clean_rows = chunk[clean]
        rows_kept = rows_kept + len(clean_rows)

        # The first chunk creates the file (with a header row);
        # every later chunk is added to the end of it (no header).
        if is_first_chunk:
            clean_rows.to_csv(temporary_file, mode="w", header=True, index=False)
            is_first_chunk = False
        else:
            clean_rows.to_csv(temporary_file, mode="a", header=False, index=False)

        print(f"  read {rows_read:,} raw rows, kept {rows_kept:,}", flush=True)

    temporary_file.replace(output_file)

    # The "manifest" records what we made, so anyone can check it later.
    manifest = {
        "generated_utc": datetime.now(common.UTC).isoformat(),
        "source": {
            "method": "local extraction from the archived snapshot (no network)",
            "path": common.RAW_FULL_SNAPSHOT.relative_to(common.ROOT).as_posix(),
            "raw_rows_read": rows_read,
        },
        "clean_definition": common.clean_where(["801"], ["6"]),
        "path": output_file.relative_to(common.ROOT).as_posix(),
        "rows": rows_kept,
        "bytes": output_file.stat().st_size,
        "sha256": common.sha256_file(output_file),
        "column_count": len(column_names),
        "route_id": "801",
        "direction_code": "6",
        # Left empty on purpose: we may not name the direction yet (Step 4).
        "direction_label": None,
        "direction_label_gate": "2021-compatible GTFS not yet verified",
    }
    return manifest


def main():
    common.ensure_dirs()
    print(f"Reading {common.RAW_FULL_SNAPSHOT.name} (no network).")

    config = common.load_config()
    manifest = extract_study_set(config)
    common.write_json(common.AUDIT_DIR / "primary_subset_manifest.json", manifest)

    print("\nStep 1 complete.")
    print(f"  rows    : {manifest['rows']:,}   (expected 229,421)")
    print(f"  columns : {manifest['column_count']}")
    print(f"  file    : {manifest['path']}")
    print(f"  sha256  : {manifest['sha256']}")


if __name__ == "__main__":
    main()
