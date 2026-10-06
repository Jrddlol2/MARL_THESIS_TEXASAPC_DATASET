"""passengers.py -- write the buses-and-riders file for one run.

Guide: Section 4, Step 2 (manuscript Sec 3.2.6 Passenger Demand, D).
write_scenario(path, seed, random_arrivals, arrivals_per_min) writes a SUMO
routes file with: one route over e0..e19, the 10 buses (each stopped at every
stop for a very long time so Python releases them), and every rider.

Riders:
  random mode -- Poisson arrivals (exponential gaps, mean 60 s), destination a
                 random 1..8 stops downstream, never past s19.
  clean  mode -- one rider exactly every 60 s, trip lengths cycle 1,2,..8,1,2..
Everything is written sorted by time, as SUMO requires.
"""
import os
import json
import numpy as np
from seeds import stream
import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
TT_FILE = os.path.join(HERE, "net", "tt.json")


def typical_times():
    """Typical time from leaving s0 to arriving at stop i (20 numbers).

    Prefer the measured values written by run.measure_tt(); fall back to a
    rough analytic estimate (free-flow drive + a typical dwell) so the very
    first bootstrap scenario can still be written.
    """
    if os.path.exists(TT_FILE):
        return np.array(json.load(open(TT_FILE)), dtype=float)
    typ_dwell = P.DWELL_BASE + P.DWELL_PER_BOARD * 9 + P.DWELL_PER_ALIGHT * 9
    return np.array([i * (P.DRIVE_PER_EDGE + typ_dwell) for i in range(P.N_STOPS)])


def _bus_elements():
    """10 buses, each with a long stop at every bus stop (Python releases them)."""
    out = []
    edges = " ".join(f"e{i}" for i in range(P.N_STOPS))
    for k in range(P.N_BUSES):
        depart = P.bus_depart(k)
        stops = "".join(
            f'<stop busStop="s{i}" duration="100000"/>' for i in range(P.N_STOPS)
        )
        out.append((depart,
                    f'<vehicle id="b{k}" type="bus" line="{P.LINE}" depart="{depart:.2f}">'
                    f'<route edges="{edges}"/>{stops}</vehicle>'))
    return out


def _rider_times_random(rng, tt):
    """For each origin stop, a list of (arrival_time, dest_stop)."""
    riders = []
    first_due = P.bus_depart(0)                 # b0 departs s0 at t=600
    last_due = P.bus_depart(P.N_BUSES - 1)      # b9 departs s0 at t=6000
    mean_gap = 60.0 / P.ARRIVALS_PER_MIN
    for i in range(P.N_STOPS - 1):              # no demand at the last stop
        # window: one headway before the first bus is due at i, until the last
        # bus is due at i.  "due at i" = depart_from_s0 + typical time to reach i
        t_start = first_due + tt[i] - P.H0
        t_end = last_due + tt[i]
        t = t_start + rng.exponential(mean_gap)
        while t <= t_end:
            span = min(P.TRIP_MAX, P.N_STOPS - 1 - i)
            dest = i + int(rng.integers(P.TRIP_MIN, span + 1))
            riders.append((t, i, dest))
            t += rng.exponential(mean_gap)
    return riders


# Clean-mode trip lengths, one value per 60 s slot within a 600 s headway.
# Period = 10 (riders per bus per stop), so EVERY bus picks up an identical set
# of trip lengths -> identical dwell -> headways stay exactly 600 s (CV -> 0).
CLEAN_PATTERN = [1, 2, 3, 4, 5, 6, 7, 8, 4, 5]


def _rider_times_clean(tt):
    """Deterministic, periodic with the headway: one rider every 60 s per stop."""
    riders = []
    first_due = P.bus_depart(0)
    last_due = P.bus_depart(P.N_BUSES - 1)
    gap = 60.0 / P.ARRIVALS_PER_MIN
    for i in range(P.N_STOPS - 1):
        t_start = first_due + tt[i] - P.H0
        t_end = last_due + tt[i]
        span = min(P.TRIP_MAX, P.N_STOPS - 1 - i)
        slot = 0
        t = t_start + gap
        while t <= t_end:
            length = min(CLEAN_PATTERN[slot % len(CLEAN_PATTERN)], span)
            slot += 1
            riders.append((t, i, i + length))
            t += gap
    return riders


def write_scenario(path, seed=0, random_arrivals=True, arrivals_per_min=None):
    if arrivals_per_min is not None:
        P.ARRIVALS_PER_MIN = arrivals_per_min
    tt = typical_times()
    rng = stream(seed, "riders")      # v2: own stream (seeds.py)

    if random_arrivals:
        riders = _rider_times_random(rng, tt)
    else:
        riders = _rider_times_clean(tt)

    # Build timed elements (buses + persons) and sort them all by depart time.
    timed = list(_bus_elements())
    for n, (t, org, dest) in enumerate(sorted(riders)):
        timed.append((t,
                      f'<person id="p{n}" depart="{t:.2f}">'
                      f'<stop busStop="s{org}" duration="1.00"/>'
                      f'<ride from="e{org}" busStop="s{dest}" lines="{P.LINE}"/>'
                      f'</person>'))
    timed.sort(key=lambda e: e[0])

    with open(path, "w") as f:
        f.write('<routes>\n')
        for _, el in timed:
            f.write("    " + el + "\n")
        f.write('</routes>\n')
    return len(riders)


if __name__ == "__main__":
    n0 = write_scenario("net/_tmp_seed0.rou.xml", seed=0)
    n1 = write_scenario("net/_tmp_seed1.rou.xml", seed=1)
    print("seed0 riders:", n0, " seed1 riders:", n1)
    import filecmp
    write_scenario("net/_tmp_seed0b.rou.xml", seed=0)
    print("seed 0 reproducible:", filecmp.cmp("net/_tmp_seed0.rou.xml",
                                              "net/_tmp_seed0b.rou.xml"))
