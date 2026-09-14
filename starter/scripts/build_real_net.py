"""
=============================================================================
 BUILD + CALIBRATE THE REAL-ROAD-SHAPE NETWORK  (sumo/corridor_real.*)
=============================================================================

WHAT IT DOES
    Same idea as calibrate_corridor.py, but the road pieces follow the REAL
    curves of Route 801 (from sim_inputs/route_shape.csv) instead of straight
    lines. This is the network the simulator uses by default.

    1. Place one node ON the route line at each stop.
    2. Road piece e{i} runs from stop i to stop i+1 and follows the real
       route points in between, so SUMO measures its length along the road.
       After the last stop there is an extra 500 m straight piece.
    3. Drive one bus, compare its segment times with the real data, adjust
       speed limits, repeat -- until GEH < 5 on 85% of segments and RMSPE < 2%.

    (Why nodes go ON the line: the stop coordinates are averages of GPS fixes
    and can sit up to 15 m off the road. Moving the node onto the line keeps
    the road smooth, so buses do not get stuck on sharp kinks.)

INPUT    corridor.txt, sim_inputs/route_shape.csv, sim_inputs/route_shape_stops.csv,
         sim_inputs/fitted/stop_params.csv   (from scripts/fit_variability.py)

TARGETS  Median stop-to-stop running time on weekday 07:00-18:00, using only
         CALIBRATION days (every other service day) and only records where the
         bus's next record is the next stop. The other half of the days (TEST
         days) is never used for fitting -- the script reports how well the
         calibrated corridor matches them.
OUTPUT   sumo/corridor_real.nod.xml, .edg.xml, .net.xml, .rou.xml, .sumocfg,
         sumo/stops_real.add.xml, results/calibration_real.csv

RUN      python scripts/build_real_net.py          (from starter/, ~15 s)
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

NETCONVERT = checkBinary("netconvert")
SUMO = checkBinary("sumo")
TAIL_LENGTH = 500.0        # metres of extra road after the last stop
MAX_ITERATIONS = 15

CORRIDOR = []
for line in open("corridor.txt"):
    if line.strip() != "":
        CORRIDOR.append(line.strip())
NUM_STOPS = len(CORRIDOR)

STOP_IDS = []
for stop in CORRIDOR:
    STOP_IDS.append(int(stop))


# =============================================================================
# HELPERS FOR A "POLYLINE" (a line made of many points joined together)
# =============================================================================
def distance_so_far(points):
    """distance_so_far(points)[k] = metres along the line from point 0 to point k."""
    totals = [0.0]
    for k in range(len(points) - 1):
        totals.append(totals[-1] + math.dist(points[k], points[k + 1]))
    return totals


def point_at_distance(points, totals, s):
    """The (x, y) position that is s metres along the line."""
    if s <= 0:
        return points[0]
    if s >= totals[-1]:
        return points[-1]

    # find the last point that is not past s
    k = 0
    for index in range(len(totals)):
        if totals[index] <= s:
            k = index
    k = min(k, len(points) - 2)

    # move the right fraction of the way from point k to point k+1
    piece_length = totals[k + 1] - totals[k]
    if piece_length == 0:
        fraction = 0.0
    else:
        fraction = (s - totals[k]) / piece_length
    x = points[k][0] + fraction * (points[k + 1][0] - points[k][0])
    y = points[k][1] + fraction * (points[k + 1][1] - points[k][1])
    return (x, y)


def piece_of_line(points, totals, start, end):
    """The part of the line from `start` metres to `end` metres."""
    piece = [point_at_distance(points, totals, start)]
    for k in range(len(points)):
        if start < totals[k] < end:
            piece.append(points[k])
    piece.append(point_at_distance(points, totals, end))

    # drop points that repeat the one before (closer than 1 cm)
    cleaned = []
    for index in range(len(piece)):
        if index == 0 or math.dist(piece[index], piece[index - 1]) > 0.01:
            cleaned.append(piece[index])
    return cleaned


# =============================================================================
# WRITING THE SUMO FILES
# =============================================================================
def build_network(speeds, shapes, nodes):
    """Write the node and edge files, then let netconvert make the network."""
    file = open("sumo/corridor_real.nod.xml", "w")
    file.write("<nodes>\n")
    for i in range(len(nodes)):
        x, y = nodes[i]
        file.write(f'  <node id="n{i}" x="{x:.2f}" y="{y:.2f}"/>\n')
    file.write("</nodes>\n")
    file.close()

    file = open("sumo/corridor_real.edg.xml", "w")
    file.write("<edges>\n")
    for i in range(NUM_STOPS):
        shape_text = ""
        for x, y in shapes[i]:
            if shape_text != "":
                shape_text += " "
            shape_text += f"{x:.2f},{y:.2f}"
        file.write(f'  <edge id="e{i}" from="n{i}" to="n{i+1}" numLanes="1" '
                   f'speed="{speeds[i]:.3f}" shape="{shape_text}"/>\n')
    file.write("</edges>\n")
    file.close()

    subprocess.run([NETCONVERT,
                    "--node-files=sumo/corridor_real.nod.xml",
                    "--edge-files=sumo/corridor_real.edg.xml",
                    "--output-file=sumo/corridor_real.net.xml",
                    "--offset.disable-normalization", "true",   # keep our x/y coordinates as they are
                    "--no-turnarounds", "true",
                    ], check=True, capture_output=True)


def write_stops_and_bus(dwell):
    """Bus stop file, a one-bus route file, and the SUMO config file."""
    file = open("sumo/stops_real.add.xml", "w")
    file.write("<additional>\n")
    for i in range(NUM_STOPS):
        file.write(f'  <busStop id="{CORRIDOR[i]}" lane="e{i}_0" startPos="5" endPos="25"/>\n')
    file.write("</additional>\n")
    file.close()

    stop_lines = ""
    for i in range(NUM_STOPS):
        stop_lines += f'    <stop busStop="{CORRIDOR[i]}" duration="{dwell[i]:.0f}"/>\n'
    edge_list = ""
    for i in range(NUM_STOPS):
        if i > 0:
            edge_list += " "
        edge_list += f"e{i}"

    file = open("sumo/corridor_real.rou.xml", "w")
    # speedDev="0": no hidden random speed variation from SUMO itself
    file.write('<routes>\n  <vType id="bus" vClass="bus" length="12" speedFactor="1" speedDev="0" accel="1.2" '
               'decel="4.0" maxSpeed="30"/>\n'
               f'  <route id="r" edges="{edge_list}"/>\n'
               f'  <vehicle id="b0" type="bus" route="r" depart="0">\n{stop_lines}  </vehicle>\n'
               '</routes>\n')
    file.close()

    file = open("sumo/corridor_real.sumocfg", "w")
    file.write('<configuration>\n <input>\n  <net-file value="corridor_real.net.xml"/>\n'
               '  <route-files value="corridor_real.rou.xml"/>\n'
               '  <additional-files value="stops_real.add.xml"/>\n </input>\n'
               ' <time><begin value="0"/><end value="9000"/></time>\n</configuration>\n')
    file.close()


def drive_one_bus():
    """Run SUMO with one bus; return its driving time for each segment."""
    traci.start([SUMO, "-c", "sumo/corridor_real.sumocfg",
                 "--no-warnings", "true", "--no-step-log", "true"])
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
            arrive_times.append(t)
        if not is_stopped and was_stopped:
            leave_times.append(t)
        was_stopped = is_stopped
    traci.close()

    count = min(len(arrive_times) - 1, len(leave_times), NUM_STOPS - 1)
    driving_time = []
    for i in range(count):
        driving_time.append(arrive_times[i + 1] - leave_times[i])
    return np.array(driving_time)


# =============================================================================
# MAIN
# =============================================================================
def main():
    os.makedirs("sumo", exist_ok=True)

    shape_table = pd.read_csv("sim_inputs/route_shape.csv")
    route_points = list(zip(shape_table["x"].values, shape_table["y"].values))
    route_totals = distance_so_far(route_points)
    stop_positions = pd.read_csv("sim_inputs/route_shape_stops.csv").set_index("bs_id")
    fitted = pd.read_csv("sim_inputs/fitted/stop_params.csv")
    stop_data = fitted[fitted["period"] == "ALL"].set_index("bs_id").loc[STOP_IDS]

    # ---- nodes: one on the route line at each stop ------------------------------
    metres_along = []                 # how far along the route each stop is
    for stop_id in STOP_IDS:
        metres_along.append(float(stop_positions.loc[stop_id, "arclen_m"]))

    nodes = []
    for s in metres_along:
        nodes.append(point_at_distance(route_points, route_totals, s))

    # one more node, 500 m past the end, continuing in the route's final direction
    end_x, end_y = route_points[-1]
    near_x, near_y = point_at_distance(route_points, route_totals, max(0.0, route_totals[-1] - 50.0))
    direction_length = math.hypot(end_x - near_x, end_y - near_y)
    if direction_length == 0:
        direction_length = 1.0
    nodes.append((end_x + TAIL_LENGTH * (end_x - near_x) / direction_length,
                  end_y + TAIL_LENGTH * (end_y - near_y) / direction_length))

    # ---- edge shapes: the real route points between neighbouring stops ------------
    shapes = []
    for i in range(NUM_STOPS - 1):
        shapes.append(piece_of_line(route_points, route_totals, metres_along[i], metres_along[i + 1]))
    shapes.append([nodes[NUM_STOPS - 1], nodes[NUM_STOPS]])      # the extra 500 m piece

    distance = []
    for i in range(NUM_STOPS - 1):
        distance.append(metres_along[i + 1] - metres_along[i])
    observed_time = stop_data["run_median_s"].values[:len(distance)]       # calibration days
    test_time = stop_data["run_median_test_s"].values[:len(distance)]      # held-out test days
    dwell = stop_data["dwell_median_s"].values

    straight_line = 0.0
    for i in range(NUM_STOPS - 1):
        straight_line += math.dist(nodes[i], nodes[i + 1])
    vertex_count = 0
    for shape in shapes:
        vertex_count += len(shape)
    print(f"corridor: {NUM_STOPS} stops, along-route {sum(distance)/1000:.2f} km vs straight-line "
          f"{straight_line/1000:.2f} km ({100*(sum(distance)/straight_line - 1):+.1f}% — the real road's curvature)")
    print(f"route polyline: {len(route_points)} points; edge shapes carry {vertex_count} vertices total")

    write_stops_and_bus(dwell)

    # first guess: speed = distance / observed time; 10 m/s on the extra piece
    speeds = []
    for i in range(len(distance)):
        speeds.append(distance[i] / observed_time[i])
    speeds.append(10.0)

    for iteration in range(1, MAX_ITERATIONS + 1):
        build_network(speeds, shapes, nodes)
        simulated = drive_one_bus()
        count = len(simulated)
        observed = observed_time[:count]

        geh = np.sqrt(2 * (simulated - observed) ** 2 / (simulated + observed))
        rmspe = np.sqrt(np.mean(((simulated - observed) / observed) ** 2)) * 100
        percent_geh_ok = np.mean(geh < 5) * 100
        print(f"iter {iteration}: GEH<5 on {percent_geh_ok:.0f}%  RMSPE={rmspe:.2f}%  GEHmax={geh.max():.2f}")

        if percent_geh_ok >= 85 and rmspe < 2.0:
            print(f"\ncalibration met on the REAL-GEOMETRY net "
                  f"(RMSPE {rmspe:.2f}%, GEH<5 on {percent_geh_ok:.0f}% of {count} segments)")
            # How well does the same calibrated corridor match the TEST days?
            test = test_time[:count]
            geh_test = np.sqrt(2 * (simulated - test) ** 2 / (simulated + test))
            rmspe_test = np.sqrt(np.mean(((simulated - test) / test) ** 2)) * 100
            percent_test_ok = np.mean(geh_test < 5) * 100
            print(f"held-out TEST days: GEH<5 on {percent_test_ok:.0f}%  RMSPE={rmspe_test:.2f}%  "
                  f"GEHmax={geh_test.max():.2f}")

            os.makedirs("results", exist_ok=True)
            file = open("results/calibration_real.csv", "w")
            file.write("segment,length_m,observed_s,simulated_s,geh,pct_err,observed_test_s,geh_test,pct_err_test\n")
            for i in range(count):
                percent_error = (simulated[i] - observed[i]) / observed[i] * 100
                percent_error_test = (simulated[i] - test[i]) / test[i] * 100
                file.write(f"{CORRIDOR[i]}-{CORRIDOR[i+1]},{distance[i]:.1f},{observed[i]:.0f},"
                           f"{simulated[i]:.0f},{geh[i]:.2f},{percent_error:+.1f},"
                           f"{test[i]:.0f},{geh_test[i]:.2f},{percent_error_test:+.1f}\n")
            file.close()
            print("wrote results/calibration_real.csv (calibration days + held-out test days)")
            print("wrote sumo/corridor_real.{nod,edg,net,rou,sumocfg}.xml + sumo/stops_real.add.xml")
            return

        # adjust each segment's speed limit in proportion to how far off it was
        for i in range(count):
            speeds[i] = speeds[i] * (simulated[i] / observed[i])

    sys.exit("calibration did not converge on the real-geometry net")


if __name__ == "__main__":
    main()
