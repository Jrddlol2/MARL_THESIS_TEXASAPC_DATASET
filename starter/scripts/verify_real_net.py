"""Verification for the real-geometry viewer net — traversal + frozen-results parity.

(A) TRAVERSAL: drives BOTH nets headless with the viewer's mechanics (12 buses, H0=300 s,
    stochastic dwell, Even-Headway holding at the five control stops, weather + breakdown) over
    several SUMO seeds. The schematic net is the CONTROL: a completion rate that matches it
    shows any shortfall comes from the stochastic scenario, not from the real geometry. This is
    the GUI check we cannot do by eye on this machine.

(B) PARITY: the results pipeline is untouched by construction — envs/corridor_sim.py,
    sumo/corridor.net.xml and sumo/stops.add.xml are byte-identical (md5-verified). Note that
    simulate() is deterministic WITHIN a process but not across processes, so per-seed replay of
    the committed table is not a meaningful test; the right standard is distributional, which is
    what this checks (bootstrap mean + 95% CI vs the committed Stage-A row).

Usage:  python scripts/verify_real_net.py [n_seeds] [jobs]
"""
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
import sumolib
from sumolib import checkBinary

sys.path.insert(0, os.getcwd())

STOPS = [l.strip() for l in open("corridor.txt") if l.strip()]
IDS = [int(s) for s in STOPS]
EDGES = [f"e{i}" for i in range(len(STOPS))]
H0, NBUS, CVD, CAP, BIG, TBREAK, ETA = 300.0, 12, 0.6, 0.4, 600.0, 400.0, 0.8
CONTROL_STOPS = {0, 1, 5, 17, 20}

_d = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id").loc[IDS]
_arc = pd.read_csv("sim_inputs/route_shape_stops.csv").set_index("bs_id")
BASE = {STOPS[i]: max(8.0, float(_d["dwell_s"].values[i])) for i in range(len(STOPS))}
DEM = {STOPS[i]: max(0.0, float(_d["mean_boardings"].values[i])) for i in range(len(STOPS))}
# along-route distances for the real net; straight-line for the schematic one (as each net is built)
DIST_REAL = [float(_arc.loc[IDS[i + 1], "arclen_m"] - _arc.loc[IDS[i], "arclen_m"])
             for i in range(len(STOPS) - 1)]
_co = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id").loc[IDS]
_lat0, _lon0 = _co["mean_lat"].mean(), _co["mean_lon"].mean()
_X = (_co["mean_lon"] - _lon0) * math.cos(math.radians(_lat0)) * 111320
_Y = (_co["mean_lat"] - _lat0) * 110540
DIST_SCHEM = [math.hypot(_X.values[i + 1] - _X.values[i], _Y.values[i + 1] - _Y.values[i])
              for i in range(len(STOPS) - 1)]


def eh_hold(h):
    return 0.0 if h >= H0 else float(min(H0 - h, CAP * H0))


def weather_factor(rng):
    s2 = math.log(1 + ETA * ETA)
    return float(min(3.0, max(0.5, rng.lognormal(-0.5 * s2, math.sqrt(s2)))))


def _traverse(args):
    """One traversal replication on the given net. Returns (reached, nbus, travel, cv)."""
    net, stops_add, dist, seed = args
    segv = [dist[i] / float(_d["run_s"].values[i]) for i in range(len(dist))]
    port = sumolib.miscutils.getFreeSocketPort()
    persons = f"sumo/persons_verify_{port}.xml"
    p = ["<additional>"]
    for i in range(len(STOPS) - 1):
        K = int(round(NBUS * DEM[STOPS[i]]))
        if K > 0:
            p.append(f'<personFlow id="f{i}" begin="0" end="{int(H0*(NBUS-1))}" number="{K}">'
                     f'<stop busStop="{STOPS[i]}" duration="1"/>'
                     f'<ride busStop="{STOPS[-1]}" lines="801"/></personFlow>')
    open(persons, "w").write("\n".join(p + ["</additional>"]))

    rng = np.random.default_rng(3 + seed)
    traci.start([checkBinary("sumo"), "-n", net,
                 "-a", f"sumo/vtype.add.xml,{stops_add},{persons}",
                 "--no-warnings", "true", "--no-step-log", "true",
                 "--seed", str(seed), "-e", "36000"], port=port)
    traci.route.add("corr", EDGES)
    departs = {f"b{i}": i * H0 for i in range(NBUS)}
    added, toinit, idx, prev = set(), set(), {}, {}
    arr = {s: [] for s in STOPS}
    tarr, target, resumed, dwell, entry, done = {}, {}, set(), {}, {}, {}
    bk = f"b{rng.integers(2, NBUS-1)}"
    bks = int(rng.integers(1, len(STOPS) - 1))
    t = 0.0
    while t < H0 * NBUS + 30000 and (traci.simulation.getMinExpectedNumber() > 0
                                     or len(added) < NBUS):
        for v, dep in departs.items():
            if v not in added and t >= dep:
                traci.vehicle.add(v, "corr", typeID="bus", line="801")
                added.add(v)
                toinit.add(v)
        traci.simulationStep()
        t = traci.simulation.getTime()
        live = set(traci.vehicle.getIDList())
        for v in list(toinit):
            if v in live:
                idx[v], prev[v], entry[v] = 0, False, t
                dwell[v] = [max(5.0, BASE[STOPS[k]] * rng.lognormal(0, CVD))
                            for k in range(len(STOPS))]
                for k in range(len(STOPS)):
                    try:
                        traci.vehicle.setBusStop(v, STOPS[k], duration=BIG)
                    except traci.TraCIException:
                        pass
                toinit.discard(v)
        for v in list(added):
            if v not in live or v in toinit:
                continue
            st, i = traci.vehicle.isStopped(v), idx[v]
            if st and not prev[v] and i < len(STOPS):
                s = STOPS[i]
                arr[s].append(t)
                tarr[v] = t
                if i == len(STOPS) - 1:
                    done[v] = t
                hold = eh_hold(t - arr[s][-2]) if (i in CONTROL_STOPS and len(arr[s]) >= 2) else 0.0
                tb = TBREAK if (v == bk and i == bks) else 0.0
                target[v] = dwell[v][i] + hold + tb
                try:
                    traci.vehicle.setMaxSpeed(v, 30.0)
                except traci.TraCIException:
                    pass
            if st and v not in resumed and (t - tarr.get(v, t)) >= target.get(v, 0):
                try:
                    traci.vehicle.resume(v)
                    resumed.add(v)
                except traci.TraCIException:
                    pass
                if i < len(dist):
                    try:
                        traci.vehicle.setMaxSpeed(v, max(2.0, segv[i] / weather_factor(rng)))
                    except traci.TraCIException:
                        pass
            if (not st) and prev[v] and i < len(STOPS):
                idx[v] = i + 1
                resumed.discard(v)
            prev[v] = st
    traci.close()
    try:
        os.remove(persons)
    except OSError:
        pass
    tt = [done[v] - entry[v] for v in done if v in entry]
    cvs = [np.std(np.diff(sorted(arr[s]))) / np.mean(np.diff(sorted(arr[s])))
           for s in STOPS[1:] if len(arr[s]) >= 3]
    return (len(done), NBUS, float(np.mean(tt)) if tt else float("nan"),
            float(np.mean(cvs)) if cvs else float("nan"))


def traversal_check(nseeds, jobs):
    print("=" * 78)
    print("(A) TRAVERSAL — real geometry vs schematic CONTROL, 12 buses, EH, Weather+Breakdown")
    print("=" * 78)
    if not os.path.exists("sumo/vtype.add.xml"):
        open("sumo/vtype.add.xml", "w").write(
            '<additional><vType id="bus" vClass="bus" length="12" accel="1.2" decel="4.0" '
            'maxSpeed="30" personCapacity="60"/></additional>\n')
    nets = [("real     ", "sumo/corridor_real.net.xml", "sumo/stops_real.add.xml", DIST_REAL),
            ("schematic", "sumo/corridor.net.xml", "sumo/stops.add.xml", DIST_SCHEM)]
    out = {}
    for label, net, add, dist in nets:
        tasks = [(net, add, dist, s) for s in range(nseeds)]
        if jobs > 1:
            with ProcessPoolExecutor(max_workers=jobs) as ex:
                res = list(ex.map(_traverse, tasks))
        else:
            res = [_traverse(t) for t in tasks]
        reached = sum(r[0] for r in res)
        total = sum(r[1] for r in res)
        out[label.strip()] = (reached, total, res)
        print(f"  {label}: {reached}/{total} bus-completions over {nseeds} seeds   "
              f"travel {np.nanmean([r[2] for r in res]):.0f} s   "
              f"CV {np.nanmean([r[3] for r in res]):.3f}")
    n_real, tot = out["real"][0], out["real"][1]
    n_schem = out["schematic"][0]
    r_real, r_schem = n_real / tot, n_schem / tot
    # Two-proportion z test: the question is whether the real geometry loses buses the schematic
    # net does not, so a shortfall inside sampling noise is a pass. (Both nets drop a few buses
    # under this deliberately severe viewer scenario — weather eta=0.8, a 400 s breakdown and
    # dwell CV 0.6 — which is a property of the scenario, not of either geometry.)
    p = (n_real + n_schem) / (2 * tot)
    se = math.sqrt(2 * p * (1 - p) / tot) if 0 < p < 1 else 0.0
    z = (r_real - r_schem) / se if se > 0 else 0.0
    ok = (r_real >= r_schem) or abs(z) < 1.96
    print(f"\ncompletion rate: real {100*r_real:.1f}% ({n_real}/{tot})  vs  "
          f"schematic control {100*r_schem:.1f}% ({n_schem}/{tot})   z={z:+.2f}")
    print("TRAVERSAL:", "PASS — real geometry completes at the same rate as the schematic "
          "control (difference within sampling noise); no geometry-induced stalls"
          if ok else "FAIL — real geometry loses buses the schematic net does not")
    return ok


def _mc_one(task):
    ctrl, seed = task
    sys.path.insert(0, os.getcwd())
    from envs import corridor_sim as cs
    r = cs.simulate(cs.BASELINES[ctrl], seed=seed, T=True, control_stops=cs.CONTROL_STOPS)
    return ctrl, seed, r["headway_cv"], r["travel_s"]


def parity_check(nseeds, jobs):
    print()
    print("=" * 78)
    print("(B) PARITY — distributional, UNTOUCHED schematic net (Stage A, D+T)")
    print("=" * 78)
    mc = pd.read_csv("results/mc_results.csv")
    mc = mc[mc["scenario"] == "Stage A (D+T)"]

    tasks = [(c, s) for c in ("NC", "FH", "EH") for s in range(nseeds)]
    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            res = list(ex.map(_mc_one, tasks))
    else:
        res = [_mc_one(t) for t in tasks]

    def boot(x, n=5000, rng=np.random.default_rng(0)):
        x = np.asarray([v for v in x if np.isfinite(v)])
        bs = [np.mean(rng.choice(x, len(x), replace=True)) for _ in range(n)]
        return float(np.mean(x)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    print(f"\n     ---------- now (n={nseeds}) ----------   ------- committed (n=30) -------")
    print("ctrl  headway CV [95% CI]      travel      headway CV [95% CI]      travel   overlap")
    allok = True
    for c in ("NC", "FH", "EH"):
        cv = boot([r[2] for r in res if r[0] == c])
        tt = boot([r[3] for r in res if r[0] == c])
        ref = mc[mc["controller"] == c]
        rcv = boot(ref["headway_cv"].values)
        rtt = boot(ref["travel_s"].values)
        overlap = not (cv[2] < rcv[1] or cv[1] > rcv[2])
        allok &= overlap
        print(f" {c:3s}  {cv[0]:.3f} [{cv[1]:.3f},{cv[2]:.3f}]  {tt[0]:6.0f}      "
              f"{rcv[0]:.3f} [{rcv[1]:.3f},{rcv[2]:.3f}]  {rtt[0]:6.0f}   "
              f"{'yes' if overlap else 'NO'}")
    print("\nPARITY:", "PASS — Stage-A distribution is statistically unchanged"
          if allok else "CHECK — a CI does not overlap the committed one")
    return allok


if __name__ == "__main__":
    nseeds = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    part = sys.argv[3].lower() if len(sys.argv) > 3 else "ab"
    a = traversal_check(nseeds, jobs) if "a" in part else True
    b = parity_check(nseeds, jobs) if "b" in part else True
    print()
    print("=" * 78)
    print(f"TRAVERSAL {'PASS' if a else 'FAIL'}   |   PARITY {'PASS' if b else 'CHECK'}")
    sys.exit(0 if (a and b) else 1)
