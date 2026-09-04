"""Plot a MARL training run's learning curve from experiments/<name>/metrics.csv.
    python scripts/plot_curve.py [name]   ->  results/figures/<name>_curve.png
"""
import sys, os, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAME = sys.argv[1] if len(sys.argv) > 1 else "gate1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "experiments", NAME, "metrics.csv")
NC, FH = 0.331, 0.237

ep, tcv, eps, ev, ev_ep = [], [], [], [], []
for r in csv.DictReader(open(P)):
    ep.append(int(r["episode"])); tcv.append(float(r["train_cv"])); eps.append(float(r["epsilon"]))
    if r["eval_cv"]:
        ev.append(float(r["eval_cv"])); ev_ep.append(int(r["episode"]))

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(ep, tcv, color="#c9d6e5", lw=1, label="train CV (per episode, exploring)")
ax.plot(ev_ep, ev, "-o", color="#1f63d6", lw=2.2, ms=6, label="eval CV (greedy policy)")
ax.axhline(NC, ls="--", color="#9e9e9e", lw=1.5, label=f"No-Control  {NC:.3f}")
ax.axhline(FH, ls="--", color="#e0913a", lw=1.5, label=f"Forward-Headway  {FH:.3f}")
ax.set_xlabel("training episode"); ax.set_ylabel("headway CV (bunching)")
ax.set_title(f"MARL learning curve — {NAME} (Stage A, holding-only)")
ax.grid(alpha=0.3); ax.set_axisbelow(True); ax.set_ylim(0, max(0.7, max(tcv) * 1.05))
ax2 = ax.twinx(); ax2.plot(ep, eps, color="#c0392b", lw=0.9, alpha=0.5)
ax2.set_ylabel("ε (exploration)", color="#c0392b"); ax2.set_ylim(0, 1.05); ax2.tick_params(colors="#c0392b")
ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
fig.tight_layout()
out = os.path.join(ROOT, "results", "figures", f"{NAME}_curve.png")
fig.savefig(out, dpi=150)
print("wrote", out, "|", len(ep), "episodes,", len(ev), "eval points")
