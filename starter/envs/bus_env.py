"""PettingZoo AEC environment skeleton for MARL bus scheduling.

Pass sumo_cfg to run the real end-to-end loop (SUMO steps under agent control via TraCI);
leave it None for a pure-Python smoke test. The SO2 learning logic is marked TODO.
Verified running against sumo/corridor.sumocfg.
"""
import functools, os, sys
import numpy as np
from gymnasium.spaces import Box, Discrete
from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
try:    from pettingzoo.utils import AgentSelector as _Selector      # PettingZoo >= 1.24
except ImportError: from pettingzoo.utils import agent_selector as _Selector
if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))


def env(**kw):
    return wrappers.OrderEnforcingWrapper(BusScheduleAEC(**kw))


class BusScheduleAEC(AECEnv):
    metadata = {"render_modes": [], "name": "bus_schedule_aec_v0"}

    def __init__(self, n_buses=4, n_stops=6, sumo_cfg=None):
        super().__init__()
        self.possible_agents = [f"bus_{i}" for i in range(n_buses)]
        # obs = [pos_norm, fwd_headway, bwd_headway, onboard_load, local_queue]  (methods Table 3.6)
        self._obs = Box(low=0.0, high=np.inf, shape=(5,), dtype=np.float32)
        self._act = Discrete(2)            # 0 = proceed, 1 = hold  (add 2 = skip at SO2)
        self.sumo_cfg = sumo_cfg
        self._traci = None

    @functools.lru_cache(None)
    def observation_space(self, a): return self._obs
    @functools.lru_cache(None)
    def action_space(self, a): return self._act

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.rewards = {a: 0.0 for a in self.agents}
        self._cumulative_rewards = {a: 0.0 for a in self.agents}
        self.terminations = {a: False for a in self.agents}
        self.truncations = {a: False for a in self.agents}
        self.infos = {a: {} for a in self.agents}
        self.state = {a: np.zeros(5, np.float32) for a in self.agents}
        self._sel = _Selector(self.agents); self.agent_selection = self._sel.next()
        if self.sumo_cfg:
            import traci
            from sumolib import checkBinary
            self._traci = traci
            traci.start([checkBinary("sumo"), "-c", self.sumo_cfg, "--no-warnings", "true", "--no-step-log", "true"])

    def observe(self, agent):
        return self.state[agent]           # TODO(SO2): pull real features from TraCI (see calibrate/run scripts)

    def step(self, action):
        a = self.agent_selection
        if self.terminations[a] or self.truncations[a]:
            self._was_dead_step(action); return
        # TODO(SO2): apply `action` to bus `a` via TraCI (hold => extend stop)
        if self._sel.is_last():
            if self._traci is not None:
                self._traci.simulationStep()
            for ag in self.agents:
                self.rewards[ag] = self._reward(ag)     # TODO(SO2)
            self._accumulate_rewards()
        else:
            self._clear_rewards()
        self.agent_selection = self._sel.next()

    def _reward(self, agent):
        return 0.0                          # TODO(SO2): penalize headway irregularity + delay

    def close(self):
        if self._traci is not None:
            self._traci.close(); self._traci = None
