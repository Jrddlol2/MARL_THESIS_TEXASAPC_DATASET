# My Week-1 Steps — Jared (distribution-free)
Your slice of `Kickoff_Guide_Week1.md`, simplified: **point values only, no distributions.** (Distributions — demand/dwell/weather — come back at SO1.2, Marquez's part; the RL library is chosen at SO2 in ~Oct.) Covers team steps **1(verify), 2, 4, 6, 7 + the end-to-end loop.** Run everything from the repo root, venv activated.

---

## 1. Verify the stack (your verify role)
After the team installs SUMO + the venv, confirm on your machine:
```powershell
sumo --version
python -c "import os,sys; sp=os.path.join(os.environ.get('SUMO_HOME','_'),'tools'); os.path.isdir(sp) and sys.path.append(sp); import traci, sumolib; print('traci OK')"
```
**Done when:** a version prints **and** `traci OK` prints.

---

## 2. Export `sim_inputs/` — simple, no distributions
One row per stop, plain numbers: mean boardings/alightings, median dwell, median segment running time (`rev_seconds − dwell_time`, so dwell isn't double-counted). No std, no distribution files.

`scripts/extract_sim_inputs.py`:
```python
import pandas as pd, os
IN  = "data/raw/capmetro/route_801_direction_6_clean.csv"   # adjust to your pipeline output
OUT = "sim_inputs"; os.makedirs(OUT, exist_ok=True)
keep = ["bs_id","actual_sequence","ons","offs","dwell_time","rev_seconds","rev_distance"]
df = pd.read_csv(IN, usecols=lambda c: c in keep, low_memory=False)
for c in ["actual_sequence","ons","offs","dwell_time","rev_seconds","rev_distance"]:
    if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
df["run_seconds"] = (df["rev_seconds"] - df["dwell_time"]).clip(lower=0)

stops = (df.groupby("bs_id")
           .agg(seq=("actual_sequence","median"),
                mean_boardings=("ons","mean"),      # one demand number per stop (no distribution)
                mean_alightings=("offs","mean"),
                dwell_s=("dwell_time","median"),     # one dwell number per stop
                run_s=("run_seconds","median"),      # one segment-time target per stop
                dist_m=("rev_distance","median"))
           .sort_values("seq").round(1))
stops.to_csv(f"{OUT}/stops.csv")
print("wrote sim_inputs/stops.csv —", len(stops), "stops")
print(stops)
```
Run `python scripts/extract_sim_inputs.py`.
**Done when:** `sim_inputs/stops.csv` has ~**29 rows**, columns `seq, mean_boardings, mean_alightings, dwell_s, run_s, dist_m`.

---

## 3. Repo scaffold + board
```powershell
git checkout -b implementation
foreach ($d in "sim_inputs","sumo","envs","baselines","training","scripts","results","notebooks") {
    New-Item -ItemType Directory -Force $d | Out-Null
    New-Item -ItemType File      -Force "$d\.gitkeep" | Out-Null   # keep empty dirs in git
}
git add -A; git commit -m "scaffold: implementation folder structure"
```
Board: GitHub Projects (or a `TASKS.md`) with one card per step + owner.
**Done when:** the `implementation` branch is pushed and the team can clone it.

---

## 4. SUMO hello-world, then the reduced net (with Lopez)
### 4a. Hello-world (proves SUMO + TraCI)
`sumo/nodes.nod.xml`, `sumo/edges.edg.xml`:
```xml
<!-- nodes.nod.xml -->
<nodes>
  <node id="A" x="0"    y="0"/>
  <node id="B" x="500"  y="0"/>
  <node id="C" x="1000" y="0"/>
</nodes>
```
```xml
<!-- edges.edg.xml -->
<edges>
  <edge id="AB" from="A" to="B" numLanes="1" speed="13.9"/>
  <edge id="BC" from="B" to="C" numLanes="1" speed="13.9"/>
</edges>
```
```powershell
netconvert --node-files=sumo/nodes.nod.xml --edge-files=sumo/edges.edg.xml --output-file=sumo/hello.net.xml
```
```xml
<!-- sumo/hello.rou.xml -->
<routes>
  <vType id="bus" vClass="bus" length="12" accel="1.2" decel="4.0" maxSpeed="16"/>
  <route id="r0" edges="AB BC"/>
  <flow id="f0" type="bus" route="r0" begin="0" end="3600" period="300"/>
</routes>
```
```xml
<!-- sumo/hello.sumocfg -->
<configuration>
  <input><net-file value="hello.net.xml"/><route-files value="hello.rou.xml"/></input>
  <time><begin value="0"/><end value="3600"/></time>
</configuration>
```
`scripts/hello_traci.py`:
```python
import os, sys
if "SUMO_HOME" in os.environ:                          # MSI install sets this; pip 'eclipse-sumo' doesn't need it
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
from sumolib import checkBinary
traci.start([checkBinary("sumo"), "-c", "sumo/hello.sumocfg", "--step-length", "1"])
step = 0
while traci.simulation.getMinExpectedNumber() > 0 and step < 300:
    traci.simulationStep()
    if step % 30 == 0:
        print("t=", step, "buses:", traci.vehicle.getIDCount())
    step += 1
traci.close()
print("OK — SUMO + TraCI works")
```
**Done when:** it ends with `OK — SUMO + TraCI works`.

### 4b. Reduced corridor net (needs Lopez's `reduced_corridor.txt`)
`scripts/build_reduced_net.py` — reads the simplified `sim_inputs/stops.csv`:
```python
import os, sys, subprocess, pandas as pd
if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
from sumolib import checkBinary
sel = [l.strip() for l in open("reduced_corridor.txt") if l.strip()]
stops = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id")
x, nodes = 0.0, []
for i, bs in enumerate(sel):
    nodes.append((f"n{i}", x))
    d = stops.loc[bs, "dist_m"] if bs in stops.index else 400.0
    x += max(float(d) if pd.notna(d) else 400.0, 100.0)
nodes.append((f"n{len(sel)}", x))                  # trailing node -> one edge per stop, so every stop gets a busStop
open("sumo/corridor.nod.xml","w").write("<nodes>\n"+"".join(f'  <node id="{n}" x="{xx:.1f}" y="0"/>\n' for n,xx in nodes)+"</nodes>\n")
open("sumo/corridor.edg.xml","w").write("<edges>\n"+"".join(f'  <edge id="e{i}" from="n{i}" to="n{i+1}" numLanes="1" speed="13.9"/>\n' for i in range(len(nodes)-1))+"</edges>\n")
subprocess.run([checkBinary("netconvert"),"--node-files=sumo/corridor.nod.xml","--edge-files=sumo/corridor.edg.xml","--output-file=sumo/corridor.net.xml"], check=True)
with open("sumo/stops.add.xml","w") as f:
    f.write("<additional>\n")
    for i, bs in enumerate(sel):                   # every stop gets a busStop
        f.write(f'  <busStop id="{bs}" lane="e{i}_0" startPos="5" endPos="25"/>\n')
    f.write("</additional>\n")
print("built corridor.net.xml +", len(sel), "busStops")
```
**Done when:** `sumo/corridor.net.xml` opens in `netedit` with your stops in order.

---

## 5. PettingZoo AEC env skeleton (with Badal)
`envs/bus_env.py` — obs = methods Table 3.6 vector; action = proceed/hold (add skip at SO2). All the SO2 logic is `TODO`:
```python
import functools, numpy as np
from gymnasium.spaces import Box, Discrete
from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
try:    from pettingzoo.utils import AgentSelector as _Selector      # PettingZoo >=1.24
except ImportError: from pettingzoo.utils import agent_selector as _Selector

def env(**kw):
    e = BusScheduleAEC(**kw); return wrappers.OrderEnforcingWrapper(e)

class BusScheduleAEC(AECEnv):
    metadata = {"render_modes": [], "name": "bus_schedule_aec_v0"}
    def __init__(self, n_buses=4, n_stops=6):
        super().__init__()
        self.possible_agents = [f"bus_{i}" for i in range(n_buses)]
        self._obs = Box(low=0.0, high=np.inf, shape=(5,), dtype=np.float32)  # [pos, fwd_hw, bwd_hw, load, queue]
        self._act = Discrete(2)                      # 0 = proceed, 1 = hold
    @functools.lru_cache(None)
    def observation_space(self, a): return self._obs
    @functools.lru_cache(None)
    def action_space(self, a): return self._act

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.rewards = {a: 0.0 for a in self.agents}
        self._cumulative_rewards = {a: 0.0 for a in self.agents}
        self.terminations = {a: False for a in self.agents}
        self.truncations  = {a: False for a in self.agents}
        self.infos = {a: {} for a in self.agents}
        self.state = {a: np.zeros(5, np.float32) for a in self.agents}
        self._sel = _Selector(self.agents); self.agent_selection = self._sel.next()
        # TODO(SO2): traci.start([...])  <-- wired in Step 6 below for the end-to-end loop

    def observe(self, agent):
        return self.state[agent]                     # TODO(SO2): real features from TraCI

    def step(self, action):
        a = self.agent_selection
        if self.terminations[a] or self.truncations[a]:
            self._was_dead_step(action); return
        # TODO(SO2): apply action to bus `a` via TraCI
        if self._sel.is_last():
            # TODO(SO2): traci.simulationStep()
            for ag in self.agents:
                self.rewards[ag] = self._reward(ag) # TODO(SO2)
            self._accumulate_rewards()
        else:
            self._clear_rewards()
        self.agent_selection = self._sel.next()

    def _reward(self, agent): return 0.0             # TODO(SO2)
    def close(self): pass                            # TODO: traci.close()
```
**Done when:** `python -c "from envs.bus_env import env; e=env(); e.reset(); print('AEC env OK')"` prints `AEC env OK` (run from repo root).

---

## 6. ⭐ End-to-end loop — your big win
Wire three TODOs in `bus_env.py`: `reset()` → `traci.start([checkBinary("sumo"),"-c","sumo/hello.sumocfg"])` (use **hello** first — it has moving buses); the `is_last()` branch → `traci.simulationStep()`; `close()` → `traci.close()`. Then `scripts/run_random.py`:
```python
from envs.bus_env import env
e = env(n_buses=4, n_stops=6); e.reset(seed=0)
for agent in e.agent_iter(max_iter=200):
    obs, rew, term, trunc, info = e.last()
    e.step(None if (term or trunc) else e.action_space(agent).sample())
e.close(); print("OK — end-to-end AEC + SUMO loop runs")
```
**Done when:** it prints `OK — end-to-end AEC + SUMO loop runs` while SUMO steps. **Reach this and the scariest integration risk is retired a month early.**

---

## My done-when checklist
- [ ] `traci OK` on my machine
- [ ] `sim_inputs/stops.csv` (~29 rows, point values, **no distributions**)
- [ ] `implementation` branch pushed + board set up
- [ ] `hello_traci.py` prints OK
- [ ] `corridor.net.xml` opens in netedit (after Lopez hands over `reduced_corridor.txt`)
- [ ] `bus_env.py` resets without error
- [ ] ⭐ end-to-end random-agent loop runs

**Deferred (not now):** distributions (demand/dwell/weather → SO1.2, Marquez); RL library choice (→ SO2, ~Oct); real reward/observation/geometry (the SO2/SO1 `TODO`s).
