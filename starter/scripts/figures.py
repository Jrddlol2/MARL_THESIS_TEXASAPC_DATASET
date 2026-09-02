"""Generate the paper figures from saved results (full 26-stop corridor).

Reads results/calibration.csv (from calibrate_corridor.py) and results/mc_results.csv (from mc.py)
and writes PNGs to results/figures/:
  calibration_validation.png  simulated vs observed segment running times (GEH<5)
  mc_headway_cv.png           headway CV by scenario, NC vs EH, 95% bootstrap CI
  mc_wait.png                 passenger wait by scenario, NC vs EH, 95% bootstrap CI
Run from the repo root after calibrate_corridor.py and mc.py.
"""
import os, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("results/figures", exist_ok=True)
SCEN = ["Baseline", "Surge", "Traffic", "Weather", "Breakdown", "All"]
BLUE, GREY = "#1f77b4", "#9e9e9e"


def boot(x, f=np.mean, n=5000, rng=np.random.default_rng(0)):
    x = np.asarray([v for v in x if np.isfinite(v)])
    if len(x) < 2: return (np.nan, np.nan, np.nan)
    bs = [f(rng.choice(x, len(x), True)) for _ in range(n)]
    return float(f(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def calibration_fig():
    if not os.path.exists("results/calibration.csv"): return
    c = pd.read_csv("results/calibration.csv")
    fig, ax = plt.subplots(figsize=(6, 6))
    lim = max(c.observed_s.max(), c.simulated_s.max()) * 1.08
    ax.plot([0, lim], [0, lim], "--", color=GREY, lw=1, label="perfect match")
    ax.scatter(c.observed_s, c.simulated_s, s=45, color=BLUE, zorder=3, edgecolor="white")
    rmspe = np.sqrt(np.mean(((c.simulated_s - c.observed_s) / c.observed_s) ** 2)) * 100
    ax.set_xlabel("Observed segment running time (s, APC)")
    ax.set_ylabel("Simulated segment running time (s, SUMO)")
    ax.set_title(f"Corridor calibration: {len(c)} segments, all GEH<5, RMSPE {rmspe:.1f}%")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.legend(loc="upper left"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("results/figures/calibration_validation.png", dpi=150); plt.close(fig)
    print("wrote calibration_validation.png")


def scenario_fig(df, col, ylabel, title, fname):
    x = np.arange(len(SCEN)); wpx = 0.38
    fig, ax = plt.subplots(figsize=(9, 5))
    for k, (c, color, off) in enumerate([("NC", GREY, -wpx/2), ("EH", BLUE, wpx/2)]):
        m, lo, hi = [], [], []
        for sc in SCEN:
            v = df[(df.scenario == sc) & (df.controller == c)][col].values
            pm, plo, phi = boot(v); m.append(pm); lo.append(pm - plo); hi.append(phi - pm)
        ax.bar(x + off, m, wpx, yerr=[lo, hi], capsize=3, color=color, label=c)
    ax.set_xticks(x); ax.set_xticklabels(SCEN); ax.set_ylabel(ylabel); ax.set_title(title)
    ax.legend(); ax.grid(axis="y", alpha=.3)
    fig.tight_layout(); fig.savefig(f"results/figures/{fname}", dpi=150); plt.close(fig)
    print(f"wrote {fname}")


def main():
    calibration_fig()
    if os.path.exists("results/mc_results.csv"):
        df = pd.read_csv("results/mc_results.csv")
        scenario_fig(df, "headway_cv", "Headway CV (bunching)",
                     "Headway irregularity by scenario (NC vs EH), 95% CI", "mc_headway_cv.png")
        scenario_fig(df, "wait_s", "Mean passenger wait (s)",
                     "Passenger wait by scenario (NC vs EH), 95% CI", "mc_wait.png")


if __name__ == "__main__":
    main()
