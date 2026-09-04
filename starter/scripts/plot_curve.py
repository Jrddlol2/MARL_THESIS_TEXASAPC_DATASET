"""Plot a MARL training run's learning curve from experiments/<name>/metrics.csv, publication style.
    python scripts/plot_curve.py [name]   ->  results/figures/<name>_curve.{pdf,png}
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S
S.apply()
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

fig, ax = plt.subplots(figsize=S.WIDE)
ax.plot(ep, tcv, color=S.CONTEXT, lw=0.9, label="train CV (per episode, exploring)")
ax.plot(ev_ep, ev, "-o", color=S.PRIMARY, lw=1.8, ms=4, label="eval CV (greedy policy)")
ax.axhline(NC, ls="--", color=S.NC_C, lw=1.2, label=f"No-Control  {NC:.3f}")
ax.axhline(FH, ls="--", color=S.FH_C, lw=1.2, label=f"Forward-Headway  {FH:.3f}")
ax.set_xlabel("training episode"); ax.set_ylabel("headway CV (bunching)")
ax.grid(alpha=0.3); ax.set_ylim(0, max(0.7, max(tcv) * 1.05))
ax2 = ax.twinx(); ax2.plot(ep, eps, color=S.GREY, lw=0.8, alpha=0.6)
ax2.set_ylabel(r"$\varepsilon$ (exploration)", color=S.GREY); ax2.set_ylim(0, 1.05)
ax2.tick_params(colors=S.GREY); ax2.grid(False); ax2.spines["top"].set_visible(False)
ax.legend(loc="upper right", fontsize=7)
S.save(fig, f"{NAME}_curve")
print(len(ep), "episodes,", len(ev), "eval points")
