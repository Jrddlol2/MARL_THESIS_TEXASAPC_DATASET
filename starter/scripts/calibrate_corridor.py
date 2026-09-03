"""First SUMO calibration pass for the reduced corridor.

Builds a SUMO net from real stop coordinates (geometry), sets dwells from real medians,
and iterates edge speeds until simulated segment travel times match the empirical run_s
targets. Acceptance: GEH < 5 on > 85% of segments (methods §3.2.3), reported with RMSPE.

NOTE ON GEH: methods define GEH on hourly bus VOLUME; when buses are injected at the
observed frequency, volume matches by construction. Here GEH is applied to segment TRAVEL
TIMES as a closeness statistic, paired with RMSPE (which is the binding travel-time metric).
"""
import os, sys, subprocess, math
import numpy as np, pandas as pd
if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
from sumolib import checkBinary

NC, SUMO = checkBinary("netconvert"), checkBinary("sumo")
CORRIDOR = [l.strip() for l in open("corridor.txt") if l.strip()]   # full 26-stop dir-6 corridor
os.makedirs("sumo", exist_ok=True)

coords = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id")
si = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id")
ids = [int(x) for x in CORRIDOR]
c, d = coords.loc[ids], si.loc[ids]
lat0, lon0 = c["mean_lat"].mean(), c["mean_lon"].mean()
X = (c["mean_lon"] - lon0) * math.cos(math.radians(lat0)) * 111320
Y = (c["mean_lat"] - lat0) * 110540
xy = list(zip(X.values, Y.values))
dist = [math.hypot(xy[i+1][0]-xy[i][0], xy[i+1][1]-xy[i][1]) for i in range(len(ids)-1)]
target = d["run_s"].values[:len(dist)]
dwell = d["dwell_s"].values


def build_and_run(speeds):
    n = len(CORRIDOR)
    xs = [0.0]
    for L in dist: xs.append(xs[-1] + L)
    xs.append(xs[-1] + 500)
    open("sumo/corridor.nod.xml", "w").write("<nodes>\n" + "".join(f'  <node id="n{i}" x="{x:.1f}" y="0"/>\n' for i, x in enumerate(xs)) + "</nodes>\n")
    open("sumo/corridor.edg.xml", "w").write("<edges>\n" + "".join(f'  <edge id="e{i}" from="n{i}" to="n{i+1}" numLanes="1" speed="{speeds[i]:.2f}" width="80"/>\n' for i in range(n)) + "</edges>\n")
    subprocess.run([NC, "--node-files=sumo/corridor.nod.xml", "--edge-files=sumo/corridor.edg.xml", "--output-file=sumo/corridor.net.xml"], check=True, capture_output=True)
    open("sumo/stops.add.xml", "w").write("<additional>\n" + "".join(f'  <busStop id="{CORRIDOR[i]}" lane="e{i}_0" startPos="5" endPos="25"/>\n' for i in range(n)) + "</additional>\n")
    stopxml = "".join(f'    <stop busStop="{CORRIDOR[i]}" duration="{dwell[i]:.0f}"/>\n' for i in range(n))
    open("sumo/corridor.rou.xml", "w").write(
        '<routes>\n  <vType id="bus" vClass="bus" length="12" accel="1.2" decel="4.0" maxSpeed="30"/>\n'
        f'  <route id="r" edges="{" ".join(f"e{i}" for i in range(n))}"/>\n'
        f'  <vehicle id="b0" type="bus" route="r" depart="0">\n{stopxml}  </vehicle>\n</routes>\n')
    open("sumo/corridor.sumocfg", "w").write(
        '<configuration>\n <input>\n  <net-file value="corridor.net.xml"/>\n  <route-files value="corridor.rou.xml"/>\n'
        '  <additional-files value="stops.add.xml"/>\n </input>\n <time><begin value="0"/><end value="9000"/></time>\n</configuration>\n')
    traci.start([SUMO, "-c", "sumo/corridor.sumocfg", "--no-warnings", "true", "--no-step-log", "true"])
    arr, dep, prev, t = [], [], False, 0
    while traci.simulation.getMinExpectedNumber() > 0 and t < 9000:
        traci.simulationStep(); t = traci.simulation.getTime()
        s = traci.vehicle.isStopped("b0") if "b0" in traci.vehicle.getIDList() else False
        if s and not prev: arr.append(t)
        if not s and prev: dep.append(t)
        prev = s
    traci.close()
    return np.array([arr[i+1] - dep[i] for i in range(min(len(arr)-1, len(dep), len(dist)))])


def main():
    speeds = [dist[i] / target[i] for i in range(len(dist))] + [10.0]
    for it in range(1, 13):
        M = build_and_run(speeds); k = len(M); C = target[:k]
        geh = np.sqrt(2 * (M - C) ** 2 / (M + C))
        rmspe = np.sqrt(np.mean(((M - C) / C) ** 2)) * 100
        ok = np.mean(geh < 5) * 100
        print(f"iter {it}: <5:{ok:.0f}% RMSPE={rmspe:.2f}% GEHmax={geh.max():.2f}")
        if ok >= 85 and rmspe < 2.0:
            print(f"calibration criterion met (RMSPE {rmspe:.2f}%, GEH<5 on {ok:.0f}%) -> sumo/corridor.* is calibrated")
            print("final segment times (s):", [round(v) for v in M])
            os.makedirs("results", exist_ok=True)
            with open("results/calibration.csv", "w") as fh:
                fh.write("segment,observed_s,simulated_s,geh,pct_err\n")
                for i in range(k):
                    fh.write(f"{CORRIDOR[i]}-{CORRIDOR[i+1]},{C[i]:.0f},{M[i]:.0f},{geh[i]:.2f},{(M[i]-C[i])/C[i]*100:+.1f}\n")
            print(f"wrote results/calibration.csv (RMSPE {rmspe:.2f}%)"); return
        for i in range(k): speeds[i] *= M[i] / C[i]


if __name__ == "__main__":
    main()
