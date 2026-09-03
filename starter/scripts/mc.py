"""Monte-Carlo evaluation (SO3): NC / FH / EH on the corridor, manuscript activation matrix.

Drives the unified core `envs/corridor_sim.simulate(decide, control_stops, ...)` so all controllers
act at the DESIGNATED CONTROL STOPS (four §3.2.2 criteria) — the same stops the MARL agent will use,
keeping the comparison fair. N paired replications per cell (seed s = identical disturbance across
controllers). Records headway CV, travel time, and wait as both the headway-model estimate (`wait_s`,
primary/robust) and SUMO's per-passenger recording (`wait_direct`, cross-check). Bootstrap 95% CIs +
paired % change vs No-Control.

Runs in PARALLEL across processes (SUMO is CPU-bound and single-threaded per instance, so this is the
speed lever). Run from the repo root:
    python scripts/mc.py            # N=30, jobs=6
    python scripts/mc.py 30 8       # N=30, 8 parallel workers
    python scripts/mc.py 20 1       # serial
Writes results/mc_results.csv and results/mc_summary.md.
"""
import os, sys, time, csv, numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
from corridor_sim import simulate, BASELINES, CONTROL_STOPS, STOPS

N    = int(sys.argv[1]) if len(sys.argv) > 1 else 30
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 6
SCEN = [("Stage A (D+T)",        dict(T=True)),
        ("Ablation S (D+T+S)",   dict(T=True, S=True)),
        ("Ablation W (D+T+W)",   dict(T=True, W=True)),
        ("Ablation B (D+T+B)",   dict(T=True, B=True)),
        ("Stage B (D+T+S+W+B)",  dict(T=True, S=True, W=True, B=True))]
CTRLS = list(BASELINES)              # NC, FH, EH
os.makedirs("results", exist_ok=True)


def _run_one(task):
    """Worker: one (scenario, controller, seed) replication. Picklable — looks up the decide fn locally."""
    name, kw, c, seed = task
    try:
        r = simulate(BASELINES[c], seed=seed, control_stops=CONTROL_STOPS, **kw)
        return (name, c, seed, r["headway_cv"], r["travel_s"], r["wait_s"], r["wait_direct"])
    except Exception:
        return (name, c, seed, float("nan"), float("nan"), float("nan"), float("nan"))


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
    bs = [((eh[i].mean() - nc[i].mean()) / nc[i].mean() * 100)
          for i in (rng.integers(0, len(nc), len(nc)) for _ in range(n))]
    return float(pt), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    t0 = time.time()
    print(f"control stops: {[STOPS[i] for i in CONTROL_STOPS]}  (N={N}, jobs={JOBS})", flush=True)
    tasks = [(name, kw, c, s) for name, kw in SCEN for c in CTRLS for s in range(N)]
    rows = []
    with open("results/mc_results.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "controller", "seed", "headway_cv", "travel_s", "wait_s", "wait_direct"])
        if JOBS > 1:
            # persistent workers (no max_tasks_per_child: with a balanced pool all workers hit the
            # recycle limit simultaneously and deadlock on Windows). Memory stays flat because each
            # run opens+closes its own SUMO subprocess, so nothing accumulates in the worker.
            with ProcessPoolExecutor(max_workers=JOBS) as ex:
                futs = [ex.submit(_run_one, t) for t in tasks]
                for k, fut in enumerate(as_completed(futs), 1):
                    row = fut.result(); rows.append(row); w.writerow(row); fh.flush()
                    if k % 15 == 0 or k == len(tasks):
                        print(f"  {k}/{len(tasks)} runs done  ({time.time()-t0:.0f}s)", flush=True)
        else:
            for k, t in enumerate(tasks, 1):
                row = _run_one(t); rows.append(row); w.writerow(row); fh.flush()
                if k % 15 == 0 or k == len(tasks):
                    print(f"  {k}/{len(tasks)} runs done  ({time.time()-t0:.0f}s)", flush=True)

    D = {}
    for name, c, s, cv, tt, wt, wd in rows:
        D.setdefault((name, c), {"cv": [], "tt": [], "wt": [], "wd": []})
        D[(name, c)]["cv"].append(cv); D[(name, c)]["tt"].append(tt)
        D[(name, c)]["wt"].append(wt); D[(name, c)]["wd"].append(wd)
    L = [f"Control stops: {[STOPS[i] for i in CONTROL_STOPS]} (§3.2.2 criteria). "
         f"Wait = headway model; wait_dir = SUMO per-passenger (cross-check).", "",
         "| Scenario | Ctrl | Headway CV [95% CI] | Travel (s) [95% CI] | Wait (s) [95% CI] | wait_dir | n |",
         "|---|---|---|---|---|--:|--:|"]
    for name, _ in SCEN:
        for c in CTRLS:
            d = D[(name, c)]
            cv = boot_ci(d["cv"]); tt = boot_ci(d["tt"]); wt = boot_ci(d["wt"]); wd = boot_ci(d["wd"])
            n = sum(np.isfinite(v) for v in d["cv"])
            L.append(f"| {name} | {c} | {cv[0]:.3f} [{cv[1]:.3f}, {cv[2]:.3f}] | "
                     f"{tt[0]:.0f} [{tt[1]:.0f}, {tt[2]:.0f}] | {wt[0]:.0f} [{wt[1]:.0f}, {wt[2]:.0f}] | "
                     f"{wd[0]:.0f} | {n} |")
    L += ["", "**Paired % change vs No-Control (negative = controller better; CV with 95% CI):**", "",
          "| Scenario | FH Δ CV % [95% CI] | FH Δ wait % | EH Δ CV % [95% CI] | EH Δ wait % |",
          "|---|---|---|---|---|"]
    for name, _ in SCEN:
        fcv = paired_pct(D[(name, "NC")]["cv"], D[(name, "FH")]["cv"])
        fwt = paired_pct(D[(name, "NC")]["wt"], D[(name, "FH")]["wt"])
        ecv = paired_pct(D[(name, "NC")]["cv"], D[(name, "EH")]["cv"])
        ewt = paired_pct(D[(name, "NC")]["wt"], D[(name, "EH")]["wt"])
        L.append(f"| {name} | {fcv[0]:+.0f}% [{fcv[1]:+.0f}, {fcv[2]:+.0f}] | {fwt[0]:+.0f}% | "
                 f"{ecv[0]:+.0f}% [{ecv[1]:+.0f}, {ecv[2]:+.0f}] | {ewt[0]:+.0f}% |")
    open("results/mc_summary.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L).encode("ascii", "replace").decode())
    print(f"\nMC done: {len(SCEN)}x{len(CTRLS)}x{N} runs in {time.time()-t0:.0f}s -> results/mc_summary.md", flush=True)


if __name__ == "__main__":
    main()
