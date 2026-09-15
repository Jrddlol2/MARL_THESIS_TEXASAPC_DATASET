"""Generate the paper figures from saved results (full 26-stop corridor), publication style (_figstyle).

Reads results/calibration_real.csv (from build_real_net.py), results/validation/ (validate_simulator.py)
and results/mc_results.csv (from mc.py) and
writes PDF+PNG to results/figures/:
  calibration_validation  simulated vs observed segment running times, calibration + test days
  load_profile_validation riders on board vs APC max_load
  stop_service_validation share of trips serving each stop, simulated vs observed
  mc_headway_cv           headway CV by scenario, NC / FH / EH, 95% bootstrap CI
  mc_wait                 passenger wait by scenario, NC / FH / EH, 95% bootstrap CI
  stageB_weather_sweep    Stage B by weather strength (observed rain, eta 0.3-1.3), CV and wait
Titles live in the LaTeX caption, not the image. Run from starter/ after build_real_net.py, validate_simulator.py and mc.py.
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
    """Simulated vs observed running time per segment: calibration days (filled)
    and held-out test days (open), from build_real_net.py."""
    if not os.path.exists("results/calibration_real.csv"): return
    c = pd.read_csv("results/calibration_real.csv")
    fig, ax = plt.subplots(figsize=S.SQUARE)
    lim = max(c.observed_s.max(), c.simulated_s.max(), c.observed_test_s.max()) * 1.08
    ax.plot([0, lim], [0, lim], "--", color=S.GREY, lw=1, label="perfect match")
    ax.scatter(c.observed_s, c.simulated_s, s=28, color=S.PRIMARY, zorder=3, edgecolor="white", linewidth=0.4,
               label="calibration days")
    ax.scatter(c.observed_test_s, c.simulated_s, s=28, facecolor="none", edgecolor=S.VERM, linewidth=0.9, zorder=4,
               label="held-out test days")
    rmspe = np.sqrt(np.mean(((c.simulated_s - c.observed_s) / c.observed_s) ** 2)) * 100
    rmspe_test = np.sqrt(np.mean(((c.simulated_s - c.observed_test_s) / c.observed_test_s) ** 2)) * 100
    ok = int((c.geh < 5).sum()); ok_test = int((c.geh_test < 5).sum())
    ax.set_xlabel("Observed segment running time (s, APC)")
    ax.set_ylabel("Simulated segment running time (s, SUMO)")
    ax.text(0.04, 0.96, f"Calibration days: RMSPE {rmspe:.2f}%, GEH $<$ 5 on {ok}/{len(c)}\n"
                        f"Test days: RMSPE {rmspe_test:.2f}%, GEH $<$ 5 on {ok_test}/{len(c)}",
            transform=ax.transAxes, va="top", ha="left", fontsize=7,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", lw=0.6))
    ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.legend(loc="lower right")
    S.save(fig, "calibration_validation")


def validation_figs(plt):
    """Loads and stop service, simulated vs observed (from validate_simulator.py)."""
    if os.path.exists("results/validation/load_profile_sim_vs_observed.csv"):
        d = pd.read_csv("results/validation/load_profile_sim_vs_observed.csv")
        fig, ax = plt.subplots(figsize=S.WIDE)
        ax.plot(d.stop_index, d.apc_mean_max_load, color=S.GREY, marker="o", label="APC mean max_load (door-open visits, weekday 07-18)")
        ax.plot(d.stop_index, d.simulated_load_leaving, color=S.BLUE, marker="s", label="Simulated riders on board leaving stop (No-Control)")
        ax.set_xticks(d.stop_index); ax.set_xticklabels(d.bs_id, rotation=90)
        ax.set_xlabel("Stop (bs_id), in driving order"); ax.set_ylabel("Riders on board")
        ax.set_ylim(bottom=0); ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=1, frameon=False)
        S.save(fig, "load_profile_validation")
    if os.path.exists("results/validation/stop_service_sim_vs_observed.csv"):
        d = pd.read_csv("results/validation/stop_service_sim_vs_observed.csv")
        free = d[~d.always_served_in_simulator]
        fig, ax = plt.subplots(figsize=S.WIDE)
        x = np.arange(len(d)); w = 0.4
        ax.bar(x - w / 2, d.observed_served_share, w, color=S.GREY, label="Observed share of trips serving the stop (test days)")
        ax.bar(x + w / 2, d.simulated_served_share, w, color=S.BLUE, label="Simulated (No-Control, 30 seeds)")
        for i in d.index[d.always_served_in_simulator]:
            ax.text(i + w / 2, 1.02, "*", ha="center", va="bottom", fontsize=9)
        r = np.corrcoef(free.observed_served_share, free.simulated_served_share)[0, 1]
        ax.set_xticks(x); ax.set_xticklabels(d.bs_id, rotation=90)
        ax.set_xlabel("Stop (bs_id), in driving order  (* always served: first, last, control stops)")
        ax.set_ylabel("Share of trips that stop"); ax.set_ylim(0, 1.15)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False,
                  title=f"stops not marked *: r = {r:.2f}", title_fontsize=8)
        S.save(fig, "stop_service_validation")


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


SWEEP = [("observed\nrain", "results/mc_results_observed_rain.csv"),
         ("0.3", "results/mc_results_stageB_eta0.3.csv"),
         ("0.6", "results/mc_results_stageB_eta0.6.csv"),
         ("0.8", "results/mc_results.csv"),
         ("1.0", "results/mc_results_stageB_eta1.0.csv"),
         ("1.3", "results/mc_results_stageB_eta1.3.csv")]


def weather_sweep_fig(plt):
    """Stage B (D+T+S+W+B) by weather strength: headway CV and wait, NC / FH / EH, 95% bootstrap CI.
    Also writes the numbers to results/stageB_weather_sweep.csv."""
    if not all(os.path.exists(f) for _, f in SWEEP): return
    table = []
    fig, axes = plt.subplots(1, 2, figsize=S.WIDE)
    x = np.arange(len(SWEEP))
    for ax, col, ylabel in [(axes[0], "headway_cv", "Headway CV (bunching)"), (axes[1], "wait_s", "Mean passenger wait (s)")]:
        for c, color in CTRLS:
            m, lo, hi = [], [], []
            for level, f in SWEEP:
                d = pd.read_csv(f)
                v = d[(d.scenario == "Stage B (D+T+S+W+B)") & (d.controller == c)][col].values
                pm, plo, phi = boot(v); m.append(pm); lo.append(pm - plo); hi.append(phi - pm)
                table.append((level.replace("\n", " "), c, col, pm, plo, phi, len(v)))
            ax.errorbar(x, m, yerr=[lo, hi], color=color, marker="o", ms=3.5, lw=1.2, capsize=2, label=c)
        ax.set_xticks(x); ax.set_xticklabels([level for level, _ in SWEEP])
        ax.set_ylabel(ylabel)
        ax.grid(axis="y")
    axes[0].legend(title="Controller", loc="upper left")
    fig.supxlabel("Stage B weather: observed rain only, then synthetic stress $\\eta$", fontsize=9)
    S.save(fig, "stageB_weather_sweep")
    pd.DataFrame(table, columns=["weather", "controller", "metric", "mean", "ci_low", "ci_high", "n"]) \
        .to_csv("results/stageB_weather_sweep.csv", index=False)


def marl_fig(plt, tag="dr1"):
    """The four controllers over the manuscript's evaluation matrix, from results/marl_eval_<tag>.csv
    (written by scripts/eval_marl.py). Headway CV and passenger wait, 95% bootstrap CI."""
    path = f"results/marl_eval_{tag}.csv"
    if not os.path.exists(path): return
    d = pd.read_csv(path)
    order = [c for c in ["A", "S", "W", "B", "B_obs", "B_0.3", "B_0.6", "B_1.0", "B_1.3"] if c in set(d.cell)]
    labels = {"A": "Stage A", "S": "+ surge", "W": "+ weather\n(obs. rain)", "B": "+ breakdown",
              "B_obs": "Stage B\n(obs. rain)", "B_0.3": "Stage B\n$\\eta$ 0.3", "B_0.6": "Stage B\n$\\eta$ 0.6",
              "B_1.0": "Stage B\n$\\eta$ 1.0", "B_1.3": "Stage B\n$\\eta$ 1.3"}
    controllers = [("NC", S.NC_C), ("FH", S.FH_C), ("EH", S.EH_C), ("MARL", S.PURPLE)]
    x = np.arange(len(order)); wpx = 0.8 / len(controllers)
    for col, ylabel, fname in [("headway_cv", "Headway CV (bunching)", f"marl_{tag}_headway_cv"),
                               ("wait_s", "Mean passenger wait (s)", f"marl_{tag}_wait")]:
        fig, ax = plt.subplots(figsize=S.WIDE)
        for k, (c, color) in enumerate(controllers):
            off = (k - (len(controllers) - 1) / 2) * wpx
            m, lo, hi = [], [], []
            for cell in order:
                v = d[(d.cell == cell) & (d.controller == c)][col].values
                pm, plo, phi = boot(v); m.append(pm); lo.append(pm - plo); hi.append(phi - pm)
            ax.bar(x + off, m, wpx, yerr=[lo, hi], capsize=2, color=color, label=c,
                   edgecolor="white", linewidth=0.4, error_kw=dict(lw=0.8, ecolor="#444"))
        ax.set_xticks(x); ax.set_xticklabels([labels[c] for c in order], fontsize=7)
        ax.set_ylabel(ylabel); ax.grid(axis="y")
        ax.legend(title="Controller", ncol=4, loc="upper left")
        S.save(fig, fname)


def main():
    S.apply()
    import matplotlib.pyplot as plt
    calibration_fig(plt)
    validation_figs(plt)
    weather_sweep_fig(plt)
    marl_fig(plt)
    if os.path.exists("results/mc_results.csv"):
        df = pd.read_csv("results/mc_results.csv")
        scenario_fig(plt, df, "headway_cv", "Headway CV (bunching)", "mc_headway_cv")
        scenario_fig(plt, df, "wait_s", "Mean passenger wait (s)", "mc_wait")


if __name__ == "__main__":
    main()
