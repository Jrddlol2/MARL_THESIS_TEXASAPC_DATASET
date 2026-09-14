"""
=============================================================================
 STEP 4 OF 4  --  WRITE DOWN THE "DIRECTION NAME" RULE (THE GTFS GATE)
=============================================================================

WHAT THIS STEP IS
    Not data processing. It writes down a RULE about what we are allowed to
    claim, together with the evidence for it.

THE PROBLEM
    The bus data marks direction with a code, direction_code_id. Route 801
    uses codes 4 and 6, but nothing in the file says which way they point
    (no stop names, no compass field). To name them we would need the 2021
    GTFS timetable files, and we do not have them.

THE RULE
    Until a checksum-verified 2021 GTFS file is found, we must:
        * call it "direction 6" only,
        * not call it northbound/southbound using TODAY's timetable,
        * not claim 2021 stop names, route shapes or scheduled headways.

    All the text comes from the "gtfs" block of config/texas_capmetro_801.json.
    When the situation changes, edit the config, not this script.

OUTPUT   data/audit/texas_capmetro/gtfs_retrieval_attempts.json
         data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md

RUN      python scripts/pipeline/04_gtfs_gate.py           (about 1 second)
=============================================================================
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common


def write_gtfs_gate(config):
    gtfs = config["gtfs"]

    # ---- 1. the JSON record ------------------------------------------------
    record = {
        "generated_utc": datetime.now(common.UTC).isoformat(),
        "required_service_window": gtfs["required_service_window"],
        "status": gtfs["status"],
        "attempts": gtfs["retrieval_attempts"],
        "gate": gtfs["gate"],
    }
    common.write_json(common.AUDIT_DIR / "gtfs_retrieval_attempts.json", record)

    # ---- 2. the human-readable markdown page -------------------------------
    attempt_lines = []
    for attempt in gtfs["retrieval_attempts"]:
        attempt_lines.append(f"- **{attempt['source']}:** {attempt['result']}")
    attempts_text = "\n".join(attempt_lines)

    first_day = gtfs["required_service_window"][0]
    last_day = gtfs["required_service_window"][1]

    content = f"""# Historical GTFS acquisition gate

Status: **open - a 2021-compatible snapshot has not yet been checksum-verified.**

Required service window: `{first_day}` through
`{last_day}`.

The current official feed is publicly available at
`{gtfs['current_official_feed']}`, but it is not valid evidence for a 2021 route
mapping. Candidate historical sources are {gtfs['candidate_archive']}.

## Retrieval attempts

{attempts_text}

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
    common.write_text(common.AUDIT_DIR / "GTFS_ACQUISITION_STATUS.md", content)


def main():
    common.ensure_dirs()
    config = common.load_config()
    write_gtfs_gate(config)

    print("\nStep 4 complete.")
    print(f"  gate status : {config['gtfs']['status']}")
    print(f"  attempts    : {len(config['gtfs']['retrieval_attempts'])} recorded")


if __name__ == "__main__":
    main()
