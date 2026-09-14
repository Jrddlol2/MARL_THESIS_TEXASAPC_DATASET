"""
=============================================================================
 THE CORRIDOR SIMULATOR  --  one simulation loop that every controller uses
=============================================================================

WHAT IT DOES
    Runs 18 buses, scheduled every 10 minutes, along the calibrated 27-stop
    Route 801 corridor inside SUMO, with passengers, dwell times and
    disturbances. Every time a bus reaches a CONTROL STOP, it asks a
    "controller" what to do.

    Every number that describes an ordinary weekday (demand, dwell, running
    time and how much they vary) is FITTED from the APC data by
    scripts/fit_variability.py -- weekday 07:00-18:00, calibration days only.

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
    hb     backward headway: estimated seconds until the bus behind arrives
           here (from its last stop + scheduled running time, like AVL data)
    load   passengers on board          queue  passengers waiting at the stop
    idx    stop number (0 = first)       n      number of stops
    H0     scheduled headway (600 s)     cap    bus capacity (60)
    bus    bus number                    w      weather factor (1.0 = clear)
    b      1.0 once a breakdown has happened, else 0.0
    max_hold  the longest hold allowed in this run (seconds)

DISTURBANCES  (switch each on with True; D and T are on in every scenario)
    D  demand       passenger counts vary day to day (fitted: 3.8x Poisson)
                    and dwell time varies beyond boardings (fitted)
    T  travel time  running time on each segment varies (fitted, dry days),
                    and buses start their trips early or late (fitted)
    S  surge        all boarding demand x f_d, f_d ~ N(1, sigma_d^2) clipped
                    to [1, 10], sigma_d = 1 (Wang & Sun 2023, Eq. 22)
    W  weather      observed ordinary-rain slow-down (fitted) x a LABELLED
                    SYNTHETIC lognormal stress with CV eta (Patil et al.)
    B  breakdown    one bus fails at a stop and is REMOVED for the rest
                    of the run; its riders get off and wait for the next
                    bus (Guedes & Borenstein 2018; Daganzo 2009)

HOW TO USE IT
    from corridor_sim import simulate, BASELINES
    result = simulate(BASELINES["FH"], seed=0, T=True)
    print(result["headway_cv"])

    Run from the starter/ folder (it reads corridor.txt, sim_inputs/, sumo/).
    The same seed always gives the same result.

TIME OF DAY
    Default: weekday 07:00-18:00 (the 10-minute service). Set the environment
    variable CORRIDOR_PERIOD to AM (07-10), MID (10-15) or PM (15-18) to use
    that period's demand, dwell and running times instead.
=============================================================================
"""

import json
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
# PART 1 -- LOAD THE CORRIDOR AND THE FITTED PARAMETERS
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

NET_FILE = "sumo/corridor_real.net.xml"
STOPS_FILE = "sumo/stops_real.add.xml"

# The two terminals are not simulated as stops (buses lay over there), but
# their passengers are: Tech Ridge riders start on board, and riders bound for
# the Southpark Meadows terminal get off at our last stop.
TECH_RIDGE = 5304

PERIOD = os.environ.get("CORRIDOR_PERIOD", "ALL")
if PERIOD not in ("ALL", "AM", "MID", "PM"):
    raise ValueError(f"CORRIDOR_PERIOD must be ALL, AM, MID or PM, not '{PERIOD}'")

fitted = pd.read_csv("sim_inputs/fitted/stop_params.csv")
calibrated_rows = fitted[fitted["period"] == "ALL"].set_index("bs_id")   # the network was calibrated to these
period_rows = fitted[fitted["period"] == PERIOD].set_index("bs_id")
MODEL = json.load(open("sim_inputs/fitted/model_params.json"))
DISPATCH_SAMPLE = pd.read_csv("sim_inputs/fitted/dispatch_deviation.csv")["deviation_s"].values

# SEGMENT_LENGTH[i] = metres of road from stop i to stop i+1 (along the real road)
along_road = pd.read_csv("sim_inputs/route_shape_stops.csv").set_index("bs_id")
SEGMENT_LENGTH = []
for i in range(NUM_STOPS - 1):
    start = along_road.loc[STOP_IDS[i], "arclen_m"]
    end = along_road.loc[STOP_IDS[i + 1], "arclen_m"]
    SEGMENT_LENGTH.append(float(end - start))

RUN_TIME = []        # RUN_TIME[i]   median seconds driving from stop i to i+1 (this period)
RUN_SCALE = []       # RUN_SCALE[i]  this period's running time / the calibrated one
RUN_LOG_SD = []      # RUN_LOG_SD[i] how much that running time varies (T)
BASE_DWELL = {}      # BASE_DWELL[stop]  median seconds stopped
DEMAND = {}          # DEMAND[stop]      average passengers boarding per bus
ALIGHTINGS = {}      # ALIGHTINGS[stop]  average passengers getting off per bus
typical_log_sd = MODEL["run_time_log_sd_pairwise_median_over_segments"]
for i in range(NUM_STOPS):
    stop = STOPS[i]
    here = period_rows.loc[STOP_IDS[i]]
    BASE_DWELL[stop] = float(here["dwell_median_s"])
    DEMAND[stop] = float(here["mean_boardings"])
    ALIGHTINGS[stop] = float(here["mean_alightings"])
for i in range(NUM_STOPS - 1):
    run_here = float(period_rows.loc[STOP_IDS[i], "run_median_s"])
    run_calibrated = float(calibrated_rows.loc[STOP_IDS[i], "run_median_s"])
    RUN_TIME.append(run_here)
    RUN_SCALE.append(run_here / run_calibrated)
    # spread fitted from neighbouring buses (see scripts/fit_variability.py)
    log_sd = period_rows.loc[STOP_IDS[i], "run_log_sd_pairwise"]
    if pd.isna(log_sd):
        log_sd = typical_log_sd
    RUN_LOG_SD.append(float(log_sd))

# Average riders already on board when a bus reaches stop 0 (Tech Ridge boardings).
START_LOAD = float(period_rows.loc[TECH_RIDGE, "mean_boardings"])


# =============================================================================
# PART 2 -- SETTINGS
# =============================================================================
# Headway: the 2021 Route 801 timetable runs every 10 minutes on weekdays
# 7 AM - 6 PM (archived in data/raw/capmetro/schedule_2021/).
H0 = 600.0

# Fleet size. A full trip takes 89.5 minutes observed, terminal to terminal
# (the simulator's first-to-last-stop part is about 76 minutes), so at a
# 10-minute headway about 9 buses are on the route at once (observed weekday
# peak: median 10). We schedule twice that, 18 buses, so the middle buses run
# with a full corridor ahead and behind.
BUSES_ON_CORRIDOR = 9
NUM_BUSES = 2 * BUSES_ON_CORRIDOR
START_OFFSET = 1800.0       # first scheduled departure; leaves room for early starters

# Dwell model, fitted: dwell = intercept + s x boardings + s x alightings, x noise
DWELL_INTERCEPT = MODEL["dwell_model"]["intercept_s"]              # 8.1 s
SECONDS_PER_BOARDING = MODEL["dwell_model"]["seconds_per_boarding"]  # 5.0 s
SECONDS_PER_ALIGHTING = MODEL["dwell_model"]["seconds_per_alighting"]  # 2.7 s
DWELL_NOISE_LOG_SD = MODEL["dwell_model"]["noise_log_sd"]          # D
MAX_DWELL = MODEL["dwell_model"]["dwell_p95_s"]                     # 95th percentile, 94 s

# D: day-to-day demand spread. Variance / mean of daily boardings per stop.
DEMAND_DISPERSION = MODEL["demand_dispersion_var_over_mean"]       # 3.8 (1.0 = Poisson)

# W: observed ordinary-rain slow-down (1.0135) and the synthetic severe layer
RAIN_MULTIPLIER = MODEL["rain"]["rain_multiplier"]
WEATHER_CV = 0.8            # eta: strength of the LABELLED SYNTHETIC weather stress

# S: surge, Wang & Sun (2023): f_d ~ N(1, SURGE_SD^2) clipped to [1, 10]
SURGE_SD = 1.0
# T: optional extra traffic stress, Wang & Sun (2023): f_s ~ N(1, sd^2) clipped to [0.8, 1.2]
TRAFFIC_STRESS_SD = 0.0

# Longest hold: 120 s. Rodriguez et al. (2023) cap holds at 0.4 x headway,
# which at their 5-minute headway is 120 s; the other reviewed studies cap at
# 90-120 s. Using 0.4 x our 10-minute headway (240 s) would exceed every cap in
# the RRL, so 240 s is only a sensitivity check: simulate(max_hold=240).
MAX_HOLD_SECONDS = 120.0
NUM_BREAKDOWNS = 1          # B: buses removed per run (Guedes & Borenstein 2018 use 1, then 2-3)

LONG_STOP = 600.0           # buses are told to stop "600 s"; we release them ourselves
BUS_CAPACITY = 60           # passengers
SUMO_SECONDS_PER_PERSON = 0.5   # SUMO's own time to move one person on or off a bus

# TIME_TO_REACH[i] = typical seconds for a bus to get from stop 0 to stop i.
# Used to time passenger arrivals and to estimate the backward headway.
TIME_TO_REACH = [0.0]
for i in range(1, NUM_STOPS):
    TIME_TO_REACH.append(TIME_TO_REACH[-1] + RUN_TIME[i - 1] + BASE_DWELL[STOPS[i - 1]])

INTERIOR = list(range(1, NUM_STOPS - 1))    # every stop except the first and last

# The 5 control stops, chosen with the four criteria in manuscript section 3.2.2:
#   index 0 = the origin terminal; 1, 5, 17, 20 = where high-demand stretches begin
#   (index 9 was removed because it carries too much through traffic).
CONTROL_STOPS = [0, 1, 5, 17, 20]           # bus stop ids 5280, 5857, 5859, 5867, 4046

BUS_NAMES = []                              # "b0", "b1", ... in scheduled order
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
# speedDev="0": SUMO adds no hidden random speed variation of its own.
os.makedirs("sumo", exist_ok=True)
VTYPE_FILE = "sumo/vtype.add.xml"
VTYPE_TEXT = ('<additional><vType id="bus" vClass="bus" length="12" width="6" speedFactor="1" speedDev="0" '
              'accel="1.2" decel="4.0" maxSpeed="30" personCapacity="60"/></additional>\n')
if not os.path.exists(VTYPE_FILE) or open(VTYPE_FILE).read() != VTYPE_TEXT:
    write_file_safely(VTYPE_FILE, VTYPE_TEXT)


# =============================================================================
# PART 3 -- THE THREE BASELINE CONTROLLERS
# =============================================================================
def forward_headway_hold(hf, max_hold=MAX_HOLD_SECONDS):
    """Forward-Headway rule: if the bus is closer than H0 to the bus ahead,
    hold it for the missing time (but never more than the maximum hold)."""
    if hf >= H0:
        return 0.0
    return float(min(H0 - hf, max_hold))


def even_headway_hold(hf, hb, max_hold=MAX_HOLD_SECONDS):
    """Even-Headway rule: hold for half the difference between the gap behind
    and the gap ahead, so the bus ends up in the middle (never negative, never
    more than the maximum hold)."""
    return float(max(0.0, min(0.5 * (hb - hf), max_hold)))


def no_control(obs):
    return 0.0, 0


def forward_headway(obs):
    return forward_headway_hold(obs["hf"], obs["max_hold"]), 0


def even_headway(obs):
    return even_headway_hold(obs["hf"], obs["hb"], obs["max_hold"]), 0


BASELINES = {"NC": no_control, "FH": forward_headway, "EH": even_headway}


# =============================================================================
# PART 4 -- PASSENGERS: WHERE THEY GET ON AND WHERE THEY GET OFF
# =============================================================================
# For each stop, the FRACTION of riders on board who get off there.
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


def passenger_count(mean, random, stochastic):
    """How many riders arrive in this run.

    stochastic=False: exactly the average (rounded).
    stochastic=True:  a random count with the fitted day-to-day spread
                      (negative binomial: variance = DEMAND_DISPERSION x mean).
    """
    if mean <= 0:
        return 0
    if not stochastic:
        return int(round(mean))
    if DEMAND_DISPERSION <= 1.0:
        return int(random.poisson(mean))
    size = mean / (DEMAND_DISPERSION - 1.0)
    probability = 1.0 / DEMAND_DISPERSION
    return int(random.negative_binomial(size, probability))


def riders_at_stop(name, board_index, total, begin, end, random, stochastic):
    """`total` riders arriving between `begin` and `end` at stop `board_index`.
    stochastic=True: random arrival times (a Poisson process);
    stochastic=False: evenly spaced. Returns a list of (arrival time, SUMO xml)."""
    if total <= 0:
        return []
    counts = split_whole_riders(total, destination_shares(board_index))
    destinations = spread_destinations(counts)
    if stochastic:
        times = np.sort(random.uniform(begin, end, size=total))
    else:
        times = begin + np.arange(total) * (end - begin) / total
    riders = []
    for k in range(total):
        riders.append((float(times[k]), f'<person id="{name}_{k}" depart="{times[k]:.2f}">'
                                         f'<stop busStop="{STOPS[board_index]}" duration="1"/>'
                                         f'<ride busStop="{STOPS[destinations[k]]}" lines="801"/></person>'))
    return riders


def write_scenario_file(file_name, departures, surge_factor, random, stochastic):
    """Write the SUMO file with the route, the 18 buses and all passengers."""
    timed = []          # (time, xml line); sorted by time before writing

    # Tech Ridge riders: already inside a bus when it starts ("triggered"),
    # dealt to the buses in turn.
    total = passenger_count(START_LOAD * surge_factor * NUM_BUSES, random, stochastic)
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
        text = f'<vehicle id="{bus}" type="bus" route="corr" depart="{departures[b]:.0f}" line="801"/>'
        timed.append((departures[b], "\n".join([text] + riders_of_bus[bus])))

    # Riders who wait at stop i: on average (18 x mean boardings x surge factor),
    # arriving from one headway before the first scheduled bus until the last one.
    for i in range(NUM_STOPS - 1):
        mean = NUM_BUSES * DEMAND[STOPS[i]] * surge_factor
        total = passenger_count(mean, random, stochastic)
        begin = START_OFFSET + TIME_TO_REACH[i] - H0
        end = START_OFFSET + TIME_TO_REACH[i] + H0 * (NUM_BUSES - 1)
        timed += riders_at_stop("p" + str(i), i, total, begin, end, random, stochastic)

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


def simulate(decide, seed=0, D=True, S=False, T=False, W=False, B=False, control_stops=None,
             eta=None, trace=False, gui=False, gui_delay=20, max_hold=None, breakdowns=NUM_BREAKDOWNS,
             surge_sd=SURGE_SD, traffic_stress_sd=TRAFFIC_STRESS_SD):
    """Run the corridor once with the controller `decide`.

    seed           makes the random disturbances repeatable (same seed = same run)
    D,S,T,W,B      which disturbances are switched on (see top of file)
    control_stops  stop indexes where decide() is asked; None = all interior stops
    eta            strength of the synthetic weather stress (None = 0.8)
    trace          also return every bus's arrival times (for Marey diagrams)
    gui            open the SUMO window and colour the buses (for demos)
    gui_delay      milliseconds the GUI waits per simulated second
    max_hold       longest hold in seconds (None = 120 s)
    breakdowns     how many buses are removed when B is on (default 1)
    surge_sd       sigma_d of the surge factor when S is on (default 1)
    traffic_stress_sd  sigma_s of the extra traffic stress when T is on (default 0 = off)

    Returns a dictionary:
        headway_cv     bunching: spread of the gaps between buses (0 = perfectly even)
        headway_cv_by_stop  the same, for each stop (index 0 is the origin)
        travel_s       average seconds from first stop to last stop
        wait_s         average passenger wait, from the headway formula
        wait_direct    average passenger wait, as recorded by SUMO (cross-check)
        load_leaving   average riders on board as buses leave each stop
        rides_unfinished  riders who never reached their stop (should be 0)
        buses_removed     B: buses taken out of service
        riders_moved      B: riders who had to get off a broken-down bus
        riders_stranded   B: moved riders no later bus picked up (should be 0)
        surge_factor      S: the demand multiplier drawn for this run
    """
    if control_stops is None:
        control_stops = set(INTERIOR)
    else:
        control_stops = set(control_stops)
    if max_hold is None:
        max_hold = MAX_HOLD_SECONDS
    if eta is None:
        weather_cv = WEATHER_CV
    else:
        weather_cv = eta

    random = np.random.default_rng(1000 + seed)

    # ---- 5a. draw all the random disturbances up front ------------------------------
    # Everything is drawn in a fixed order before the run, so every controller
    # sees exactly the same disturbances for a given seed (a PAIRED comparison).

    # D: dwell noise, one per bus per stop (median 1, fitted spread)
    dwell_noise = random.lognormal(0.0, DWELL_NOISE_LOG_SD, size=(NUM_BUSES, NUM_STOPS))

    # T: running-time factor per bus per segment (median 1, fitted spread per segment)
    run_factor = np.exp(random.normal(0.0, 1.0, size=(NUM_BUSES, NUM_STOPS)) * (RUN_LOG_SD + [RUN_LOG_SD[-1]]))
    run_factor = np.clip(run_factor, 0.5, 2.5)
    # T: an optional episode-wide traffic stress (Wang & Sun 2023), off by default
    traffic_stress = float(np.clip(random.normal(1.0, max(traffic_stress_sd, 1e-12)), 0.8, 1.2))
    if traffic_stress_sd <= 0:
        traffic_stress = 1.0
    # T: how early or late each bus starts its trip, drawn from the observed deviations
    dispatch_draw = random.choice(DISPATCH_SAMPLE, size=NUM_BUSES)

    # W: synthetic weather stress per bus per segment, mean 1, clipped to [0.5, 3]
    if weather_cv > 0:
        log_variance = math.log(1 + weather_cv * weather_cv)
        weather_stress = random.lognormal(-0.5 * log_variance, math.sqrt(log_variance), size=(NUM_BUSES, NUM_STOPS))
        weather_stress = np.clip(weather_stress, 0.5, 3.0)
    else:
        weather_stress = np.ones((NUM_BUSES, NUM_STOPS))

    # S: one demand multiplier for the whole run
    surge_draw = random.normal(1.0, max(surge_sd, 1e-12))
    if S:
        surge_factor = float(np.clip(surge_draw, 1.0, 10.0))
    else:
        surge_factor = 1.0

    # B: which buses fail, and at which stop. breakdown_at[bus number] = stop index.
    # Never one of the first two or last two scheduled buses; never the first or last stop.
    breakdown_at = {}
    first_bus = int(random.integers(2, NUM_BUSES - 1))
    if B:
        breakdown_at[first_bus] = int(random.integers(1, NUM_STOPS - 1))
        while len(breakdown_at) < breakdowns:
            extra_bus = int(random.integers(2, NUM_BUSES - 1))
            if extra_bus not in breakdown_at:
                breakdown_at[extra_bus] = int(random.integers(1, NUM_STOPS - 1))

    # Departure times. With T on, buses start early or late as observed, so two
    # buses can even swap places -- the ORDER below is the order they actually run in.
    departures = []
    for b in range(NUM_BUSES):
        if T:
            departures.append(START_OFFSET + b * H0 + float(dispatch_draw[b]))
        else:
            departures.append(START_OFFSET + b * H0)
    running_order = sorted(range(NUM_BUSES), key=lambda b: (departures[b], b))
    position_of = {}
    for position in range(NUM_BUSES):
        position_of[running_order[position]] = position

    # ---- 5b. start SUMO ----------------------------------------------------------
    # Each run gets its own port number and file names, so several runs can
    # happen at the same time without clashing.
    port = sumolib.miscutils.getFreeSocketPort()
    tripinfo_file = f"sumo/tri_{port}.xml"
    scenario_file = f"sumo/scenario_{port}.xml"
    write_scenario_file(scenario_file, departures, surge_factor, random, stochastic=D)

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
                "--seed", str(seed), "--step-length", "1", "-e", "40000"]

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
        last_stop_reached = {}             # bus number -> (stop index, arrival time)
        removed_buses = set()              # B: bus numbers taken out of service
        riders_moved = 0                   # B: riders who had to change bus
        breakdown_happened = False

        # ---- 5d. the main loop: one pass = one simulated second -----------------
        # NOTE: buses are always handled in the fixed order b0, b1, b2, ...
        # (never by looping over a set), so every run with the same seed is identical.
        end_time = START_OFFSET + H0 * NUM_BUSES + 30000
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

                    # B: this bus breaks down here and leaves service for good.
                    # Its riders get off and wait here for the next bus.
                    if breakdown_at.get(bus_number) == i:
                        riders_moved += remove_broken_bus(bus, stop)
                        removed_buses.add(bus_number)
                        breakdown_happened = True
                        continue

                    # The bus ahead is whichever bus reached this stop last
                    # (buses cannot overtake on this one-lane corridor).
                    if len(arrivals_at_stop[stop]) > 0:
                        last_arrival_here = arrivals_at_stop[stop][-1]
                    else:
                        last_arrival_here = None
                    arrivals_at_stop[stop].append(t)
                    arrived_at[bus] = t
                    arrival_time[(bus_number, i)] = t
                    last_stop_reached[bus_number] = (i, t)
                    if i == NUM_STOPS - 1:
                        finish_time[bus] = t

                    # Dwell = intercept + seconds per boarding and per alighting (fitted),
                    # times random noise when D is on, capped at the 95th percentile.
                    try:
                        waiting = traci.busstop.getPersonCount(stop)
                    except traci.TraCIException:
                        waiting = 0
                    getting_off = count_riders_getting_off(bus, stop)
                    dwell = DWELL_INTERCEPT + SECONDS_PER_BOARDING * waiting + SECONDS_PER_ALIGHTING * getting_off
                    if D:
                        dwell = dwell * dwell_noise[bus_number, i]
                    dwell = min(MAX_DWELL, dwell)

                    # SUMO needs a little time to move riders on and off.
                    # Make sure the stop lasts long enough for that.
                    doors_time = SUMO_SECONDS_PER_PERSON * (getting_off + waiting) + 1.0

                    # At a control stop, ask the controller -- unless this is the
                    # front bus of the whole fleet (it has no bus ahead).
                    hold = 0.0
                    if i in control_stops and position_of[bus_number] > 0:
                        # forward headway: time since the bus ahead arrived here
                        if last_arrival_here is not None:
                            hf = t - last_arrival_here
                        else:
                            hf = H0
                        hb = estimate_backward_headway(bus_number, i, t, running_order, position_of,
                                                       removed_buses, last_stop_reached, departures)
                        try:
                            load = traci.vehicle.getPersonNumber(bus)
                        except traci.TraCIException:
                            load = 0
                        if W:
                            w = float(weather_stress[bus_number, i])
                        else:
                            w = 1.0
                        if breakdown_happened:
                            b = 1.0
                        else:
                            b = 0.0

                        obs = {"hf": hf, "hb": hb, "load": load, "queue": waiting, "idx": i,
                               "n": NUM_STOPS, "H0": H0, "cap": BUS_CAPACITY,
                               "bus": bus_number, "w": w, "b": b, "max_hold": max_hold}
                        hold, skip = decide(obs)
                        # keep the hold between 0 and the maximum allowed
                        hold = float(max(0.0, min(hold, max_hold)))

                    if gui and hold > 0:
                        traci.vehicle.setColor(bus, AMBER)

                    stop_duration[bus] = max(dwell, doors_time) + hold

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
                    # Running time on the next road piece: the period's typical time,
                    # x traffic variation (T), x rain and weather stress (W).
                    # A speed factor of 1/time_factor makes the drive take that long.
                    if i < NUM_STOPS - 1:
                        time_factor = RUN_SCALE[i]
                        if T:
                            time_factor = time_factor * float(run_factor[bus_number, i]) * traffic_stress
                        if W:
                            time_factor = time_factor * RAIN_MULTIPLIER * float(weather_stress[bus_number, i])
                        try:
                            traci.vehicle.setSpeedFactor(bus, 1.0 / time_factor)
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
    # Then average over stops 1..26. 0 means perfectly even buses; bigger = more bunching.
    cv_by_stop = []
    for stop in STOPS:
        if len(arrivals_at_stop[stop]) >= 3:
            gaps = np.diff(sorted(arrivals_at_stop[stop]))
            cv_by_stop.append(float(np.std(gaps) / np.mean(gaps)))
        else:
            cv_by_stop.append(float("nan"))
    cv_per_stop = []
    for value in cv_by_stop[1:]:
        if not math.isnan(value):
            cv_per_stop.append(value)

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
    # Rides on a broken-down bus did not really finish, so they are skipped too;
    # those riders' second wait (as "moved_...") is counted instead.
    removed_names = set()
    for b in removed_buses:
        removed_names.add(BUS_NAMES[b])
    recorded_waits = []
    rides_unfinished = 0
    riders_stranded = 0
    try:
        for person in ET.parse(tripinfo_file).getroot().findall("personinfo"):
            for ride in person.findall("ride"):
                vehicle = ride.get("vehicle", "NULL")
                if vehicle in removed_names:
                    continue
                if float(ride.get("arrival", "-1")) >= 0:
                    if not person.get("id").startswith("tr"):
                        recorded_waits.append(float(ride.get("waitingTime", 0)))
                elif vehicle not in ("NULL", ""):
                    rides_unfinished += 1          # boarded but never got off
                elif person.get("id").startswith("moved_"):
                    riders_stranded += 1           # a moved rider no bus picked up
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
        "headway_cv_by_stop": cv_by_stop,
        "travel_s": np.mean(travel_times) if travel_times else float("nan"),
        "wait_s": weighted_sum / total_weight if total_weight else float("nan"),
        "wait_direct": float(np.mean(recorded_waits)) if recorded_waits else float("nan"),
        "load_leaving": load_leaving,
        "rides_unfinished": rides_unfinished,
        "buses_removed": len(removed_buses),
        "riders_moved": riders_moved,
        "riders_stranded": riders_stranded,
        "surge_factor": surge_factor,
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
def estimate_backward_headway(bus_number, i, t, running_order, position_of, removed_buses,
                              last_stop_reached, departures):
    """Estimated seconds until the bus BEHIND reaches stop i.

    Like a real AVL feed: take the follower's last stop and when it got there,
    add the typical time from that stop to stop i, and subtract the time
    already passed. A follower that has not started yet is timed from its
    departure. Removed buses are skipped. No follower at all: return H0.
    """
    position = position_of[bus_number] + 1
    while position < len(running_order) and running_order[position] in removed_buses:
        position = position + 1
    if position >= len(running_order):
        return H0
    follower = running_order[position]
    if follower in last_stop_reached:
        j, time_at_j = last_stop_reached[follower]
        expected_arrival = time_at_j + (TIME_TO_REACH[i] - TIME_TO_REACH[j])
    else:
        expected_arrival = max(departures[follower], t) + TIME_TO_REACH[i]
    return float(max(0.0, expected_arrival - t))


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


def remove_broken_bus(bus, stop):
    """B: take a broken-down bus out of service at `stop`.

    Riders going to this stop just get off. Every other rider gets off, walks
    onto the stop, and waits for the next bus to their own stop -- so the bus
    behind inherits them, as the manuscript describes.
    Returns how many riders had to change bus.
    """
    riders = list(traci.vehicle.getPersonIDList(bus))
    destinations = []
    for person in riders:
        destinations.append(traci.person.getStage(person).destStop)

    traci.vehicle.remove(bus)

    stop_edge = traci.lane.getEdgeID(traci.busstop.getLaneID(stop))
    stop_position = traci.busstop.getStartPos(stop)
    moved = 0
    for k in range(len(riders)):
        if destinations[k] == stop:
            continue
        new_id = "moved_" + riders[k]
        destination_edge = traci.lane.getEdgeID(traci.busstop.getLaneID(destinations[k]))
        traci.person.add(new_id, stop_edge, stop_position + 1.0)
        # a 1-metre walk onto the stop, so SUMO counts them as waiting there
        traci.person.appendWalkingStage(new_id, [stop_edge], stop_position + 2.0, stopID=stop)
        traci.person.appendDrivingStage(new_id, destination_edge, "801", destinations[k])
        moved = moved + 1
    return moved


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
        shape = pd.read_csv("sim_inputs/route_shape.csv")
        traci.gui.setBoundary("View #0", shape["x"].min() - margin, shape["y"].min() - margin,
                              shape["x"].max() + margin, shape["y"].max() + margin)
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
