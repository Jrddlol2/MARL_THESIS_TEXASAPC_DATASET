#!/usr/bin/env bash
# Overnight queue 2026-10-06 -> 07: first MARL runs WITH the skip action (manuscript p.45), on the
# boarding-fixed simulator. Small EO 2.1 reward-weight sweep, training seed 0, development seeds only
# (test seeds 100-129 are NOT touched). Waits for the baseline re-run to finish first.
# Three lanes x two runs; each run ~5 h (800 episodes). Run from starter/.
# Progress: results/overnight_2026-10-06.log
cd "$(dirname "$0")/.." || exit 1
LOG=results/overnight_2026-10-06.log
log() { echo "[$(date '+%m-%d %H:%M')] $*" >> "$LOG"; }

powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File scripts/keep_awake.ps1 -ParentPid $$ &
log "queue started (keep-awake on)"

log "waiting for the boarding-fix baselines to finish"
for _ in $(seq 1 1080); do
    grep -q "QUEUE DONE" results/queue_2026-10-06.log 2>/dev/null && break
    grep -q "Traceback" results/queue_2026-10-06.log 2>/dev/null && { log "WARNING: baseline queue reported an error; continuing"; break; }
    sleep 10
done
log "baselines done; starting skip training lanes"

train() {  # train NAME [train_marl options...], then evaluate it on the development seeds
    local name=$1; shift
    if [ -f "experiments/$name/checkpoint.pt" ]; then
        log "$name already trained; skipping training"
    else
        for attempt in 1 2 3; do
            local extra=""
            [ -f "experiments/$name/training_state.pt" ] && extra="--resume"
            log "$name training (attempt $attempt) $*"
            if python scripts/train_marl.py --episodes 800 --jobs 4 --name "$name" "$@" $extra >> "results/train_$name.log" 2>&1; then
                log "$name trained"; break
            fi
            log "$name training FAILED on attempt $attempt (see results/train_$name.log)"
        done
    fi
    if [ -f "experiments/$name/checkpoint_best.pt" ] && [ ! -f "results/marl_eval_$name.md" ]; then
        log "$name evaluating on development seeds 0-29"
        if python scripts/eval_marl.py --ckpt "experiments/$name/checkpoint_best.pt" --jobs 4 >> "results/eval_$name.log" 2>&1; then
            log "$name evaluated -> results/marl_eval_$name.md"
        else
            log "$name evaluation FAILED (see results/eval_$name.log)"
        fi
    fi
}

# w = (irregularity, waiting, skip penalty)
lane1() { train sk_D_w1-05-1  --skip --irr even --wait both --weights 1,0.5,1 --seed 0
          train sk_D_w1-05-2  --skip --irr even --wait both --weights 1,0.5,2 --seed 0; }
lane2() { train sk_P5_w1-05-1 --skip --irr even --wait priced --hold-price 0.5 --weights 1,0.5,1 --seed 0
          train sk_D_w1-05-05 --skip --irr even --wait both --weights 1,0.5,0.5 --seed 0; }
lane3() { train sk_D_w1-1-1   --skip --irr even --wait both --weights 1,1,1 --seed 0
          train sk_P5_w1-1-1  --skip --irr even --wait priced --hold-price 0.5 --weights 1,1,1 --seed 0; }

lane1 & lane2 & lane3 &
wait
log "ALL OVERNIGHT WORK DONE"
