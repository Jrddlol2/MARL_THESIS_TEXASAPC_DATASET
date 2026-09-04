"""Convergence curves for a MARL run: episode return and per-episode headway CV (raw + rolling mean),
publication style (_figstyle).  python scripts/convergence.py [name] -> results/figures/<name>_convergence.{pdf,png}
"""
import sys, os, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S
S.apply()
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
    return np.convolve(x, np.ones(w) / w, mode="valid")


rx = ep[len(ep) - len(roll(ret)):]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.9, 2.9))
a1.plot(ep, ret, color=S.CONTEXT, lw=0.8)
a1.plot(rx, roll(ret), color=S.PRIMARY, lw=1.8, label="15-episode mean")
a1.set_xlabel("training episode"); a1.set_ylabel("episode return (per-agent)")
a1.grid(alpha=0.3); a1.legend()

a2.plot(ep, tcv, color=S.CONTEXT, lw=0.8)
a2.plot(rx, roll(tcv), color=S.PRIMARY, lw=1.8, label="15-episode mean")
a2.axhline(NC, ls="--", color=S.NC_C, lw=1.2, label=f"No-Control {NC:.3f}")
a2.axhline(FH, ls="--", color=S.FH_C, lw=1.2, label=f"Forward-Headway {FH:.3f}")
a2.set_xlabel("training episode"); a2.set_ylabel("headway CV (bunching)")
a2.grid(alpha=0.3); a2.legend(fontsize=7); a2.set_ylim(0, max(0.7, tcv.max() * 1.05))

S.save(fig, f"{NAME}_convergence")
print(len(ep), "episodes")
