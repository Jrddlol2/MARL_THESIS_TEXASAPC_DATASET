"""Config-driven MARL training loop (SO2). Isolated: writes only to experiments/<name>/.

Each episode runs one corridor day under a MarlController (the shared DDQN acting + learning online).
Periodically evaluates the greedy policy and logs headway CV so you can watch it learn. This is the
harness you SWEEP — reward form/weights, ΔT, hyperparameters all live in Config (envs/marl_env.py);
nothing here is a committed decision.

Run from the repo root:
    python scripts/train_marl.py --episodes 6 --eval_every 3 --name smoke   # quick plumbing check
    python scripts/train_marl.py --episodes 800 --name gate                 # a real fail-fast gate
Scenario defaults to Stage A (D+T), holding-only — the gate condition. Writes metrics.csv + checkpoint.pt.
"""
import os, sys, time, csv, argparse, numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "envs"))
sys.path.insert(0, os.path.join(_here, "..", "agents"))
from corridor_sim import simulate
from marl_env import Config, MarlController, N_ACTIONS
from obs import OBS_DIM
from ddqn import DDQNAgent


def train(cfg, scenario=dict(T=True), eval_every=50, eval_seeds=5):
    exp = f"experiments/{cfg.name}"; os.makedirs(exp, exist_ok=True)
    cs = list(cfg.control_stops)
    agent = DDQNAgent(OBS_DIM, N_ACTIONS, lr=cfg.lr, gamma=cfg.gamma, buffer=cfg.buffer,
                      batch=cfg.batch, target_every=cfg.target_every, warmup=cfg.warmup,
                      eps_start=cfg.eps_start, eps_end=cfg.eps_end, eps_decay=cfg.eps_decay,
                      hidden=cfg.net, seed=cfg.seed)
    log = open(f"{exp}/metrics.csv", "w", newline=""); w = csv.writer(log)
    w.writerow(["episode", "train_return", "train_cv", "eval_cv", "epsilon"])
    t0 = time.time()
    print(f"[{cfg.name}] reward=({cfg.irr},{cfg.wait},{cfg.skip}) w={cfg.w} skip={cfg.skip_enabled} "
          f"stops={cs} scenario={scenario}", flush=True)
    for ep in range(cfg.episodes):
        ctrl = MarlController(agent, cfg, training=True)
        r = simulate(ctrl, seed=1000 + ep, control_stops=cs, **scenario)
        ctrl.finalize()
        eval_cv = ""
        if (ep + 1) % eval_every == 0:
            evs = [simulate(MarlController(agent, cfg, training=False), seed=90000 + s,
                            control_stops=cs, **scenario)["headway_cv"] for s in range(eval_seeds)]
            eval_cv = float(np.nanmean(evs))
            print(f"  ep {ep+1:4d}  ret {ctrl.ret:7.1f}  train_cv {r['headway_cv']:.3f}  "
                  f"eval_cv {eval_cv:.3f}  eps {agent.epsilon():.2f}  ({time.time()-t0:.0f}s)", flush=True)
        w.writerow([ep + 1, round(ctrl.ret, 2), round(r["headway_cv"], 4), eval_cv,
                    round(agent.epsilon(), 3)]); log.flush()
    agent.save(f"{exp}/checkpoint.pt"); log.close()
    print(f"[{cfg.name}] done in {time.time()-t0:.0f}s -> {exp}/ (checkpoint.pt, metrics.csv)", flush=True)
    return agent


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=800)
    ap.add_argument("--eval_every", type=int, default=50)
    ap.add_argument("--name", default="gate")
    a = ap.parse_args()
    train(Config(episodes=a.episodes, name=a.name), eval_every=a.eval_every)
