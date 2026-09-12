"""
=============================================================================
 STEP 5 OF 5  --  WRITE THE HISTORICAL GTFS GATE
=============================================================================

WHAT THIS STEP IS
    Not data processing. It writes down a RULE about what we are allowed to
    claim, and the evidence for why that rule exists.

THE PROBLEM IT RECORDS
    The APC file identifies direction with a vendor software key,
    `direction_code_id`. Route 801 uses codes 4 and 6. Nothing in the file
    says which way either one points -- there are no stop names, no headsigns,
    and no compass field.

    Naming them would require a GTFS schedule snapshot from the study window
    (July-December 2021). We do not have one.

THE RULE
    Until a 2021-compatible GTFS snapshot is checksum-verified, the manuscript
    and the code must:
        * refer to direction 6 by code only,
        * not assign northbound/southbound labels from the CURRENT schedule,
        * not claim historical stop names, route shapes or scheduled headways,
        * keep schedule-derived parameters marked as pending.

    This is a source-availability limit, NOT a failure of the APC or weather
    work. Stop IDs and event coordinates are in the data, so all the
    segment-level work proceeds regardless.

WHERE THE CONTENT COMES FROM
    Everything written here is read from the `gtfs` block of
    config/texas_capmetro_801.json -- the required window, the retrieval
    attempts and their results, and the gate text itself. Update the config,
    not this script, when the situation changes.

OUTPUTS  data/audit/texas_capmetro/gtfs_retrieval_attempts.json
         data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md

RUN      python scripts/pipeline/05_gtfs_gate.py
=============================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    AUDIT_DIR,
    UTC,
    ensure_dirs,
    load_config,
    write_json,
    write_text,
)


def write_gtfs_gate(config: dict[str, Any]) -> None:
    gtfs = config["gtfs"]

    write_json(
        AUDIT_DIR / "gtfs_retrieval_attempts.json",
        {
            "generated_utc": datetime.now(UTC).isoformat(),
            "required_service_window": gtfs["required_service_window"],
            "status": gtfs["status"],
            "attempts": gtfs["retrieval_attempts"],
            "gate": gtfs["gate"],
        },
    )

    attempt_lines = "\n".join(
        f"- **{attempt['source']}:** {attempt['result']}"
        for attempt in gtfs["retrieval_attempts"]
    )

    content = f"""# Historical GTFS acquisition gate

Status: **open - a 2021-compatible snapshot has not yet been checksum-verified.**

Required service window: `{gtfs['required_service_window'][0]}` through
`{gtfs['required_service_window'][1]}`.

The current official feed is publicly available at
`{gtfs['current_official_feed']}`, but it is not valid evidence for a 2021 route
mapping. Candidate historical sources are {gtfs['candidate_archive']}.

## Retrieval attempts

{attempt_lines}

Until the gate closes, the manuscript and code must:

- refer to APC direction `6` by code only;
- avoid assigning northbound/southbound labels from the current schedule;
- avoid claiming historical stop names, route shapes, or scheduled headways; and
- keep schedule-derived parameters as `%TODO-DATA`.

This is a source-availability limitation, not a failed weather/APC feasibility
check. The APC records themselves contain stop IDs and stop-event coordinates,
so segment-level empirical work can proceed while authoritative 2021 schedule
semantics remain gated.
"""
    write_text(AUDIT_DIR / "GTFS_ACQUISITION_STATUS.md", content)


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    ensure_dirs()
    config = load_config()
    write_gtfs_gate(config)

    print("\nStep 5 complete.")
    print(f"  gate status : {config['gtfs']['status']}")
    print(f"  attempts    : {len(config['gtfs']['retrieval_attempts'])} recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
