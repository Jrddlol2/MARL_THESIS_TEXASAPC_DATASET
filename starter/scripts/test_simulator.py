"""
=============================================================================
 TESTS FOR THE SIMULATOR'S CONTROL RULES
=============================================================================

WHAT IT CHECKS
    1. Forward-Headway follows Daganzo's rule (slack 25 s on headway,
       longer when close, never negative, never over the cap).
    2. Even-Headway uses the gap behind (it is not always the 600 s fallback).
    3. The skip action does nothing unless skip_enabled=True.
    4. The skip action is refused at the origin stop.
    5. The skip action is refused if the bus ahead skipped the same stop
       (so no stop is skipped by two buses in a row).
    6. A skipped stop is not served by that bus, riders bound for it are
       carried on, and nobody is left stuck on a bus.
    7. Stops are served on demand: some ordinary stops are passed, while the
       first stop, the last stop and the control stops are always served.
    8. The breakdown flag reaches only buses behind the broken-down bus, and
       the decision time t given to controllers increases for each bus.
    9. Weather is one corridor-wide slow-down: observed rain = x1.0135, heavy
       and extreme rain slow buses in proportion (FHWA 2006; FHWA Road Weather Management).
   10. The weather value a controller sees is that corridor-wide level, the
       same for every bus and every decision -- never a bus's own future draw.
   11. Bus capacity is 55 (NTD 2021 Revenue Vehicle Inventory, 60-ft artics).

RUN      python scripts/test_simulator.py        (from starter/, ~2 min)
         Prints PASS / FAIL for each check and exits with 1 if any fail.
=============================================================================
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "envs"))
import corridor_sim as C

failures = []


def check(name, condition, detail=""):
    if condition:
        print(f"PASS  {name}  {detail}")
    else:
        print(f"FAIL  {name}  {detail}")
        failures.append(name)


# 1. Daganzo Forward-Headway ----------------------------------------------------------
on_headway = C.forward_headway_hold(C.H0, 1)
too_close = C.forward_headway_hold(C.H0 / 2, 1)
too_far = C.forward_headway_hold(C.H0 * 2, 1)
very_close = C.forward_headway_hold(0, 1)
check("FH holds the slack on headway", abs(on_headway - C.DAGANZO_SLACK) < 1e-9, f"{on_headway:.1f} s")
check("FH holds longer when too close", too_close > on_headway, f"{too_close:.1f} s")
check("FH never negative", too_far == 0.0, f"{too_far:.1f} s")
check("FH never over the cap", very_close <= C.MAX_HOLD_SECONDS, f"{very_close:.1f} s")

# 2. Even-Headway sees the bus behind ---------------------------------------------------------
backward = []


def spy_even_headway(obs):
    backward.append(obs["hb"])
    return C.BASELINES["EH"](obs)


C.simulate(spy_even_headway, seed=1, T=True, control_stops=C.CONTROL_STOPS)
fallback_share = sum(1 for h in backward if h == C.H0) / len(backward)
check("EH backward headway is estimated, not the fallback", fallback_share < 0.2,
      f"{100 * fallback_share:.0f}% of {len(backward)} decisions used the fallback")

# 3-5. The skip action -------------------------------------------------------------------------


def always_skip(obs):
    return 0.0, 1


off = C.simulate(always_skip, seed=1, T=True, control_stops=C.CONTROL_STOPS, skip_enabled=False)
check("skip ignored when skip_enabled=False", off["controller_skips"] == 0, f"{off['controller_skips']} skips")

only_origin = C.simulate(always_skip, seed=1, T=True, control_stops=[0], skip_enabled=True)
check("skip refused at the origin", only_origin["controller_skips"] == 0, f"{only_origin['controller_skips']} skips")

only_stop_one = C.simulate(always_skip, seed=1, T=True, control_stops=[1], skip_enabled=True)
buses_that_could = C.NUM_BUSES - 1          # the front bus is never asked
check("no stop skipped by two buses in a row",
      0 < only_stop_one["controller_skips"] <= math.ceil(buses_that_could / 2),
      f"{only_stop_one['controller_skips']} skips of stop 2 by {buses_that_could} buses")

# 6. A single ordered skip --------------------------------------------------------------------
target_bus = 5


def skip_one_bus(obs):
    return 0.0, int(obs["bus"] == target_bus and obs["idx"] == 5)


baseline = C.simulate(C.BASELINES["NC"], seed=1, T=True, control_stops=C.CONTROL_STOPS)
one_skip = C.simulate(skip_one_bus, seed=1, T=True, control_stops=C.CONTROL_STOPS, skip_enabled=True)
check("exactly one ordered skip", one_skip["controller_skips"] == 1, f"{one_skip['controller_skips']}")
check("the skipped stop was served less", one_skip["stop_served_share"][6] <= baseline["stop_served_share"][6],
      f"stop 6 served share {one_skip['stop_served_share'][6]:.3f} vs {baseline['stop_served_share'][6]:.3f}")
check("nobody left stuck on a bus", one_skip["rides_unfinished"] == 0,
      f"{one_skip['riders_overcarried']} carried past their stop, {one_skip['rides_unfinished']} unfinished")

# 7. Stops served on demand ---------------------------------------------------------------------
served = baseline["stop_served_share"]
always = all(served[i] == 1.0 for i in C.ALWAYS_SERVED)
some_passed = any(served[i] < 1.0 for i in range(C.NUM_STOPS) if i not in C.ALWAYS_SERVED)
check("first, last and control stops always served", always)
check("some ordinary stops are passed", some_passed,
      f"lowest served share {min(served):.2f}")

# 8. Breakdown flag: only buses behind the broken-down bus see it -------------------------------
decisions = []          # (time, bus, breakdown flag) at every decision


def spy_breakdown_flag(obs):
    decisions.append((obs["t"], obs["bus"], obs["b"]))
    return 0.0, 0


# Seed 5: its breakdown happens with buses still running ahead of the broken one, so the
# "buses ahead are not flagged" check has something to look at. (Seed 3 was used until the
# 2026-09-18 weather change shifted the random draws; its breakdown now hits a bus near the front.)
broken = C.simulate(spy_breakdown_flag, seed=5, T=True, B=True, control_stops=C.CONTROL_STOPS)
flag_times = [t for t, bus, b in decisions if b == 1.0]
check("a bus was removed", broken["buses_removed"] == 1)
check("breakdown flag reaches buses behind it", len(flag_times) > 0, f"{len(flag_times)} flagged decisions")
if flag_times:
    unflagged_later = [bus for t, bus, b in decisions if t > min(flag_times) and b == 0.0]
    check("buses ahead of the breakdown are not flagged", len(unflagged_later) > 0,
          f"{len(unflagged_later)} unflagged decisions after the first flag")
switched_off = False
times_per_bus = {}
for t, bus, b in decisions:
    earlier = times_per_bus.setdefault(bus, [])
    if b == 0.0 and any(flag == 1.0 for _, flag in earlier):
        switched_off = True
    earlier.append((t, b))
check("breakdown flag never switches off for a bus", not switched_off)
check("decision time t increases for each bus",
      all([t for t, _ in rows] == sorted({t for t, _ in rows}) for rows in times_per_bus.values()))

# 9-10. Weather is one corridor-wide slow-down, and controllers see only that level ------------
seen_w = []


def spy_weather(obs):
    seen_w.append(obs["w"])
    return 0.0, 0


factors = {name: C.weather_factor_for(value) for name, value in C.WEATHER_LEVELS.items()}
check("observed rain uses the fitted multiplier", abs(factors["observed"] - C.RAIN_MULTIPLIER) < 1e-12,
      f"x{factors['observed']:.4f}")
check("heavy rain = -7.5% speed", abs(factors["heavy"] - 1 / (1 - 0.075)) < 1e-12, f"x{factors['heavy']:.4f}")
check("wet arterial = -10% speed", abs(factors["wet_arterial"] - 1 / 0.9) < 1e-12, f"x{factors['wet_arterial']:.4f}")
check("extreme wet arterial = -25% speed", abs(factors["extreme"] - 1 / 0.75) < 1e-12, f"x{factors['extreme']:.4f}")
dry = C.simulate(C.BASELINES["NC"], seed=3, T=True)
wet = C.simulate(spy_weather, seed=3, T=True, W=True, weather_slowdown=C.WEATHER_LEVELS["extreme"])
slower = wet["travel_s"] / dry["travel_s"]
check("extreme rainstorm lengthens trips", 1.15 < slower < 1.40, f"trip time x{slower:.3f}")
check("controllers see one corridor-wide weather value",
      len(set(round(v, 9) for v in seen_w)) == 1 and abs(seen_w[0] - factors["extreme"]) < 1e-9,
      f"{len(seen_w)} decisions, values {sorted(set(round(v, 4) for v in seen_w))}")
seen_w.clear()
C.simulate(spy_weather, seed=3, T=True)
check("weather value is 1.0 when W is off", set(seen_w) == {1.0}, f"{sorted(set(seen_w))}")

# 11. Capacity --------------------------------------------------------------------------------
check("bus capacity is 55 (NTD 2021)", C.BUS_CAPACITY == 55, f"{C.BUS_CAPACITY}")
check("SUMO bus type uses the same capacity", f'personCapacity="{C.BUS_CAPACITY}"' in C.VTYPE_TEXT)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED: {failures}")
    sys.exit(1)
print("all checks passed")
