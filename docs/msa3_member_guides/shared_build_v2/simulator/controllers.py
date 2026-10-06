"""controllers.py -- the holding rules. The checker imports decide() by name.

Guide: Section 5 (manuscript Sec 3.2.8, Eq. 3.13).
Even-Headway (EH):  T_EH = max{ min[ (hb - hf)/2 , h_max ] , 0 }
  hf = seconds since the bus ahead arrived at this stop   (obs['hf'])
  hb = estimated seconds until the bus behind reaches here (obs['hb'])
Hold the bus until it sits in the middle between the gap ahead and behind.
"""


def decide(obs):
    """Even-Headway holding, in seconds, clipped to [0, max_hold]."""
    hold = 0.5 * (obs["hb"] - obs["hf"])
    cap = obs["max_hold"]
    if hold < 0.0:
        hold = 0.0
    elif hold > cap:
        hold = cap
    return hold


def no_control(obs):
    """NC baseline: never hold. Used for the E3 comparison."""
    return 0.0
