"""Evaluate a trained MARL checkpoint as the 4th controller vs NC/FH/EH (SO3 / the Dec-5 comparison).

Runs the greedy policy (and, by default, the three baselines) across the manuscript activation-matrix
cells at the SAME control stops and matched seeds, and reports headway CV / wait with bootstrap 95% CIs
plus the paired % change vs No-Control. This is the table the MARL result slots into.

    python scripts/eval_marl.py --ckpt experiments/gate/checkpoint.pt --N 20
"""
import os, sys, argparse, numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "envs"))
sys.path.insert(0, os.path.join(_here, "..", "agents"))
from corridor_sim import simulate, BASELINES, STOPS
from marl_env import Config, MarlController, N_ACTIONS
from obs import OBS_DIM
from ddqn import DDQNAgent

SCEN = [("Stage A (D+T)", dict(T=True)), ("Ablation S (D+T+S)", dict(T=True, S=True)),
        ("Ablation W (D+T+W)", dict(T=True, W=True)), ("Ablation B (D+T+B)", dict(T=True, B=True)),
        ("Stage B (D+T+S+W+B)", dict(T=True, S=True, W=True, B=True))]


def boot(x, n=5000, rng=np.random.default_rng(0)):
    x = np.asarray([v for v in x if np.isfinite(v)])
    if len(x) < 2: return (float("nan"), float("nan"), float("nan"))
    bs = [np.mean(rng.choice(x, len(x), True)) for _ in range(n)]
    return float(np.mean(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def pct(nc, o, n=5000, rng=np.random.default_rng(1)):
    nc, o = np.asarray(nc), np.asarray(o); m = np.isfinite(nc) & np.isfinite(o); nc, o = nc[m], o[m]
    if len(nc) < 2: return float("nan")
    return (o.mean() - nc.mean()) / nc.mean() * 100


def evaluate(ckpt, cfg, N=20, with_baselines=True):
    agent = DDQNAgent(OBS_DIM, N_ACTIONS, hidden=cfg.net, seed=cfg.seed); agent.load(ckpt)
    cs = list(cfg.control_stops)
    ctrls = (["NC", "FH", "EH"] if with_baselines else []) + ["MARL"]
    D = {}
    for name, kw in SCEN:
        for c in ctrls:
            cvs, wts = [], []
            for s in range(N):
                dec = MarlController(agent, cfg, training=False) if c == "MARL" else BASELINES[c]
                r = simulate(dec, seed=s, control_stops=cs, **kw)
                cvs.append(r["headway_cv"]); wts.append(r["wait_s"])
            D[(name, c)] = (cvs, wts)
        row = " | ".join(f"{c} {boot(D[(name,c)][0])[0]:.3f}" for c in ctrls)
        pv = "" if not with_baselines else "  vs NC: " + ", ".join(
            f"{c} {pct(D[(name,'NC')][0], D[(name,c)][0]):+.0f}%" for c in ctrls if c != "NC")
        print(f"{name:20s} | {row}{pv}", flush=True)
    return D


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--N", type=int, default=20)
    ap.add_argument("--no-baselines", action="store_true")
    a = ap.parse_args()
    print(f"control stops: {[STOPS[i] for i in Config().control_stops]}  N={a.N}")
    evaluate(a.ckpt, Config(), N=a.N, with_baselines=not a.no_baselines)
