"""Reward library for the MARL agent (SO2 / EO2.1).

The manuscript fixes the STRUCTURE — a weighted sum of three non-positive penalty terms
(headway irregularity, passenger waiting, degenerate-skip) — and leaves the exact expressions and
weights as the implementation deliverable. So each term is a CANDIDATE function here; a Config picks
which form and what weights. Nothing is committed: you sweep `irr`/`wait`/`skip` and `w=(w1,w2,w3)`.

A reward is assigned to a bus's action a_prev, realized at its NEXT control-stop decision, using the
state that action produced (semi-MDP: transition (s_prev, a_prev, r, s_cur)). `compose(...)` returns the
scalar reward; `decode_action` maps the discrete action id to (hold_seconds, skip).

    r = −( w1·irr(...) + w2·wait(...) + w3·skip(...) )      [each term ≥ 0]
"""
Q_REF = 20.0                           # reference queue for normalization (tunable scale constant)


def decode_action(a, H0=300.0, dt=300.0):
    """action id 0..9 -> (hold_seconds, skip). alpha in {0,.1,.2,.3,.4}, scaled by dt (=ΔT); skip binary."""
    alpha = (a % 5) * 0.1
    skip = a // 5
    return alpha * dt, int(skip)


# --- candidate terms: term(prev, cur, ctx) -> penalty >= 0.  ctx has H0, hold, skip ---------------
def irr_dev(prev, cur, ctx):           # 1a: squared deviation of forward headway from schedule H0
    return ((cur["hf"] - ctx["H0"]) / ctx["H0"]) ** 2
def irr_even(prev, cur, ctx):          # 1b: squared forward/backward headway asymmetry (even-spacing)
    return ((cur["hf"] - cur["hb"]) / ctx["H0"]) ** 2
def irr_both(prev, cur, ctx):          # 1c: both, averaged
    return 0.5 * (((cur["hf"] - ctx["H0"]) / ctx["H0"]) ** 2 + ((cur["hb"] - ctx["H0"]) / ctx["H0"]) ** 2)

def wait_queue(prev, cur, ctx):        # 2b: at-stop wait ~ waiting riders x headway they endured
    return (cur["queue"] * cur["hf"]) / (Q_REF * ctx["H0"])
def wait_hold(prev, cur, ctx):         # 2a: in-vehicle delay from holding, weighted by onboard load
    return (ctx["hold"] / ctx["H0"]) * (prev["load"] / prev["cap"])

def skip_stranded(prev, cur, ctx):     # 3a: stranded riders (demand-aware)
    return ctx["skip"] * (prev["queue"] / Q_REF)
def skip_flat(prev, cur, ctx):         # 3b: flat discouragement per skip
    return float(ctx["skip"])

IRR  = {"dev": irr_dev, "even": irr_even, "both": irr_both}
WAIT = {"queue": wait_queue, "hold": wait_hold}
SKIP = {"stranded": skip_stranded, "flat": skip_flat}


def compose(prev, cur, a_prev, cfg):
    """Scalar reward for action a_prev, realized at the next decision (state cur, prior state prev).
    cfg: object/dict with .irr .wait .skip (keys above), .w=(w1,w2,w3), .H0, .dt (=ΔT)."""
    g = (lambda k: getattr(cfg, k) if not isinstance(cfg, dict) else cfg[k])
    hold, skip = decode_action(a_prev, g("H0"), g("dt"))
    ctx = {"H0": g("H0"), "hold": hold, "skip": skip}
    w1, w2, w3 = g("w")
    ir = IRR[g("irr")](prev, cur, ctx)
    wt = WAIT[g("wait")](prev, cur, ctx)
    sk = SKIP[g("skip")](prev, cur, ctx)
    return -(w1 * ir + w2 * wt + w3 * sk)


if __name__ == "__main__":
    cfg = dict(irr="dev", wait="queue", skip="stranded", w=(1.0, 0.5, 1.0), H0=300.0, dt=300.0)
    prev = dict(hf=300, hb=300, load=20, queue=5, cap=60)
    on_time = dict(hf=300, hb=300, queue=3, cap=60)     # perfect headway -> ~0 penalty
    bunched = dict(hf=120, hb=480, queue=12, cap=60)    # early + long back gap -> large penalty
    print("action decode 0,4,5,9:", [decode_action(a) for a in (0, 4, 5, 9)])
    print(f"reward on-time (a=0 hold): {compose(prev, on_time, 0, cfg):.3f}")
    print(f"reward bunched (a=0 hold): {compose(prev, bunched, 0, cfg):.3f}")
    print(f"reward bunched (a=9 max hold+skip): {compose(prev, bunched, 9, cfg):.3f}")
