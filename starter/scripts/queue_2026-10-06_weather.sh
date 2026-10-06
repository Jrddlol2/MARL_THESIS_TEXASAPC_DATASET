#!/usr/bin/env bash
# 2026-10-06 evening: weather levels changed to US sources (FHWA 2006 light 3% / heavy 7.5%;
# FHWA Road Weather Management, arterial wet pavement 10% and 25%). Waits for the boarding-fix
# baseline queue, re-runs the changed Stage B weather cells on dev and test seeds (extreme 25% is
# unchanged), re-runs the self-test, then starts the overnight skip training sweep.
# Log: results/queue_2026-10-06_weather.log. Run from starter/.
cd "$(dirname "$0")/.." || exit 1
LOG=results/queue_2026-10-06_weather.log
log() { echo "[$(date '+%m-%d %H:%M')] $*" >> "$LOG"; }
log "waiting for the boarding-fix baseline queue"
until grep -q "QUEUE DONE" results/queue_2026-10-06.log 2>/dev/null; do sleep 15; done
rm -f results/mc_results_stageB_moderate*.csv results/mc_summary_stageB_moderate*.md
for START in 0 100; do
  for LEVEL in light heavy wet_arterial; do
    log "Stage B $LEVEL, seeds from $START"
    python scripts/mc.py 30 10 --weather $LEVEL --only StageB --tag stageB_$LEVEL --seed-start $START >> "$LOG" 2>&1
  done
done
log "self-test"
python scripts/test_simulator.py >> "$LOG" 2>&1
log "WEATHER DONE; starting the overnight skip sweep"
bash scripts/overnight_2026-10-06_skip_sweep.sh
