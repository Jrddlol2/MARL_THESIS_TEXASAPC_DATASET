"""MARL controller + Config — plugs the shared DDQN into corridor_sim as a decide() function.

corridor_sim calls `decide(obs) -> (hold_seconds, skip)` at each control-stop arrival. `MarlController`
is a stateful decide: for each bus it remembers its last (obs, action), and on the bus's NEXT decision
it computes the reward for that action (from the resulting state), pushes the transition
(s_prev, a_prev, r, s_cur) into the shared replay buffer, learns, then picks the new action. This is
the semi-MDP assembly; parameter sharing = one agent instance serves every bus.

`Config` is the single place every experiment knob lives — reward form/weights, ΔT, skip on/off,
DDQN hyperparameters, control stops, training budget. Copy it, change a field, run; commit nothing.
"""
from dataclasses import dataclass
import numpy as np
from obs import featurize, OBS_DIM
from reward import compose, decode_action

N_ACTIONS = 10


@dataclass
class Config:
    # reward (candidate forms from reward.py; weights are the EO2.1 sweep)
    irr: str = "dev"; wait: str = "queue"; skip: str = "stranded"
    w: tuple = (1.0, 0.5, 1.0)
    # action
    H0: float = 300.0; dt: float = 300.0; skip_enabled: bool = False
    # DDQN hyperparameters
    lr: float = 1e-3; gamma: float = 0.99
    eps_start: float = 1.0; eps_end: float = 0.05; eps_decay: int = 30_000
    buffer: int = 100_000; batch: int = 64; target_every: int = 500; warmup: int = 1_000
    net: tuple = (128, 128)
    # env / training
    control_stops: tuple = (0, 1, 5, 17, 20)
    episodes: int = 2_000
    seed: int = 0
    name: str = "gate"


class MarlController:
    """Use as the `decide` passed to corridor_sim.simulate. training=True explores + learns."""
    def __init__(self, agent, cfg, training=True):
        self.agent, self.cfg, self.training = agent, cfg, training
        self.prev = {}                 # bus -> (obs_vec, action, obs_dict)
        self.ret = 0.0; self.n = 0     # episode return and transition count (diagnostics)

    def __call__(self, obs):
        bi = obs["bus"]
        ov = featurize(obs)
        if bi in self.prev:
            pov, pa, pobs = self.prev[bi]
            r = compose(pobs, obs, pa, self.cfg)
            self.ret += r; self.n += 1
            if self.training:
                self.agent.push(pov, pa, r, ov, False)
                self.agent.learn()
        a = self.agent.act(ov, greedy=not self.training)
        self.prev[bi] = (ov, a, obs)
        hold, skip = decode_action(a, self.cfg.H0, self.cfg.dt)
        return hold, (skip if self.cfg.skip_enabled else 0)

    def finalize(self):
        """End of episode: drop each bus's last (obs, action) — it has no next state to bootstrap from."""
        self.prev.clear()
