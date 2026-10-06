#!/usr/bin/env bash
# Baselines on the fixed simulator (corridor-wide weather, capacity 55), 2026-09-18.
# Development seeds 0-29 first, then the fresh test seeds 100-129. Run from starter/.
set -e
for START in 0 100; do
  python scripts/mc.py 30 10 --seed-start $START
  for LEVEL in light moderate heavy extreme; do
    python scripts/mc.py 30 10 --weather $LEVEL --only StageB --tag stageB_$LEVEL --seed-start $START
  done
done
echo "ALL BASELINES DONE"
