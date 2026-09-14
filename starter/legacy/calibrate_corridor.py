"""
=============================================================================
 CALIBRATE THE CORRIDOR  (straight-line "schematic" network)
=============================================================================

WHAT IT DOES
    1. Builds a SUMO road network from the real stop positions: one straight
       road piece between each pair of neighbouring stops.
    2. Drives ONE bus down it, stopping at every stop for the observed dwell.
    3. Measures how long the bus took between each pair of stops.
    4. Compares that with the real bus data (run_s in sim_inputs/stops.csv).
    5. Adjusts each road piece's speed limit and repeats, until they match.

WHEN IS IT "GOOD ENOUGH"  (manuscript section 3.2.3)
    * GEH < 5 on at least 85% of segments, AND
    * RMSPE < 2%

    GEH   = sqrt( 2 (simulated - observed)^2 / (simulated + observed) )
            a standard traffic-model closeness score; under 5 is a good match
    RMSPE = root-mean-square percentage error over all segments

    Note: GEH is normally used on vehicle COUNTS. Our bus counts match by
    design, so here GEH is applied to travel TIMES, and RMSPE is the main test.

INPUT    corridor.txt, sim_inputs/stop_coordinates.csv, sim_inputs/stops.csv
OUTPUT   sumo/corridor.nod.xml, .edg.xml, .net.xml, .rou.xml, .sumocfg,
         sumo/stops.add.xml, results/calibration.csv

RUN      python scripts/calibrate_corridor.py        (from starter/, ~10 s)

The real-road-shape version of this script is scripts/build_real_net.py.
=============================================================================
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

NETCONVERT = checkBinary("netconvert")   # SUMO tool that turns node/edge files into a network
SUMO = checkBinary("sumo")               # SUMO without the window

# ---- read the corridor ---------------------------------------------------------
CORRIDOR = []                            # stop ids in driving order (27 stops)
for line in open("corridor.txt"):
    if line.strip() != "":
        CORRIDOR.append(line.strip())
NUM_STOPS = len(CORRIDOR)

STOP_IDS = []
for stop in CORRIDOR:
    STOP_IDS.append(int(stop))

os.makedirs("sumo", exist_ok=True)

coordinates = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id").loc[STOP_IDS]
stop_data = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id").loc[STOP_IDS]

# ---- turn latitude/longitude into metres ----------------------------------------
# Around the corridor's centre, 1 degree of latitude  = 110,540 m and
#                                1 degree of longitude = 111,320 m x cos(latitude).
center_lat = coordinates["mean_lat"].mean()
center_lon = coordinates["mean_lon"].mean()
x_metres = ((coordinates["mean_lon"] - center_lon) * math.cos(math.radians(center_lat)) * 111320).values
y_metres = ((coordinates["mean_lat"] - center_lat) * 110540).values

# straight-line distance from each stop to the next
distance = []
for i in range(NUM_STOPS - 1):
    distance.append(math.hypot(x_metres[i + 1] - x_metres[i], y_metres[i + 1] - y_metres[i]))

observed_time = stop_data["run_s"].values[:len(distance)]   # target: real driving seconds
dwell = stop_data["dwell_s"].values                          # real seconds stopped


def write_file(name, text):
    file = open(name, "w")
    file.write(text)
    file.close()


def build_and_run(speeds):
    """Build the network with these speed limits, drive one bus, and
    return the simulated driving time for each segment."""

    # ---- nodes: points on a straight line, spaced by the real distances ----------
    positions = [0.0]
    for length in distance:
        positions.append(positions[-1] + length)
    positions.append(positions[-1] + 500)        # a 500 m road piece after the last stop

    text = "<nodes>\n"
    for i in range(len(positions)):
        text += f'  <node id="n{i}" x="{positions[i]:.1f}" y="0"/>\n'
    text += "</nodes>\n"
    write_file("sumo/corridor.nod.xml", text)

    # ---- edges: road piece e{i} goes from node i to node i+1 -------------------
    text = "<edges>\n"
    for i in range(NUM_STOPS):
        text += f'  <edge id="e{i}" from="n{i}" to="n{i+1}" numLanes="1" speed="{speeds[i]:.2f}"/>\n'
    text += "</edges>\n"
    write_file("sumo/corridor.edg.xml", text)

    # ---- netconvert joins nodes + edges into a SUMO network file ------------------
    subprocess.run([NETCONVERT, "--node-files=sumo/corridor.nod.xml",
                    "--edge-files=sumo/corridor.edg.xml",
                    "--output-file=sumo/corridor.net.xml"], check=True, capture_output=True)

    # ---- bus stops: stop i sits 5-25 m into road piece e{i} ---------------------
    text = "<additional>\n"
    for i in range(NUM_STOPS):
        text += f'  <busStop id="{CORRIDOR[i]}" lane="e{i}_0" startPos="5" endPos="25"/>\n'
    text += "</additional>\n"
    write_file("sumo/stops.add.xml", text)

    # ---- one bus that stops at every stop for the observed dwell ----------------
    stop_lines = ""
    for i in range(NUM_STOPS):
        stop_lines += f'    <stop busStop="{CORRIDOR[i]}" duration="{dwell[i]:.0f}"/>\n'
    edge_list = ""
    for i in range(NUM_STOPS):
        if i > 0:
            edge_list += " "
        edge_list += f"e{i}"
    write_file("sumo/corridor.rou.xml",
               '<routes>\n  <vType id="bus" vClass="bus" length="12" accel="1.2" decel="4.0" maxSpeed="30"/>\n'
               f'  <route id="r" edges="{edge_list}"/>\n'
               f'  <vehicle id="b0" type="bus" route="r" depart="0">\n{stop_lines}  </vehicle>\n</routes>\n')

    # ---- the SUMO configuration file (open this in sumo-gui to watch the bus) -----
    write_file("sumo/corridor.sumocfg",
               '<configuration>\n <input>\n  <net-file value="corridor.net.xml"/>\n  <route-files value="corridor.rou.xml"/>\n'
               '  <additional-files value="stops.add.xml"/>\n </input>\n <time><begin value="0"/><end value="9000"/></time>\n</configuration>\n')

    # ---- run SUMO and note when the bus stops and starts ------------------------
    traci.start([SUMO, "-c", "sumo/corridor.sumocfg", "--no-warnings", "true", "--no-step-log", "true"])
    arrive_times = []
    leave_times = []
    was_stopped = False
    t = 0
    while traci.simulation.getMinExpectedNumber() > 0 and t < 9000:
        traci.simulationStep()
        t = traci.simulation.getTime()
        if "b0" in traci.vehicle.getIDList():
            is_stopped = traci.vehicle.isStopped("b0")
        else:
            is_stopped = False
        if is_stopped and not was_stopped:
            arrive_times.append(t)             # just stopped = arrived at a stop
        if not is_stopped and was_stopped:
            leave_times.append(t)              # just started = left a stop
        was_stopped = is_stopped
    traci.close()

    # driving time of segment i = arrival at stop i+1 minus departure from stop i
    count = min(len(arrive_times) - 1, len(leave_times), len(distance))
    driving_time = []
    for i in range(count):
        driving_time.append(arrive_times[i + 1] - leave_times[i])
    return np.array(driving_time)


def main():
    # First guess: speed = distance / observed time. The last (extra) piece gets 10 m/s.
    speeds = []
    for i in range(len(distance)):
        speeds.append(distance[i] / observed_time[i])
    speeds.append(10.0)

    for iteration in range(1, 13):
        simulated = build_and_run(speeds)
        count = len(simulated)
        observed = observed_time[:count]

        geh = np.sqrt(2 * (simulated - observed) ** 2 / (simulated + observed))
        rmspe = np.sqrt(np.mean(((simulated - observed) / observed) ** 2)) * 100
        percent_geh_ok = np.mean(geh < 5) * 100
        print(f"iter {iteration}: <5:{percent_geh_ok:.0f}% RMSPE={rmspe:.2f}% GEHmax={geh.max():.2f}")

        if percent_geh_ok >= 85 and rmspe < 2.0:
            print(f"calibration criterion met (RMSPE {rmspe:.2f}%, GEH<5 on {percent_geh_ok:.0f}%) -> sumo/corridor.* is calibrated")
            rounded = []
            for value in simulated:
                rounded.append(round(value))
            print("final segment times (s):", rounded)

            os.makedirs("results", exist_ok=True)
            file = open("results/calibration.csv", "w")
            file.write("segment,observed_s,simulated_s,geh,pct_err\n")
            for i in range(count):
                percent_error = (simulated[i] - observed[i]) / observed[i] * 100
                file.write(f"{CORRIDOR[i]}-{CORRIDOR[i+1]},{observed[i]:.0f},{simulated[i]:.0f},"
                           f"{geh[i]:.2f},{percent_error:+.1f}\n")
            file.close()
            print(f"wrote results/calibration.csv (RMSPE {rmspe:.2f}%)")
            return

        # Not good enough yet: if a segment was too slow, raise its speed limit
        # in proportion (and lower it if it was too fast), then try again.
        for i in range(count):
            speeds[i] = speeds[i] * (simulated[i] / observed[i])

    print("calibration did not meet the criterion after 12 iterations")


if __name__ == "__main__":
    main()
