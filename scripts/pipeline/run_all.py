"""
=============================================================================
 RUN THE DATA PIPELINE  (steps 1 -> 4, in order)
=============================================================================

    python scripts/pipeline/run_all.py

    01_extract_dir6.py     the 229,421-row direction-6 study set
    02_prepare_weather.py  NOAA timezone normalisation
    03_join_weather.py     the 90-minute nearest-observation join
    04_gtfs_gate.py        the direction-label gate

NOT PART OF THE PIPELINE
    audit_route_selection.py answers "why Route 801 and not 803?" and produces
    the cleaning-funnel numbers on the slide. It is EVIDENCE, not a processing
    step -- nothing downstream reads its output, and the route decision it
    justifies was settled long ago. Run it when you need to regenerate that
    evidence, not on every pipeline run:

        python scripts/pipeline/audit_route_selection.py

ORDER MATTERS
    03 needs the study set from 01 and the weather tables from 02.
    01, 02 and 04 can each be run on their own.

NO NETWORK
    Every step reads our archived, checksummed copies of the source data.
    Nothing here downloads anything -- `grep -r urllib scripts/pipeline/`
    returns nothing. See common.py for why, and the README's "Getting the
    data" section for how to obtain the source files on a new machine.

HOW LONG
    About 60 seconds. Step 1 dominates: it reads all 9.2 million rows of the
    3.7 GB snapshot. Steps 2, 3 and 4 take a second or two each.
=============================================================================
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STEPS = [
    ("01_extract_dir6.py", "Extract the direction-6 study set"),
    ("02_prepare_weather.py", "Normalise the NOAA weather observations"),
    ("03_join_weather.py", "Join weather to every stop event"),
    ("04_gtfs_gate.py", "Write the historical GTFS gate"),
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
