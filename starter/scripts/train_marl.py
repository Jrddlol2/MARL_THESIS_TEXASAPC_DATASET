"""Config-driven MARL training loop (SO2). Isolated: writes only to experiments/<name>/.

Each episode runs one corridor day under a MarlController (the shared DDQN acting + learning online).
Periodically evaluates the greedy policy and logs headway CV so you can watch it learn. This is the
harness you SWEEP — reward form/weights, ΔT, discount, hyperparameters all live in Config
(envs/marl_env.py); nothing here is a committed decision.

Files in experiments/<name>/
    config.json          the Config and scenario the run used
    metrics.csv          one row per episode (appended to when resuming)
    training_state.pt    everything needed to resume (network, target, optimizer, replay buffer,
                         random states, episode) — rewritten every --save_every episodes
    checkpoint_best.pt   the policy with the lowest evaluation headway CV so far
    checkpoint.pt        the policy at the end of the run
Evaluation during training uses seeds 90000+, never the seeds 0-29 used for the final comparison,
so picking the best checkpoint does not peek at the test seeds.

Run from starter/:
    python scripts/train_marl.py --episodes 6 --eval_every 3 --save_every 3 --name smoke  # plumbing check
    python scripts/train_marl.py --episodes 800 --name gate                               # the Stage A gate
    python scripts/train_marl.py --episodes 800 --name gate --resume                      # continue a stopped run
Then: python scripts/eval_marl.py --ckpt experiments/gate/checkpoint_best.pt
Scenario defaults to Stage A (D+T), holding-only — the gate condition.
"""
import os, sys, time, csv, json, argparse, dataclasses, numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "envs"))
sys.path.insert(0, os.path.join(_here, "..", "agents"))
from corridor_sim import simulate
from marl_env import Config, MarlController, N_ACTIONS
from obs import OBS_DIM
from ddqn import DDQNAgent


def train(cfg, scenario=dict(T=True), eval_every=50, eval_seeds=5, save_every=50, resume=False):
    exp = f"experiments/{cfg.name}"; os.makedirs(exp, exist_ok=True)
    state_file = f"{exp}/training_state.pt"
    cs = list(cfg.control_stops)
    agent = DDQNAgent(OBS_DIM, N_ACTIONS, lr=cfg.lr, gamma=cfg.gamma, buffer=cfg.buffer,
                      batch=cfg.batch, target_every=cfg.target_every, warmup=cfg.warmup,
                      eps_start=cfg.eps_start, eps_end=cfg.eps_end, eps_decay=cfg.eps_decay,
                      hidden=cfg.net, seed=cfg.seed)

    start_episode, best_cv = 0, float("inf")
    if resume and os.path.exists(state_file):
        extra = agent.load_training_state(state_file)
        start_episode, best_cv = extra["episode"], extra["best_cv"]
        print(f"[{cfg.name}] resuming after episode {start_episode} (best eval CV {best_cv:.3f})", flush=True)
    elif resume:
        print(f"[{cfg.name}] --resume given but no {state_file}; starting fresh", flush=True)

    if start_episode == 0:
        json.dump({"config": dataclasses.asdict(cfg), "scenario": scenario, "eval_seeds": eval_seeds},
                  open(f"{exp}/config.json", "w"), indent=2)
        log = open(f"{exp}/metrics.csv", "w", newline=""); w = csv.writer(log)
        w.writerow(["episode", "train_return", "train_cv", "eval_cv", "epsilon"])
    else:
        # keep the rows up to the saved episode, drop any written after it
        rows = list(csv.reader(open(f"{exp}/metrics.csv", newline="")))
        rows = [rows[0]] + [r for r in rows[1:] if int(r[0]) <= start_episode]
        log = open(f"{exp}/metrics.csv", "w", newline=""); w = csv.writer(log); w.writerows(rows)

    t0 = time.time()
    print(f"[{cfg.name}] reward=({cfg.irr},{cfg.wait},{cfg.skip}) w={cfg.w} discount={cfg.discount} "
          f"skip={cfg.skip_enabled} stops={cs} scenario={scenario}", flush=True)
    for ep in range(start_episode, cfg.episodes):
        ctrl = MarlController(agent, cfg, training=True)
        r = simulate(ctrl, seed=1000 + ep, control_stops=cs, skip_enabled=cfg.skip_enabled, **scenario)
        ctrl.finalize()
        eval_cv = ""
        if (ep + 1) % eval_every == 0:
            evs = [simulate(MarlController(agent, cfg, training=False), seed=90000 + s, skip_enabled=cfg.skip_enabled,
                            control_stops=cs, **scenario)["headway_cv"] for s in range(eval_seeds)]
            eval_cv = float(np.nanmean(evs))
            marker = ""
            if eval_cv < best_cv:
                best_cv = eval_cv; agent.save(f"{exp}/checkpoint_best.pt"); marker = "  <- best"
            print(f"  ep {ep+1:4d}  ret {ctrl.ret:7.1f}  train_cv {r['headway_cv']:.3f}  "
                  f"eval_cv {eval_cv:.3f}  eps {agent.epsilon():.2f}  ({time.time()-t0:.0f}s){marker}", flush=True)
        w.writerow([ep + 1, round(ctrl.ret, 2), round(r["headway_cv"], 4), eval_cv,
                    round(agent.epsilon(), 3)]); log.flush()
        if (ep + 1) % save_every == 0 or ep + 1 == cfg.episodes:
            agent.save_training_state(state_file, extra={"episode": ep + 1, "best_cv": best_cv})
    agent.save(f"{exp}/checkpoint.pt"); log.close()
    print(f"[{cfg.name}] done in {time.time()-t0:.0f}s -> {exp}/ (checkpoint_best.pt, checkpoint.pt, "
          f"training_state.pt, metrics.csv)", flush=True)
    return agent


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=800)
    ap.add_argument("--eval_every", type=int, default=50)
    ap.add_argument("--save_every", type=int, default=50, help="write training_state.pt every N episodes")
    ap.add_argument("--eps_decay", type=int, default=30_000, help="exploration decay in steps (lower = exploit sooner)")
    ap.add_argument("--discount", choices=["event", "fixed"], default="event")
    ap.add_argument("--resume", action="store_true", help="continue from experiments/<name>/training_state.pt")
    ap.add_argument("--name", default="gate")
    a = ap.parse_args()
    train(Config(episodes=a.episodes, eps_decay=a.eps_decay, discount=a.discount, name=a.name),
          eval_every=a.eval_every, save_every=a.save_every, resume=a.resume)
