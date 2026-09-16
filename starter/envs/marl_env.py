"""
=============================================================================
 THE GLUE:  LET THE LEARNING AGENT DRIVE THE BUSES
=============================================================================

WHAT IT DOES
    The simulator (envs/corridor_sim.py) does not know what a neural network
    is. It just calls a function every time a bus reaches a control stop:

        hold_seconds, skip = decide(obs)

    MarlController below IS that function. Each time it is called it:
        1. turns the situation into 7 numbers            (envs/obs.py)
        2. scores the bus's PREVIOUS decision            (envs/reward.py)
        3. hands that score to the learner to learn from (agents/ddqn.py)
        4. asks the learner what to do now
        5. remembers this decision, to be scored next time

    Step 2 is one stop behind on purpose: you cannot tell whether holding
    helped until you see what happened afterwards.

ONE BRAIN, EVERY BUS
    All 18 buses call the same controller and share one network. That is what
    "parameter sharing" means in the manuscript: the buses act independently,
    on their own local view, but they learn from each other's experience.

CONFIG: EVERY EXPERIMENT KNOB IN ONE PLACE
    Below is every setting a run can change -- which reward to use, how long
    holds may be, how often disturbances appear during training, the network
    size, how long to train. To run a different experiment, change a value
    here (or pass the matching flag to scripts/train_marl.py); never edit the
    simulator.
=============================================================================
"""
from dataclasses import dataclass
import math

from obs import featurize, OBS_DIM
from reward import compose, decode_action

# 5 holding choices (0, 30, 60, 90, 120 s) x 2 skip choices (no, yes)
N_ACTIONS = 10


@dataclass
class Config:
    """All the settings for one experiment. `@dataclass` just means "a bag of named settings"."""

    # ---- the score (see envs/reward.py) ---------------------------------------------
    irr: str = "dev"            # spacing penalty: "dev", "even" or "both"
    wait: str = "queue"         # delay penalty:   "queue", "hold" or "both"
    skip: str = "stranded"      # skip penalty:    "stranded" or "flat"
    w: tuple = (1.0, 0.5, 1.0)  # how much each of the three counts

    # ---- what the bus is allowed to do ----------------------------------------------
    H0: float = 600.0           # the scheduled headway, 10 minutes
    dt: float = 300.0           # holds are 0 to 0.4 x dt, so at most 120 s, the same cap as FH and EH
    skip_enabled: bool = False  # False: the skip half of the action space is ignored

    # ---- the learner (see agents/ddqn.py) -------------------------------------------
    lr: float = 1e-3            # learning rate: how big a nudge each update gives
    gamma: float = 0.99         # how much a later score counts, if the discount is "fixed"
    # "event": a score is worth e^(-beta x seconds since the bus's last decision), because decisions
    # happen at irregular times (methods.tex, Bradtke & Duff). beta is set so one full headway of
    # elapsed time discounts by 0.99.
    discount: str = "event"
    beta: float = -math.log(0.99) / 600.0
    eps_start: float = 1.0      # start by acting at random...
    eps_end: float = 0.05       # ...and end up random only 1 time in 20
    eps_decay: int = 30_000     # over this many learning steps
    buffer: int = 100_000       # how many past decisions the learner remembers
    batch: int = 64             # how many of them it revisits per update
    target_every: int = 500     # only used when tau = 0 (see agents/ddqn.py)
    warmup: int = 1_000         # collect this many decisions before learning starts
    net: tuple = (128, 128)     # two hidden layers of 128 units

    # ---- what the weather is like while training (methods.tex activation matrix) -----
    # Demand and traffic are always on. Surge, weather and breakdown are switched on at
    # random each episode, and when weather is on its strength is drawn from 0 to eta_max.
    randomize: bool = True
    p_surge: float = 0.5
    p_weather: float = 0.5
    p_breakdown: float = 0.5
    eta_max: float = 1.3

    # ---- keeping the learning stable (methods.tex) ----------------------------------
    # Scores worse than -5 are trimmed to -5 before learning, so one catastrophic episode
    # cannot dominate. Measured: under the worst weather a random policy sees scores down
    # to -11, but 95% are above -4.4 (2026-09-16).
    reward_clip: float = 5.0
    tau: float = 0.005          # how fast the "target" network follows the main one

    # ---- the run itself ---------------------------------------------------------------
    control_stops: tuple = (0, 1, 5, 17, 20)    # stops 5280, 5857, 5859, 5867, 4046
    episodes: int = 2_000
    seed: int = 0
    name: str = "gate"          # results go to experiments/<name>/


class MarlController:
    """The decide() function handed to corridor_sim.simulate().

    training=True  -> explores and learns as it goes (used while training)
    training=False -> always takes what it thinks is best, and learns nothing (used to test it)
    """

    def __init__(self, agent, config, training=True):
        self.agent = agent
        self.config = config
        self.training = training
        # For each bus: what it saw last time, what it chose, and the raw readings.
        self.last_decision = {}
        self.ret = 0.0      # total score this episode, for the training log
        self.n = 0          # how many decisions were scored

    def __call__(self, obs):
        """Called by the simulator when a bus reaches a control stop."""
        bus = obs["bus"]
        situation = featurize(obs)

        # 1. If this bus has decided before, we can now score that earlier decision.
        if bus in self.last_decision:
            before_numbers, earlier_action, before_readings = self.last_decision[bus]
            score = compose(before_readings, obs, earlier_action, self.config)
            self.ret += score
            self.n += 1

            if self.training:
                trimmed = max(score, -self.config.reward_clip)
                self.agent.push(before_numbers, earlier_action, trimmed, situation, False,
                                discount=self.discount(before_readings, obs))
                self.agent.learn()

        # 2. Choose what to do now. While training it sometimes tries something random.
        action = self.agent.act(situation, greedy=not self.training)

        # 3. Remember it, so it can be scored at this bus's next control stop.
        self.last_decision[bus] = (situation, action, obs)

        hold_seconds, skip = decode_action(action, self.config.H0, self.config.dt)
        if not self.config.skip_enabled:
            skip = 0
        return hold_seconds, skip

    def discount(self, before_readings, obs):
        """How much the later score counts, given how long it took to arrive."""
        if self.config.discount == "fixed":
            return self.config.gamma
        seconds_elapsed = max(0.0, obs["t"] - before_readings["t"])
        return math.exp(-self.config.beta * seconds_elapsed)

    def finalize(self):
        """End of the day: forget each bus's last decision.

        It never gets scored, because there is no "next stop" to see the result at.
        """
        self.last_decision.clear()
