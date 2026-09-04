"""Marey (time-space) diagram — bus trajectories over the corridor, publication style (_figstyle).
Bunching shows as converging lines. 2x2: No-Control vs Even-Headway, under Stage A (D+T) and Weather
(D+T+W), at the designated control stops (one seed). -> results/figures/marey_diagram.{pdf,png}.
"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S
S.apply()
import matplotlib.pyplot as plt
sys.path.insert(0, "envs")
import corridor_sim as C

SEED = 5
CS = C.CONTROL_STOPS
PANELS = [("Stage A (D+T)", dict(T=True)), ("Weather (D+T+W)", dict(T=True, W=True))]
CTRLS = [("No-Control", "NC"), ("Even-Headway", "EH")]

fig, axes = plt.subplots(len(PANELS), len(CTRLS), figsize=(5.9, 4.6), sharex=True, sharey=True)
for ri, (sname, kw) in enumerate(PANELS):
    for ci, (clabel, cname) in enumerate(CTRLS):
        ax = axes[ri][ci]
        out = C.simulate(C.BASELINES[cname], seed=SEED, control_stops=CS, trace=True, **kw)
        cum = np.array(out["cum"]) / 1000.0                       # km
        for i in CS:
            ax.axhline(cum[i], color=S.CTRL_ACCENT, lw=0.6, alpha=0.5, zorder=0)
        for b, traj in out["traj"].items():
            if len(traj) < 2: continue
            ts = [t / 60.0 for t, i in traj]; ys = [cum[i] for t, i in traj]
            ax.plot(ts, ys, lw=0.9, alpha=0.7, color=S.PRIMARY)
        ax.set_title(f"{clabel} — {sname}", fontsize=8)
        if ci == 0: ax.set_ylabel("distance along corridor (km)")
        if ri == len(PANELS) - 1: ax.set_xlabel("time (min)")
        ax.grid(alpha=0.2)
os.makedirs("results/figures", exist_ok=True)
S.save(fig, "marey_diagram")
