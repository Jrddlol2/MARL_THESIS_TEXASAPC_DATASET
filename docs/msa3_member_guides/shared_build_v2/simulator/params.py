"""params.py -- Table 1 shared settings. NOTHING else lives here.

These numbers are identical for all three members (FH / EH / the third rule).
If a setting changes, it changes here and nowhere else.
Guide: Section 2, Table 1.
"""

# --- Corridor geometry ---
N_STOPS = 20                 # stops s0 .. s19, in a straight line
STOP_SPACING = 400.0         # m between consecutive stops
TAIL = 500.0                 # m of road after the last stop (buses drive off)
SPEED_LIMIT = 8.33           # m/s (= 30 km/h) everywhere
BUSSTOP_START = 5.0          # m along the stop's own edge
BUSSTOP_END = 25.0           # m along the stop's own edge

# --- Fleet ---
N_BUSES = 10                 # buses b0 .. b9
BUS_LENGTH = 12.0            # m
BUS_CAPACITY = 55            # persons (NTD 2021: CapMetro 60-ft bus, 46 seated + 9 standing)
LINE = "TEST"               # must match on buses and rides, or nobody boards

# --- Service ---
H0 = 600.0                   # scheduled headway (s)
def bus_depart(k):           # bus k leaves at 600 + k*600
    return H0 + k * H0

# --- Demand ---
ARRIVALS_PER_MIN = 1.0       # riders per minute at every stop except the last
TRIP_MIN, TRIP_MAX = 1, 8    # trip length in stops, equally likely, never past s19

# --- Dwell ---  dwell = 2 + 3*boarding + 2*alighting  (seconds)
DWELL_BASE = 2.0
DWELL_PER_BOARD = 3.0
DWELL_PER_ALIGHT = 2.0
SUMO_MOVE_PER_RIDER = 0.5    # s SUMO itself needs to move one rider on/off

# --- Control ---
CONTROL_STOPS = [0, 5, 10, 15]
HOLD_CAP = 120.0             # s (240 s only as a sensitivity case)

# --- Forward-Headway constants (kept here so the corridor is identical) ---
FH_ALPHA = 0.2
FH_SLACK = 25.0              # d-bar, typical dwell slack (s)

# --- Disturbance (E3) ---
NOISE_SPREAD = 0.10          # 10% spread on travel time, per bus per road piece

# --- Derived helpers ---
DRIVE_PER_EDGE = STOP_SPACING / SPEED_LIMIT   # ~48 s free-flow per 400 m piece
