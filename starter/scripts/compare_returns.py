"""Reward convergence: episode return over training, one panel per run.

    python scripts/compare_returns.py [name ...]   -> results/figures/marl_runs_return.{pdf,png}

Each panel is one run: the grey line is the return of every episode, the coloured line a 25-episode
mean, and the vertical mark is where exploration reaches its 5% floor.

Each panel is scaled to its own mean curve rather than to the raw episodes, which swing about three
times as far. The panels are NOT on a shared scale on purpose. Each run optimises a different reward, so their
returns are different quantities and comparing their heights would be meaningless; what is comparable
is the SHAPE -- whether each run's own return stops improving, and when.
"""
import sys, os, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S
S.apply()
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = sys.argv[1:] or ["dr1", "dr2_even", "dr3_both", "dr4_even_hold"]
LABELS = {"dr1": "A  schedule adherence", "dr2_even": "B  evenness",
          "dr3_both": "C  both gaps vs schedule", "dr4_even_hold": "D  evenness + in-vehicle cost"}
COLOURS = {"dr1": S.GREY, "dr2_even": S.BLUE, "dr3_both": S.ORANGE, "dr4_even_hold": S.PURPLE}


def rolling(x, w=25):
    if len(x) < w:
        return np.asarray(x, float), np.arange(1, len(x) + 1)
    mean = np.convolve(x, np.ones(w) / w, mode="valid")
    return mean, np.arange(w, len(x) + 1)


present = [r for r in RUNS if os.path.exists(os.path.join(ROOT, "experiments", r, "metrics.csv"))]
fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.6), sharex=True)
for ax, name in zip(axes.flat, present):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "experiments", name, "metrics.csv"))))
    episode = [int(r["episode"]) for r in rows]
    ret = [float(r["train_return"]) for r in rows]
    eps = [float(r["epsilon"]) for r in rows]
    colour = COLOURS.get(name, S.PRIMARY)
    ax.plot(episode, ret, color=S.CONTEXT, lw=0.5, alpha=0.55)
    mean, x = rolling(ret)
    ax.plot(x, mean, color=colour, lw=1.8, label="25-episode mean")
    # scale to the mean curve, not to the raw spikes: individual episodes swing three times as far,
    # which otherwise squashes every curve into a flat band
    low, high = float(np.min(mean)), float(np.max(mean))
    pad = 0.35 * (high - low)
    ax.set_ylim(low - pad, high + pad)
    floor = next((e for e, v in zip(episode, eps) if v <= 0.051), None)
    if floor:
        ax.axvline(floor, ls=":", lw=1.0, color=S.GREY)
        ax.annotate("exploration floor", (floor, low - pad), fontsize=6, color=S.GREY,
                    rotation=90, va="bottom", ha="right")
    last = np.mean(ret[-100:])
    ax.axhline(last, ls="--", lw=0.9, color=colour, alpha=0.6)
    ax.set_title(f"{LABELS.get(name, name)}   (last 100 episodes: {last:.1f})", fontsize=7.5)
    ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=6)
for ax in axes.flat[len(present):]:
    ax.axis("off")
for ax in axes[1]:
    ax.set_xlabel("training episode")
for ax in axes[:, 0]:
    ax.set_ylabel("episode return (per agent)")
S.save(fig, "marl_runs_return")
print("return curves:", ", ".join(present))
