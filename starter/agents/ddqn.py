"""Parameter-shared Double DQN learner (SO2 core) — the shared network + replay + update rule.

One shared Q-network serves every bus (parameter sharing); each bus calls `act(obs)` with its own
local observation and stores its own `(o,a,r,o2,done)` transition in one shared replay buffer
(CTDE: centralized training on pooled per-agent transitions, decentralized execution). The update is
Double-DQN: the online net selects the next action, the target net evaluates it.

    y = r + γ (1-done) · Q(o2, argmaxₐ Q(o2,a; θ); θ⁻)

This module is the algorithm only — obs featurization (the 7-vector of Table 3.6), the reward, the
action decode (α×ΔT, skip), and the SUMO training loop live in the env/train layer. Hyperparameters
here are implementation defaults (EO2.1), tunable. Depends on torch (CPU is fine).

Self-test: `python agents/ddqn.py` trains on a synthetic contextual bandit and checks the shared net
learns to pick the rewarding action (accuracy climbs well above chance).
"""
from __future__ import annotations
import random, numpy as np, torch, torch.nn as nn

OBS_DIM, N_ACTIONS = 7, 10                     # manuscript: Table 3.6 obs; |A| = 5 holding × 2 skip


class QNet(nn.Module):
    def __init__(self, obs_dim=OBS_DIM, n_actions=N_ACTIONS, hidden=(128, 128)):
        super().__init__()
        layers, d = [], obs_dim
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU()]; d = h
        layers += [nn.Linear(d, n_actions)]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class ReplayBuffer:
    def __init__(self, capacity, obs_dim=OBS_DIM):
        self.cap = capacity; self.i = 0; self.full = False
        self.o  = np.zeros((capacity, obs_dim), np.float32)
        self.a  = np.zeros(capacity, np.int64)
        self.r  = np.zeros(capacity, np.float32)
        self.o2 = np.zeros((capacity, obs_dim), np.float32)
        self.d  = np.zeros(capacity, np.float32)

    def push(self, o, a, r, o2, done):
        i = self.i
        self.o[i], self.a[i], self.r[i], self.o2[i], self.d[i] = o, a, r, o2, float(done)
        self.i = (i + 1) % self.cap
        self.full = self.full or self.i == 0

    def __len__(self):
        return self.cap if self.full else self.i

    def sample(self, batch):
        idx = np.random.randint(0, len(self), size=batch)
        t = lambda x: torch.as_tensor(x[idx])
        return t(self.o), t(self.a), t(self.r), t(self.o2), t(self.d)


class DDQNAgent:
    """Shared learner. All buses share this one instance: act(obs) per bus, push(...) per bus."""
    def __init__(self, obs_dim=OBS_DIM, n_actions=N_ACTIONS, lr=1e-3, gamma=0.99,
                 buffer=100_000, batch=64, target_every=500, warmup=1_000,
                 eps_start=1.0, eps_end=0.05, eps_decay=30_000, hidden=(128, 128),
                 device="cpu", seed=0):
        torch.manual_seed(seed); np.random.seed(seed); random.seed(seed)
        self.n_actions, self.gamma, self.batch = n_actions, gamma, batch
        self.target_every, self.warmup = target_every, warmup
        self.eps_start, self.eps_end, self.eps_decay = eps_start, eps_end, eps_decay
        self.device = torch.device(device)
        self.q  = QNet(obs_dim, n_actions, hidden).to(self.device)
        self.qt = QNet(obs_dim, n_actions, hidden).to(self.device)
        self.qt.load_state_dict(self.q.state_dict())
        self.opt = torch.optim.Adam(self.q.parameters(), lr=lr)
        self.buf = ReplayBuffer(buffer, obs_dim)
        self.steps = 0

    def epsilon(self):
        f = min(1.0, self.steps / self.eps_decay)
        return self.eps_start + f * (self.eps_end - self.eps_start)

    @torch.no_grad()
    def act(self, obs, greedy=False):
        if (not greedy) and random.random() < self.epsilon():
            return random.randrange(self.n_actions)
        o = torch.as_tensor(np.asarray(obs, np.float32), device=self.device).unsqueeze(0)
        return int(self.q(o).argmax(1).item())

    def push(self, o, a, r, o2, done):
        self.buf.push(np.asarray(o, np.float32), a, r, np.asarray(o2, np.float32), done)

    def learn(self):
        self.steps += 1
        if len(self.buf) < max(self.batch, self.warmup):
            return None
        o, a, r, o2, d = (x.to(self.device) for x in self.buf.sample(self.batch))
        q = self.q(o).gather(1, a.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            a2 = self.q(o2).argmax(1)                                   # online selects
            q2 = self.qt(o2).gather(1, a2.unsqueeze(1)).squeeze(1)      # target evaluates (double-Q)
            y = r + self.gamma * (1.0 - d) * q2
        loss = nn.functional.smooth_l1_loss(q, y)
        self.opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(self.q.parameters(), 10.0)
        self.opt.step()
        if self.steps % self.target_every == 0:
            self.qt.load_state_dict(self.q.state_dict())
        return float(loss.item())

    def save(self, path): torch.save(self.q.state_dict(), path)
    def load(self, path): self.q.load_state_dict(torch.load(path, map_location=self.device)); self.qt.load_state_dict(self.q.state_dict())


if __name__ == "__main__":
    # Synthetic contextual bandit: reward 1 for the "correct" action (argmax of a fixed linear map of
    # obs), else 0. A working DDQN core should learn to pick it — accuracy climbs well above 1/10.
    rng = np.random.default_rng(0)
    W = rng.normal(size=(OBS_DIM, N_ACTIONS)).astype(np.float32)
    def best(o): return int(np.argmax(o @ W))
    ag = DDQNAgent(warmup=500, eps_decay=4000)
    correct, total = 0, 0
    for step in range(12_000):
        o = rng.normal(size=OBS_DIM).astype(np.float32)
        a = ag.act(o)
        r = 1.0 if a == best(o) else 0.0
        o2 = rng.normal(size=OBS_DIM).astype(np.float32)              # bandit: next state independent
        ag.push(o, a, r, o2, True); ag.learn()
        if step > 10_000:
            correct += (ag.act(o, greedy=True) == best(o)); total += 1
    print(f"DDQN self-test: greedy accuracy over last {total} steps = {correct/max(1,total):.2f} "
          f"(chance = {1/N_ACTIONS:.2f}); eps now {ag.epsilon():.3f}, buffer {len(ag.buf)}")
