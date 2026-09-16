"""Compare training runs on one pair of axes, scaled to the curves rather than to the noise.

    python scripts/compare_runs.py [name ...]     -> results/figures/marl_runs_comparison.{pdf,png}

Left: the greedy policy on Stage A, every 50 episodes. Right: the mean over the three validation cells
(Stage A, Stage B with observed rain, Stage B at eta 0.6). Dashed reference lines are the 30-seed
baselines in the matching condition, so the vertical scale shows the range the controllers actually
occupy. Per-episode training values are deliberately left out: they include exploratory moves and swing
between 0.3 and 1.2, which flattens everything else.
"""
import sys, os, csv
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S
S.apply()
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = sys.argv[1:] or ["dr1", "dr2_even", "dr3_both", "dr4_even_hold"]
LABELS = {"dr1": "A  schedule adherence", "dr2_even": "B  evenness",
          "dr3_both": "C  both gaps vs schedule", "dr4_even_hold": "D  evenness + in-vehicle cost"}
COLOURS = {"dr1": S.GREY, "dr2_even": S.BLUE, "dr3_both": S.ORANGE, "dr4_even_hold": S.PURPLE}
CELLS = [("results/mc_results.csv", "Stage A (D+T)"),
         ("results/mc_results_observed_rain.csv", "Stage B (D+T+S+W+B)"),
         ("results/mc_results_stageB_eta0.6.csv", "Stage B (D+T+S+W+B)")]


def baseline(controller, file, scenario):
    d = pd.read_csv(os.path.join(ROOT, file))
    return float(d[(d.scenario == scenario) & (d.controller == controller)]["headway_cv"].mean())


stage_a = {c: baseline(c, *CELLS[0]) for c in ("NC", "FH", "EH")}
mean_cell = {c: float(np.mean([baseline(c, f, s) for f, s in CELLS])) for c in ("NC", "FH", "EH")}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2))
for panel, column, refs, title in [(ax1, "eval_A", stage_a, "Stage A"),
                                   (ax2, "eval_score", mean_cell, "mean of the three validation cells")]:
    for name in RUNS:
        path = os.path.join(ROOT, "experiments", name, "metrics.csv")
        if not os.path.exists(path):
            continue
        rows = [r for r in csv.DictReader(open(path)) if r.get(column)]
        if not rows:
            continue
        x = [int(r["episode"]) for r in rows]
        y = [float(r[column]) for r in rows]
        panel.plot(x, y, "-o", ms=3, lw=1.4, color=COLOURS.get(name, S.PRIMARY), label=LABELS.get(name, name))
    for controller, colour in [("NC", S.NC_C), ("FH", S.FH_C), ("EH", S.EH_C)]:
        panel.axhline(refs[controller], ls="--", lw=1.0, color=colour)
        panel.annotate(f"{controller} {refs[controller]:.3f}", (800, refs[controller]), fontsize=6,
                       color=colour, va="bottom", ha="right")
    panel.set_xlabel("training episode"); panel.set_title(title, fontsize=8)
    panel.grid(alpha=0.3)
ax1.set_ylabel("headway CV (greedy policy)")
ax1.set_ylim(0.30, 0.62); ax2.set_ylim(0.45, 0.72)
ax1.legend(loc="upper right", fontsize=6.5)
fig.supxlabel("")
S.save(fig, "marl_runs_comparison")
print("runs plotted:", ", ".join(RUNS))
