"""
=============================================================================
 WATCH THE CORRIDOR LIVE IN THE SUMO WINDOW  (for demos)
=============================================================================

WHAT YOU SEE
    The SUMO-GUI window opens and 18 buses (one every 10 minutes) drive the
    real Route 801 road shape.

    This runs the REAL simulator, envs/corridor_sim.py, with the window
    switched on. The window only adds colours, so what you watch is exactly
    what the reported results measure.

    Colours:
        grey bus     No-Control (NC)
        blue bus     a controller is on (FH or EH)
        amber bus    being HELD at a control stop right now
        red bus      the broken-down bus
        red marker   one of the 5 control stops
        dark marker  an ordinary stop

HOW TO RUN  (from the starter/ folder)
    python scripts/watch.py                       EH, all disturbances
    python scripts/watch.py NC StageA             No-Control, dwell + traffic only
    python scripts/watch.py FH Weather            Forward-Headway, weather added
    python scripts/watch.py EH Breakdown 7        Even-Headway, breakdown, seed 7

    First word  (controller): NC, FH or EH
    Second word (scenario):   StageA, Surge, Weather, Breakdown or StageB
    Third word  (seed):       any whole number (default 3)

    In the SUMO window, change "Delay (ms)" to slow down or speed up.
    At the start value (20 ms) a whole run takes about 5 minutes.
    The results are printed when the run ends.
=============================================================================
"""

import os
import sys

# corridor_sim.py lives in the envs/ folder next to scripts/.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
import corridor_sim

# Scenario name -> which disturbances are on (D is always on).
SCENARIOS = {
    "StageA": {"T": True},
    "Surge": {"T": True, "S": True},
    "Weather": {"T": True, "W": True},
    "Breakdown": {"T": True, "B": True},
    "StageB": {"T": True, "S": True, "W": True, "B": True},
    # older names, still accepted so earlier notes and slides keep working
    "Baseline": {"T": True},
    "Weather+Breakdown": {"T": True, "W": True, "B": True},
}

if len(sys.argv) > 1:
    controller = sys.argv[1]
else:
    controller = "EH"
if len(sys.argv) > 2:
    scenario = sys.argv[2]
else:
    scenario = "StageB"
if len(sys.argv) > 3:
    seed = int(sys.argv[3])
else:
    seed = 3

if controller not in corridor_sim.BASELINES:
    sys.exit(f"controller must be one of {list(corridor_sim.BASELINES)}, not '{controller}'")
if scenario not in SCENARIOS:
    sys.exit(f"scenario must be one of {list(SCENARIOS)}, not '{scenario}'")

print(f"Watching: controller={controller}, scenario={scenario}, seed={seed}  (close the window to stop)")

try:
    result = corridor_sim.simulate(corridor_sim.BASELINES[controller], seed=seed,
                                   control_stops=corridor_sim.CONTROL_STOPS,
                                   gui=True, gui_delay=20, **SCENARIOS[scenario])
except corridor_sim.traci.exceptions.FatalTraCIError:
    sys.exit("The SUMO window was closed before the run finished.")

print("done.")
print(f"  headway CV  : {result['headway_cv']:.3f}   (0 = perfectly even buses)")
print(f"  travel time : {result['travel_s'] / 60:.1f} min")
print(f"  mean wait   : {result['wait_s'] / 60:.1f} min")
