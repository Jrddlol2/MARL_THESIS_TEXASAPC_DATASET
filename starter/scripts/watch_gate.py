"""Live view of a MARL training run. Shows the greedy-eval checkpoints against the baseline targets.

    python scripts/watch_gate.py            # watches experiments/gate1
    python scripts/watch_gate.py <name>     # watches experiments/<name>
Ctrl+C to stop watching (training is unaffected).
"""
import os, sys, time

NAME = sys.argv[1] if len(sys.argv) > 1 else "gate1"
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # starter_kit/
P = os.path.join(_root, "experiments", NAME, "metrics.csv")
NC, FH = 0.331, 0.237          # No-Control and Forward-Headway headway CV at the control stops (targets)
TOTAL = 400

print(f"Watching {P}")
print(f"Targets:  No-Control CV = {NC:.3f}   Forward-Headway CV = {FH:.3f}   (lower is better)")
print("Waiting for evaluation checkpoints (every 40 episodes)...  Ctrl+C to stop.\n")
print(f"{'episode':>8} {'eval_cv':>9} {'epsilon':>8}   verdict")
print("-" * 52)

shown = 0
try:
    while True:
        if os.path.exists(P):
            rows = [r.split(",") for r in open(P).read().splitlines()[1:]]
            evals = [r for r in rows if len(r) >= 5 and r[3] not in ("", "eval_cv")]
            for r in evals[shown:]:
                ep = int(r[0]); cv = float(r[3]); eps = float(r[4])
                verdict = ("beats FH ✔" if cv <= FH else
                           "below NC (learning)" if cv < NC else
                           "not yet below NC")
                print(f"{ep:>8} {cv:>9.3f} {eps:>8.2f}   {verdict}")
            shown = len(evals)
            if rows:
                last = rows[-1]
                sys.stdout.write(f"\r  ...episode {int(last[0])}/{TOTAL}, eps {float(last[4]):.2f}   ")
                sys.stdout.flush()
        time.sleep(3)
except KeyboardInterrupt:
    print("\nstopped watching (training continues).")
