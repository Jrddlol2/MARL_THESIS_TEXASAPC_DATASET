"""Degradation curve — headway CV vs weather intensity per controller (EO 3.2), publication style.

Sweeps the weather CV parameter eta and plots mean headway CV for NC / FH / EH at the designated control
stops. Parallel across processes. Caches the sweep to results/figures/_degradation_data.json so restyles
don't recompute. -> results/figures/degradation_curve.{pdf,png}
Run from starter/ :  python scripts/degradation.py [N] [JOBS]   (add --refresh to recompute the sweep)
"""
import os, sys, json, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
import corridor_sim as C
# matplotlib imported in main() ONLY (workers must never import it — Windows font-cache crash).

ETAS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]
N    = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 12
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 4
CS = C.CONTROL_STOPS
CACHE = "results/figures/_degradation_data.json"


def _run(task):
    c, e, s = task
    cv = C.simulate(C.BASELINES[c], seed=s, control_stops=list(CS), T=True, W=(e > 0), eta=e)["headway_cv"]
    return (c, e, cv)


def compute():
    import time
    tasks = [(c, e, s) for c in ["NC", "FH", "EH"] for e in ETAS for s in range(N)]
    res = {}; t0 = time.time()
    if JOBS > 1:
        with ProcessPoolExecutor(max_workers=JOBS) as ex:
            for k, (c, e, cv) in enumerate(ex.map(_run, tasks), 1):
                res.setdefault(f"{c}|{e}", []).append(cv)
                if k % 30 == 0: print(f"  {k}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
    else:
        for k, t in enumerate(tasks, 1):
            c, e, cv = _run(t); res.setdefault(f"{c}|{e}", []).append(cv)
            if k % 15 == 0: print(f"  {k}/{len(tasks)} ({time.time()-t0:.0f}s)", flush=True)
    os.makedirs("results/figures", exist_ok=True)
    json.dump({"N": N, "etas": ETAS, "res": res}, open(CACHE, "w"))
    return res


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _figstyle as S
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        D = json.load(open(CACHE)); res = {tuple(k.split("|")[:1]) + (float(k.split("|")[1]),): v
                                           for k, v in D["res"].items()}
        res = {(k.split("|")[0], float(k.split("|")[1])): v for k, v in D["res"].items()}
        etas = D["etas"]; n = D["N"]; print("loaded degradation cache")
    else:
        raw = compute(); res = {(k.split("|")[0], float(k.split("|")[1])): v for k, v in raw.items()}
        etas = ETAS; n = N
    S.apply()
    import matplotlib.pyplot as plt
    COLORS = {"NC": S.NC_C, "FH": S.FH_C, "EH": S.EH_C}
    MARK = {"NC": "o", "FH": "s", "EH": "^"}
    fig, ax = plt.subplots(figsize=S.WIDE)
    for c in ["NC", "FH", "EH"]:
        m = [np.nanmean(res[(c, e)]) for e in etas]
        sd = [np.nanstd(res[(c, e)]) / np.sqrt(n) for e in etas]
        ax.errorbar(etas, m, yerr=sd, fmt=f"-{MARK[c]}", color=COLORS[c], label=c, capsize=2.5, lw=1.5, ms=4)
    ax.set_xlabel(r"weather intensity $\eta$ (CV of the weather speed factor)")
    ax.set_ylabel("headway CV (bunching)")
    ax.legend(title="Controller"); ax.grid(alpha=0.3)
    S.save(fig, "degradation_curve")


if __name__ == "__main__":
    main()
