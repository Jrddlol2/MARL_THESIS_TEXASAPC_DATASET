"""
=============================================================================
 RUN THE WHOLE DATA PIPELINE  (steps 1 -> 4, in order)
=============================================================================

    python scripts/pipeline/run_all.py            (about 1 minute)

    01_extract_dir6.py     the 229,421-row direction-6 study set
    02_prepare_weather.py  fix the NOAA weather clock
    03_join_weather.py     match weather to each bus event (90-minute rule)
    04_gtfs_gate.py        write down the direction-name rule

NOT INCLUDED
    audit_route_selection.py ("why Route 801?") is evidence, not a processing
    step. Run it by itself when you need those numbers again:

        python scripts/pipeline/audit_route_selection.py

ORDER
    Step 3 needs the outputs of Steps 1 and 2. The others can run alone.
=============================================================================
"""

import subprocess
import sys
from pathlib import Path

THIS_FOLDER = Path(__file__).resolve().parent

# (script file, what it does)
STEPS = [
    ("01_extract_dir6.py", "Extract the direction-6 study set"),
    ("02_prepare_weather.py", "Normalise the NOAA weather observations"),
    ("03_join_weather.py", "Join weather to every stop event"),
    ("04_gtfs_gate.py", "Write the historical GTFS gate"),
]


def main():
    step_number = 0
    for script, description in STEPS:
        step_number = step_number + 1
        print("\n" + "=" * 78)
        print(f" STEP {step_number} OF {len(STEPS)}  --  {description}")
        print("=" * 78)

        # Run the step as its own Python program, exactly as if typed by hand.
        result = subprocess.run([sys.executable, str(THIS_FOLDER / script)])

        # A return code other than 0 means the step failed: stop here.
        if result.returncode != 0:
            print(f"\nFAILED at step {step_number} ({script}). Stopping.", file=sys.stderr)
            sys.exit(result.returncode)

    print("\n" + "=" * 78)
    print(" ALL STEPS COMPLETE")
    print("=" * 78)
    print(" Evidence written to data/audit/texas_capmetro/")


if __name__ == "__main__":
    main()
