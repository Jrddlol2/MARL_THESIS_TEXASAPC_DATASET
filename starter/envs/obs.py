"""
=============================================================================
 WHAT A BUS SEES:  TURN THE SITUATION INTO 7 NUMBERS
=============================================================================

WHAT IT DOES
    The simulator hands over a bus's situation as labelled readings -- 480
    seconds since the bus ahead, 22 people on board, and so on. A neural
    network cannot use those directly: it behaves badly when one input is 480
    and the next is 6. So this file rescales all of them to roughly 0 to 1.

    These are the seven inputs the manuscript lists in Table 3.6:

        0  where the bus is        stop number out of 27          0 = first stop
        1  gap ahead               seconds / 600                  1.0 = on schedule
        2  gap behind              seconds / 600                  1.0 = on schedule
        3  how full it is          riders / 60 seats
        4  queue at the stop       people waiting / 20
        5  weather right now       1.0 in clear weather -> 0.2
        6  breakdown ahead         0 = no, 1 = a bus ahead has broken down

    Nothing here is learned or tuned; it is pure arithmetic, and it is the
    reason a trained policy can be dropped onto a corridor with a different
    length or headway: every input is a ratio, not a raw count.

RUN      python envs/obs.py       (prints one example vector)
=============================================================================
"""
import numpy as np

from reward import Q_REF          # 20 riders = "a normally busy stop"

OBS_DIM = 7                       # how many numbers the network expects


def featurize(readings):
    """Turn one situation into the 7 numbers the network reads."""
    headway = readings["H0"]              # 600 s, the scheduled gap
    capacity = readings["cap"]            # 60 riders
    number_of_stops = readings["n"]       # 27

    where_it_is = readings["idx"] / max(1, number_of_stops - 1)
    gap_ahead = readings["hf"] / headway
    gap_behind = readings["hb"] / headway
    how_full = readings["load"] / capacity
    queue_at_stop = readings["queue"] / Q_REF
    # The weather multiplier is 1.0 in clear conditions and rises when it is bad;
    # this shifts it onto the same 0-to-1 scale as everything else.
    weather = (readings["w"] - 0.5) / 2.5
    breakdown_ahead = readings["b"]

    return np.array([where_it_is, gap_ahead, gap_behind, how_full,
                     queue_at_stop, weather, breakdown_ahead], dtype=np.float32)


if __name__ == "__main__":
    example = dict(hf=600, hb=600, load=20, queue=5, idx=5, n=27,
                   H0=600.0, cap=60, bus=3, w=1.0, b=0.0)
    vector = featurize(example)
    print("obs vector (len %d):" % len(vector), np.round(vector, 3))
    assert len(vector) == OBS_DIM
    print("ok")
