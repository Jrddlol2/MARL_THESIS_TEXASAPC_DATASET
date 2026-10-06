#!/usr/bin/env bash
# Overnight queue, 2026-09-18 -> 19. Runs on its own (no Claude session needed). Run from starter/.
#
# Waits for the new baselines, then trains and evaluates on the FIXED simulator (corridor-wide weather,
# capacity 55, recorded wait primary) in three parallel lanes, most important runs first:
#   lane 1: run B (evenness + waiting at stops)          training seeds 0, 1, 2
#   lane 2: run D (evenness + in-vehicle priced equally) training seeds 0, 1, 2
#   lane 3: priced waiting, kappa = 1/9 (Rodriguez et al. 2023 W_wait = 9) and kappa = 0.5, seed 0;
#           then the capacity-48 baseline sensitivity check
# Every policy is evaluated on the DEVELOPMENT seeds 0-29 only. The test seeds 100-129 are NOT touched
# (they are used once, after the configuration is chosen).
# Progress: results/overnight_2026-09-18.log; summary: results/OVERNIGHT_SUMMARY.md
# Safe to re-run: finished runs are skipped and interrupted runs resume from training_state.pt.

cd "$(dirname "$0")/.." || exit 1
LOG=results/overnight_2026-09-18.log
log() { echo "[$(date '+%m-%d %H:%M')] $*" >> "$LOG"; }

powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File scripts/keep_awake.ps1 -ParentPid $$ &
log "queue started (keep-awake on)"

log "waiting for the baselines to finish"
for _ in $(seq 1 720); do
    grep -q "ALL BASELINES DONE" results/baselines_2026-09-18.log 2>/dev/null && break
    grep -q "Traceback" results/baselines_2026-09-18.log 2>/dev/null && { log "WARNING: baseline job reported an error; continuing"; break; }
    sleep 10
done
log "baselines done; starting training lanes"

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

lane1() { for s in 0 1 2; do train "v2_B_s$s" --irr even --wait queue --seed "$s"; done; }
lane2() { for s in 0 1 2; do train "v2_D_s$s" --irr even --wait both --seed "$s"; done; }
lane3() {
    train v2_K111_s0 --irr even --wait priced --hold-price 0.1111 --seed 0
    train v2_K500_s0 --irr even --wait priced --hold-price 0.5 --seed 0
    if [ ! -f results/mc_summary_cap48.md ]; then
        log "capacity-48 baseline sensitivity (development seeds)"
        CORRIDOR_CAPACITY=48 python scripts/mc.py 30 4 --tag cap48 >> results/mc_cap48.log 2>&1 \
            && log "capacity-48 baselines done" || log "capacity-48 baselines FAILED"
    fi
}

lane1 & lane2 & lane3 &
wait

python scripts/overnight_summary.py >> "$LOG" 2>&1
log "ALL OVERNIGHT WORK DONE"
