"""
=============================================================================
 RUN THE WHOLE DATA PIPELINE  (steps 1 -> 5, in order)
=============================================================================

    python scripts/pipeline/run_all.py
    python scripts/pipeline/run_all.py --force     (redownload everything)

This is the same work the old single-file scripts/texas_capmetro_pipeline.py
did, split into five readable steps:

    01_audit_routes.py     Route 801 vs 803, and the cleaning funnel
    02_download_dir6.py    the 229,421-row direction-6 study set
    03_prepare_weather.py  NOAA download + timezone normalisation
    04_join_weather.py     the 90-minute nearest-observation join
    05_gtfs_gate.py        the direction-label gate

ORDER MATTERS
    02 uses the column list that 01 saves.
    04 needs the study set from 02 and the weather tables from 03.
    01, 03 and 05 can each be run on their own.

RE-RUNNING IS CHEAP
    Every download checks for an existing local copy first and reuses it,
    recording "reused_existing_file": true. Nothing is fetched twice unless
    you pass --force.
=============================================================================
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STEPS = [
    ("01_audit_routes.py", "Route selection audit (801 vs 803)", True),
    ("02_download_dir6.py", "Download the direction-6 study set", True),
    ("03_prepare_weather.py", "Download and normalise NOAA weather", True),
    ("04_join_weather.py", "Join weather to every stop event", False),
    ("05_gtfs_gate.py", "Write the historical GTFS gate", False),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload raw files instead of reusing local copies",
    )
    args = parser.parse_args()

    for index, (script, description, accepts_force) in enumerate(STEPS, start=1):
        print("\n" + "=" * 78)
        print(f" STEP {index} OF {len(STEPS)}  --  {description}")
        print("=" * 78)

        command = [sys.executable, str(HERE / script)]
        if args.force and accepts_force:
            command.append("--force")

        result = subprocess.run(command)
        if result.returncode != 0:
            print(f"\nFAILED at step {index} ({script}). Stopping.", file=sys.stderr)
            return result.returncode

    print("\n" + "=" * 78)
    print(" ALL STEPS COMPLETE")
    print("=" * 78)
    print(" Evidence written to data/audit/texas_capmetro/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
