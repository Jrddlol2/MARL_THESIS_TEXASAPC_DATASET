#!/usr/bin/env bash
# 2026-10-06: after the boarding-count fix, pooled CV (Eq. 3.15) and departure-based travel time.
# 1) re-check bunching/load validation, 2) re-run every baseline cell on dev seeds 0-29 and test seeds 100-129.
# Run from starter/. Log: results/queue_2026-10-06.log
set -e
echo "START $(date)"
python scripts/validate_simulator.py 30 10
echo "VALIDATION DONE $(date)"
bash scripts/run_baselines_2026-09-18.sh
echo "QUEUE DONE $(date)"
