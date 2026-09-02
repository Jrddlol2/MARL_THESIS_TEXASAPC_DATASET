"""Reusable corridor simulation core — one loop that ANY controller drives.

`simulate(decide, ...)` runs the calibrated 26-stop corridor with the demand-responsive dwell and the
D/S/T/W/B disturbance generators, and calls `decide(obs) -> (hold_seconds, skip)` whenever a bus reaches
a CONTROL stop. Baselines (NC/FH/EH) and the MARL policy are just different `decide` functions, so they
all run on an identical environment — apples-to-apples by construction.

obs (dict) at a control stop:
    hf, hb  forward / backward headway (s)      load   onboard passengers
    queue   passengers waiting at the stop       idx    stop index (0..n-1)
    n       number of stops                      H0     scheduled headway (s), cap  bus capacity
decide returns (hold_seconds, skip_bool). hold is clipped to [0, 0.4*H0]; skip is accepted but only
takes effect if the caller enabled skipping (SKIP_ENABLED) — the fail-fast gate runs holding-only.

Run from the repo root (needs the calibrated sumo/ net + sim_inputs + corridor.txt).
"""
import os, sys, math, numpy as np, pandas as pd
if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci, sumolib
from sumolib import checkBinary

STOPS = [l.strip() for l in open("corridor.txt") if l.strip()]
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
FIXED_DWELL, BOARD_S, MAX_SERV, CAP_PAX = 6.0, 4.0, 90.0, 60
RUN = [float(d["run_s"].values[i]) for i in range(len(STOPS))]
CUM = [0.0]
for i in range(1, len(STOPS)):
    CUM.append(CUM[-1] + RUN[i-1] + BASE[STOPS[i-1]])
SURGE_I = len(STOPS) // 3
INTERIOR = list(range(1, len(STOPS) - 1))            # stops eligible to be control points

os.makedirs("sumo", exist_ok=True)
open("sumo/vtype.add.xml", "w").write('<additional><vType id="bus" vClass="bus" length="12" '
    'accel="1.2" decel="4.0" maxSpeed="30" personCapacity="60"/></additional>\n')

# ---- baseline decide functions (a controller is just decide: obs -> (hold_s, skip)) --------------
def fh_hold(hf): return 0.0 if hf >= H0 else float(min(H0 - hf, CAP * H0))
def eh_hold(hf, hb): return float(max(0.0, min(0.5 * (hb - hf), CAP * H0)))
def nc_decide(o): return 0.0, 0
def fh_decide(o): return fh_hold(o["hf"]), 0
def eh_decide(o): return eh_hold(o["hf"], o["hb"]), 0
BASELINES = {"NC": nc_decide, "FH": fh_decide, "EH": eh_decide}


def _make_persons(S):
    p = ["<additional>"]
    for i in range(len(STOPS) - 1):
        K = int(round(NBUS * DEM[STOPS[i]]))
        if K > 0:
            b, e = int(CUM[i]), int(CUM[i] + H0 * (NBUS - 1))
            p.append(f'<personFlow id="f{i}" begin="{b}" end="{e}" number="{K}">'
                     f'<stop busStop="{STOPS[i]}" duration="1"/><ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
    if S:
        sb = int(CUM[SURGE_I] + H0)
        p.append(f'<personFlow id="surge" begin="{sb}" end="{sb+900}" number="120">'
                 f'<stop busStop="{STOPS[SURGE_I]}" duration="1"/><ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
    open("sumo/persons_x.add.xml", "w").write("\n".join(p + ["</additional>"]))


def simulate(decide, seed=0, D=True, S=False, T=False, W=False, B=False, control_stops=None):
    """Drive the corridor with controller `decide`. Returns metrics dict (headway_cv, travel_s, wait_s)."""
    control_stops = set(INTERIOR if control_stops is None else control_stops)
    rng = np.random.default_rng(1000 + seed); _make_persons(S)
    ns = len(STOPS)
    DWN = rng.lognormal(0.0, CVD, size=(NBUS, ns))                       # dwell noise (pre-drawn field)
    s2 = math.log(1 + ETA * ETA)
    WF = np.clip(rng.lognormal(-0.5 * s2, math.sqrt(s2), size=(NBUS, ns)), 0.5, 3.0)   # weather
    TF = rng.uniform(0.8, 1.2, size=(NBUS, ns))                          # traffic
    bk_idx = int(rng.integers(2, NBUS - 1)); bks = int(rng.integers(1, ns - 1)) if B else -1
    port = sumolib.miscutils.getFreeSocketPort(); started = False
    try:
        traci.start([checkBinary("sumo"), "-n", "sumo/corridor.net.xml",
                     "-a", "sumo/vtype.add.xml,sumo/stops.add.xml,sumo/persons_x.add.xml",
                     "--no-warnings", "true", "--no-step-log", "true", "--seed", str(seed),
                     "--step-length", "1", "-e", "36000"], port=port); started = True
        traci.route.add("corr", EDGES)
        departs = {f"b{i}": i * H0 for i in range(NBUS)}
        added, toinit, idx, prev = set(), set(), {}, {}
        arr = {s: [] for s in STOPS}; tarr, target, resumed, entry, ca = {}, {}, set(), {}, {}
        barr = {}
        t = 0.0
        while t < H0 * NBUS + 30000 and (traci.simulation.getMinExpectedNumber() > 0 or len(added) < NBUS):
            for v, dep in departs.items():
                if v not in added and t >= dep:
                    traci.vehicle.add(v, "corr", typeID="bus", line="801"); added.add(v); toinit.add(v)
            traci.simulationStep(); t = traci.simulation.getTime(); live = set(traci.vehicle.getIDList())
            for v in list(toinit):
                if v in live:
                    idx[v], prev[v], entry[v] = 0, False, t
                    for k in range(ns):
                        try: traci.vehicle.setBusStop(v, STOPS[k], duration=BIG)
                        except traci.TraCIException: pass
                    toinit.discard(v)
            for v in list(added):
                if v not in live or v in toinit: continue
                st, i = traci.vehicle.isStopped(v), idx[v]
                if st and not prev[v] and i < ns:
                    s = STOPS[i]; arr[s].append(t); tarr[v] = t; bi = int(v[1:]); barr[(bi, i)] = t
                    if i == ns - 1: ca[v] = t
                    try: nwait = traci.busstop.getPersonCount(s)
                    except traci.TraCIException: nwait = 0
                    dserv = min(MAX_SERV, FIXED_DWELL + BOARD_S * nwait) * DWN[bi, i]
                    hold = 0.0
                    if i in control_stops and bi > 0:
                        hf = t - barr[(bi-1, i)] if (bi-1, i) in barr else H0
                        hb = (barr[(bi, i-1)] - barr[(bi+1, i-1)]) if ((bi+1, i-1) in barr and (bi, i-1) in barr) else H0
                        try: load = traci.vehicle.getPersonNumber(v)
                        except traci.TraCIException: load = 0
                        obs = dict(hf=hf, hb=hb, load=load, queue=nwait, idx=i, n=ns, H0=H0, cap=CAP_PAX)
                        hold, _skip = decide(obs)
                        hold = float(max(0.0, min(hold, CAP * H0)))
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
                if (not st) and prev[v] and i < ns: idx[v] = i + 1; resumed.discard(v)
                prev[v] = st
    finally:
        if started:
            try: traci.close()
            except Exception: pass
    cvs = [np.std(np.diff(sorted(arr[s]))) / np.mean(np.diff(sorted(arr[s]))) for s in STOPS[1:] if len(arr[s]) >= 3]
    tt  = [ca[v] - entry[v] for v in ca if v in entry]
    num, den = 0.0, 0.0
    for s in STOPS[1:]:
        h = np.diff(sorted(arr[s]))
        if len(h) >= 2 and DEM[s] > 0:
            Hb = h.mean(); cv = h.std() / Hb; num += DEM[s] * 0.5 * Hb * (1 + cv * cv); den += DEM[s]
    return dict(headway_cv=np.mean(cvs) if cvs else float("nan"),
                travel_s=np.mean(tt) if tt else float("nan"),
                wait_s=num / den if den else float("nan"))


if __name__ == "__main__":
    # Parity check: NC/FH/EH via simulate() at ALL interior control stops, D+T (Stage A), should
    # reproduce the committed MC (NC~0.335, FH~0.153, EH~0.172 headway CV).
    import numpy as np
    print("controller | mean headway CV (D+T, all-interior control stops, seeds 0-2)")
    for name, fn in BASELINES.items():
        cvs = [simulate(fn, seed=s, T=True)["headway_cv"] for s in range(3)]
        print(f"   {name:2s}      |  {np.mean(cvs):.3f}   (per-seed {[round(c,3) for c in cvs]})")
