"""Build + calibrate the REAL-GEOMETRY viewer net (sumo/corridor_real.*) from route_shape.csv.

VIEWER ONLY — this script never writes sumo/corridor.net.xml, sumo/corridor.rou.xml,
sumo/corridor.sumocfg, sumo/stops.add.xml or results/calibration.csv. The calibrated schematic
net that produces every committed result is left byte-identical; run_baseline.py, mc.py and
envs/corridor_sim.py keep using it.

Geometry
--------
Node n{i} sits at stop i's foot-of-perpendicular ON the route polyline (<=15 m from the raw
stop coordinate, which is itself an average of APC GPS fixes). Putting the node on the line
rather than at the raw coordinate makes the node and the edge shape coincide exactly, so the
road runs straight THROUGH each junction instead of kinking by up to 15 m — this is what stops
buses stalling on sharp junction angles.

Edge e{i} runs n{i} -> n{i+1} carrying `shape` = the real route vertices between the two stops,
so SUMO derives edge length = along-route distance. Edge e25 (past the last stop) is a 500 m
stub extrapolated along the final bearing, matching the schematic net's trailing edge; no stop
or metric depends on it.

Calibration
-----------
Same loop and acceptance test as scripts/calibrate_corridor.py (GEH < 5 on > 85% of segments and
RMSPE < 2%), against the same empirical run_s targets; writes results/calibration_real.csv.

Usage:  python scripts/build_real_net.py
"""
import math
import os
import subprocess
import sys

import numpy as np
import pandas as pd

if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
from sumolib import checkBinary

NETCONVERT, SUMO = checkBinary("netconvert"), checkBinary("sumo")
TAIL_M = 500.0          # stub past the last stop (matches the schematic net)
MAX_ITERS = 15

CORRIDOR = [l.strip() for l in open("corridor.txt") if l.strip()]
IDS = [int(s) for s in CORRIDOR]
N = len(CORRIDOR)


# ---------------------------------------------------------------- polyline helpers
def cumulative(poly):
    cum = [0.0]
    for k in range(len(poly) - 1):
        cum.append(cum[-1] + math.dist(poly[k], poly[k + 1]))
    return cum


def point_at(poly, cum, s):
    """Point at arclength s along the polyline (clamped)."""
    if s <= 0:
        return poly[0]
    if s >= cum[-1]:
        return poly[-1]
    k = max(i for i in range(len(cum)) if cum[i] <= s)
    k = min(k, len(poly) - 2)
    seg = cum[k + 1] - cum[k]
    t = 0.0 if seg == 0 else (s - cum[k]) / seg
    return (poly[k][0] + t * (poly[k + 1][0] - poly[k][0]),
            poly[k][1] + t * (poly[k + 1][1] - poly[k][1]))


def slice_between(poly, cum, s0, s1):
    """Polyline from arclength s0 to s1, endpoints included exactly."""
    out = [point_at(poly, cum, s0)]
    out += [poly[k] for k in range(len(poly)) if s0 < cum[k] < s1]
    out.append(point_at(poly, cum, s1))
    return [p for i, p in enumerate(out) if i == 0 or math.dist(p, out[i - 1]) > 0.01]


# ---------------------------------------------------------------- net construction
def build_net(speeds, shapes, nodes):
    with open("sumo/corridor_real.nod.xml", "w") as fh:
        fh.write("<nodes>\n")
        for i, (x, y) in enumerate(nodes):
            fh.write(f'  <node id="n{i}" x="{x:.2f}" y="{y:.2f}"/>\n')
        fh.write("</nodes>\n")

    with open("sumo/corridor_real.edg.xml", "w") as fh:
        fh.write("<edges>\n")
        for i in range(N):
            shp = " ".join(f"{x:.2f},{y:.2f}" for x, y in shapes[i])
            fh.write(f'  <edge id="e{i}" from="n{i}" to="n{i+1}" numLanes="1" '
                     f'speed="{speeds[i]:.3f}" shape="{shp}"/>\n')
        fh.write("</edges>\n")

    subprocess.run([NETCONVERT,
                    "--node-files=sumo/corridor_real.nod.xml",
                    "--edge-files=sumo/corridor_real.edg.xml",
                    "--output-file=sumo/corridor_real.net.xml",
                    "--offset.disable-normalization", "true",  # keep the projected X/Y frame
                    "--no-turnarounds", "true",
                    ], check=True, capture_output=True)


def write_scenario(dwell):
    """Stops + a single-bus route file for the calibration run (separate from the schematic's)."""
    with open("sumo/stops_real.add.xml", "w") as fh:
        fh.write("<additional>\n")
        for i in range(N):
            fh.write(f'  <busStop id="{CORRIDOR[i]}" lane="e{i}_0" startPos="5" endPos="25"/>\n')
        fh.write("</additional>\n")
    stopxml = "".join(f'    <stop busStop="{CORRIDOR[i]}" duration="{dwell[i]:.0f}"/>\n'
                      for i in range(N))
    with open("sumo/corridor_real.rou.xml", "w") as fh:
        fh.write('<routes>\n  <vType id="bus" vClass="bus" length="12" accel="1.2" '
                 'decel="4.0" maxSpeed="30"/>\n'
                 f'  <route id="r" edges="{" ".join(f"e{i}" for i in range(N))}"/>\n'
                 f'  <vehicle id="b0" type="bus" route="r" depart="0">\n{stopxml}  </vehicle>\n'
                 '</routes>\n')
    with open("sumo/corridor_real.sumocfg", "w") as fh:
        fh.write('<configuration>\n <input>\n  <net-file value="corridor_real.net.xml"/>\n'
                 '  <route-files value="corridor_real.rou.xml"/>\n'
                 '  <additional-files value="stops_real.add.xml"/>\n </input>\n'
                 ' <time><begin value="0"/><end value="9000"/></time>\n</configuration>\n')


def run_once():
    """Single-bus traversal; returns measured inter-stop travel times (departure -> next arrival)."""
    traci.start([SUMO, "-c", "sumo/corridor_real.sumocfg",
                 "--no-warnings", "true", "--no-step-log", "true"])
    arr, dep, prev, t = [], [], False, 0
    while traci.simulation.getMinExpectedNumber() > 0 and t < 9000:
        traci.simulationStep()
        t = traci.simulation.getTime()
        s = traci.vehicle.isStopped("b0") if "b0" in traci.vehicle.getIDList() else False
        if s and not prev:
            arr.append(t)
        if not s and prev:
            dep.append(t)
        prev = s
    traci.close()
    return np.array([arr[i + 1] - dep[i] for i in range(min(len(arr) - 1, len(dep), N - 1))])


def main():
    os.makedirs("sumo", exist_ok=True)
    shape_df = pd.read_csv("sim_inputs/route_shape.csv")
    poly = list(zip(shape_df["x"].values, shape_df["y"].values))
    cum = cumulative(poly)
    arc = pd.read_csv("sim_inputs/route_shape_stops.csv").set_index("bs_id")
    si = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id").loc[IDS]

    s_at = [float(arc.loc[i, "arclen_m"]) for i in IDS]
    nodes = [point_at(poly, cum, s) for s in s_at]
    # trailing stub: extrapolate the final bearing TAIL_M past the last stop
    ex, ey = poly[-1]
    px, py = point_at(poly, cum, max(0.0, cum[-1] - 50.0))
    bl = math.hypot(ex - px, ey - py) or 1.0
    nodes.append((ex + TAIL_M * (ex - px) / bl, ey + TAIL_M * (ey - py) / bl))

    shapes = [slice_between(poly, cum, s_at[i], s_at[i + 1]) for i in range(N - 1)]
    shapes.append([nodes[N - 1], nodes[N]])          # e25 stub

    dist = [s_at[i + 1] - s_at[i] for i in range(N - 1)]
    target = si["run_s"].values[:len(dist)]
    dwell = si["dwell_s"].values
    straight = sum(math.dist(nodes[i], nodes[i + 1]) for i in range(N - 1))
    print(f"corridor: {N} stops, along-route {sum(dist)/1000:.2f} km vs straight-line "
          f"{straight/1000:.2f} km ({100*(sum(dist)/straight - 1):+.1f}% — the real road's curvature)")
    print(f"route polyline: {len(poly)} points; edge shapes carry "
          f"{sum(len(s) for s in shapes)} vertices total")

    write_scenario(dwell)
    speeds = [dist[i] / target[i] for i in range(len(dist))] + [10.0]

    for it in range(1, MAX_ITERS + 1):
        build_net(speeds, shapes, nodes)
        M = run_once()
        k = len(M)
        C = target[:k]
        geh = np.sqrt(2 * (M - C) ** 2 / (M + C))
        rmspe = np.sqrt(np.mean(((M - C) / C) ** 2)) * 100
        ok = np.mean(geh < 5) * 100
        print(f"iter {it}: GEH<5 on {ok:.0f}%  RMSPE={rmspe:.2f}%  GEHmax={geh.max():.2f}")
        if ok >= 85 and rmspe < 2.0:
            print(f"\ncalibration met on the REAL-GEOMETRY net "
                  f"(RMSPE {rmspe:.2f}%, GEH<5 on {ok:.0f}% of {k} segments)")
            os.makedirs("results", exist_ok=True)
            with open("results/calibration_real.csv", "w") as fh:
                fh.write("segment,length_m,observed_s,simulated_s,geh,pct_err\n")
                for i in range(k):
                    fh.write(f"{CORRIDOR[i]}-{CORRIDOR[i+1]},{dist[i]:.1f},{C[i]:.0f},"
                             f"{M[i]:.0f},{geh[i]:.2f},{(M[i]-C[i])/C[i]*100:+.1f}\n")
            print("wrote results/calibration_real.csv")
            print("wrote sumo/corridor_real.{nod,edg,net,rou,sumocfg}.xml + sumo/stops_real.add.xml")
            return
        for i in range(k):
            speeds[i] *= M[i] / C[i]

    sys.exit("calibration did not converge on the real-geometry net")


if __name__ == "__main__":
    main()
