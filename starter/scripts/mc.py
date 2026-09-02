"""Monte-Carlo evaluation (SO3): NC vs EH over the full corridor, all disturbance scenarios.

For each scenario x controller, run N paired replications (seed s gives NC and EH the IDENTICAL
disturbance realization, so the comparison is paired). Records headway CV, corridor travel time,
and passenger wait (headway-model wait, robust to demand timing). Reports bootstrap 95% CIs and
the paired EH-vs-NC % change in each metric.

Run from the repo root (needs the calibrated sumo/ net + vtype/stops, and corridor.txt):
    python scripts/mc.py                # default N=30
    python scripts/mc.py 20             # N=20 (faster)
Writes results/mc_results.csv (per-replication) and results/mc_summary.md (table).
"""
import os, sys, time, csv, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_disturbances import run          # single source of truth for the simulation

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SCEN = [("Baseline", {}), ("Surge", dict(S=True)), ("Traffic", dict(T=True)),
        ("Weather", dict(W=True)), ("Breakdown", dict(B=True)),
        ("All", dict(S=True, T=True, W=True, B=True))]
os.makedirs("results", exist_ok=True)


def boot_ci(x, f=np.mean, n=5000, rng=np.random.default_rng(0)):
    x = np.asarray([v for v in x if np.isfinite(v)])
    if len(x) < 2: return (float("nan"), float("nan"), float("nan"))
    bs = [f(rng.choice(x, len(x), replace=True)) for _ in range(n)]
    return float(f(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def paired_pct(nc, eh, n=5000, rng=np.random.default_rng(1)):
    nc, eh = np.asarray(nc), np.asarray(eh); m = np.isfinite(nc) & np.isfinite(eh)
    nc, eh = nc[m], eh[m]
    if len(nc) < 2: return (float("nan"), float("nan"), float("nan"))
    pt = (eh.mean() - nc.mean()) / nc.mean() * 100
    bs = []
    for _ in range(n):
        idx = rng.integers(0, len(nc), len(nc))
        bs.append((eh[idx].mean() - nc[idx].mean()) / nc[idx].mean() * 100)
    return float(pt), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    t0 = time.time()
    rows = []
    with open("results/mc_results.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["scenario", "controller", "seed", "headway_cv", "travel_s", "wait_s"])
        for name, kw in SCEN:
            for c in ["NC", "EH"]:
                ok = 0
                for s in range(N):
                    try:
                        cv, tt, wt = run(c, seed=s, **kw)
                    except Exception:
                        cv, tt, wt = float("nan"), float("nan"), float("nan")
                    if np.isfinite(cv) and np.isfinite(wt): ok += 1
                    rows.append((name, c, s, cv, tt, wt)); w.writerow([name, c, s, cv, tt, wt]); fh.flush()
                print(f"  {name:10s}/{c}: {ok}/{N} valid  ({time.time()-t0:.0f}s)", flush=True)

    # summarize
    D = {}
    for name, c, s, cv, tt, wt in rows:
        D.setdefault((name, c), {"cv": [], "tt": [], "wt": []})
        D[(name, c)]["cv"].append(cv); D[(name, c)]["tt"].append(tt); D[(name, c)]["wt"].append(wt)
    L = ["| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | n |",
         "|---|---|---|---|---|--:|"]
    for name, _ in SCEN:
        for c in ["NC", "EH"]:
            d = D[(name, c)]
            cv = boot_ci(d["cv"]); tt = boot_ci(d["tt"]); wt = boot_ci(d["wt"])
            n = sum(np.isfinite(v) for v in d["cv"])
            L.append(f"| {name} | {c} | {cv[0]:.3f} [{cv[1]:.3f}, {cv[2]:.3f}] | "
                     f"{tt[0]:.0f} [{tt[1]:.0f}, {tt[2]:.0f}] | {wt[0]:.0f} [{wt[1]:.0f}, {wt[2]:.0f}] | {n} |")
    L += ["", "**EH vs NC, paired % change (negative = EH better):**", ""]
    L.append("| Scenario | Δ Headway CV % [95% CI] | Δ Wait % [95% CI] |")
    L.append("|---|---|---|")
    for name, _ in SCEN:
        pc = paired_pct(D[(name, "NC")]["cv"], D[(name, "EH")]["cv"])
        pw = paired_pct(D[(name, "NC")]["wt"], D[(name, "EH")]["wt"])
        L.append(f"| {name} | {pc[0]:+.0f}% [{pc[1]:+.0f}%, {pc[2]:+.0f}%] | {pw[0]:+.0f}% [{pw[1]:+.0f}%, {pw[2]:+.0f}%] |")
    open("results/mc_summary.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L).encode("ascii", "replace").decode())     # console is cp1252-safe
    print(f"\nMC done: {len(SCEN)}x2x{N} runs in {time.time()-t0:.0f}s -> results/mc_summary.md", flush=True)


if __name__ == "__main__":
    main()
