"""Monte-Carlo evaluation (SO3): NC / FH / EH on the corridor, manuscript activation matrix.

Drives the unified simulation core `envs/corridor_sim.simulate(decide, control_stops, ...)`, so the
baselines run at exactly the DESIGNATED CONTROL STOPS (derived from the four §3.2.2 criteria) — the
same stops the MARL agent will act at, keeping the comparison fair. For each cell (scenario ×
controller) it runs N paired replications (seed s gives every controller the IDENTICAL disturbance),
recording headway CV, corridor travel time, and passenger wait as BOTH the headway-model estimate
(`wait_s`, primary/robust) and SUMO's per-passenger recording (`wait_direct`, cross-check). Reports
bootstrap 95% CIs and the paired % change vs No-Control.

Run from the repo root:
    python scripts/mc.py            # N=30
    python scripts/mc.py 20         # N=20 (faster)
Writes results/mc_results.csv and results/mc_summary.md.
"""
import os, sys, time, csv, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
from corridor_sim import simulate, BASELINES, CONTROL_STOPS, STOPS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
# Manuscript activation matrix (Ch.2 scope): D and T present in every cell; Stage A = ideal (D+T),
# three ablations add one class each, Stage B = combined.
SCEN = [("Stage A (D+T)",        dict(T=True)),
        ("Ablation S (D+T+S)",   dict(T=True, S=True)),
        ("Ablation W (D+T+W)",   dict(T=True, W=True)),
        ("Ablation B (D+T+B)",   dict(T=True, B=True)),
        ("Stage B (D+T+S+W+B)",  dict(T=True, S=True, W=True, B=True))]
CTRLS = list(BASELINES)              # NC, FH, EH
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
    bs = [((eh[i].mean() - nc[i].mean()) / nc[i].mean() * 100)
          for i in (rng.integers(0, len(nc), len(nc)) for _ in range(n))]
    return float(pt), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    t0 = time.time()
    print(f"control stops: {[STOPS[i] for i in CONTROL_STOPS]}  (N={N})", flush=True)
    rows = []
    with open("results/mc_results.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "controller", "seed", "headway_cv", "travel_s", "wait_s", "wait_direct"])
        for name, kw in SCEN:
            for c in CTRLS:
                ok = 0
                for s in range(N):
                    try:
                        r = simulate(BASELINES[c], seed=s, control_stops=CONTROL_STOPS, **kw)
                        cv, tt, wt, wd = r["headway_cv"], r["travel_s"], r["wait_s"], r["wait_direct"]
                    except Exception:
                        cv = tt = wt = wd = float("nan")
                    if np.isfinite(cv) and np.isfinite(wt): ok += 1
                    rows.append((name, c, s, cv, tt, wt, wd))
                    w.writerow([name, c, s, cv, tt, wt, wd]); fh.flush()
                print(f"  {name:20s}/{c}: {ok}/{N} valid  ({time.time()-t0:.0f}s)", flush=True)

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
