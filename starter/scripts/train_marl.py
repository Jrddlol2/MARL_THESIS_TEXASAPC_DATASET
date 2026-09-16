"""Config-driven MARL training loop (SO2). Isolated: writes only to experiments/<name>/.

Each episode runs one corridor day under a MarlController (the shared DDQN acting + learning online).
Every --eval_every episodes the greedy policy is evaluated and the best one kept. Reward form/weights,
ΔT, discount, randomization and hyperparameters all live in Config (envs/marl_env.py).

TRAINING DISTURBANCES (methods.tex, activation matrix "Training" row)
    D and T are always on. S, W and B are switched on at random, each with probability 0.5, drawn
    fresh for every episode; when W is on its synthetic strength eta ~ Uniform(0, 1.3), where 0 means
    observed ordinary rain only. The draw for episode k depends only on k, so --resume repeats it.
    --stage-a-only turns this off (D+T every episode).

EVALUATION DURING TRAINING (to pick checkpoint_best.pt)
    Stage A, Stage B with observed rain, and Stage B at eta 0.6, 3 seeds each (seeds 90000+, never the
    seeds 0-29 used for the final comparison). Score = mean headway CV over the three cells. Runs in
    parallel.

Files in experiments/<name>/
    config.json          the Config the run used
    metrics.csv          one row per episode: its disturbances, return, CV, evaluation scores
    training_state.pt    everything needed to resume, rewritten every --save_every episodes
    checkpoint_best.pt   the policy with the best evaluation score so far
    checkpoint.pt        the policy at the end of the run

Run from starter/:
    python scripts/train_marl.py --episodes 4 --eval_every 2 --save_every 2 --name smoke   # plumbing check
    python scripts/train_marl.py --episodes 800 --name dr1                                 # the real run
    python scripts/train_marl.py --episodes 800 --irr even --name dr2_even                 # a reward variant
    python scripts/train_marl.py --episodes 800 --name dr1 --resume                        # continue it
Then: python scripts/eval_marl.py --ckpt experiments/dr1/checkpoint_best.pt
"""
import os, sys, time, csv, json, argparse, dataclasses, numpy as np
from concurrent.futures import ProcessPoolExecutor
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "envs"))
sys.path.insert(0, os.path.join(_here, "..", "agents"))
from corridor_sim import simulate
from marl_env import Config, MarlController, N_ACTIONS
from obs import OBS_DIM
from ddqn import DDQNAgent

STAGE_B = dict(T=True, S=True, W=True, B=True)
VALIDATION = [("A", dict(T=True)), ("B_obs", dict(STAGE_B, eta=0.0)), ("B_0.6", dict(STAGE_B, eta=0.6))]
EVAL_SEEDS = 3


def training_scenario(cfg, episode):
    """The disturbances for one training episode (always the same for the same episode number)."""
    if not cfg.randomize:
        return dict(T=True)
    rng = np.random.default_rng(700_000 + episode)
    surge, weather, breakdown, eta = rng.random(), rng.random(), rng.random(), rng.uniform(0.0, cfg.eta_max)
    scenario = dict(T=True, S=bool(surge < cfg.p_surge), W=bool(weather < cfg.p_weather),
                    B=bool(breakdown < cfg.p_breakdown))
    if scenario["W"]:
        scenario["eta"] = float(eta)
    return scenario


# ---- parallel evaluation: each worker loads the policy saved for this evaluation ---------------------
_policy = None


def _load_policy(path, cfg):
    global _policy
    _policy = DDQNAgent(OBS_DIM, N_ACTIONS, hidden=cfg.net, seed=cfg.seed)
    _policy.load(path)


def _evaluate_one(task):
    cell, settings, seed, cfg = task
    r = simulate(MarlController(_policy, cfg, training=False), seed=seed, control_stops=list(cfg.control_stops),
                 skip_enabled=cfg.skip_enabled, **settings)
    return cell, r["headway_cv"]


def evaluate(agent, cfg, exp, cells, jobs):
    path = f"{exp}/_policy_for_evaluation.pt"
    agent.save(path)
    tasks = [(cell, settings, 90_000 + s, cfg) for cell, settings in cells for s in range(EVAL_SEEDS)]
    scores = {cell: [] for cell, _ in cells}
    with ProcessPoolExecutor(max_workers=jobs, initializer=_load_policy, initargs=(path, cfg)) as pool:
        for cell, cv in pool.map(_evaluate_one, tasks):
            scores[cell].append(cv)
    return {cell: float(np.nanmean(v)) for cell, v in scores.items()}


def train(cfg, eval_every=50, save_every=50, resume=False, jobs=9):
    exp = f"experiments/{cfg.name}"; os.makedirs(exp, exist_ok=True)
    state_file = f"{exp}/training_state.pt"
    cs = list(cfg.control_stops)
    cells = VALIDATION if cfg.randomize else VALIDATION[:1]
    agent = DDQNAgent(OBS_DIM, N_ACTIONS, lr=cfg.lr, gamma=cfg.gamma, buffer=cfg.buffer,
                      batch=cfg.batch, target_every=cfg.target_every, warmup=cfg.warmup,
                      eps_start=cfg.eps_start, eps_end=cfg.eps_end, eps_decay=cfg.eps_decay,
                      hidden=cfg.net, seed=cfg.seed, tau=cfg.tau)

    start_episode, best_score = 0, float("inf")
    if resume and os.path.exists(state_file):
        extra = agent.load_training_state(state_file)
        start_episode, best_score = extra["episode"], extra["best_score"]
        print(f"[{cfg.name}] resuming after episode {start_episode} (best score {best_score:.3f})", flush=True)
    elif resume:
        print(f"[{cfg.name}] --resume given but no {state_file}; starting fresh", flush=True)

    header = ["episode", "S", "W", "B", "eta", "train_return", "train_cv", "eval_score"] + \
             [f"eval_{cell}" for cell, _ in cells] + ["epsilon"]
    if start_episode == 0:
        json.dump({"config": dataclasses.asdict(cfg), "validation": [c for c, _ in cells], "eval_seeds": EVAL_SEEDS},
                  open(f"{exp}/config.json", "w"), indent=2)
        log = open(f"{exp}/metrics.csv", "w", newline=""); w = csv.writer(log); w.writerow(header)
    else:
        # keep the rows up to the saved episode, drop any written after it
        rows = list(csv.reader(open(f"{exp}/metrics.csv", newline="")))
        rows = [rows[0]] + [r for r in rows[1:] if int(r[0]) <= start_episode]
        log = open(f"{exp}/metrics.csv", "w", newline=""); w = csv.writer(log); w.writerows(rows)

    t0 = time.time()
    print(f"[{cfg.name}] reward=({cfg.irr},{cfg.wait},{cfg.skip}) w={cfg.w} discount={cfg.discount} "
          f"randomize={cfg.randomize} clip={cfg.reward_clip} tau={cfg.tau} skip={cfg.skip_enabled} stops={cs}", flush=True)
    for ep in range(start_episode, cfg.episodes):
        scenario = training_scenario(cfg, ep)
        ctrl = MarlController(agent, cfg, training=True)
        r = simulate(ctrl, seed=1000 + ep, control_stops=cs, skip_enabled=cfg.skip_enabled, **scenario)
        ctrl.finalize()
        evals = {}
        if (ep + 1) % eval_every == 0:
            evals = evaluate(agent, cfg, exp, cells, jobs)
            score = float(np.mean(list(evals.values())))
            marker = ""
            if score < best_score:
                best_score = score; agent.save(f"{exp}/checkpoint_best.pt"); marker = "  <- best"
            detail = "  ".join(f"{cell} {v:.3f}" for cell, v in evals.items())
            print(f"  ep {ep+1:4d}  eps {agent.epsilon():.2f}  eval score {score:.3f} ({detail})  "
                  f"({(time.time()-t0)/60:.0f} min){marker}", flush=True)
        w.writerow([ep + 1, int(scenario.get("S", False)), int(scenario.get("W", False)), int(scenario.get("B", False)),
                    round(scenario.get("eta", 0.0), 3), round(ctrl.ret, 2), round(r["headway_cv"], 4),
                    round(float(np.mean(list(evals.values()))), 4) if evals else ""] +
                   [round(evals[c], 4) if evals else "" for c, _ in cells] + [round(agent.epsilon(), 3)])
        log.flush()
        if (ep + 1) % save_every == 0 or ep + 1 == cfg.episodes:
            agent.save_training_state(state_file, extra={"episode": ep + 1, "best_score": best_score})
    agent.save(f"{exp}/checkpoint.pt"); log.close()
    print(f"[{cfg.name}] done in {(time.time()-t0)/60:.0f} min -> {exp}/", flush=True)
    return agent


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=800)
    ap.add_argument("--eval_every", type=int, default=50)
    ap.add_argument("--save_every", type=int, default=50, help="write training_state.pt every N episodes")
    ap.add_argument("--eps_decay", type=int, default=30_000, help="exploration decay in steps (lower = exploit sooner)")
    ap.add_argument("--discount", choices=["event", "fixed"], default="event")
    ap.add_argument("--irr", choices=["dev", "even", "both"], default="dev",
                    help="irregularity term: dev = gap ahead vs the timetable, even = gap ahead vs gap behind, both")
    ap.add_argument("--wait", choices=["queue", "hold"], default="queue",
                    help="waiting term: queue = riders waiting at the stop, hold = in-vehicle delay from holding")
    ap.add_argument("--weights", default="1.0,0.5,1.0", help="w1,w2,w3 for the three reward terms")
    ap.add_argument("--stage-a-only", action="store_true", help="train on D+T only (no randomized S, W, B)")
    ap.add_argument("--jobs", type=int, default=9, help="parallel workers for evaluation")
    ap.add_argument("--resume", action="store_true", help="continue from experiments/<name>/training_state.pt")
    ap.add_argument("--name", default="dr1")
    a = ap.parse_args()
    train(Config(episodes=a.episodes, eps_decay=a.eps_decay, discount=a.discount, randomize=not a.stage_a_only,
                 irr=a.irr, wait=a.wait, w=tuple(float(x) for x in a.weights.split(",")), name=a.name),
          eval_every=a.eval_every, save_every=a.save_every, resume=a.resume, jobs=a.jobs)
