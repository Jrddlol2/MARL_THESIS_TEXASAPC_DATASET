"""Baseline evaluation harness (SO3): No-Control vs Even-Headway, with passenger demand.

A fleet runs the calibrated corridor at scheduled headway H0 with stochastic dwell (stand-in
for demand variability that induces bunching). Passengers are injected at each stop at the
empirical APC boarding rate and ride to the last stop; SUMO records each rider's wait.
No-Control: buses run freely. Even-Headway: a bus whose forward headway < H0 is held
(Rodriguez et al., 0.4*H cap). Departures are controlled with resume() so both boarding
(full stop list known) and holding work together.

Metrics: headway CV (bunching), mean corridor travel time, mean & SD passenger waiting time.
Self-contained: generates sumo/vtype.add.xml and sumo/persons.add.xml. Run from repo root;
needs sumo/corridor.net.xml + sumo/stops.add.xml + sim_inputs/stops.csv.
Note: mean wait scales as (H0/2)(1+CV^2), so EH's waiting benefit grows with bunching severity.
"""
import os, sys, numpy as np, pandas as pd, xml.etree.ElementTree as ET
if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
from sumolib import checkBinary

STOPS = ["5857", "5858", "4540", "467", "5859", "5606"]
EDGES = [f"e{i}" for i in range(len(STOPS))]
H0, NBUS, CV_DWELL, CAP, BIG = 300.0, 8, 0.6, 0.4, 600.0

d = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id").loc[[int(s) for s in STOPS]]
BASE   = {STOPS[i]: max(8.0, float(d["dwell_s"].values[i]))        for i in range(len(STOPS))}
DEMAND = {STOPS[i]: max(0.0, float(d["mean_boardings"].values[i])) for i in range(len(STOPS))}

os.makedirs("sumo", exist_ok=True)
open("sumo/vtype.add.xml", "w").write(
    '<additional><vType id="bus" vClass="bus" length="12" accel="1.2" decel="4.0" '
    'maxSpeed="30" personCapacity="60"/></additional>\n')
Tend = int(H0 * (NBUS - 1))
p = ["<additional>"]
for i in range(len(STOPS) - 1):
    K = int(round(NBUS * DEMAND[STOPS[i]]))
    if K > 0:
        p.append(f'  <personFlow id="f{i}" begin="0" end="{Tend}" number="{K}">'
                 f'<stop busStop="{STOPS[i]}" duration="1"/>'
                 f'<ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
p.append("</additional>")
open("sumo/persons.add.xml", "w").write("\n".join(p))

def eh_hold(h_fwd):
    return 0.0 if h_fwd >= H0 else float(min(H0 - h_fwd, CAP * H0))

def run(controller, seed=1):
    rng = np.random.default_rng(seed); tri = f"sumo/tripinfo_{controller}.xml"
    traci.start([checkBinary("sumo"), "-n", "sumo/corridor.net.xml",
                 "-a", "sumo/vtype.add.xml,sumo/stops.add.xml,sumo/persons.add.xml",
                 "--tripinfo-output", tri, "--no-warnings", "true", "--no-step-log", "true",
                 "--step-length", "1", "-e", "12000"])
    traci.route.add("corr", EDGES)
    departs = {f"b{i}": i * H0 for i in range(NBUS)}
    added, toinit = set(), set()
    idx, prev, tarr, target, resumed, entry, corr_arr, dwell = {}, {}, {}, {}, set(), {}, {}, {}
    arr = {s: [] for s in STOPS}
    t = 0.0
    while t < H0 * NBUS + 7000 and (traci.simulation.getMinExpectedNumber() > 0 or len(added) < NBUS):
        for v, dep in departs.items():
            if v not in added and t >= dep:
                traci.vehicle.add(v, "corr", typeID="bus", line="801"); added.add(v); toinit.add(v)
        traci.simulationStep(); t = traci.simulation.getTime(); live = set(traci.vehicle.getIDList())
        for v in list(toinit):
            if v in live:
                idx[v], prev[v], entry[v] = 0, False, t
                dwell[v] = [max(5.0, BASE[STOPS[k]] * rng.lognormal(0, CV_DWELL)) for k in range(len(STOPS))]
                for k in range(len(STOPS)):
                    try: traci.vehicle.setBusStop(v, STOPS[k], duration=BIG)   # long stops; resume() controls departure
                    except traci.TraCIException: pass
                toinit.discard(v)
        for v in list(added):
            if v not in live or v in toinit: continue
            st, i = traci.vehicle.isStopped(v), idx[v]
            if st and not prev[v] and i < len(STOPS):                          # arrived at STOPS[i]
                s = STOPS[i]; arr[s].append(t); tarr[v] = t
                if i == len(STOPS) - 1: corr_arr[v] = t
                hold = eh_hold(t - arr[s][-2]) if (controller == "EH" and 0 < i < len(STOPS) - 1 and len(arr[s]) >= 2) else 0.0
                target[v] = dwell[v][i] + hold
            if st and v not in resumed and (t - tarr.get(v, t)) >= target.get(v, 0):
                try: traci.vehicle.resume(v); resumed.add(v)
                except traci.TraCIException: pass
            if (not st) and prev[v] and i < len(STOPS):
                idx[v] = i + 1; resumed.discard(v)
            prev[v] = st
    traci.close()
    cvs = [np.std(np.diff(sorted(arr[s]))) / np.mean(np.diff(sorted(arr[s]))) for s in STOPS[1:] if len(arr[s]) >= 3]
    tt  = [corr_arr[v] - entry[v] for v in corr_arr if v in entry]
    waits = []
    for pi in ET.parse(tri).getroot().findall("personinfo"):
        for ride in pi.findall("ride"):
            if float(ride.get("arrival", "-1")) >= 0: waits.append(float(ride.get("waitingTime", 0)))
    return dict(headway_cv=np.mean(cvs) if cvs else float("nan"),
                travel_s=np.mean(tt) if tt else float("nan"),
                wait_mean=np.mean(waits) if waits else float("nan"),
                wait_sd=np.std(waits) if waits else float("nan"), boarded=len(waits))

if __name__ == "__main__":
    print("controller | headway CV | travel (s) | mean wait (s) | wait SD (s) | boarded")
    R = {}
    for c in ["NC", "EH"]:
        r = run(c); R[c] = r
        print(f"   {c:3s}    |   {r['headway_cv']:6.3f}   |   {r['travel_s']:6.1f}  |    {r['wait_mean']:6.1f}     |   {r['wait_sd']:6.1f}    |  {r['boarded']}")
    print(f"\nEH vs NC: headway CV {(R['NC']['headway_cv']-R['EH']['headway_cv'])/R['NC']['headway_cv']*100:+.0f}%, "
          f"travel {(R['EH']['travel_s']-R['NC']['travel_s'])/R['NC']['travel_s']*100:+.0f}%")
