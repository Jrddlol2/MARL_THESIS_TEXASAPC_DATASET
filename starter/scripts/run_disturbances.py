"""Disturbance generators (SO1.2) — full D/S/T/W/B suite + scenario comparison (NC vs EH).

Generators (toggle per run):
  D  baseline stochastic demand — always on (persons injected at empirical APC boarding rates).
  S  demand surge — a burst of extra passengers at a mid-corridor stop over a time window.
  T  traffic-speed — per-segment speed factor U(0.8, 1.2)  (Wangsun clip).
  W  weather — per-segment heavy-tailed factor F_W~LogNormal, E=1, CV=eta, capped [0.5,3] (Patil et al.).
  B  breakdown — one bus immobilized mid-corridor for TBREAK s (Cao et al.).

Speed factors combine as segment_speed / (F_W * (1/F_T)); dwell/hold via resume() so boarding
and holding coexist. Metrics: headway CV, corridor travel time, mean passenger wait.
Run from repo root; needs sumo/corridor.net.xml, sumo/stops.add.xml, sim_inputs/{stops,stop_coordinates}.csv.
"""
import os, sys, math, numpy as np, pandas as pd, xml.etree.ElementTree as ET
if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci, sumolib
from sumolib import checkBinary

STOPS = ["5857", "5858", "4540", "467", "5859", "5606"]
EDGES = [f"e{i}" for i in range(len(STOPS))]
co = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id").loc[[int(s) for s in STOPS]]
d  = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id").loc[[int(s) for s in STOPS]]
lat0, lon0 = co["mean_lat"].mean(), co["mean_lon"].mean()
Xs = (co["mean_lon"] - lon0) * math.cos(math.radians(lat0)) * 111320
Ys = (co["mean_lat"] - lat0) * 110540
DIST = [math.hypot(Xs.values[i+1]-Xs.values[i], Ys.values[i+1]-Ys.values[i]) for i in range(len(STOPS)-1)]
SEGV = [DIST[i] / d["run_s"].values[i] for i in range(len(DIST))]
BASE = {STOPS[i]: max(8.0, float(d["dwell_s"].values[i]))        for i in range(len(STOPS))}
DEM  = {STOPS[i]: max(0.0, float(d["mean_boardings"].values[i])) for i in range(len(STOPS))}
H0, NBUS, CVD, CAP, BIG, TBREAK, ETA = 300.0, 8, 0.6, 0.4, 600.0, 400.0, 0.8

def eh_hold(h): return 0.0 if h >= H0 else float(min(H0 - h, CAP * H0))
def w_factor(rng): s2 = math.log(1 + ETA*ETA); return float(min(3.0, max(0.5, rng.lognormal(-0.5*s2, math.sqrt(s2)))))
def t_factor(rng): return float(rng.uniform(0.8, 1.2))
def make_persons(S):
    p = ["<additional>"]
    for i in range(len(STOPS)-1):
        K = int(round(NBUS * DEM[STOPS[i]]))
        if K > 0:
            p.append(f'<personFlow id="f{i}" begin="0" end="{int(H0*(NBUS-1))}" number="{K}">'
                     f'<stop busStop="{STOPS[i]}" duration="1"/><ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
    if S:  # demand surge at stop 4540 over 600-1400 s
        p.append(f'<personFlow id="surge" begin="600" end="1400" number="45">'
                 f'<stop busStop="4540" duration="1"/><ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
    open("sumo/persons_x.add.xml", "w").write("\n".join(p + ["</additional>"]))

def run(ctrl, D=True, S=False, T=False, W=False, B=False, seed=1):
    rng = np.random.default_rng(1000 + seed); make_persons(S)
    tri = "sumo/tri_x.xml"; port = sumolib.miscutils.getFreeSocketPort()
    traci.start([checkBinary("sumo"), "-n", "sumo/corridor.net.xml",
                 "-a", "sumo/vtype.add.xml,sumo/stops.add.xml,sumo/persons_x.add.xml",
                 "--tripinfo-output", tri, "--no-warnings", "true", "--no-step-log", "true",
                 "--step-length", "1", "-e", "22000"], port=port)
    traci.route.add("corr", EDGES)
    departs = {f"b{i}": i*H0 for i in range(NBUS)}
    added, toinit, idx, prev = set(), set(), {}, {}
    arr = {s: [] for s in STOPS}; tarr, target, resumed, entry, ca, dwell = {}, {}, set(), {}, {}, {}
    bk, bks = f"b{rng.integers(2, NBUS-1)}", (int(rng.integers(1, 5)) if B else -1)
    t = 0.0
    while t < H0*NBUS + 16000 and (traci.simulation.getMinExpectedNumber() > 0 or len(added) < NBUS):
        for v, dep in departs.items():
            if v not in added and t >= dep:
                traci.vehicle.add(v, "corr", typeID="bus", line="801"); added.add(v); toinit.add(v)
        traci.simulationStep(); t = traci.simulation.getTime(); live = set(traci.vehicle.getIDList())
        for v in list(toinit):
            if v in live:
                idx[v], prev[v], entry[v] = 0, False, t
                dwell[v] = [max(5.0, BASE[STOPS[k]] * rng.lognormal(0, CVD)) for k in range(len(STOPS))]
                for k in range(len(STOPS)):
                    try: traci.vehicle.setBusStop(v, STOPS[k], duration=BIG)
                    except traci.TraCIException: pass
                toinit.discard(v)
        for v in list(added):
            if v not in live or v in toinit: continue
            st, i = traci.vehicle.isStopped(v), idx[v]
            if st and not prev[v] and i < len(STOPS):
                s = STOPS[i]; arr[s].append(t); tarr[v] = t
                if i == len(STOPS)-1: ca[v] = t
                hold = eh_hold(t - arr[s][-2]) if (ctrl == "EH" and 0 < i < len(STOPS)-1 and len(arr[s]) >= 2) else 0.0
                tb = TBREAK if (B and v == bk and i == bks) else 0.0
                target[v] = dwell[v][i] + hold + tb
                try: traci.vehicle.setMaxSpeed(v, 30.0)
                except traci.TraCIException: pass
            if st and v not in resumed and (t - tarr.get(v, t)) >= target.get(v, 0):
                try: traci.vehicle.resume(v); resumed.add(v)
                except traci.TraCIException: pass
                if i < len(DIST):
                    f = 1.0
                    if W: f *= w_factor(rng)
                    if T: f /= t_factor(rng)
                    if f != 1.0:
                        try: traci.vehicle.setMaxSpeed(v, max(2.0, SEGV[i] / f))
                        except traci.TraCIException: pass
            if (not st) and prev[v] and i < len(STOPS): idx[v] = i + 1; resumed.discard(v)
            prev[v] = st
    traci.close()
    cvs = [np.std(np.diff(sorted(arr[s]))) / np.mean(np.diff(sorted(arr[s]))) for s in STOPS[1:] if len(arr[s]) >= 3]
    tt  = [ca[v] - entry[v] for v in ca if v in entry]
    waits = [float(r.get("waitingTime", 0)) for pi in ET.parse(tri).getroot().findall("personinfo")
             for r in pi.findall("ride") if float(r.get("arrival", "-1")) >= 0]
    return (np.mean(cvs) if cvs else float("nan"), np.mean(tt) if tt else float("nan"),
            np.mean(waits) if waits else float("nan"))

if __name__ == "__main__":
    scen = [("D baseline", {}), ("S surge", dict(S=True)), ("T traffic", dict(T=True)),
            ("W weather", dict(W=True)), ("B breakdown", dict(B=True)),
            ("all D/S/T/W/B", dict(S=True, T=True, W=True, B=True))]
    print("scenario        | ctrl | headwayCV | travel(s) | wait(s)")
    for name, kw in scen:
        for c in ["NC", "EH"]:
            cv, tt, w = run(c, **kw)
            print(f"{name:15s} | {c:2s}   |  {cv:6.3f}  |   {tt:6.0f}  | {w:6.1f}")
