"""Marey (time-space) diagram — bus trajectories over the corridor. Bunching shows as converging lines.

A 2x2 panel: No-Control vs Even-Headway, each under Stage A (D+T) and Weather (D+T+W), at the designated
control stops. Uses one representative seed. -> results/figures/marey_diagram.png. Run from repo root.
"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "envs")
import corridor_sim as C

SEED = 5
CS = C.CONTROL_STOPS
PANELS = [("Stage A  (D+T)", dict(T=True)), ("Weather  (D+T+W)", dict(T=True, W=True))]
CTRLS = [("No-Control", "NC"), ("Even-Headway", "EH")]

fig, axes = plt.subplots(len(PANELS), len(CTRLS), figsize=(11, 8), sharex=True, sharey=True)
for ri, (sname, kw) in enumerate(PANELS):
    for ci, (clabel, cname) in enumerate(CTRLS):
        ax = axes[ri][ci]
        out = C.simulate(C.BASELINES[cname], seed=SEED, control_stops=CS, trace=True, **kw)
        cum = np.array(out["cum"]) / 1000.0                       # km
        for i in CS:                                              # mark control stops
            ax.axhline(cum[i], color="#cbd5e1", lw=0.8, zorder=0)
        for b, traj in out["traj"].items():
            if len(traj) < 2: continue
            ts = [t / 60.0 for t, i in traj]; ys = [cum[i] for t, i in traj]
            ax.plot(ts, ys, lw=1.2, alpha=0.85)
        ax.set_title(f"{clabel}  —  {sname}", fontsize=11)
        if ci == 0: ax.set_ylabel("distance along corridor (km)")
        if ri == len(PANELS) - 1: ax.set_xlabel("time (min)")
        ax.grid(alpha=0.2)
fig.suptitle("Bus trajectories at the designated control stops (grey lines) — bunching = trajectories converging",
             fontsize=12.5)
fig.tight_layout(rect=[0, 0, 1, 0.96])
os.makedirs("results/figures", exist_ok=True)
fig.savefig("results/figures/marey_diagram.png", dpi=150)
print("wrote results/figures/marey_diagram.png")
