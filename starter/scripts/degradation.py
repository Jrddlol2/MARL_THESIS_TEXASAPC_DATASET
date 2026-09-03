"""Degradation curve — headway CV vs weather intensity, per controller (visualizes EO 3.2).

Sweeps the weather CV parameter eta and plots mean headway CV for NC / FH / EH at the designated control
stops, so the loss of control as conditions worsen is a curve. Parallel across processes.
-> results/figures/degradation_curve.png. Run from repo root:  python scripts/degradation.py [N] [JOBS]
"""
import os, sys, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
import corridor_sim as C
# NOTE: matplotlib is imported inside main() ONLY — importing it at module level makes every spawned
# worker re-import it, and concurrent matplotlib/font-cache init crashes workers on Windows.

ETAS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]
N    = int(sys.argv[1]) if len(sys.argv) > 1 else 12
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
CS = C.CONTROL_STOPS
COLORS = {"NC": "#9e9e9e", "FH": "#e0913a", "EH": "#1f63d6"}


def _run(task):
    c, e, s = task
    cv = C.simulate(C.BASELINES[c], seed=s, control_stops=list(CS), T=True, W=(e > 0), eta=e)["headway_cv"]
    return (c, e, cv)


def main():
    import time
    tasks = [(c, e, s) for c in ["NC", "FH", "EH"] for e in ETAS for s in range(N)]
    res = {}; t0 = time.time()
    if JOBS > 1:
        with ProcessPoolExecutor(max_workers=JOBS) as ex:          # workers never import matplotlib
            for k, (c, e, cv) in enumerate(ex.map(_run, tasks), 1):
                res.setdefault((c, e), []).append(cv)
                if k % 30 == 0: print(f"  {k}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
    else:                                                          # reliable serial fallback
        for k, t in enumerate(tasks, 1):
            c, e, cv = _run(t); res.setdefault((c, e), []).append(cv)
            if k % 15 == 0: print(f"  {k}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
    import matplotlib; matplotlib.use("Agg")                       # parent only
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for c in ["NC", "FH", "EH"]:
        m = [np.nanmean(res[(c, e)]) for e in ETAS]
        sd = [np.nanstd(res[(c, e)]) / np.sqrt(N) for e in ETAS]
        ax.errorbar(ETAS, m, yerr=sd, fmt="-o", color=COLORS[c], label=c, capsize=3, lw=1.8)
    ax.set_xlabel("weather intensity  η  (coefficient of variation of the weather speed factor)")
    ax.set_ylabel("headway CV (bunching)")
    ax.set_title(f"Degradation of headway control with weather severity (D+T+W, N={N} per point)")
    ax.legend(title="Controller"); ax.grid(alpha=0.3); ax.set_axisbelow(True)
    fig.tight_layout(); os.makedirs("results/figures", exist_ok=True)
    fig.savefig("results/figures/degradation_curve.png", dpi=150)
    print("wrote results/figures/degradation_curve.png")


if __name__ == "__main__":
    main()
