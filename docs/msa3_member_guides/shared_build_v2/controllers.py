"""controllers.py -- the three baseline controllers in ONE file (shared build v2).

Do not change these. Every disturbance study uses exactly these rules.
  NC  never hold                                              (manuscript Sec 3.2.8)
  FH  hold = d + (alpha + b) * (H0 - hf), clipped [0, cap]    (Eq. 3.12, Daganzo 2009)
  EH  hold = (hb - hf) / 2,               clipped [0, cap]    (Eq. 3.13, Rodriguez et al. 2023)
"""
import os
import sys

SIM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulator")
if SIM_DIR not in sys.path:
    sys.path.append(SIM_DIR)
import params as P  # noqa: E402

FH_B_PER_STOP = P.ARRIVALS_PER_MIN * P.DWELL_PER_BOARD / 60.0   # 0.05


def no_control(obs):
    return 0.0


def _b_factor(stop):
    later = [c for c in P.CONTROL_STOPS if c > stop]
    end = later[0] if later else P.N_STOPS
    return FH_B_PER_STOP * (end - stop)


def forward_headway(obs):
    hold = P.FH_SLACK + (P.FH_ALPHA + _b_factor(obs["stop"])) * (obs["H0"] - obs["hf"])
    return min(max(hold, 0.0), obs["max_hold"])


def even_headway(obs):
    hold = 0.5 * (obs["hb"] - obs["hf"])
    return min(max(hold, 0.0), obs["max_hold"])


CONTROLLERS = {"NC": no_control, "FH": forward_headway, "EH": even_headway}
