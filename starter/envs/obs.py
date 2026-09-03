"""Observation featurizer — corridor_sim's obs dict -> the manuscript 7-vector (Table 3.6), normalized.

Features (all ~[0,1] so the shared network sees a consistent scale):
    0 stop index      idx/(n-1)          spatial location along the corridor
    1 forward headway hf/H0              gap to leader (1.0 = on schedule)
    2 backward headway hb/H0             estimated gap to follower
    3 onboard load    load/cap           occupancy
    4 waiting queue   queue/Q_REF        passengers waiting at the stop
    5 weather flag    (w-0.5)/2.5        realized speed-factor intensity (neutral 1.0 -> 0.2)
    6 breakdown flag  b                  downstream incident present (0/1)

`featurize(obs)` returns a float32 array of length OBS_DIM. Variants (e.g. + neighboring-trip info)
are added here behind a config flag; the default is the manuscript vector.
"""
import numpy as np
from reward import Q_REF

OBS_DIM = 7


def featurize(o):
    H0, cap, n = o["H0"], o["cap"], o["n"]
    return np.array([
        o["idx"] / max(1, n - 1),
        o["hf"] / H0,
        o["hb"] / H0,
        o["load"] / cap,
        o["queue"] / Q_REF,
        (o["w"] - 0.5) / 2.5,
        o["b"],
    ], dtype=np.float32)


if __name__ == "__main__":
    o = dict(hf=300, hb=300, load=20, queue=5, idx=5, n=26, H0=300.0, cap=60, bus=3, w=1.0, b=0.0)
    v = featurize(o)
    print("obs vector (len %d):" % len(v), np.round(v, 3))
    assert len(v) == OBS_DIM
    print("ok")
