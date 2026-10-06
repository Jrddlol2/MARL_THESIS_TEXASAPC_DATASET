"""run.py -- simulate() runs SUMO once and returns the measurements.

Guide: Section 4, Step 3 (manuscript Sec 3.2.1 TraCI, 3.2.7 Table 3.6, 3.2.9).
SUMO moves the buses; this Python loop decides when each bus may leave a stop.

The controller is passed in as `decide(obs) -> hold_seconds`.  All randomness
(rider arrivals, travel-time noise) is drawn from the seed BEFORE SUMO starts,
so every controller faces exactly the same disturbances for the same seed.
"""
import os
import json
import socket
import numpy as np
import traci
from sumolib import checkBinary

import params as P
import build_net
from passengers import write_scenario, TT_FILE
from seeds import stream

HERE = os.path.dirname(os.path.abspath(__file__))
NET_DIR = os.path.join(HERE, "net")


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _net_paths():
    net = os.path.join(NET_DIR, "corridor.net.xml")
    if not os.path.exists(net):
        return build_net.build()
    return {"net": net,
            "busstops": os.path.join(NET_DIR, "busstops.add.xml"),
            "vtype": os.path.join(NET_DIR, "vtype.add.xml")}


def _load_tt():
    if os.path.exists(TT_FILE):
        return np.array(json.load(open(TT_FILE)), dtype=float)
    typ_dwell = P.DWELL_BASE + P.DWELL_PER_BOARD * 9 + P.DWELL_PER_ALIGHT * 9
    return np.array([i * (P.DRIVE_PER_EDGE + typ_dwell) for i in range(P.N_STOPS)])


def simulate(decide, seed=0, random_arrivals=True, arrivals_per_min=1.0,
             noise=0.0, delay_bus=None, delay_stop=2, delay_s=0,
             max_hold=None, control_stops=None, label="run"):
    if max_hold is None:
        max_hold = P.HOLD_CAP
    if control_stops is None:
        control_stops = list(P.CONTROL_STOPS)
    paths = _net_paths()
    tt = _load_tt()

    # --- unique file names so parallel runs never collide ---
    tag = f"{label}_s{seed}_{os.getpid()}"
    rou = os.path.join(NET_DIR, f"_sc_{tag}.rou.xml")
    tripinfo = os.path.join(NET_DIR, f"_ti_{tag}.xml")
    write_scenario(rou, seed=seed, random_arrivals=random_arrivals,
                   arrivals_per_min=arrivals_per_min)

    # --- draw travel-time noise up front: factor per bus per road piece ---
    rng = stream(seed, "noise")      # v2: own stream (seeds.py)
    if noise > 0:
        nf = rng.lognormal(mean=0.0, sigma=noise, size=(P.N_BUSES, P.N_STOPS))
    else:
        nf = np.ones((P.N_BUSES, P.N_STOPS))

    sumo = checkBinary("sumo")
    traci.start([sumo,
                 "-n", paths["net"],
                 "-a", paths["vtype"] + "," + paths["busstops"],
                 "-r", rou,
                 "--tripinfo-output", tripinfo,
                 "--tripinfo-output.write-unfinished", "true",
                 "--step-length", "1",
                 "--seed", str(seed),
                 "--no-step-log", "true", "--no-warnings", "true"],
                port=_free_port())

    B = [f"b{k}" for k in range(P.N_BUSES)]
    target = {b: 0 for b in B}            # next stop this bus heads to
    was_stopped = {b: False for b in B}
    release = {b: 0.0 for b in B}         # time this bus may leave
    arrive = {b: {} for b in B}           # arrive[b][stop] = time
    depart = {b: {} for b in B}           # depart[b][stop] = time
    hold_at = {b: {} for b in B}          # hold[b][stop] = seconds
    last_arr_t = [None] * P.N_STOPS       # last time ANY bus arrived at stop i
    foll_last_stop = {b: None for b in B}  # follower tracking
    foll_last_t = {b: None for b in B}
    appeared = set()
    hold_total = 0.0
    # v2: who was on each bus when it last left a stop. SUMO boards and drops
    # riders in the same second the bus stops, before we can count them, so on
    # arrival we compare with this set to find riders SUMO already moved.
    riders_at_departure = {b: set() for b in B}

    step = 0
    MAX_STEPS = 200000
    while step < MAX_STEPS:
        traci.simulationStep()
        now = traci.simulation.getTime()
        present = set(traci.vehicle.getIDList())
        appeared |= (present & set(B))

        for k, b in enumerate(B):
            if b not in present:
                continue
            stopped = traci.vehicle.isStopped(b)

            # --- just arrived at a stop ---
            if stopped and not was_stopped[b]:
                st = target[b]
                arrive[b][st] = now
                foll_last_stop[b], foll_last_t[b] = st, now

                riders_now = set(traci.vehicle.getPersonIDList(b))
                boarded_already = len(riders_now - riders_at_departure[b])
                alighted_already = len(riders_at_departure[b] - riders_now)
                waiting = traci.busstop.getPersonCount(f"s{st}")
                boarding = waiting + boarded_already          # v2: all riders counted
                alighting = alighted_already
                for pid in traci.vehicle.getPersonIDList(b):
                    try:
                        if traci.person.getStage(pid).destStop == f"s{st}":
                            alighting += 1
                    except traci.TraCIException:
                        pass

                dwell = (P.DWELL_BASE + P.DWELL_PER_BOARD * boarding
                         + P.DWELL_PER_ALIGHT * alighting)
                if delay_bus is not None and k == delay_bus and st == delay_stop:
                    dwell += delay_s
                need = P.SUMO_MOVE_PER_RIDER * (boarding + alighting) + 1.0   # (as v1)
                dwell = max(dwell, need)

                hold = 0.0
                if st in control_stops and k > 0:        # b0 has nobody ahead
                    hf = (now - last_arr_t[st]) if last_arr_t[st] is not None else P.H0
                    hb = _estimate_hb(k, st, now, tt, foll_last_stop, foll_last_t)
                    obs = {"hf": hf, "hb": hb, "stop": st, "H0": P.H0,
                           "max_hold": max_hold,
                           "load": traci.vehicle.getPersonNumber(b),
                           "queue": boarding}
                    hold = decide(obs)
                    hold = max(0.0, min(hold, max_hold))

                hold_at[b][st] = hold
                hold_total += hold
                release[b] = now + dwell + hold
                last_arr_t[st] = now

            # --- time is up: release the bus ---
            if stopped and now >= release[b] and target[b] in arrive[b] \
                    and target[b] not in depart[b]:
                traci.vehicle.resume(b)
                st = target[b]
                # set speed for the next road piece: drive takes normal * nf
                traci.vehicle.setSpeedFactor(b, 1.0 / nf[k][st])

            # --- just left the stop ---
            if (not stopped) and was_stopped[b]:
                st = target[b]
                depart[b][st] = now
                target[b] = st + 1
                riders_at_departure[b] = set(traci.vehicle.getPersonIDList(b))

            was_stopped[b] = stopped

        # stop when all buses have appeared and none remain
        if len(appeared) == P.N_BUSES and not (present & set(B)):
            break
        step += 1

    traci.close()

    res = _measure(arrive, depart, hold_at, hold_total, tripinfo)
    try:
        os.remove(rou); os.remove(tripinfo)
    except OSError:
        pass
    return res


def _estimate_hb(k, st, now, tt, foll_last_stop, foll_last_t):
    """Estimated backward headway for bus b_k arriving at stop st."""
    if k == P.N_BUSES - 1:
        return P.H0                                   # last bus has no follower
    f = f"b{k + 1}"
    if foll_last_stop[f] is not None:
        frm = foll_last_stop[f]
        eta = foll_last_t[f] + (tt[st] - tt[frm])     # typical time from->here
    else:
        eta = P.bus_depart(k + 1) + tt[st]            # follower not started yet
    return eta - now


def _measure(arrive, depart, hold_at, hold_total, tripinfo):
    import xml.etree.ElementTree as ET

    # headway CV (v2): ONE standard deviation / mean over all gaps at stops
    # 1..19 pooled together (manuscript Eq. 3.15). The v1 value (a CV per stop,
    # then averaged) is kept as cv_stop_mean for comparison with MSA 2.
    cvs, all_gaps = [], []
    for st in range(1, P.N_STOPS):
        times = sorted(arrive[b][st] for b in arrive if st in arrive[b])
        if len(times) >= 3:
            gaps = np.diff(times)
            all_gaps.extend(gaps)
            if gaps.mean() > 0:
                cvs.append(gaps.std() / gaps.mean())
    cv = float(np.std(all_gaps) / np.mean(all_gaps)) if all_gaps else float("nan")
    cv_stop_mean = float(np.mean(cvs)) if cvs else float("nan")

    # travel time: arrive at s19 - depart from s0, averaged over buses
    tr = [arrive[b][P.N_STOPS - 1] - depart[b][0]
          for b in arrive
          if (P.N_STOPS - 1) in arrive[b] and 0 in depart[b]]
    travel_s = float(np.mean(tr)) if tr else float("nan")

    # waiting time + unfinished from the trip-info person records
    waits, unfinished = [], 0
    if os.path.exists(tripinfo):
        for pi in ET.parse(tripinfo).getroot().iter("personinfo"):
            for ride in pi.iter("ride"):
                arr = float(ride.get("arrival", "-1"))
                if arr < 0:
                    unfinished += 1
                else:
                    waits.append(float(ride.get("waitingTime", "0")))
    wait_s = float(np.mean(waits)) if waits else float("nan")

    records = []
    for b in sorted(arrive, key=lambda x: int(x[1:])):
        for st in sorted(arrive[b]):
            records.append({"bus": b, "stop": st,
                            "arrive_s": round(arrive[b][st], 2),
                            "depart_s": round(depart[b].get(st, float("nan")), 2),
                            "hold_s": round(hold_at[b].get(st, 0.0), 2)})

    return {"cv": cv, "cv_stop_mean": cv_stop_mean, "wait_s": wait_s, "hold_total_s": round(hold_total, 2),
            "travel_s": travel_s, "unfinished": unfinished, "records": records}


def measure_tt(save=True):
    """Run clean-mode NC once, measure mean time from s0 to each stop, save it."""
    from controllers import no_control
    res = simulate(no_control, seed=0, random_arrivals=False, noise=0.0,
                   label="tt")
    arr = {r["stop"]: [] for r in res["records"]}
    dep0 = {}
    for r in res["records"]:
        if r["stop"] == 0:
            dep0[r["bus"]] = r["depart_s"]
    for r in res["records"]:
        if r["bus"] in dep0 and not np.isnan(r["depart_s"]):
            arr[r["stop"]].append(r["arrive_s"] - dep0[r["bus"]])
    tt = [float(np.mean(arr[i])) if arr.get(i) else 0.0 for i in range(P.N_STOPS)]
    tt[0] = 0.0
    if save:
        json.dump(tt, open(TT_FILE, "w"))
        print("measured typical times (s):",
              [round(x) for x in tt])
    return tt


if __name__ == "__main__":
    from controllers import no_control, decide
    _net_paths()
    measure_tt()
    r = simulate(no_control, seed=0, random_arrivals=False, noise=0.0, label="smoke")
    print("NC clean:  cv=%.4f  wait=%.0f  travel=%.0f  riders_unfinished=%d"
          % (r["cv"], r["wait_s"], r["travel_s"], r["unfinished"]))
