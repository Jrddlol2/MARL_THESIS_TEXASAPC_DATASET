"""
=============================================================================
 STEP 2 OF 5  --  DOWNLOAD THE DIRECTION-6 STUDY SET
=============================================================================

WHAT THIS STEP PRODUCES
    route_801_direction_6_clean.csv  --  229,421 rows, all 47 columns.
    This is the FINAL STUDY SET: the bottom bar of the cleaning funnel and the
    input to everything downstream (corridor, calibration, weather join).

WHAT IT DOES
    Sends one filtered query to the Texas Open Data portal:

        route_id in ('801') and route_id=current_route_id
        and import_error='0' and import_trip_error='0' and bs_id<>'0'
        and direction_code_id in ('6')

    and pages through the result 50,000 rows at a time.

    Same six cleaning rules as Step 1, but narrowed to Route 801 and direction
    code 6 only -- and this time we keep every column, not just the 19 needed
    for the route comparison.

WHY ALL 47 COLUMNS
    The corridor model only needs about 13 of them. The rest are kept because
    the archived subset is meant to be a complete, checksummed record of what
    we studied -- so that questions we have not thought of yet can still be
    answered from it without another download. (max_load, quality_indicator
    and the GPS coordinates all live in this group.)

WHY DIRECTION 6 AND NOT DIRECTION 4
    Headway regularity is only defined between buses travelling the same way,
    so the study uses one direction. Under the same coverage criterion used to
    pick Route 801, direction 6 has more clean stop events (229,421 vs
    226,233) and more boardings (420,201 vs 390,108) across an identical
    29-stop set. See Step 1's direction_summary for both.

    The compass meaning of code 6 is NOT assigned here. It is a vendor
    software key; see Step 5 for the gate that governs labelling it.

INPUTS   config/texas_capmetro_801.json
         data/audit/texas_capmetro/socrata_metadata.json  (from Step 1, for
         the column list -- refetched if missing)

OUTPUTS  data/raw/capmetro/route_801_direction_6_clean.csv
         data/audit/texas_capmetro/primary_subset_manifest.json

RUN      python scripts/pipeline/02_download_dir6.py
=============================================================================
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR,
    RAW_FULL_SNAPSHOT,
    ROOT,
    UTC,
    clean_where,
    download_soda_csv,
    ensure_dirs,
    fetch_json,
    load_config,
    passes_clean_rules,
    sha256_file,
    stream_raw_snapshot,
    write_json,
)


def download_primary_subset(config: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    apc = config["apc"]

    # The portal's metadata lists all 47 column names. Step 1 already saved it;
    # refetch only if this script is run on its own.
    metadata_path = AUDIT_DIR / "socrata_metadata.json"
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.exists()
        else fetch_json(apc["metadata_url"])
    )
    fields = [column["fieldName"] for column in metadata["columns"]]

    # Where the study set lands -- the path comes from the config, not hardcoded.
    destination = ROOT / apc["raw_output"]

    manifest = download_soda_csv(
        base_url=apc["resource_csv_url"],
        destination=destination,
        select=fields,
        where=clean_where(["801"], ["6"]),
        # Sorting makes the download deterministic: the same query always
        # produces byte-identical output, which is what makes the SHA-256
        # meaningful as a provenance record.
        order="apc_date_time,vehicle_id,actual_sequence,bs_id",
        force=force,
    )

    manifest.update(
        {
            "generated_utc": datetime.now(UTC).isoformat(),
            "route_id": "801",
            "direction_code": "6",
            # Deliberately null: the compass label is gated. See Step 5.
            "direction_label": None,
            "direction_label_gate": "2021-compatible GTFS not yet verified",
            "column_count": len(fields),
        }
    )
    write_json(AUDIT_DIR / "primary_subset_manifest.json", manifest)
    return manifest


def extract_primary_subset_local(config: dict[str, Any]) -> dict[str, Any]:
    """OFFLINE ALTERNATIVE: build the same study set from the 3.7 GB local file.

    Instead of asking the portal to filter, we stream the archival snapshot
    ourselves and apply the identical six rules via passes_clean_rules().

    Slower (it reads all 9.2 million rows) but needs no network at all, and
    the result must match the API path row for row -- that agreement is the
    cross-check.
    """
    destination = ROOT / config["apc"]["raw_output"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")

    read = kept = 0
    writer: csv.DictWriter | None = None

    with temporary.open("w", encoding="utf-8", newline="") as output:
        for row in stream_raw_snapshot():
            read += 1
            if writer is None:
                writer = csv.DictWriter(output, fieldnames=list(row))
                writer.writeheader()
            if passes_clean_rules(row, ("801",), ("6",)):
                kept += 1
                writer.writerow(row)
            if read % 1_000_000 == 0:
                print(f"  read {read:,} raw rows, kept {kept:,}", flush=True)

    temporary.replace(destination)
    print(f"  read {read:,} raw rows, kept {kept:,}")

    return {
        "source": "local archival snapshot (offline extraction)",
        "snapshot_path": RAW_FULL_SNAPSHOT.relative_to(ROOT).as_posix(),
        "raw_rows_read": read,
        "rows": kept,
        "path": destination.relative_to(ROOT).as_posix(),
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "column_count": len(writer.fieldnames) if writer else 0,
        "clean_rules": clean_where(["801"], ["6"]),
        "generated_utc": datetime.now(UTC).isoformat(),
        "route_id": "801",
        "direction_code": "6",
        "direction_label": None,
        "direction_label_gate": "2021-compatible GTFS not yet verified",
        "reused_existing_file": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload instead of reusing the existing local copy",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="extract from the local 3.7 GB snapshot instead of the portal (no network)",
    )
    args = parser.parse_args()

    ensure_dirs()
    if args.local:
        manifest = extract_primary_subset_local(load_config())
        write_json(AUDIT_DIR / "primary_subset_manifest_local.json", manifest)
    else:
        manifest = download_primary_subset(load_config(), force=args.force)

    print("\nStep 2 complete.")
    print(f"  rows     : {manifest['rows']:,}   (expected 229,421)")
    print(f"  columns  : {manifest['column_count']}")
    print(f"  file     : {manifest['path']}")
    print(f"  sha256   : {manifest['sha256']}")
    print(f"  reused   : {manifest['reused_existing_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
