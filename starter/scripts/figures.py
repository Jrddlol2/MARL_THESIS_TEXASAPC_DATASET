"""Generate the paper figures from saved results (full 26-stop corridor), publication style (_figstyle).

Reads results/calibration.csv (from calibrate_corridor.py) and results/mc_results.csv (from mc.py) and
writes PDF+PNG to results/figures/:
  calibration_validation  simulated vs observed segment running times (GEH<5)
  mc_headway_cv           headway CV by scenario, NC / FH / EH, 95% bootstrap CI
  mc_wait                 passenger wait by scenario, NC / FH / EH, 95% bootstrap CI
Titles live in the LaTeX caption, not the image. Run from starter/ after calibrate_corridor.py and mc.py.
"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S

SCEN  = ["Stage A (D+T)", "Ablation S (D+T+S)", "Ablation W (D+T+W)", "Ablation B (D+T+B)", "Stage B (D+T+S+W+B)"]
SHORT = ["Stage A\n(D+T)", "Abl. S\n(+surge)", "Abl. W\n(+weather)", "Abl. B\n(+breakdown)", "Stage B\n(all)"]
CTRLS = [("NC", S.NC_C), ("FH", S.FH_C), ("EH", S.EH_C)]


def boot(x, f=np.mean, n=5000, rng=np.random.default_rng(0)):
    x = np.asarray([v for v in x if np.isfinite(v)])
    if len(x) < 2: return (np.nan, np.nan, np.nan)
    bs = [f(rng.choice(x, len(x), True)) for _ in range(n)]
    return float(f(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def calibration_fig(plt):
    if not os.path.exists("results/calibration.csv"): return
    c = pd.read_csv("results/calibration.csv")
    fig, ax = plt.subplots(figsize=S.SQUARE)
    lim = max(c.observed_s.max(), c.simulated_s.max()) * 1.08
    ax.plot([0, lim], [0, lim], "--", color=S.GREY, lw=1, label="perfect match")
    ax.scatter(c.observed_s, c.simulated_s, s=28, color=S.PRIMARY, zorder=3, edgecolor="white", linewidth=0.4)
    rmspe = np.sqrt(np.mean(((c.simulated_s - c.observed_s) / c.observed_s) ** 2)) * 100
    ax.set_xlabel("Observed segment running time (s, APC)")
    ax.set_ylabel("Simulated segment running time (s, SUMO)")
    ax.text(0.04, 0.96, f"RMSPE {rmspe:.2f}%\nGEH $<$ 5 on {len(c)}/{len(c)} segments",
            transform=ax.transAxes, va="top", ha="left", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", lw=0.6))
    ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.legend(loc="lower right")
    S.save(fig, "calibration_validation")


def scenario_fig(plt, df, col, ylabel, fname):
    x = np.arange(len(SCEN)); n = len(CTRLS); wpx = 0.8 / n
    fig, ax = plt.subplots(figsize=S.WIDE)
    for k, (c, color) in enumerate(CTRLS):
        off = (k - (n - 1) / 2) * wpx
        m, lo, hi = [], [], []
        for sc in SCEN:
            v = df[(df.scenario == sc) & (df.controller == c)][col].values
            pm, plo, phi = boot(v); m.append(pm); lo.append(pm - plo); hi.append(phi - pm)
        ax.bar(x + off, m, wpx, yerr=[lo, hi], capsize=2, color=color, label=c,
               edgecolor="white", linewidth=0.4, error_kw=dict(lw=0.8, ecolor="#444"))
    ax.set_xticks(x); ax.set_xticklabels(SHORT); ax.set_ylabel(ylabel)
    ax.legend(title="Controller", ncol=3, loc="upper left"); ax.grid(axis="y")
    S.save(fig, fname)


def main():
    S.apply()
    import matplotlib.pyplot as plt
    calibration_fig(plt)
    if os.path.exists("results/mc_results.csv"):
        df = pd.read_csv("results/mc_results.csv")
        scenario_fig(plt, df, "headway_cv", "Headway CV (bunching)", "mc_headway_cv")
        scenario_fig(plt, df, "wait_s", "Mean passenger wait (s)", "mc_wait")


if __name__ == "__main__":
    main()
