"""
=============================================================================
 THE LEARNER:  A SHARED DOUBLE-DQN BRAIN FOR ALL 18 BUSES
=============================================================================

WHAT IT DOES
    Holds the neural network that every bus uses, remembers past decisions,
    and nudges the network after each one so better decisions score higher.

    Three pieces:
        QNet          the network: 7 numbers in, 10 scores out (one per action)
        ReplayBuffer  a notebook of past decisions to revisit
        DDQNAgent     ties them together: act, remember, learn, save

HOW IT LEARNS, IN ONE SENTENCE
    "The value of the action I took should equal the score I got, plus what
    the situation I ended up in is worth" -- and every update shuffles the
    network a little closer to making that true.

WHY "DOUBLE"
    Two copies of the network are kept. The main one picks which next action
    looks best; the slower copy says what it is worth. Asking one network to
    do both jobs makes it flatter itself and over-value everything, which gets
    worse when the scores are wild -- exactly our case under heavy weather.

WHY THE DISCOUNT IS STORED PER DECISION
    Buses decide at irregular moments, sometimes 2 minutes apart, sometimes
    40. So the trainer passes in a discount for each decision, e^(-beta x
    seconds elapsed), instead of one fixed number for all of them.

RUN      python agents/ddqn.py     (~40 s; three self-tests, see the bottom)
=============================================================================
"""
from __future__ import annotations
import os, random, numpy as np, torch, torch.nn as nn

OBS_DIM, N_ACTIONS = 7, 10          # 7 numbers in, 10 possible actions out


class QNet(nn.Module):
    """The network: 7 numbers in, one score per action out.

    Two hidden layers of 128 units. ReLU between them is what lets the network
    represent something other than a straight line.
    """

    def __init__(self, obs_dim=OBS_DIM, n_actions=N_ACTIONS, hidden=(128, 128)):
        super().__init__()
        layers = []
        width = obs_dim
        for units in hidden:
            layers += [nn.Linear(width, units), nn.ReLU()]
            width = units
        layers += [nn.Linear(width, n_actions)]
        self.net = nn.Sequential(*layers)

    def forward(self, situations):
        return self.net(situations)


class ReplayBuffer:
    """A notebook of past decisions, kept so the network can revisit them.

    Learning only from the newest decision would make the network chase
    whatever just happened. Instead every decision is written down and updates
    are computed on a random handful, which breaks that.

    One row per decision:
        situation      the 7 numbers the bus saw
        action         what it chose (0-9)
        score          what that earned, once it could be judged
        next_situation what it saw at its next control stop
        finished       1 if the day ended there, else 0
        discount       how much the future is worth for this particular gap
    """

    def __init__(self, capacity, obs_dim=OBS_DIM):
        self.capacity = capacity
        self.position = 0           # where the next row goes
        self.wrapped = False        # True once we have written all the way round
        self.situation = np.zeros((capacity, obs_dim), np.float32)
        self.action = np.zeros(capacity, np.int64)
        self.score = np.zeros(capacity, np.float32)
        self.next_situation = np.zeros((capacity, obs_dim), np.float32)
        self.finished = np.zeros(capacity, np.float32)
        self.discount = np.zeros(capacity, np.float32)

    def push(self, situation, action, score, next_situation, finished, discount):
        i = self.position
        self.situation[i] = situation
        self.action[i] = action
        self.score[i] = score
        self.next_situation[i] = next_situation
        self.finished[i] = float(finished)
        self.discount[i] = discount
        self.position = (i + 1) % self.capacity      # start overwriting the oldest once full
        self.wrapped = self.wrapped or self.position == 0

    def __len__(self):
        return self.capacity if self.wrapped else self.position

    def sample(self, batch):
        """Pick `batch` rows at random and hand them to PyTorch."""
        rows = np.random.randint(0, len(self), size=batch)
        as_tensor = lambda column: torch.as_tensor(column[rows])
        return (as_tensor(self.situation), as_tensor(self.action), as_tensor(self.score),
                as_tensor(self.next_situation), as_tensor(self.finished), as_tensor(self.discount))

    def state(self):
        """Everything written so far, for saving."""
        n = len(self)
        return {"cap": self.capacity, "i": self.position, "full": self.wrapped,
                "o": self.situation[:n], "a": self.action[:n], "r": self.score[:n],
                "o2": self.next_situation[:n], "d": self.finished[:n], "g": self.discount[:n]}

    def restore(self, saved):
        n = len(saved["a"])
        self.position, self.wrapped = saved["i"], saved["full"]
        self.situation[:n] = saved["o"]
        self.action[:n] = saved["a"]
        self.score[:n] = saved["r"]
        self.next_situation[:n] = saved["o2"]
        self.finished[:n] = saved["d"]
        self.discount[:n] = saved["g"]


class DDQNAgent:
    """One shared brain. Every bus calls act() and push() on this same object."""

    def __init__(self, obs_dim=OBS_DIM, n_actions=N_ACTIONS, lr=1e-3, gamma=0.99,
                 buffer=100_000, batch=64, target_every=500, warmup=1_000,
                 eps_start=1.0, eps_end=0.05, eps_decay=30_000, hidden=(128, 128),
                 device="cpu", seed=0, tau=0.0):
        torch.manual_seed(seed); np.random.seed(seed); random.seed(seed)
        self.n_actions = n_actions
        self.gamma = gamma                  # used only if the trainer passes no discount
        self.batch = batch                  # decisions revisited per update
        self.target_every = target_every    # copy the main network across every N updates (if tau = 0)
        self.warmup = warmup                # collect this many decisions before learning at all
        self.tau = tau                      # if > 0, the slow copy creeps along every update instead
        self.eps_start, self.eps_end, self.eps_decay = eps_start, eps_end, eps_decay
        self.device = torch.device(device)

        self.network = QNet(obs_dim, n_actions, hidden).to(self.device)        # the one being trained
        self.slow_copy = QNet(obs_dim, n_actions, hidden).to(self.device)      # the steadier reference
        self.slow_copy.load_state_dict(self.network.state_dict())
        self.optimiser = torch.optim.Adam(self.network.parameters(), lr=lr)
        self.memory = ReplayBuffer(buffer, obs_dim)
        self.steps = 0

        # Older names, kept because other files and saved runs refer to them.
        self.q, self.qt, self.opt, self.buf = self.network, self.slow_copy, self.optimiser, self.memory

    def epsilon(self):
        """How often to act at random right now: 100% at the start, 5% later on."""
        progress = min(1.0, self.steps / self.eps_decay)
        return self.eps_start + progress * (self.eps_end - self.eps_start)

    @torch.no_grad()
    def act(self, situation, greedy=False):
        """Choose an action. greedy=True always takes the best-looking one."""
        if (not greedy) and random.random() < self.epsilon():
            return random.randrange(self.n_actions)
        as_batch_of_one = torch.as_tensor(np.asarray(situation, np.float32),
                                          device=self.device).unsqueeze(0)
        scores = self.network(as_batch_of_one)
        return int(scores.argmax(1).item())

    def push(self, situation, action, score, next_situation, finished, discount=None):
        """Write one finished decision into the notebook."""
        self.memory.push(np.asarray(situation, np.float32), action, score,
                         np.asarray(next_situation, np.float32), finished,
                         self.gamma if discount is None else discount)

    def learn(self):
        """One update: revisit a random handful of past decisions and nudge the network."""
        self.steps += 1
        if len(self.memory) < max(self.batch, self.warmup):
            return None                         # not enough experience yet

        situation, action, score, next_situation, finished, discount = (
            x.to(self.device) for x in self.memory.sample(self.batch))

        # What the network currently thinks the action it took was worth.
        predicted = self.network(situation).gather(1, action.unsqueeze(1)).squeeze(1)

        # What it should have been worth: the score, plus whatever the next situation is worth.
        with torch.no_grad():
            best_next_action = self.network(next_situation).argmax(1)               # main net chooses
            value_of_next = self.slow_copy(next_situation).gather(                  # slow copy values
                1, best_next_action.unsqueeze(1)).squeeze(1)
            target = score + discount * (1.0 - finished) * value_of_next

        loss = nn.functional.smooth_l1_loss(predicted, target)
        self.optimiser.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.network.parameters(), 10.0)   # never take a huge step
        self.optimiser.step()

        # Keep the slow copy trailing the main network.
        if self.tau > 0:
            with torch.no_grad():
                for slow, main in zip(self.slow_copy.parameters(), self.network.parameters()):
                    slow.mul_(1.0 - self.tau).add_(main, alpha=self.tau)
        elif self.steps % self.target_every == 0:
            self.slow_copy.load_state_dict(self.network.state_dict())

        return float(loss.item())

    # ---- saving just the policy (what an evaluation needs) ---------------------------------
    def save(self, path):
        torch.save(self.network.state_dict(), path)

    def load(self, path):
        self.network.load_state_dict(torch.load(path, map_location=self.device))
        self.slow_copy.load_state_dict(self.network.state_dict())

    # ---- saving everything, so training can stop and pick up again -------------------------
    def save_training_state(self, path, extra=None):
        state = {"q": self.network.state_dict(), "qt": self.slow_copy.state_dict(),
                 "opt": self.optimiser.state_dict(), "steps": self.steps,
                 "buffer": self.memory.state(), "extra": extra or {},
                 "rng": {"python": random.getstate(), "numpy": np.random.get_state(),
                         "torch": torch.get_rng_state()}}
        being_written = path + ".part"      # write in full, then swap, so a crash never leaves
        torch.save(state, being_written)    # behind a half-written checkpoint
        os.replace(being_written, path)

    def load_training_state(self, path):
        state = torch.load(path, map_location=self.device, weights_only=False)
        self.network.load_state_dict(state["q"])
        self.slow_copy.load_state_dict(state["qt"])
        self.optimiser.load_state_dict(state["opt"])
        self.steps = state["steps"]
        self.memory.restore(state["buffer"])
        random.setstate(state["rng"]["python"])
        np.random.set_state(state["rng"]["numpy"])
        torch.set_rng_state(state["rng"]["torch"])
        return state["extra"]


if __name__ == "__main__":
    import tempfile

    # TEST 1: can it learn at all? A made-up task where exactly one action is right for each
    # situation. A working learner climbs well above 1-in-10 guessing.
    rng = np.random.default_rng(0)
    hidden_rule = rng.normal(size=(OBS_DIM, N_ACTIONS)).astype(np.float32)
    right_answer = lambda situation: int(np.argmax(situation @ hidden_rule))

    agent = DDQNAgent(warmup=500, eps_decay=4000)
    correct = total = 0
    for step in range(12_000):
        situation = rng.normal(size=OBS_DIM).astype(np.float32)
        action = agent.act(situation)
        score = 1.0 if action == right_answer(situation) else 0.0
        next_situation = rng.normal(size=OBS_DIM).astype(np.float32)
        agent.push(situation, action, score, next_situation, True)
        agent.learn()
        if step > 10_000:
            correct += (agent.act(situation, greedy=True) == right_answer(situation))
            total += 1
    print(f"DDQN self-test: greedy accuracy over last {total} steps = {correct/max(1,total):.2f} "
          f"(chance = {1/N_ACTIONS:.2f}); eps now {agent.epsilon():.3f}, buffer {len(agent.memory)}")
    assert correct / max(1, total) > 0.5

    # TEST 2: does the stored discount do anything? With the same score forever, a situation is
    # worth score / (1 - discount), so a smaller discount must give a smaller value.
    values = []
    for discount in (0.9, 0.5):
        tester = DDQNAgent(obs_dim=1, n_actions=1, warmup=64, target_every=50, seed=1, tau=0.02)
        for _ in range(3000):
            tester.push([0.0], 0, 1.0, [0.0], False, discount=discount)
            tester.learn()
        values.append(float(tester.network(torch.zeros(1, 1)).item()))
    print(f"event discount: Q with g=0.9 -> {values[0]:.1f} (expect ~10), "
          f"g=0.5 -> {values[1]:.1f} (expect ~2)")
    assert values[0] > values[1] and abs(values[1] - 2.0) < 0.5

    # TEST 3: can training stop and resume exactly? Save, take 50 steps, reload, take the same 50,
    # and the two networks must match to the last digit.
    path = os.path.join(tempfile.mkdtemp(), "state.pt")
    agent.save_training_state(path, extra={"episode": 7})

    def fifty_more_steps(learner):
        for _ in range(50):
            situation = np.random.normal(size=OBS_DIM).astype(np.float32)
            learner.push(situation, learner.act(situation), 1.0, situation, False, discount=0.95)
            learner.learn()
        return torch.cat([p.flatten() for p in learner.network.parameters()])

    first_time = fifty_more_steps(agent)
    extra = agent.load_training_state(path)
    second_time = fifty_more_steps(agent)
    print(f"resume: extra={extra}, networks identical after resuming = {torch.equal(first_time, second_time)}")
    assert extra == {"episode": 7} and torch.equal(first_time, second_time)
    print("ok")
