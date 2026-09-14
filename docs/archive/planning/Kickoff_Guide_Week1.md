# Week-1 Kickoff Guide — Group B3 MARL Thesis (do-now, step by step)
**Goal of the week:** prove the toolchain runs end-to-end and lock the reduced corridor. **No RL library decision needed yet** — these steps use only SUMO + PettingZoo + NumPy. Pick RLlib/SB3/CleanRL later, at training time.

**Who does what**
| # | Task | Owner |
|---|---|---|
| 1 | Install the stack | Everyone (Jared/Badal verify) |
| 2 | Export `sim_inputs/` | Jared |
| 3 | Lock the 5–8-stop corridor | Lopez |
| 4 | Repo scaffold + board | Jared |
| 5 | IP Registry Form | Marquez/any |
| 6 | SUMO hello-world + reduced net | Lopez/Jared |
| 7 | PettingZoo AEC env skeleton | Badal/Jared |
| 8 | Even-Headway baseline | Medenilla |
| 9 | PR1 + MSA-1 pack | Marquez |

Work in the repo root. Where a path like `data/raw/capmetro/route_801_direction_6_clean.csv` appears, adjust to wherever your pipeline wrote it.

---

## Step 1 — Install the stack (everyone)
**Goal:** `sumo` runs and `import traci` works inside a Python venv.

1. **SUMO (Windows):** download the SUMO MSI installer from <https://sumo.dlr.de/docs/Downloads.php>, run it, and let it set `SUMO_HOME` + PATH. Open a **new** PowerShell and check:
```powershell
sumo --version
echo $env:SUMO_HOME
```
2. **Python venv + libs** (Python 3.12 is already on this machine):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope Process -Bypass then re-run
python -m pip install --upgrade pip
pip install pettingzoo gymnasium numpy pandas matplotlib
```
   `traci`/`sumolib` ship **with** SUMO — don't pip-install them (version must match the SUMO binary). Every script below adds `%SUMO_HOME%\tools` to the path so the bundled ones import cleanly.
3. **Verify the bindings:**
```powershell
python -c "import os,sys; sp=os.path.join(os.environ.get('SUMO_HOME','_'),'tools'); os.path.isdir(sp) and sys.path.append(sp); import traci, sumolib; print('traci OK')"
```
**Done when:** `sumo --version` prints a version **and** the last command prints `traci OK`, for every member.

*(Alternative if the MSI is a hassle: `pip install eclipse-sumo traci sumolib` puts everything in the venv; then skip the `SUMO_HOME` lines and use `sumolib.checkBinary("sumo")`.)*

---

## Step 2 — Export `sim_inputs/` (Jared)
**Goal:** the numbers calibration needs — per-stop demand, dwell, and per-segment running time — as CSVs. Recall `rev_seconds` is open-to-open (includes that stop's dwell), so **segment running time = `rev_seconds − dwell_time`**.

`scripts/extract_sim_inputs.py`:
```python
import pandas as pd, json, os
IN  = "data/raw/capmetro/route_801_direction_6_clean.csv"   # adjust to your pipeline output
OUT = "sim_inputs"; os.makedirs(OUT, exist_ok=True)
keep = ["bs_id","actual_sequence","ons","offs","dwell_time","rev_seconds","rev_distance"]
df = pd.read_csv(IN, usecols=lambda c: c in keep, low_memory=False)
for c in ["actual_sequence","ons","offs","dwell_time","rev_seconds","rev_distance"]:
    if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
df["run_seconds"] = (df["rev_seconds"] - df["dwell_time"]).clip(lower=0)   # segment running time (avoids double-counting dwell)

g = df.groupby("bs_id")
demand = g.agg(seq=("actual_sequence","median"), n=("ons","size"),
               mean_ons=("ons","mean"), mean_offs=("offs","mean"),
               tot_ons=("ons","sum"),  tot_offs=("offs","sum")).sort_values("seq")
dwell  = g.agg(seq=("actual_sequence","median"), dwell_median=("dwell_time","median"),
               dwell_mean=("dwell_time","mean"), dwell_std=("dwell_time","std")).sort_values("seq")
seg    = g.agg(seq=("actual_sequence","median"), run_median=("run_seconds","median"),
               run_mean=("run_seconds","mean"), dist_median=("rev_distance","median")).sort_values("seq")

demand.to_csv(f"{OUT}/stop_demand.csv"); dwell.to_csv(f"{OUT}/stop_dwell.csv"); seg.to_csv(f"{OUT}/segment_running_time.csv")
json.dump({"n_events": int(len(df)), "n_stops": int(df['bs_id'].nunique())},
          open(f"{OUT}/summary.json","w"), indent=2)
print("wrote", os.listdir(OUT))
```
Run: `python scripts/extract_sim_inputs.py`
**Done when:** `sim_inputs/` holds `stop_demand.csv`, `stop_dwell.csv`, `segment_running_time.csv`, `summary.json`, and `summary.json` shows **29 stops**.

---

## Step 3 — Lock the 5–8-stop corridor (Lopez)
**Goal:** choose a contiguous, high-ridership run of stops and save the selection.
```python
import pandas as pd
df = pd.read_csv("data/raw/capmetro/route_801_direction_6_clean.csv",
                 usecols=["bs_id","actual_sequence","ons","offs"], low_memory=False)
for c in ["actual_sequence","ons","offs"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
g = (df.groupby("bs_id")
       .agg(events=("ons","size"), boardings=("ons","sum"), seq=("actual_sequence","median"))
       .sort_values("seq"))
print(g)   # stops in spatial order — read down the list, pick a contiguous block of 5–8 with high boardings
```
Then hard-code the chosen block (in sequence order) and save it:
```python
chosen = ["<bs_id_1>","<bs_id_2>","<bs_id_3>","<bs_id_4>","<bs_id_5>","<bs_id_6>"]  # your picks, in order
open("reduced_corridor.txt","w").write("\n".join(chosen))
print("saved", len(chosen), "stops")
```
**Pick rule:** contiguous in `seq`, highest summed `boardings`, avoid the two end terminals (odd dwell). **Done when:** `reduced_corridor.txt` lists 5–8 bs_ids in order.

---

## Step 4 — Repo scaffold + board (Jared)
```powershell
git checkout -b implementation
foreach ($d in "sim_inputs","sumo","envs","baselines","training","scripts","results","notebooks") {
    New-Item -ItemType Directory -Force $d | Out-Null
    New-Item -ItemType File      -Force "$d\.gitkeep" | Out-Null   # keep empty dirs in git
}
git add -A; git commit -m "scaffold: implementation folder structure"
```
Suggested layout: `scripts/` (extractors), `sumo/` (net/routes/config), `envs/` (the AEC env), `baselines/` (NC/FH/EH), `training/` (later), `results/`.
**Board:** GitHub Projects (or a `TASKS.md`) with one card per roadmap step and the owner. **Done when:** the branch is pushed and every member can clone it.

---

## Step 5 — IP Research Registry Form (due Sep 5)
Fill and submit the course's IP Research Registry Form on the course site. **Done when:** submitted; screenshot in the repo `results/` or your drive. *(Admin only — no code.)*

---

## Step 6 — SUMO hello-world, then the reduced net (Lopez/Jared)
### 6a. Hello-world (proves SUMO + TraCI)
Create `sumo/nodes.nod.xml`, `sumo/edges.edg.xml`:
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
Build the net, then add routes + config:
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
Run `python scripts/hello_traci.py`. **Done when:** it prints bus counts and ends with `OK — SUMO + TraCI works`.

### 6b. Reduced corridor net (start of SO1)
`scripts/build_reduced_net.py` — straight-line net + busStops from your selection + segment distances:
```python
import os, sys, subprocess, pandas as pd
if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
from sumolib import checkBinary
sel = [l.strip() for l in open("reduced_corridor.txt") if l.strip()]
seg = pd.read_csv("sim_inputs/segment_running_time.csv").set_index("bs_id")
x, nodes = 0.0, []
for i, bs in enumerate(sel):
    nodes.append((f"n{i}", x))
    d = seg.loc[bs, "dist_median"] if bs in seg.index else 400.0
    x += max(float(d) if pd.notna(d) else 400.0, 100.0)
nodes.append((f"n{len(sel)}", x))                  # trailing node -> one edge per stop, so every stop gets a busStop
open("sumo/corridor.nod.xml","w").write("<nodes>\n"+"".join(f'  <node id="{n}" x="{xx:.1f}" y="0"/>\n' for n,xx in nodes)+"</nodes>\n")
open("sumo/corridor.edg.xml","w").write("<edges>\n"+"".join(f'  <edge id="e{i}" from="n{i}" to="n{i+1}" numLanes="1" speed="13.9"/>\n' for i in range(len(nodes)-1))+"</edges>\n")
subprocess.run([checkBinary("netconvert"),"--node-files=sumo/corridor.nod.xml","--edge-files=sumo/corridor.edg.xml","--output-file=sumo/corridor.net.xml"], check=True)
with open("sumo/stops.add.xml","w") as f:
    f.write("<additional>\n")
    for i, bs in enumerate(sel):                   # every stop now gets a busStop
        f.write(f'  <busStop id="{bs}" lane="e{i}_0" startPos="5" endPos="25"/>\n')
    f.write("</additional>\n")
print("built corridor.net.xml +", len(sel), "busStops")
```
**Done when:** `sumo/corridor.net.xml` opens in `netedit` and shows your stops in order. *(Straight-line, one lane — fine for now; real geometry + calibration is SO1 proper.)*

---

## Step 7 — PettingZoo AEC env skeleton (Badal/Jared)
**Goal:** a frame for SO2 to fill. Observation = methods Table 3.6 vector; action = proceed/hold. `envs/bus_env.py`:
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
        # obs = [norm_position, fwd_headway_s, bwd_headway_s, onboard_load, local_queue]
        self._obs = Box(low=0.0, high=np.inf, shape=(5,), dtype=np.float32)
        self._act = Discrete(2)                      # 0 = proceed, 1 = hold  (add 2 = skip later)
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
        # TODO(SO2-14): traci.start([...]) with sumo/corridor.net.xml + stops

    def observe(self, agent):
        return self.state[agent]                     # TODO(SO2-9): pull real features from TraCI

    def step(self, action):
        a = self.agent_selection
        if self.terminations[a] or self.truncations[a]:
            self._was_dead_step(action); return
        # TODO(SO2-10): apply action to bus `a` via TraCI (hold => extend stop)
        if self._sel.is_last():
            # TODO(SO2-14): traci.simulationStep()
            for ag in self.agents:
                self.rewards[ag] = self._reward(ag)  # TODO(SO2-12)
            self._accumulate_rewards()
        else:
            self._clear_rewards()
        self.agent_selection = self._sel.next()

    def _reward(self, agent):                        # TODO(SO2-12): penalize headway irregularity + delay
        return 0.0
    def close(self):
        pass                                         # TODO: traci.close()
```
**Done when:** `python -c "from envs.bus_env import env; e=env(); e.reset(); print('AEC env OK')"` prints `AEC env OK`.

---

## Step 8 — Even-Headway baseline (Medenilla)
**Goal:** the key benchmark, buildable now with no trained model. `baselines/even_headway.py`:
```python
def even_headway_hold(forward_headway_s, target_headway_s, max_hold_frac=0.4):
    """Hold a bus to push its forward headway toward target; capped at 0.4*H (Rodriguez et al. style)."""
    if forward_headway_s >= target_headway_s:
        return 0.0
    return float(min(target_headway_s - forward_headway_s, max_hold_frac * target_headway_s))

class EvenHeadwayController:
    def __init__(self, target_headway_s): self.H = target_headway_s
    def act(self, bus_state):            # bus_state = {"forward_headway_s": ...}
        return {"hold_s": even_headway_hold(bus_state["forward_headway_s"], self.H)}

if __name__ == "__main__":
    c = EvenHeadwayController(target_headway_s=300)
    for h in (120, 300, 420):
        print(f"fwd={h}s -> hold {c.act({'forward_headway_s': h})['hold_s']:.0f}s")
```
Run it to sanity-check. **Done when:** it prints holds (e.g. `fwd=120s -> hold 120s`, `fwd=420s -> hold 0s`). *(Reconcile the exact rule with methods / Rodriguez Eq. 11 later — the interface is what matters now.)*

---

## Step 9 — Progress Report 1 + MSA-1 pack (Marquez)
Assemble against the course PR template; content = this week's floor:
- Title, group, objectives recap (SO1–SO3).
- **Done this cycle:** dataset confirmed (229,421 events / 29 stops); `sim_inputs/` exported; reduced corridor locked; toolchain verified; SUMO hello-world + reduced net; AEC env + EH baseline skeletons.
- **Next cycle:** calibrate the reduced env to GEH<5 (SO1.1); wire the env's TraCI TODOs (SO2).
- **Risks + plan:** point to `Implementation_Roadmap_2026-09-01.md` (the Oct-3 calib and Oct-20 reward-gate targets).
**Done when:** PR1 drafted and reviewed by the group before the meeting.

---

## ⭐ The one thing that de-risks the whole semester: the end-to-end loop
Once Steps 6a and 7 pass **separately**, merge them and run a **random-agent loop** — this proves the MARL↔SUMO plumbing a month before the Oct-20 gate. In `bus_env.py`, wire just three TODOs: `reset()` → `traci.start([checkBinary("sumo"),"-c","sumo/hello.sumocfg"])` (use the **hello** config for the first proof — it already has moving buses; switch to the corridor once you add a bus route); the `is_last()` branch → `traci.simulationStep()`; `close()` → `traci.close()`. Then run `scripts/run_random.py`:
```python
from envs.bus_env import env
e = env(n_buses=4, n_stops=6); e.reset(seed=0)
for agent in e.agent_iter(max_iter=200):
    obs, rew, term, trunc, info = e.last()
    e.step(None if (term or trunc) else e.action_space(agent).sample())
e.close(); print("OK — end-to-end AEC + SUMO loop runs")
```
**Done when:** it prints `OK — end-to-end AEC + SUMO loop runs` while SUMO steps in the background. **If you get here this week, the scariest risk in the plan is basically gone.**

---

## Definition of done for Week 1 (tick these before MSA 1)
- [ ] Everyone: `sumo --version` + `traci OK`
- [ ] `sim_inputs/` exported (29 stops)
- [ ] `reduced_corridor.txt` locked (5–8 stops)
- [ ] `implementation` branch pushed + board set up
- [ ] IP Registry Form submitted
- [ ] `hello_traci.py` prints OK
- [ ] `corridor.net.xml` opens in netedit with stops
- [ ] `bus_env.py` resets without error
- [ ] `even_headway.py` prints holds
- [ ] PR1 drafted
- [ ] ⭐ Stretch: end-to-end random-agent loop runs

**Decision still pending (needed only for SO2 training, ~Oct):** RL library — RLlib vs Stable-Baselines3 vs CleanRL/custom. Not required for anything above.
