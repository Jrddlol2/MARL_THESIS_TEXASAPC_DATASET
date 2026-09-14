"""Parameter-shared Double DQN learner (SO2 core) — the shared network + replay + update rule.

One shared Q-network serves every bus (parameter sharing); each bus calls `act(obs)` with its own
local observation and stores its own `(o,a,r,o2,done)` transition in one shared replay buffer
(CTDE: centralized training on pooled per-agent transitions, decentralized execution). The update is
Double-DQN: the online net selects the next action, the target net evaluates it.

    y = r + g (1-done) · Q(o2, argmaxₐ Q(o2,a; θ); θ⁻)

g is the discount stored with each transition. Bus decisions are events at random times, so the
trainer passes g = e^(−β·Δt), with Δt the seconds between the bus's two decisions (Bradtke & Duff
1995; methods.tex §3, event-based discount). If no discount is passed, g = the fixed `gamma`.

This module is the algorithm only — obs featurization (the 7-vector of Table 3.6), the reward, the
action decode (α×ΔT, skip), and the SUMO training loop live in the env/train layer. Hyperparameters
here are implementation defaults (EO2.1), tunable. Depends on torch (CPU is fine).

Saving: `save/load` write only the network (for evaluation). `save_training_state/load_training_state`
also keep the target net, optimizer, step count, replay buffer and random states, so a training run
can stop and resume where it left off.

Self-test: `python agents/ddqn.py` trains on a synthetic contextual bandit and checks the shared net
learns to pick the rewarding action (accuracy climbs well above chance), then checks the event
discount and that a saved training state resumes identically.
"""
from __future__ import annotations
import os, random, numpy as np, torch, torch.nn as nn

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
        self.g  = np.zeros(capacity, np.float32)   # discount for this transition

    def push(self, o, a, r, o2, done, g):
        i = self.i
        self.o[i], self.a[i], self.r[i], self.o2[i], self.d[i], self.g[i] = o, a, r, o2, float(done), g
        self.i = (i + 1) % self.cap
        self.full = self.full or self.i == 0

    def __len__(self):
        return self.cap if self.full else self.i

    def sample(self, batch):
        idx = np.random.randint(0, len(self), size=batch)
        t = lambda x: torch.as_tensor(x[idx])
        return t(self.o), t(self.a), t(self.r), t(self.o2), t(self.d), t(self.g)

    def state(self):
        n = len(self)
        return {"cap": self.cap, "i": self.i, "full": self.full, "o": self.o[:n], "a": self.a[:n],
                "r": self.r[:n], "o2": self.o2[:n], "d": self.d[:n], "g": self.g[:n]}

    def restore(self, s):
        n = len(s["a"])
        self.i, self.full = s["i"], s["full"]
        self.o[:n], self.a[:n], self.r[:n], self.o2[:n], self.d[:n], self.g[:n] = \
            s["o"], s["a"], s["r"], s["o2"], s["d"], s["g"]


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

    def push(self, o, a, r, o2, done, discount=None):
        g = self.gamma if discount is None else discount
        self.buf.push(np.asarray(o, np.float32), a, r, np.asarray(o2, np.float32), done, g)

    def learn(self):
        self.steps += 1
        if len(self.buf) < max(self.batch, self.warmup):
            return None
        o, a, r, o2, d, g = (x.to(self.device) for x in self.buf.sample(self.batch))
        q = self.q(o).gather(1, a.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            a2 = self.q(o2).argmax(1)                                   # online selects
            q2 = self.qt(o2).gather(1, a2.unsqueeze(1)).squeeze(1)      # target evaluates (double-Q)
            y = r + g * (1.0 - d) * q2
        loss = nn.functional.smooth_l1_loss(q, y)
        self.opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(self.q.parameters(), 10.0)
        self.opt.step()
        if self.steps % self.target_every == 0:
            self.qt.load_state_dict(self.q.state_dict())
        return float(loss.item())

    # --- the policy only (what evaluation needs) -------------------------------------------------
    def save(self, path): torch.save(self.q.state_dict(), path)
    def load(self, path): self.q.load_state_dict(torch.load(path, map_location=self.device)); self.qt.load_state_dict(self.q.state_dict())

    # --- everything needed to resume training ---------------------------------------------------------
    def save_training_state(self, path, extra=None):
        state = {"q": self.q.state_dict(), "qt": self.qt.state_dict(), "opt": self.opt.state_dict(),
                 "steps": self.steps, "buffer": self.buf.state(), "extra": extra or {},
                 "rng": {"python": random.getstate(), "numpy": np.random.get_state(),
                         "torch": torch.get_rng_state()}}
        temporary = path + ".part"                   # write fully, then swap, so a crash never
        torch.save(state, temporary)                 # leaves a half-written checkpoint
        os.replace(temporary, path)

    def load_training_state(self, path):
        state = torch.load(path, map_location=self.device, weights_only=False)
        self.q.load_state_dict(state["q"]); self.qt.load_state_dict(state["qt"])
        self.opt.load_state_dict(state["opt"]); self.steps = state["steps"]
        self.buf.restore(state["buffer"])
        random.setstate(state["rng"]["python"]); np.random.set_state(state["rng"]["numpy"])
        torch.set_rng_state(state["rng"]["torch"])
        return state["extra"]


if __name__ == "__main__":
    import tempfile
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
    assert correct / max(1, total) > 0.5

    # Event discount: with done=False and a constant reward, Q converges to r / (1 - g), so a smaller
    # stored discount must give a smaller value.
    values = []
    for g in (0.9, 0.5):
        test = DDQNAgent(obs_dim=1, n_actions=1, warmup=64, target_every=50, seed=1)
        for _ in range(3000):
            test.push([0.0], 0, 1.0, [0.0], False, discount=g); test.learn()
        values.append(float(test.q(torch.zeros(1, 1)).item()))
    print(f"event discount: Q with g=0.9 -> {values[0]:.1f} (expect ~10), g=0.5 -> {values[1]:.1f} (expect ~2)")
    assert values[0] > values[1] and abs(values[1] - 2.0) < 0.5

    # Resume: save, take 50 more steps; reload, take the same 50 steps; the networks must match.
    path = os.path.join(tempfile.mkdtemp(), "state.pt")
    ag.save_training_state(path, extra={"episode": 7})
    def run_50(agent):
        for _ in range(50):
            o = np.random.normal(size=OBS_DIM).astype(np.float32)
            agent.push(o, agent.act(o), 1.0, o, False, discount=0.95); agent.learn()
        return torch.cat([p.flatten() for p in agent.q.parameters()])
    first = run_50(ag)
    extra = ag.load_training_state(path)
    second = run_50(ag)
    print(f"resume: extra={extra}, networks identical after resuming = {torch.equal(first, second)}")
    assert extra == {"episode": 7} and torch.equal(first, second)
    print("ok")
