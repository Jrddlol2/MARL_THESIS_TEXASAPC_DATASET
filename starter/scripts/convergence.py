"""Convergence curves for a MARL run: episode return and per-episode headway CV, raw + rolling mean.
    python scripts/convergence.py [name]  ->  results/figures/<name>_convergence.png
"""
import sys, os, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAME = sys.argv[1] if len(sys.argv) > 1 else "gate1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "experiments", NAME, "metrics.csv")
NC, FH = 0.331, 0.237

ep, ret, tcv = [], [], []
for r in csv.DictReader(open(P)):
    ep.append(int(r["episode"])); ret.append(float(r["train_return"])); tcv.append(float(r["train_cv"]))
ep, ret, tcv = np.array(ep), np.array(ret), np.array(tcv)


def roll(x, w=15):
    if len(x) < w: return x.astype(float)
    k = np.ones(w) / w
    return np.convolve(x, k, mode="valid")


rx = ep[len(ep) - len(roll(ret)):]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))

a1.plot(ep, ret, color="#cfe0f0", lw=1)
a1.plot(rx, roll(ret), color="#1f63d6", lw=2.4, label="15-episode mean")
a1.set_xlabel("training episode"); a1.set_ylabel("episode return (per-agent, cumulative reward)")
a1.set_title("Return convergence"); a1.grid(alpha=0.3); a1.legend(fontsize=9)

a2.plot(ep, tcv, color="#cfe0f0", lw=1)
a2.plot(rx, roll(tcv), color="#1f63d6", lw=2.4, label="15-episode mean")
a2.axhline(NC, ls="--", color="#9e9e9e", lw=1.4, label=f"No-Control {NC:.3f}")
a2.axhline(FH, ls="--", color="#e0913a", lw=1.4, label=f"Forward-Headway {FH:.3f}")
a2.set_xlabel("training episode"); a2.set_ylabel("headway CV (bunching)")
a2.set_title("Bunching convergence"); a2.grid(alpha=0.3); a2.legend(fontsize=8); a2.set_ylim(0, max(0.7, tcv.max() * 1.05))

fig.suptitle(f"MARL convergence — {NAME} ({len(ep)} episodes, Stage A holding-only)", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.96])
out = os.path.join(ROOT, "results", "figures", f"{NAME}_convergence.png")
fig.savefig(out, dpi=150)
print("wrote", out, "|", len(ep), "episodes")
