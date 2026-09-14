"""
=============================================================================
 THE CORRIDOR SIMULATOR  --  one simulation loop that every controller uses
=============================================================================

WHAT IT DOES
    Runs 18 buses, one every 10 minutes, along the calibrated 27-stop Route 801
    corridor inside SUMO, with passengers, dwell times and optional
    disturbances. Every time a bus reaches a CONTROL STOP, it asks a
    "controller" what to do.

WHAT A CONTROLLER IS
    Any function that looks at the situation and answers with a hold time:

        def decide(obs):
            ...
            return hold_seconds, skip

    No-Control, Forward-Headway and Even-Headway (below) are controllers.
    The MARL agent is also a controller. Because they all run through this
    SAME loop, the comparison between them is fair.

WHAT "obs" CONTAINS  (a dictionary)
    hf     forward headway: seconds since the bus ahead arrived at this stop
    hb     backward headway: estimated gap to the bus behind (seconds)
    load   passengers on board          queue  passengers waiting at the stop
    idx    stop number (0 = first)       n      number of stops
    H0     scheduled headway (600 s)     cap    bus capacity (60)
    bus    bus number                    w      weather factor (1.0 = clear)
    b      1.0 once a breakdown has happened, else 0.0

DISTURBANCES  (switch each on with True)
    D  dwell noise      every stop takes a random bit longer or shorter
    S  demand surge     120 extra passengers appear at one stop
    T  traffic          each road segment is randomly 0.8x - 1.2x speed
    W  weather          each road segment is randomly slowed (lognormal)
    B  breakdown        one bus stops for 400 extra seconds at one stop

PASSENGERS  (from the APC data, see PART 4)
    * Each bus leaves the first stop already carrying Tech Ridge's riders.
    * Every rider gets off at a stop chosen so that, on average, the number
      getting off at each stop matches the APC alighting counts.

HOW TO USE IT
    from corridor_sim import simulate, BASELINES
    result = simulate(BASELINES["FH"], seed=0, T=True)
    print(result["headway_cv"])

    Run from the starter/ folder (it reads corridor.txt, sim_inputs/, sumo/).
    The same seed always gives the same result.

WHICH ROAD NETWORK
    Default: the real road shape, sumo/corridor_real.net.xml.
    Set the environment variable CORRIDOR_NET=schematic to use the older
    straight-line network.
=============================================================================
"""

import math
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

# SUMO's Python tools (traci, sumolib) are inside the SUMO install folder.
if "SUMO_HOME" in os.environ:
    sys.path.insert(0, os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
import sumolib
from sumolib import checkBinary


# =============================================================================
# PART 1 -- LOAD THE CORRIDOR (stops, distances, demand) FROM THE DATA FILES
# =============================================================================

# corridor.txt lists the stop ids in driving order, one per line.
STOPS = []
for line in open("corridor.txt"):
    if line.strip() != "":
        STOPS.append(line.strip())

NUM_STOPS = len(STOPS)
STOP_IDS = []
for stop in STOPS:
    STOP_IDS.append(int(stop))

# In the SUMO network, road piece "e0" leaves stop 0, "e1" leaves stop 1, ...
EDGES = []
for i in range(NUM_STOPS):
    EDGES.append("e" + str(i))

# Per-stop numbers measured from the bus data (made by extract_sim_inputs.py).
# all_stops has every direction-6 stop; stop_data is re-ordered so row i = stop i.
all_stops = pd.read_csv("sim_inputs/stops.csv").set_index("bs_id")
stop_data = all_stops.loc[STOP_IDS]
coordinates = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id").loc[STOP_IDS]

# The two terminals are not simulated as stops (buses lay over there), but
# their passengers are: Tech Ridge riders start on board, and the riders who
# would get off at the Southpark Meadows terminal get off at our last stop.
TECH_RIDGE = 5304
SOUTHPARK_MEADOWS = 5873

# Which network to use: "real" (default) or "schematic".
NET = os.environ.get("CORRIDOR_NET", "real")

# SEGMENT_LENGTH[i] = metres of road from stop i to stop i+1
SEGMENT_LENGTH = []
if NET == "real":
    NET_FILE = "sumo/corridor_real.net.xml"
    STOPS_FILE = "sumo/stops_real.add.xml"
    # Distance along the real road, from route_shape_stops.csv
    along_road = pd.read_csv("sim_inputs/route_shape_stops.csv").set_index("bs_id")
    for i in range(NUM_STOPS - 1):
        start = along_road.loc[STOP_IDS[i], "arclen_m"]
        end = along_road.loc[STOP_IDS[i + 1], "arclen_m"]
        SEGMENT_LENGTH.append(float(end - start))
elif NET == "schematic":
    NET_FILE = "sumo/corridor.net.xml"
    STOPS_FILE = "sumo/stops.add.xml"
    # Straight-line distance: turn latitude/longitude into metres, then Pythagoras.
    center_lat = coordinates["mean_lat"].mean()
    center_lon = coordinates["mean_lon"].mean()
    x_metres = ((coordinates["mean_lon"] - center_lon) * math.cos(math.radians(center_lat)) * 111320).values
    y_metres = ((coordinates["mean_lat"] - center_lat) * 110540).values
    for i in range(NUM_STOPS - 1):
        SEGMENT_LENGTH.append(math.hypot(x_metres[i + 1] - x_metres[i], y_metres[i + 1] - y_metres[i]))
else:
    raise ValueError(f"CORRIDOR_NET must be 'real' or 'schematic', not '{NET}'")

RUN_TIME = []        # RUN_TIME[i]      observed seconds of driving from stop i to i+1
SEGMENT_SPEED = []   # SEGMENT_SPEED[i] metres per second that gives that driving time
BASE_DWELL = {}      # BASE_DWELL[stop] observed seconds stopped (at least 8)
DEMAND = {}          # DEMAND[stop]     average passengers boarding per bus
ALIGHTINGS = {}      # ALIGHTINGS[stop] average passengers getting off per bus
for i in range(NUM_STOPS):
    stop = STOPS[i]
    RUN_TIME.append(float(stop_data["run_s"].values[i]))
    BASE_DWELL[stop] = max(8.0, float(stop_data["dwell_s"].values[i]))
    DEMAND[stop] = max(0.0, float(stop_data["mean_boardings"].values[i]))
    ALIGHTINGS[stop] = max(0.0, float(stop_data["mean_alightings"].values[i]))
for i in range(NUM_STOPS - 1):
    SEGMENT_SPEED.append(SEGMENT_LENGTH[i] / stop_data["run_s"].values[i])

# Average riders already on board when a bus reaches stop 0 (Tech Ridge boardings).
START_LOAD = float(all_stops.loc[TECH_RIDGE, "mean_boardings"])


# =============================================================================
# PART 2 -- SETTINGS
# =============================================================================
# Headway: the 2021 Route 801 timetable runs every 10 minutes on weekdays
# 7 AM - 6 PM (archived in data/raw/capmetro/schedule_2021/).
H0 = 600.0

# Fleet size. One trip takes about 87 minutes in the simulator (89.5 minutes
# observed, terminal to terminal), so at a 10-minute headway about
# 87 / 10 = 9 buses are on the corridor at once (observed weekday peak:
# median 10). We send out twice that, 18 buses, so the middle buses run with
# a full corridor of buses both ahead of them and behind them.
BUSES_ON_CORRIDOR = 9
NUM_BUSES = 2 * BUSES_ON_CORRIDOR

DWELL_NOISE_CV = 0.25       # D: how much dwell times vary (coefficient of variation)
MAX_HOLD_FRACTION = 0.4     # a controller may hold a bus at most 0.4 x H0 = 240 s
LONG_STOP = 600.0           # buses are told to stop "600 s"; we release them ourselves
BREAKDOWN_SECONDS = 400.0   # B: extra time the broken-down bus is stuck
WEATHER_CV = 0.8            # W: how strongly weather varies

FIXED_DWELL = 6.0           # seconds to open/close doors even with nobody boarding
SECONDS_PER_BOARDING = 4.0  # each waiting passenger adds 4 s of dwell
MAX_DWELL = 90.0            # dwell from boarding is capped at 90 s
BUS_CAPACITY = 60           # passengers
SUMO_SECONDS_PER_PERSON = 0.5   # SUMO's own time to move one person on or off a bus

# TIME_TO_REACH[i] = scheduled seconds for a bus to get from stop 0 to stop i.
# Used to start each stop's passenger arrivals when the first bus could get there.
TIME_TO_REACH = [0.0]
for i in range(1, NUM_STOPS):
    TIME_TO_REACH.append(TIME_TO_REACH[-1] + RUN_TIME[i - 1] + BASE_DWELL[STOPS[i - 1]])

SURGE_STOP = NUM_STOPS // 3                 # S: the surge happens a third of the way along
INTERIOR = list(range(1, NUM_STOPS - 1))    # every stop except the first and last

# The 5 control stops, chosen with the four criteria in manuscript section 3.2.2:
#   index 0 = the origin terminal; 1, 5, 17, 20 = where high-demand stretches begin
#   (index 9 was removed because it carries too much through traffic).
CONTROL_STOPS = [0, 1, 5, 17, 20]           # bus stop ids 5280, 5857, 5859, 5867, 4046

BUS_NAMES = []                              # "b0", "b1", ... in departure order
for b in range(NUM_BUSES):
    BUS_NAMES.append("b" + str(b))


def write_file_safely(file_name, text):
    """Write to a temporary name, then rename, so parallel runs never read half a file."""
    temporary = file_name + "." + str(os.getpid()) + ".part"
    file = open(temporary, "w")
    file.write(text)
    file.close()
    os.replace(temporary, file_name)


# The bus type. width=6 only makes buses easier to see in the GUI.
os.makedirs("sumo", exist_ok=True)
VTYPE_FILE = "sumo/vtype.add.xml"
VTYPE_TEXT = ('<additional><vType id="bus" vClass="bus" length="12" width="6" accel="1.2" '
              'decel="4.0" maxSpeed="30" personCapacity="60"/></additional>\n')
if not os.path.exists(VTYPE_FILE) or open(VTYPE_FILE).read() != VTYPE_TEXT:
    write_file_safely(VTYPE_FILE, VTYPE_TEXT)


# =============================================================================
# PART 3 -- THE THREE BASELINE CONTROLLERS
# =============================================================================
def forward_headway_hold(hf):
    """Forward-Headway rule: if the bus is closer than H0 to the bus ahead,
    hold it for the missing time (but never more than the maximum hold)."""
    if hf >= H0:
        return 0.0
    return float(min(H0 - hf, MAX_HOLD_FRACTION * H0))


def even_headway_hold(hf, hb):
    """Even-Headway rule: hold for half the difference between the gap behind
    and the gap ahead, so the bus ends up in the middle (never negative, never
    more than the maximum hold)."""
    return float(max(0.0, min(0.5 * (hb - hf), MAX_HOLD_FRACTION * H0)))


def no_control(obs):
    return 0.0, 0


def forward_headway(obs):
    return forward_headway_hold(obs["hf"]), 0


def even_headway(obs):
    return even_headway_hold(obs["hf"], obs["hb"]), 0


BASELINES = {"NC": no_control, "FH": forward_headway, "EH": even_headway}


# =============================================================================
# PART 4 -- PASSENGERS: WHERE THEY GET ON AND WHERE THEY GET OFF
# =============================================================================
# Step 1: work out, for each stop, what FRACTION of the riders on board get off.
#   Start with Tech Ridge's riders on board. At each stop:
#       fraction getting off = APC alightings / expected riders on board
#       riders on board next = riders now x (1 - fraction) + APC boardings
#   At the last stop everyone gets off (fraction = 1).
#   Done this way, the expected number getting off at each stop equals the
#   APC average, and the expected load along the corridor follows the APC data.
ALIGHT_FRACTION = {}
EXPECTED_LOAD_LEAVING = []       # expected riders on board as the bus leaves stop i
expected_load = START_LOAD
for i in range(NUM_STOPS):
    stop = STOPS[i]
    if i == NUM_STOPS - 1:
        fraction = 1.0
    elif expected_load > 0:
        fraction = min(1.0, ALIGHTINGS[stop] / expected_load)
    else:
        fraction = 0.0
    ALIGHT_FRACTION[stop] = fraction
    expected_load = expected_load * (1 - fraction)
    if i < NUM_STOPS - 1:
        expected_load = expected_load + DEMAND[stop]
    EXPECTED_LOAD_LEAVING.append(expected_load)


def destination_shares(board_index):
    """For a rider who boards at stop `board_index` (-1 = already on board at
    Tech Ridge), the chance of getting off at each later stop."""
    shares = [0.0] * NUM_STOPS
    still_on_board = 1.0
    for j in range(board_index + 1, NUM_STOPS):
        shares[j] = still_on_board * ALIGHT_FRACTION[STOPS[j]]
        still_on_board = still_on_board * (1 - ALIGHT_FRACTION[STOPS[j]])
    return shares


def split_whole_riders(total, shares):
    """Turn `total` riders and a list of shares into whole numbers per stop that
    add up to exactly `total` (round down, then hand out the leftovers to the
    biggest remainders)."""
    counts = []
    remainders = []
    for j in range(len(shares)):
        exact = total * shares[j]
        counts.append(int(math.floor(exact)))
        remainders.append((exact - math.floor(exact), -j))
    leftover = total - sum(counts)
    remainders.sort(reverse=True)
    for k in range(leftover):
        j = -remainders[k][1]
        counts[j] = counts[j] + 1
    return counts


def spread_destinations(counts):
    """Put riders' destinations in an evenly mixed order over time.

    Example: counts {stop 3: 2, stop 7: 4} -> 7, 3, 7, 7, 3, 7 (not 3, 3, 7, 7, 7, 7).
    Each rider to stop j is placed at position (m + 0.5) / count_j, then all
    riders are sorted by position.
    """
    placed = []
    for j in range(len(counts)):
        for m in range(counts[j]):
            placed.append(((m + 0.5) / counts[j], j))
    placed.sort()
    order = []
    for position, j in placed:
        order.append(j)
    return order


def riders_at_stop(name, board_index, total, begin, end):
    """`total` riders arriving evenly between `begin` and `end` at stop
    `board_index`. Returns a list of (arrival time, SUMO xml line)."""
    counts = split_whole_riders(total, destination_shares(board_index))
    destinations = spread_destinations(counts)
    spacing = (end - begin) / total
    riders = []
    for k in range(total):
        arrival = begin + k * spacing
        riders.append((arrival, f'<person id="{name}_{k}" depart="{arrival:.2f}">'
                                f'<stop busStop="{STOPS[board_index]}" duration="1"/>'
                                f'<ride busStop="{STOPS[destinations[k]]}" lines="801"/></person>'))
    return riders


def write_scenario_file(with_surge, file_name):
    """Write the SUMO file with the route, the 18 buses and all passengers."""
    timed = []          # (time, xml line); sorted by time before writing

    # The buses (one every H0 seconds). Each bus is followed by its Tech Ridge
    # riders, who are already inside it when it starts ("triggered").
    # Tech Ridge riders in total = average x number of buses, dealt to buses in turn.
    total = int(round(START_LOAD * NUM_BUSES))
    tech_ridge_destinations = spread_destinations(split_whole_riders(total, destination_shares(-1)))
    riders_of_bus = {}
    for bus in BUS_NAMES:
        riders_of_bus[bus] = []
    for k in range(total):
        bus = BUS_NAMES[k % NUM_BUSES]
        destination = STOPS[tech_ridge_destinations[k]]
        riders_of_bus[bus].append(f'<person id="tr{k}" depart="triggered">'
                                  f'<ride from="e0" busStop="{destination}" lines="{bus}"/></person>')
    for b in range(NUM_BUSES):
        bus = BUS_NAMES[b]
        text = f'<vehicle id="{bus}" type="bus" route="corr" depart="{b * H0}" line="801"/>'
        timed.append((b * H0, "\n".join([text] + riders_of_bus[bus])))

    # Riders who wait at stop i: (18 x average boardings) people, arriving
    # evenly while the buses pass.
    for i in range(NUM_STOPS - 1):
        total = int(round(NUM_BUSES * DEMAND[STOPS[i]]))
        if total > 0:
            begin = TIME_TO_REACH[i]
            end = TIME_TO_REACH[i] + H0 * (NUM_BUSES - 1)
            timed += riders_at_stop("p" + str(i), i, total, begin, end)

    # S: 120 extra riders at the surge stop over 15 minutes.
    if with_surge:
        begin = TIME_TO_REACH[SURGE_STOP] + H0
        timed += riders_at_stop("surge", SURGE_STOP, 120, begin, begin + 900)

    timed.sort(key=first_item)
    lines = ["<additional>", f'<route id="corr" edges="{" ".join(EDGES)}"/>']
    for time, text in timed:
        lines.append(text)
    lines.append("</additional>")
    file = open(file_name, "w")
    file.write("\n".join(lines))
    file.close()


def first_item(pair):
    return pair[0]


# =============================================================================
# PART 5 -- ONE SIMULATION RUN
# =============================================================================
BLUE = (0, 120, 255)      # GUI colours
GREY = (160, 160, 160)
AMBER = (255, 170, 0)
RED = (230, 40, 40)


def simulate(decide, seed=0, D=True, S=False, T=False, W=False, B=False, control_stops=None,
             eta=None, trace=False, gui=False, gui_delay=20):
    """Run the corridor once with the controller `decide`.

    seed           makes the random disturbances repeatable (same seed = same run)
    D,S,T,W,B      which disturbances are switched on (see top of file)
    control_stops  stop indexes where decide() is asked; None = all interior stops
    eta            override the weather strength (for severity sweeps)
    trace          also return every bus's arrival times (for Marey diagrams)
    gui            open the SUMO window and colour the buses (for demos)
    gui_delay      milliseconds the GUI waits per simulated second

    Returns a dictionary:
        headway_cv     bunching: spread of the gaps between buses (0 = perfectly even)
        travel_s       average seconds from first stop to last stop
        wait_s         average passenger wait, from the headway formula
        wait_direct    average passenger wait, as recorded by SUMO (cross-check)
        load_leaving   average riders on board as buses leave each stop
        rides_unfinished  riders who never reached their stop (should be 0)
    """
    if control_stops is None:
        control_stops = set(INTERIOR)
    else:
        control_stops = set(control_stops)

    random = np.random.default_rng(1000 + seed)

    if eta is None:
        weather_cv = WEATHER_CV
    else:
        weather_cv = eta

    # ---- 5a. draw all the random disturbances up front (one per bus per stop) --
    # dwell_noise[bus][stop]: multiply the dwell time by this (D)
    dwell_noise = random.lognormal(0.0, DWELL_NOISE_CV, size=(NUM_BUSES, NUM_STOPS))

    # weather_factor[bus][stop]: divide the speed on the next road piece by this (W).
    # Lognormal with average 1.0, kept between 0.5 and 3.0.
    log_variance = math.log(1 + weather_cv * weather_cv)
    weather_factor = random.lognormal(-0.5 * log_variance, math.sqrt(log_variance),
                                      size=(NUM_BUSES, NUM_STOPS))
    weather_factor = np.clip(weather_factor, 0.5, 3.0)

    # traffic_factor[bus][stop]: multiply the speed by this, 0.8 to 1.2 (T)
    traffic_factor = random.uniform(0.8, 1.2, size=(NUM_BUSES, NUM_STOPS))

    # which bus breaks down, and at which stop (B)
    breakdown_bus = int(random.integers(2, NUM_BUSES - 1))
    if B:
        breakdown_stop = int(random.integers(1, NUM_STOPS - 1))
    else:
        breakdown_stop = -1

    # ---- 5b. start SUMO ----------------------------------------------------------
    # Each run gets its own port number and file names, so several runs can
    # happen at the same time without clashing.
    port = sumolib.miscutils.getFreeSocketPort()
    tripinfo_file = f"sumo/tri_{port}.xml"
    scenario_file = f"sumo/scenario_{port}.xml"
    write_scenario_file(S, scenario_file)

    stops_file = STOPS_FILE
    command = [checkBinary("sumo"), "-n", NET_FILE]
    if gui:
        stops_file = write_coloured_stops(control_stops)
        command = [checkBinary("sumo-gui"), "-n", NET_FILE, "--start", "--delay", str(gui_delay)]
        if os.path.exists("sumo/view.settings.xml"):
            command += ["--gui-settings-file", "sumo/view.settings.xml"]
    command += ["-a", f"{VTYPE_FILE},{stops_file},{scenario_file}",
                "--tripinfo-output", tripinfo_file, "--tripinfo-output.write-unfinished", "true",
                "--no-warnings", "true", "--no-step-log", "true",
                "--seed", str(seed), "--step-length", "1", "-e", "36000"]

    load_sum = [0.0] * NUM_STOPS            # for load_leaving
    load_count = [0] * NUM_STOPS

    sumo_started = False
    try:
        traci.start(command, port=port)
        sumo_started = True
        if gui:
            zoom_to_corridor()

        # ---- 5c. bookkeeping ------------------------------------------------------
        buses_set_up = set()               # buses that have entered and got their stops
        next_stop = {}                     # bus -> index of the stop it is heading to
        was_stopped = {}                   # bus -> was it stopped in the previous second?
        arrivals_at_stop = {}              # stop -> list of bus arrival times
        for stop in STOPS:
            arrivals_at_stop[stop] = []
        arrived_at = {}                    # bus -> time it arrived at its current stop
        stop_duration = {}                 # bus -> how long it must stay at its current stop
        buses_released = set()             # buses already told to leave their current stop
        entry_time = {}                    # bus -> time it started the corridor
        finish_time = {}                   # bus -> time it reached the last stop
        arrival_time = {}                  # (bus number, stop index) -> arrival time
        breakdown_happened = False

        # ---- 5d. the main loop: one pass = one simulated second -----------------
        # NOTE: buses are always handled in the fixed order b0, b1, b2, ...
        # (never by looping over a set), so every run with the same seed is identical.
        end_time = H0 * NUM_BUSES + 30000
        t = 0.0
        while t < end_time:
            traci.simulationStep()
            t = traci.simulation.getTime()
            buses_in_sumo = set(traci.vehicle.getIDList())

            # Every bus has entered and left again: the run is over.
            if len(buses_set_up) == NUM_BUSES and len(buses_in_sumo) == 0:
                break

            for bus in BUS_NAMES:
                if bus not in buses_in_sumo:
                    continue
                bus_number = int(bus[1:])            # "b7" -> 7

                # New bus: tell it to stop at every stop. The 600 s is a
                # placeholder -- we release each bus ourselves when its time is up.
                if bus not in buses_set_up:
                    next_stop[bus] = 0
                    was_stopped[bus] = False
                    entry_time[bus] = t
                    for k in range(NUM_STOPS):
                        try:
                            traci.vehicle.setBusStop(bus, STOPS[k], duration=LONG_STOP)
                        except traci.TraCIException:
                            pass
                    if gui:
                        traci.vehicle.setColor(bus, base_colour(decide))
                    buses_set_up.add(bus)
                    continue

                is_stopped = traci.vehicle.isStopped(bus)
                i = next_stop[bus]

                # ---- (1) the bus has JUST arrived at stop i ----------------------
                if is_stopped and not was_stopped[bus] and i < NUM_STOPS:
                    stop = STOPS[i]
                    arrivals_at_stop[stop].append(t)
                    arrived_at[bus] = t
                    arrival_time[(bus_number, i)] = t
                    if i == NUM_STOPS - 1:
                        finish_time[bus] = t

                    # Dwell grows with the number of people waiting (D adds noise).
                    try:
                        waiting = traci.busstop.getPersonCount(stop)
                    except traci.TraCIException:
                        waiting = 0
                    dwell = min(MAX_DWELL, FIXED_DWELL + SECONDS_PER_BOARDING * waiting)
                    if D:
                        dwell = dwell * dwell_noise[bus_number, i]

                    # SUMO needs a little time to move riders on and off.
                    # Make sure the stop lasts long enough for that.
                    getting_off = count_riders_getting_off(bus, stop)
                    doors_time = SUMO_SECONDS_PER_PERSON * (getting_off + waiting) + 1.0

                    # At a control stop (and not the first bus), ask the controller.
                    hold = 0.0
                    if i in control_stops and bus_number > 0:
                        # forward headway: time since the bus ahead arrived here
                        if (bus_number - 1, i) in arrival_time:
                            hf = t - arrival_time[(bus_number - 1, i)]
                        else:
                            hf = H0
                        # backward headway: at the previous stop, how far behind us
                        # the next bus arrived
                        if (bus_number + 1, i - 1) in arrival_time and (bus_number, i - 1) in arrival_time:
                            hb = arrival_time[(bus_number, i - 1)] - arrival_time[(bus_number + 1, i - 1)]
                        else:
                            hb = H0
                        try:
                            load = traci.vehicle.getPersonNumber(bus)
                        except traci.TraCIException:
                            load = 0
                        if W:
                            w = float(weather_factor[bus_number, i])
                        else:
                            w = 1.0
                        if breakdown_happened:
                            b = 1.0
                        else:
                            b = 0.0

                        obs = {"hf": hf, "hb": hb, "load": load, "queue": waiting, "idx": i,
                               "n": NUM_STOPS, "H0": H0, "cap": BUS_CAPACITY,
                               "bus": bus_number, "w": w, "b": b}
                        hold, skip = decide(obs)
                        # keep the hold between 0 and the maximum allowed
                        hold = float(max(0.0, min(hold, MAX_HOLD_FRACTION * H0)))

                    # Breakdown: the chosen bus at the chosen stop is stuck longer.
                    if B and bus_number == breakdown_bus and i == breakdown_stop:
                        breakdown_delay = BREAKDOWN_SECONDS
                        breakdown_happened = True
                    else:
                        breakdown_delay = 0.0

                    if gui and breakdown_delay > 0:
                        traci.vehicle.setColor(bus, RED)
                    elif gui and hold > 0:
                        traci.vehicle.setColor(bus, AMBER)

                    stop_duration[bus] = max(FIXED_DWELL, dwell, doors_time) + hold + breakdown_delay
                    try:
                        traci.vehicle.setMaxSpeed(bus, 30.0)
                    except traci.TraCIException:
                        pass

                # ---- (2) the bus has waited long enough: release it --------------
                time_at_stop = t - arrived_at.get(bus, t)
                if is_stopped and bus not in buses_released and time_at_stop >= stop_duration.get(bus, 0):
                    if i < NUM_STOPS:
                        load_sum[i] += traci.vehicle.getPersonNumber(bus)
                        load_count[i] += 1
                    try:
                        traci.vehicle.resume(bus)
                        buses_released.add(bus)
                    except traci.TraCIException:
                        pass
                    if gui:
                        traci.vehicle.setColor(bus, base_colour(decide))
                    # Set its speed for the next road piece (slower in weather/traffic).
                    if i < len(SEGMENT_LENGTH):
                        slowdown = 1.0
                        if W:
                            slowdown = slowdown * float(weather_factor[bus_number, i])
                        if T:
                            slowdown = slowdown / float(traffic_factor[bus_number, i])
                        if slowdown != 1.0:
                            try:
                                traci.vehicle.setMaxSpeed(bus, max(2.0, SEGMENT_SPEED[i] / slowdown))
                            except traci.TraCIException:
                                pass

                # ---- (3) the bus has just driven off: aim at the next stop --------
                if not is_stopped and was_stopped[bus] and i < NUM_STOPS:
                    next_stop[bus] = i + 1
                    buses_released.discard(bus)

                was_stopped[bus] = is_stopped
    finally:
        if sumo_started:
            try:
                traci.close()
            except Exception:
                pass

    # ---- 5e. results ------------------------------------------------------------
    # Headway CV at each stop = standard deviation of the gaps / average gap.
    # Then average over stops. 0 means perfectly even buses; bigger = more bunching.
    cv_per_stop = []
    for stop in STOPS[1:]:
        if len(arrivals_at_stop[stop]) >= 3:
            gaps = np.diff(sorted(arrivals_at_stop[stop]))
            cv_per_stop.append(np.std(gaps) / np.mean(gaps))

    travel_times = []
    for bus in BUS_NAMES:
        if bus in finish_time and bus in entry_time:
            travel_times.append(finish_time[bus] - entry_time[bus])

    # Passenger wait (main measure): if people arrive at random, the average wait
    # is (average gap / 2) x (1 + CV squared). Weighted by how many board there.
    weighted_sum = 0.0
    total_weight = 0.0
    for stop in STOPS[1:]:
        gaps = np.diff(sorted(arrivals_at_stop[stop]))
        if len(gaps) >= 2 and DEMAND[stop] > 0:
            mean_gap = gaps.mean()
            cv = gaps.std() / mean_gap
            weighted_sum += DEMAND[stop] * 0.5 * mean_gap * (1 + cv * cv)
            total_weight += DEMAND[stop]

    # Passenger wait (cross-check): the waiting time SUMO recorded for each rider
    # who boarded at a stop (Tech Ridge riders never waited, so they are left out).
    recorded_waits = []
    rides_unfinished = 0
    try:
        for person in ET.parse(tripinfo_file).getroot().findall("personinfo"):
            for ride in person.findall("ride"):
                if float(ride.get("arrival", "-1")) >= 0:
                    if not person.get("id").startswith("tr"):
                        recorded_waits.append(float(ride.get("waitingTime", 0)))
                elif ride.get("vehicle", "NULL") not in ("NULL", ""):
                    rides_unfinished += 1          # boarded but never got off
    except Exception:
        pass

    # Delete this run's temporary files.
    for temporary_file in [tripinfo_file, scenario_file]:
        try:
            os.remove(temporary_file)
        except OSError:
            pass

    load_leaving = []
    for i in range(NUM_STOPS):
        if load_count[i] > 0:
            load_leaving.append(load_sum[i] / load_count[i])
        else:
            load_leaving.append(float("nan"))

    result = {
        "headway_cv": np.mean(cv_per_stop) if cv_per_stop else float("nan"),
        "travel_s": np.mean(travel_times) if travel_times else float("nan"),
        "wait_s": weighted_sum / total_weight if total_weight else float("nan"),
        "wait_direct": float(np.mean(recorded_waits)) if recorded_waits else float("nan"),
        "load_leaving": load_leaving,
        "rides_unfinished": rides_unfinished,
    }

    if trace:
        # For each bus: a sorted list of (arrival time, stop index)
        result["traj"] = {}
        for b in range(NUM_BUSES):
            visits = []
            for i in range(NUM_STOPS):
                if (b, i) in arrival_time:
                    visits.append((arrival_time[(b, i)], i))
            result["traj"][b] = sorted(visits)
        # distance (m) from the first stop to each stop
        result["cum"] = []
        for i in range(NUM_STOPS):
            result["cum"].append(sum(SEGMENT_LENGTH[:i]))

    return result


# =============================================================================
# PART 6 -- SMALL HELPERS
# =============================================================================
def count_riders_getting_off(bus, stop):
    """How many riders on this bus are heading to this stop."""
    count = 0
    try:
        for person in traci.vehicle.getPersonIDList(bus):
            if traci.person.getStage(person).destStop == stop:
                count = count + 1
    except traci.TraCIException:
        pass
    return count


def base_colour(decide):
    """Grey for No-Control, blue for any controller (GUI only)."""
    if decide is no_control:
        return GREY
    return BLUE


def write_coloured_stops(control_stops):
    """Copy the bus-stop file, colouring control stops red and others dark (GUI only).
    Stop positions are unchanged, so the GUI run behaves exactly like a normal run."""
    tree = ET.parse(STOPS_FILE)
    for index, element in enumerate(tree.getroot().findall("busStop")):
        if index in control_stops:
            element.set("color", "235,30,30")
        else:
            element.set("color", "70,90,110")
    file_name = "sumo/stops_view.add.xml"
    tree.write(file_name)
    return file_name


def zoom_to_corridor():
    """Fit the whole corridor in the GUI window."""
    try:
        margin = 400.0
        if NET == "real":
            shape = pd.read_csv("sim_inputs/route_shape.csv")
            traci.gui.setBoundary("View #0", shape["x"].min() - margin, shape["y"].min() - margin,
                                  shape["x"].max() + margin, shape["y"].max() + margin)
        else:
            traci.gui.setBoundary("View #0", -50.0, -160.0, sum(SEGMENT_LENGTH) + 560.0, 160.0)
    except Exception:
        pass


# =============================================================================
# QUICK SELF-CHECK:  python envs/corridor_sim.py   (run from starter/)
# =============================================================================
if __name__ == "__main__":
    print("controller | mean headway CV (D+T, 5 control stops, seeds 0-2)")
    for name, controller in BASELINES.items():
        cvs = []
        for s in range(3):
            cvs.append(simulate(controller, seed=s, T=True, control_stops=CONTROL_STOPS)["headway_cv"])
        rounded = []
        for c in cvs:
            rounded.append(round(float(c), 3))
        print(f"   {name:2s}      |  {np.mean(cvs):.3f}   (per-seed {rounded})")
