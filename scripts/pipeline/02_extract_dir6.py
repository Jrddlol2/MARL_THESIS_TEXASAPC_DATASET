"""
=============================================================================
 STEP 2 OF 5  --  EXTRACT THE DIRECTION-6 STUDY SET
=============================================================================

WHAT THIS STEP PRODUCES
    route_801_direction_6_clean.csv  --  229,421 rows, all 47 columns.
    This is the FINAL STUDY SET: the bottom bar of the cleaning funnel and the
    input to everything downstream (corridor, calibration, weather join).

WHAT IT DOES
    Reads the archived snapshot a million rows at a time and keeps the rows
    that pass all six cleaning rules, with route = 801 and direction = 6.
    Same rules as Step 1, narrowed to one route and one direction.

    No network. See common.py for why.

WHY ALL 47 COLUMNS
    The corridor model only needs about 13 of them. The rest are kept because
    this subset is meant to be a complete, checksummed record of what we
    studied -- so questions we have not thought of yet can still be answered
    from it. (max_load, quality_indicator and the GPS coordinates all live in
    that group.)

WHY DIRECTION 6 AND NOT DIRECTION 4
    Headway regularity is only defined between buses travelling the same way,
    so the study uses one direction. Under the same coverage criterion used to
    pick Route 801, direction 6 has more clean stop events (229,421 vs
    226,233) and more boardings (420,201 vs 390,108) across an identical
    29-stop set. Step 1's direction_summary reports both.

    The compass meaning of code 6 is NOT assigned here -- it is a vendor
    software key. See Step 5 for the gate that governs labelling it.

INPUTS   data/raw/capmetro/APC_Raw_..._full.csv   the archived snapshot
         config/texas_capmetro_801.json

OUTPUTS  data/raw/capmetro/route_801_direction_6_clean.csv
         data/audit/texas_capmetro/primary_subset_manifest.json

RUN      python scripts/pipeline/02_extract_dir6.py
=============================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR, RAW_FULL_SNAPSHOT, ROOT, UTC,
    clean_masks, clean_where, ensure_dirs, load_config, require_file, sha256_file,
    write_json,
)

CHUNK_SIZE = 1_000_000


def extract_primary_subset(config: dict[str, Any]) -> dict[str, Any]:
    """Keep every row of the snapshot that passes the six cleaning rules."""
    require_file(RAW_FULL_SNAPSHOT, "the raw APC snapshot")

    destination = ROOT / config["apc"]["raw_output"]
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Write to a .part file and rename at the end, so an interrupted run can
    # never leave a truncated study set that looks complete.
    temporary = destination.with_suffix(destination.suffix + ".part")

    rows_read = rows_kept = 0
    columns: list[str] = []
    first_chunk = True

    reader = pd.read_csv(
        RAW_FULL_SNAPSHOT,
        dtype=str,          # the source types every column as text
        na_filter=False,    # keep blanks as "" so the comparisons below behave
        chunksize=CHUNK_SIZE,
    )

    for chunk in reader:
        rows_read += len(chunk)
        columns = list(chunk.columns)

        # The six cleaning rules live in common.clean_masks(). We only need the
        # last of its four cumulative masks -- the fully clean one.
        *_, keep = clean_masks(chunk, ["801"], ["6"])

        survivors = chunk[keep]
        rows_kept += len(survivors)
        survivors.to_csv(temporary, mode="w" if first_chunk else "a",
                         header=first_chunk, index=False)
        first_chunk = False

        print(f"  read {rows_read:,} raw rows, kept {rows_kept:,}", flush=True)

    temporary.replace(destination)

    return {
        "generated_utc": datetime.now(UTC).isoformat(),
        "source": {
            "method": "local extraction from the archived snapshot (no network)",
            "path": RAW_FULL_SNAPSHOT.relative_to(ROOT).as_posix(),
            "raw_rows_read": rows_read,
        },
        "clean_definition": clean_where(["801"], ["6"]),
        "path": destination.relative_to(ROOT).as_posix(),
        "rows": rows_kept,
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "column_count": len(columns),
        "route_id": "801",
        "direction_code": "6",
        # Deliberately null: the compass label is gated. See Step 5.
        "direction_label": None,
        "direction_label_gate": "2021-compatible GTFS not yet verified",
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    ensure_dirs()
    print(f"Reading {RAW_FULL_SNAPSHOT.name} (no network).")
    manifest = extract_primary_subset(load_config())
    write_json(AUDIT_DIR / "primary_subset_manifest.json", manifest)

    print("\nStep 2 complete.")
    print(f"  rows    : {manifest['rows']:,}   (expected 229,421)")
    print(f"  columns : {manifest['column_count']}")
    print(f"  file    : {manifest['path']}")
    print(f"  sha256  : {manifest['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
