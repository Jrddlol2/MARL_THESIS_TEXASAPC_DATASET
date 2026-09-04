"""Watch the corridor + controller + disturbances LIVE in sumo-gui.

Opens the graphical SUMO window and drives the same simulation as run_disturbances.py,
so you can see buses traverse the corridor, dwell at stops, board passengers, bunch under
weather/breakdown, and (under EH) be held to re-space.

Usage (from the repo root, needs a display):
    python scripts/watch.py                 # default: Even-Headway, Weather+Breakdown
    python scripts/watch.py NC Weather      # No-Control under Weather
    python scripts/watch.py EH Baseline     # Even-Headway, no disturbances
Args: [NC|EH] [Baseline|Weather|Weather+Breakdown].  Adjust the on-screen 'Delay (ms)' box
to speed up / slow down. Close the window (or let it finish) to stop.
"""
import os, sys, math, numpy as np, pandas as pd
if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci, sumolib
from sumolib import checkBinary

CTRL = sys.argv[1] if len(sys.argv) > 1 else "EH"
SCEN = sys.argv[2] if len(sys.argv) > 2 else "Weather+Breakdown"
ETA  = 0.8 if "Weather" in SCEN else 0.0
BREAKDOWN = "Breakdown" in SCEN

STOPS = [l.strip() for l in open("corridor.txt") if l.strip()]   # full 26-stop dir-6 corridor
EDGES = [f"e{i}" for i in range(len(STOPS))]
co = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id").loc[[int(s) for s in STOPS]]
d  = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id").loc[[int(s) for s in STOPS]]
lat0, lon0 = co["mean_lat"].mean(), co["mean_lon"].mean()
Xs = (co["mean_lon"] - lon0) * math.cos(math.radians(lat0)) * 111320
Ys = (co["mean_lat"] - lat0) * 110540

# Render on the REAL-GEOMETRY net (sumo/corridor_real.net.xml, built by scripts/build_real_net.py
# from the OSM route relation) so buses follow the true Route-801 shape. Falls back to the
# schematic net if it hasn't been built. Segment distances follow whichever net is loaded, so the
# weather/traffic speed model stays calibrated to the same empirical run_s targets either way.
REAL_NET = "sumo/corridor_real.net.xml"
USE_REAL = os.path.exists(REAL_NET) and os.path.exists("sim_inputs/route_shape_stops.csv")
if USE_REAL:
    _arc = pd.read_csv("sim_inputs/route_shape_stops.csv").set_index("bs_id")
    DIST = [float(_arc.loc[int(STOPS[i+1]), "arclen_m"] - _arc.loc[int(STOPS[i]), "arclen_m"])
            for i in range(len(STOPS)-1)]
else:
    DIST = [math.hypot(Xs.values[i+1]-Xs.values[i], Ys.values[i+1]-Ys.values[i]) for i in range(len(STOPS)-1)]
SEGV = [DIST[i] / d["run_s"].values[i] for i in range(len(DIST))]
BASE = {STOPS[i]: max(8.0, float(d["dwell_s"].values[i])) for i in range(len(STOPS))}
DEM  = {STOPS[i]: max(0.0, float(d["mean_boardings"].values[i])) for i in range(len(STOPS))}
H0, NBUS, CVD, CAP, BIG, TBREAK = 300.0, 12, 0.6, 0.4, 600.0, 400.0
CONTROL_STOPS = {0, 1, 5, 17, 20}    # the designated control stops (5280,5857,5859,5867,4046) — where actions apply

def eh_hold(h): return 0.0 if h >= H0 else float(min(H0 - h, CAP * H0))
def weather_factor(rng):
    if ETA <= 0: return 1.0
    s2 = math.log(1 + ETA*ETA); return float(min(3.0, max(0.5, rng.lognormal(-0.5*s2, math.sqrt(s2)))))

os.makedirs("sumo", exist_ok=True)   # generate the vType + passenger files so this runs standalone
# width=6 (vs the 2.5 m default) keeps buses legible when the whole 27.6 km corridor is on screen
open("sumo/vtype.add.xml", "w").write('<additional><vType id="bus" vClass="bus" length="12" width="6" accel="1.2" decel="4.0" maxSpeed="30" personCapacity="60"/></additional>\n')
_p = ["<additional>"]
for i in range(len(STOPS) - 1):
    K = int(round(NBUS * DEM[STOPS[i]]))
    if K > 0:
        _p.append(f'<personFlow id="f{i}" begin="0" end="{int(H0*(NBUS-1))}" number="{K}">'
                  f'<stop busStop="{STOPS[i]}" duration="1"/><ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
open("sumo/persons.add.xml", "w").write("\n".join(_p + ["</additional>"]))
# colour the busStops so you can see where actions are applied:
#   the five §3.2.2 CONTROL stops -> bright red, and drawn 3x longer so they read at a glance
#   the other 21 stops            -> dark slate (reads against the white background)
# Only the marker geometry differs; nothing here affects dwell or holding.
_st = ["<additional>"]
for i in range(len(STOPS)):
    ctrl = i in CONTROL_STOPS
    _st.append(f'<busStop id="{STOPS[i]}" lane="e{i}_0" startPos="5" '
               f'endPos="{65 if ctrl else 25}" '
               f'color="{"235,30,30" if ctrl else "70,90,110"}"/>')
open("sumo/stops_view.add.xml", "w").write("\n".join(_st + ["</additional>"]))

rng = np.random.default_rng(3)
# GUI: auto-start, human-watchable step delay
NET = REAL_NET if USE_REAL else "sumo/corridor.net.xml"
gui_args = [checkBinary("sumo-gui"), "-n", NET,
            "-a", "sumo/vtype.add.xml,sumo/stops_view.add.xml,sumo/persons.add.xml",
            "--start", "--delay", "80", "--no-warnings", "true", "-e", "36000"]
if os.path.exists("sumo/view.settings.xml"):
    gui_args += ["--gui-settings-file", "sumo/view.settings.xml"]
traci.start(gui_args, port=sumolib.miscutils.getFreeSocketPort())
traci.route.add("corr", EDGES)
try:
    if USE_REAL:                       # frame the real corridor's projected extent
        _sh = pd.read_csv("sim_inputs/route_shape.csv")
        m = 400.0
        traci.gui.setBoundary("View #0", _sh["x"].min()-m, _sh["y"].min()-m,
                              _sh["x"].max()+m, _sh["y"].max()+m)
    else:
        traci.gui.setBoundary("View #0", -50.0, -160.0, sum(DIST) + 560.0, 160.0)
except Exception: pass
print(f"Watching: controller={CTRL}, scenario={SCEN}  "
      f"net={'REAL route geometry' if USE_REAL else 'schematic'}  (close the window to stop)")
departs = {f"b{i}": i*H0 for i in range(NBUS)}
added, toinit, idx, prev, arr, tarr, target, resumed, dwell = set(), set(), {}, {}, {s: [] for s in STOPS}, {}, {}, set(), {}
bk, bks = f"b{rng.integers(2, NBUS-1)}", (int(rng.integers(1, len(STOPS)-1)) if BREAKDOWN else -1)
t = 0.0
while t < H0*NBUS + 30000 and (traci.simulation.getMinExpectedNumber() > 0 or len(added) < NBUS):
    for v, dep in departs.items():
        if v not in added and t >= dep:
            traci.vehicle.add(v, "corr", typeID="bus", line="801"); added.add(v); toinit.add(v)
    traci.simulationStep(); t = traci.simulation.getTime(); live = set(traci.vehicle.getIDList())
    for v in list(toinit):
        if v in live:
            idx[v], prev[v] = 0, False
            dwell[v] = [max(5.0, BASE[STOPS[k]] * rng.lognormal(0, CVD)) for k in range(len(STOPS))]
            for k in range(len(STOPS)):
                try: traci.vehicle.setBusStop(v, STOPS[k], duration=BIG)
                except traci.TraCIException: pass
            traci.vehicle.setColor(v, (0, 120, 255) if CTRL == "EH" else (160, 160, 160))
            toinit.discard(v)
    for v in list(added):
        if v not in live or v in toinit: continue
        st, i = traci.vehicle.isStopped(v), idx[v]
        if st and not prev[v] and i < len(STOPS):
            s = STOPS[i]; arr[s].append(t); tarr[v] = t
            hold = eh_hold(t - arr[s][-2]) if (CTRL == "EH" and i in CONTROL_STOPS and len(arr[s]) >= 2) else 0.0
            tb = TBREAK if (BREAKDOWN and v == bk and i == bks) else 0.0
            if tb > 0: traci.vehicle.setColor(v, (230, 40, 40))            # breakdown = red
            elif hold > 0: traci.vehicle.setColor(v, (255, 170, 0))        # applying a hold action = amber
            target[v] = dwell[v][i] + hold + tb
            try: traci.vehicle.setMaxSpeed(v, 30.0)
            except traci.TraCIException: pass
        if st and v not in resumed and (t - tarr.get(v, t)) >= target.get(v, 0):
            try:
                traci.vehicle.resume(v); resumed.add(v)
                traci.vehicle.setColor(v, (0, 120, 255) if CTRL == "EH" else (160, 160, 160))   # back to base after acting
            except traci.TraCIException: pass
            if i < len(DIST) and ETA > 0:
                try: traci.vehicle.setMaxSpeed(v, max(2.0, SEGV[i] / weather_factor(rng)))
                except traci.TraCIException: pass
        if (not st) and prev[v] and i < len(STOPS): idx[v] = i + 1; resumed.discard(v)
        prev[v] = st
traci.close()
print("done.")
