"""
=============================================================================
 RUN THE WHOLE DATA PIPELINE  (steps 1 -> 5, in order)
=============================================================================

    python scripts/pipeline/run_all.py

This is the same work the old single-file scripts/texas_capmetro_pipeline.py
did, split into five readable steps:

    01_audit_routes.py     Route 801 vs 803, and the cleaning funnel
    02_extract_dir6.py     the 229,421-row direction-6 study set
    03_prepare_weather.py  NOAA timezone normalisation
    04_join_weather.py     the 90-minute nearest-observation join
    05_gtfs_gate.py        the direction-label gate

ORDER MATTERS
    04 needs the study set from 02 and the weather tables from 03.
    01, 02, 03 and 05 can each be run on their own.

NO NETWORK
    Every step reads our archived, checksummed copies of the source data.
    Nothing here downloads anything -- `grep -r urllib scripts/pipeline/`
    returns nothing. See common.py for why, and the README's "Getting the
    data" section for how to obtain the source files on a new machine.
=============================================================================
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STEPS = [
    ("01_audit_routes.py", "Route selection audit (801 vs 803)"),
    ("02_extract_dir6.py", "Extract the direction-6 study set"),
    ("03_prepare_weather.py", "Normalise the NOAA weather observations"),
    ("04_join_weather.py", "Join weather to every stop event"),
    ("05_gtfs_gate.py", "Write the historical GTFS gate"),
]


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    for index, (script, description) in enumerate(STEPS, start=1):
        print("\n" + "=" * 78)
        print(f" STEP {index} OF {len(STEPS)}  --  {description}")
        print("=" * 78)

        result = subprocess.run([sys.executable, str(HERE / script)])
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
