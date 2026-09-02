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

STOPS = [l.strip() for l in open("corridor.txt") if l.strip()]   # full 26-stop dir-6 corridor
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
H0, NBUS, CVD, CAP, BIG, TBREAK, ETA = 300.0, 12, 0.25, 0.4, 600.0, 400.0, 0.8
FIXED_DWELL, BOARD_S, MAX_SERV = 6.0, 4.0, 90.0   # dwell = door time + boarding_s * waiting pax (capped)
# CUM[i] = time for a bus leaving the terminal at t=0 to reach stop i (run + upstream dwell);
# used to align each stop's demand window with when buses actually serve it (steady-state waits).
RUN = [float(d["run_s"].values[i]) for i in range(len(STOPS))]
CUM = [0.0]
for i in range(1, len(STOPS)):
    CUM.append(CUM[-1] + RUN[i - 1] + BASE[STOPS[i - 1]])
SURGE_I = len(STOPS) // 3                              # an upper-corridor stop, so the surge has room to propagate

def fh_hold(hf):                       # Forward-Headway: hold up to target headway behind the leader
    return 0.0 if hf >= H0 else float(min(H0 - hf, CAP * H0))
def eh_hold(hf, hb):                    # Even-Headway (two-way): center the bus between leader and follower
    return float(max(0.0, min(0.5 * (hb - hf), CAP * H0)))
def w_factor(rng): s2 = math.log(1 + ETA*ETA); return float(min(3.0, max(0.5, rng.lognormal(-0.5*s2, math.sqrt(s2)))))
def t_factor(rng): return float(rng.uniform(0.8, 1.2))
def make_persons(S):
    p = ["<additional>"]
    for i in range(len(STOPS)-1):
        K = int(round(NBUS * DEM[STOPS[i]]))
        if K > 0:
            b, e = int(CUM[i]), int(CUM[i] + H0*(NBUS-1))
            p.append(f'<personFlow id="f{i}" begin="{b}" end="{e}" number="{K}">'
                     f'<stop busStop="{STOPS[i]}" duration="1"/><ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
    if S:  # sustained demand surge at an upper-corridor stop over ~3 headways (overflow propagates downstream)
        sb = int(CUM[SURGE_I] + H0)
        p.append(f'<personFlow id="surge" begin="{sb}" end="{sb+900}" number="120">'
                 f'<stop busStop="{STOPS[SURGE_I]}" duration="1"/><ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
    open("sumo/persons_x.add.xml", "w").write("\n".join(p + ["</additional>"]))

def run(ctrl, D=True, S=False, T=False, W=False, B=False, seed=1):
    rng = np.random.default_rng(1000 + seed); make_persons(S)
    # Pre-draw every disturbance as a fixed field per (bus, stop) so NC and EH at the same seed
    # experience the IDENTICAL realization -> a truly paired comparison (controller-independent).
    ns = len(STOPS)
    DWN = rng.lognormal(0.0, CVD, size=(NBUS, ns))                       # dwell noise
    s2 = math.log(1 + ETA * ETA)
    WF = np.clip(rng.lognormal(-0.5 * s2, math.sqrt(s2), size=(NBUS, ns)), 0.5, 3.0)  # weather factor
    TF = rng.uniform(0.8, 1.2, size=(NBUS, ns))                          # traffic factor
    bk_idx = int(rng.integers(2, NBUS - 1)); bks = int(rng.integers(1, ns - 1)) if B else -1
    tri = "sumo/tri_x.xml"; port = sumolib.miscutils.getFreeSocketPort()
    traci.start([checkBinary("sumo"), "-n", "sumo/corridor.net.xml",
                 "-a", "sumo/vtype.add.xml,sumo/stops.add.xml,sumo/persons_x.add.xml",
                 "--tripinfo-output", tri, "--no-warnings", "true", "--no-step-log", "true",
                 "--seed", str(seed), "--step-length", "1", "-e", "36000"], port=port)
    traci.route.add("corr", EDGES)
    departs = {f"b{i}": i*H0 for i in range(NBUS)}
    added, toinit, idx, prev = set(), set(), {}, {}
    arr = {s: [] for s in STOPS}; tarr, target, resumed, entry, ca, dwell = {}, {}, set(), {}, {}, {}
    barr = {}                          # (bus_index, stop_index) -> arrival time, for leader/follower headways
    t = 0.0
    while t < H0*NBUS + 30000 and (traci.simulation.getMinExpectedNumber() > 0 or len(added) < NBUS):
        for v, dep in departs.items():
            if v not in added and t >= dep:
                traci.vehicle.add(v, "corr", typeID="bus", line="801"); added.add(v); toinit.add(v)
        traci.simulationStep(); t = traci.simulation.getTime(); live = set(traci.vehicle.getIDList())
        for v in list(toinit):
            if v in live:
                idx[v], prev[v], entry[v] = 0, False, t
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
                bi = int(v[1:]); barr[(bi, i)] = t
                try: nwait = traci.busstop.getPersonCount(s)          # passengers waiting -> demand-driven dwell
                except traci.TraCIException: nwait = 0
                dserv = min(MAX_SERV, FIXED_DWELL + BOARD_S * nwait) * DWN[bi, i]
                hold = 0.0
                if ctrl in ("FH", "EH") and 0 < i < len(STOPS)-1 and bi > 0:
                    hf = t - barr[(bi-1, i)] if (bi-1, i) in barr else H0             # gap to leader (this stop)
                    if ctrl == "FH":
                        hold = fh_hold(hf)
                    else:                                                            # EH: gap to follower via previous stop
                        hb = (barr[(bi, i-1)] - barr[(bi+1, i-1)]) if ((bi+1, i-1) in barr and (bi, i-1) in barr) else H0
                        hold = eh_hold(hf, hb)
                tb = TBREAK if (B and bi == bk_idx and i == bks) else 0.0
                target[v] = max(FIXED_DWELL, dserv) + hold + tb
                try: traci.vehicle.setMaxSpeed(v, 30.0)
                except traci.TraCIException: pass
            if st and v not in resumed and (t - tarr.get(v, t)) >= target.get(v, 0):
                try: traci.vehicle.resume(v); resumed.add(v)
                except traci.TraCIException: pass
                if i < len(DIST):
                    f = 1.0
                    if W: f *= float(WF[bi, i])
                    if T: f /= float(TF[bi, i])
                    if f != 1.0:
                        try: traci.vehicle.setMaxSpeed(v, max(2.0, SEGV[i] / f))
                        except traci.TraCIException: pass
            if (not st) and prev[v] and i < len(STOPS): idx[v] = i + 1; resumed.discard(v)
            prev[v] = st
    traci.close()
    cvs = [np.std(np.diff(sorted(arr[s]))) / np.mean(np.diff(sorted(arr[s]))) for s in STOPS[1:] if len(arr[s]) >= 3]
    tt  = [ca[v] - entry[v] for v in ca if v in entry]
    # Passenger wait from the simulated bus-arrival headways via the random-arrival model
    # w = (E[H]/2)(1 + CV^2), boardings-weighted over stops (robust to demand-injection timing;
    # this is the same (H0/2)(1+CV^2) relationship stated in the methods).
    num, den = 0.0, 0.0
    for s in STOPS[1:]:
        h = np.diff(sorted(arr[s]))
        if len(h) >= 2 and DEM[s] > 0:
            Hb = h.mean(); cv = h.std() / Hb
            num += DEM[s] * 0.5 * Hb * (1 + cv * cv); den += DEM[s]
    wait = num / den if den else float("nan")
    return (np.mean(cvs) if cvs else float("nan"), np.mean(tt) if tt else float("nan"), wait)

if __name__ == "__main__":
    scen = [("D baseline", {}), ("S surge", dict(S=True)), ("T traffic", dict(T=True)),
            ("W weather", dict(W=True)), ("B breakdown", dict(B=True)),
            ("all D/S/T/W/B", dict(S=True, T=True, W=True, B=True))]
    print("scenario        | ctrl | headwayCV | travel(s) | wait(s)")
    for name, kw in scen:
        for c in ["NC", "EH"]:
            cv, tt, w = run(c, **kw)
            print(f"{name:15s} | {c:2s}   |  {cv:6.3f}  |   {tt:6.0f}  | {w:6.1f}")
