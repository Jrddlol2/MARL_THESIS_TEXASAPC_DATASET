"""Monte-Carlo evaluation (SO3): NC / FH / EH on the corridor, manuscript activation matrix.

Drives the unified core `envs/corridor_sim.simulate(decide, control_stops, ...)` so all controllers
act at the DESIGNATED CONTROL STOPS (four §3.2.2 criteria) — the same stops the MARL agent will use,
keeping the comparison fair. N paired replications per cell (seed s = identical disturbance across
controllers). Records headway CV, travel time, and wait as both the headway-model estimate (`wait_s`,
primary/robust) and SUMO's per-passenger recording (`wait_direct`, cross-check). Bootstrap 95% CIs +
paired % change vs No-Control.

Runs in PARALLEL across processes (SUMO is CPU-bound and single-threaded per instance, so this is the
speed lever). Run from the starter/ folder:
    python scripts/mc.py            # N=30, jobs=6
    python scripts/mc.py 30 8       # N=30, 8 parallel workers
    python scripts/mc.py 20 1       # serial
Writes results/mc_results.csv and results/mc_summary.md.

Options (after N and JOBS), used for sensitivity checks:
    --max-hold 240      cap every hold at 240 s instead of the default 120 s
    --breakdowns 3      remove 3 buses instead of 1 when B is on
    --surge-sd 2        surge strength sigma_d (default 1; Wang & Sun test 1, 2, 3)
    --eta 1.2           synthetic weather strength (default 0.8)
    --traffic-sd 0.1    extra episode-wide traffic stress sigma_s (default 0 = off)
    --only-breakdown    run only the two scenarios that include B
    --only A,W,StageB   run only these scenarios (A, S, W, B, StageB)
    --tag NAME          write results/mc_results_NAME.csv and mc_summary_NAME.md
Example:  python scripts/mc.py 30 10 --max-hold 240 --tag hold240
          python scripts/mc.py 30 10 --eta 0 --only W,StageB --tag observed_rain
With --eta 0 the weather W is the observed ordinary-rain slow-down only (manuscript definition for
the W ablation and the observed-weather Stage B cell).
"""
import os, sys, time, csv, numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
from corridor_sim import simulate, BASELINES, CONTROL_STOPS, STOPS, H0, NUM_BUSES



def option(name, default):
    """Value written after --name on the command line, or `default`."""
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


N    = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 6
MAX_HOLD = float(option("--max-hold", "nan"))          # nan = the simulator's default (120 s)
BREAKDOWNS = int(option("--breakdowns", "1"))
SURGE_SD = float(option("--surge-sd", "1.0"))
ETA = float(option("--eta", "0.8"))
TRAFFIC_SD = float(option("--traffic-sd", "0.0"))
TAG = option("--tag", "")
SUFFIX = "_" + TAG if TAG else ""
SCEN = [("Stage A (D+T)",        dict(T=True)),
        ("Ablation S (D+T+S)",   dict(T=True, S=True)),
        ("Ablation W (D+T+W)",   dict(T=True, W=True)),
        ("Ablation B (D+T+B)",   dict(T=True, B=True)),
        ("Stage B (D+T+S+W+B)",  dict(T=True, S=True, W=True, B=True))]
SHORT_NAMES = {"A": "Stage A (D+T)", "S": "Ablation S (D+T+S)", "W": "Ablation W (D+T+W)",
               "B": "Ablation B (D+T+B)", "StageB": "Stage B (D+T+S+W+B)"}
if "--only" in sys.argv:
    wanted = [SHORT_NAMES[k] for k in option("--only", "").split(",")]
    SCEN = [s for s in SCEN if s[0] in wanted]
if "--only-breakdown" in sys.argv:
    SCEN = [s for s in SCEN if s[1].get("B")]
CTRLS = list(BASELINES)              # NC, FH, EH
os.makedirs("results", exist_ok=True)


def _run_one(task):
    """Worker: one (scenario, controller, seed) replication. Picklable — looks up the decide fn locally."""
    name, kw, c, seed = task
    extra = dict(breakdowns=BREAKDOWNS, surge_sd=SURGE_SD, eta=ETA, traffic_stress_sd=TRAFFIC_SD)
    if np.isfinite(MAX_HOLD):
        extra["max_hold"] = MAX_HOLD
    try:
        r = simulate(BASELINES[c], seed=seed, control_stops=CONTROL_STOPS, **kw, **extra)
        return (name, c, seed, r["headway_cv"], r["travel_s"], r["wait_s"], r["wait_direct"])
    except Exception as error:
        print(f"  FAILED {name} {c} seed {seed}: {error!r}", flush=True)
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
    print(f"control stops: {[STOPS[i] for i in CONTROL_STOPS]}  (N={N}, jobs={JOBS}, "
          f"max_hold={'120 (default)' if not np.isfinite(MAX_HOLD) else MAX_HOLD}, breakdowns={BREAKDOWNS}, surge_sd={SURGE_SD}, eta={ETA}, traffic_sd={TRAFFIC_SD})", flush=True)
    tasks = [(name, kw, c, s) for name, kw in SCEN for c in CTRLS for s in range(N)]
    rows = []
    with open(f"results/mc_results{SUFFIX}.csv", "w", newline="") as fh:
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
    cap_text = "120 s" if not np.isfinite(MAX_HOLD) else f"{MAX_HOLD:.0f} s"
    L = [f"H0 = {H0:.0f} s, {NUM_BUSES} buses, {len(STOPS)} stops, N = {N} paired seeds, "
         f"max hold {cap_text}, B removes {BREAKDOWNS} bus(es), surge sigma_d {SURGE_SD}, weather eta {ETA}, "
         f"traffic stress sigma_s {TRAFFIC_SD}. Ordinary-day variability fitted from APC (fit_variability.py). "
         f"Control stops: {[STOPS[i] for i in CONTROL_STOPS]} (§3.2.2 criteria). "
         f"Wait = headway model; wait_dir = SUMO per-passenger (cross-check)."
         + (" Weather W = observed ordinary-rain slow-down only (eta 0)." if ETA == 0 else ""), "",
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
    open(f"results/mc_summary{SUFFIX}.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L).encode("ascii", "replace").decode())
    print(f"\nMC done: {len(SCEN)}x{len(CTRLS)}x{N} runs in {time.time()-t0:.0f}s -> results/mc_summary{SUFFIX}.md", flush=True)


if __name__ == "__main__":
    main()
