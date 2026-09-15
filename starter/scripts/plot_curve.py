"""Learning curve of a MARL training run, publication style.

    python scripts/plot_curve.py [name]   ->  results/figures/<name>_curve.{pdf,png}

Reads experiments/<name>/metrics.csv: the per-episode training CV (exploring, under whatever
disturbances that episode drew) and the periodic greedy evaluation on each validation cell.
Even-Headway in the matching cell is drawn as a dashed target line, read from results/mc_results*.csv
so the figure never carries a hard-coded baseline.
"""
import sys, os, csv
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S
S.apply()
import matplotlib.pyplot as plt

NAME = sys.argv[1] if len(sys.argv) > 1 else "dr1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS = os.path.join(ROOT, "experiments", NAME, "metrics.csv")

# validation cell -> (label, colour, baseline file, scenario name in that file)
CELLS = {
    "eval_A":     ("Stage A", S.BLUE, "results/mc_results.csv", "Stage A (D+T)"),
    "eval_B_obs": ("Stage B, observed rain", S.VERM, "results/mc_results_observed_rain.csv", "Stage B (D+T+S+W+B)"),
    "eval_B_0.6": ("Stage B, $\\eta$ 0.6", S.PURPLE, "results/mc_results_stageB_eta0.6.csv", "Stage B (D+T+S+W+B)"),
}


def even_headway(file, scenario):
    path = os.path.join(ROOT, file)
    if not os.path.exists(path):
        return None
    d = pd.read_csv(path)
    v = d[(d.scenario == scenario) & (d.controller == "EH")]["headway_cv"]
    return float(v.mean()) if len(v) else None


rows = list(csv.DictReader(open(METRICS)))
episode = [int(r["episode"]) for r in rows]
train_cv = [float(r["train_cv"]) for r in rows]
epsilon = [float(r["epsilon"]) for r in rows]

fig, ax = plt.subplots(figsize=S.WIDE)
ax.plot(episode, train_cv, color=S.CONTEXT, lw=0.8, label="training episode (exploring, random disturbances)")
for column, (label, colour, file, scenario) in CELLS.items():
    if column not in rows[0]:
        continue
    x = [int(r["episode"]) for r in rows if r.get(column)]
    y = [float(r[column]) for r in rows if r.get(column)]
    if not x:
        continue
    ax.plot(x, y, "-o", color=colour, lw=1.6, ms=3.5, label=f"greedy policy, {label}")
    target = even_headway(file, scenario)
    if target:
        ax.axhline(target, ls="--", color=colour, lw=1.0, alpha=0.7)
        ax.annotate(f"Even-Headway {target:.3f}", (episode[-1], target), fontsize=6, color=colour,
                    va="bottom", ha="right")

ax.set_xlabel("training episode"); ax.set_ylabel("headway CV (bunching)")
ax.grid(alpha=0.3); ax.set_ylim(0, max(1.0, max(train_cv) * 1.05))
ax2 = ax.twinx(); ax2.plot(episode, epsilon, color=S.GREY, lw=0.8, alpha=0.6)
ax2.set_ylabel(r"$\varepsilon$ (exploration)", color=S.GREY); ax2.set_ylim(0, 1.05)
ax2.tick_params(colors=S.GREY); ax2.grid(False); ax2.spines["top"].set_visible(False)
ax.legend(loc="upper right", fontsize=6.5)
S.save(fig, f"{NAME}_curve")
print(len(episode), "episodes,", sum(1 for r in rows if r.get("eval_A")), "evaluation points")
