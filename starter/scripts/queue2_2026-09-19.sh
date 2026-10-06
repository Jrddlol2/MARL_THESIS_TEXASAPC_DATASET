#!/usr/bin/env bash
# Follow-up queue, 2026-09-19. Waits for the overnight queue to finish, then repeats the two priced-waiting
# configurations with training seeds 1 and 2 (kappa = 0.5 and kappa = 1/9), all four at once, and
# evaluates each on the development seeds 0-29. Test seeds 100-129 stay untouched. Run from starter/.
cd "$(dirname "$0")/.." || exit 1
LOG=results/queue2_2026-09-19.log
log() { echo "[$(date '+%m-%d %H:%M')] $*" >> "$LOG"; }

WINPID=$(cat /proc/$$/winpid 2>/dev/null)
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File scripts/keep_awake.ps1 -ParentPid "$WINPID" &
log "queue 2 started (keep-awake tied to Windows pid $WINPID); waiting for the overnight queue"
until grep -q "ALL OVERNIGHT WORK DONE" results/overnight_2026-09-18.log 2>/dev/null; do sleep 30; done
log "overnight queue done; starting"

train() {
    local name=$1; shift
    if [ ! -f "experiments/$name/checkpoint.pt" ]; then
        for attempt in 1 2 3; do
            local extra=""; [ -f "experiments/$name/training_state.pt" ] && extra="--resume"
            log "$name training (attempt $attempt) $*"
            python scripts/train_marl.py --episodes 800 --jobs 3 --name "$name" "$@" $extra >> "results/train_$name.log" 2>&1 \
                && { log "$name trained"; break; }
            log "$name training FAILED on attempt $attempt"
        done
    fi
    if [ -f "experiments/$name/checkpoint_best.pt" ] && [ ! -f "results/marl_eval_$name.md" ]; then
        python scripts/eval_marl.py --ckpt "experiments/$name/checkpoint_best.pt" --jobs 3 >> "results/eval_$name.log" 2>&1 \
            && log "$name evaluated -> results/marl_eval_$name.md" || log "$name evaluation FAILED"
    fi
}

# four lanes at once: overnight, three parallel runs went almost as fast per run as two
train v2_K500_s1 --irr even --wait priced --hold-price 0.5 --seed 1 &
train v2_K500_s2 --irr even --wait priced --hold-price 0.5 --seed 2 &
train v2_K111_s1 --irr even --wait priced --hold-price 0.1111 --seed 1 &
train v2_K111_s2 --irr even --wait priced --hold-price 0.1111 --seed 2 &
wait
python scripts/overnight_summary.py >> "$LOG" 2>&1
log "ALL QUEUE 2 WORK DONE"
