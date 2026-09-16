"""
=============================================================================
 THE SCORE:  HOW GOOD WAS THAT DECISION?
=============================================================================

WHAT IT DOES
    After a bus decides to hold (and possibly skip), we need to tell it how
    well that worked. This file turns "what happened next" into a single
    number. The number is always zero or negative: zero is perfect, and the
    worse things went, the more negative it gets.

    The score adds up three penalties:

        score = -( w1 x uneven spacing + w2 x passenger delay + w3 x skipping )

    The three weights w1, w2, w3 say how much each one matters. They live in
    Config (envs/marl_env.py).

WHY THE SCORE ARRIVES LATE
    A bus cannot know straight away whether holding for 60 s helped. So the
    score for a decision is worked out at that bus's NEXT control stop, using
    what the corridor looks like by then. The manuscript calls this a
    semi-Markov decision process; in plain terms, "grade the move once you can
    see what it did".

THE CHOICES BEING SWEPT  (Expected Output 2.1)
    The manuscript fixes the three penalties above but leaves their exact form
    open, so each one has alternatives here and Config picks which to use.
    What each run chose, and how it did, is in
    docs/reference/REWARD_DESIGN_NOTES.md.

RUN      python envs/reward.py        (prints a few example scores)
=============================================================================
"""

# Used to turn a queue of people into a number near 1: 20 riders waiting is
# "a normal busy stop" on this corridor.
Q_REF = 20.0


def decode_action(action_id, H0=600.0, dt=300.0):
    """Turn the action number (0 to 9) into what the bus should actually do.

    The agent picks a number. The first five mean "hold, don't skip"; the last
    five mean "hold, and skip the next stop". The hold is a fraction of dt
    (300 s), so the choices are 0, 30, 60, 90 and 120 seconds.

        action 0 -> hold   0 s, no skip        action 5 -> hold   0 s, skip
        action 4 -> hold 120 s, no skip        action 9 -> hold 120 s, skip
    """
    fraction_of_window = (action_id % 5) * 0.1      # 0.0, 0.1, 0.2, 0.3, 0.4
    skip = action_id // 5                           # 0 for actions 0-4, 1 for 5-9
    hold_seconds = fraction_of_window * dt
    return hold_seconds, int(skip)


# =============================================================================
# PENALTY 1 OF 3 -- UNEVEN SPACING
# =============================================================================
# "before" and "after" are the bus's situation at its previous and its current
# control stop. "decision" holds the scheduled headway, the hold it chose and
# whether it skipped. Each function returns a penalty of zero or more.

def spacing_vs_timetable(before, after, decision):
    """How far the gap AHEAD is from the 10-minute timetable, squared.

    A bus exactly on headway scores 0. One at half the headway scores 0.25.
    Squaring means one big error hurts much more than two small ones.
    """
    error = (after["hf"] - decision["H0"]) / decision["H0"]
    return error ** 2


def spacing_vs_neighbours(before, after, decision):
    """How different the gap ahead is from the gap behind, squared.

    This is what "bunching" actually means: a bus sitting midway between its
    two neighbours scores 0, even if the whole fleet is running late.
    """
    difference = (after["hf"] - after["hb"]) / decision["H0"]
    return difference ** 2


def spacing_both_gaps(before, after, decision):
    """Both gaps measured against the timetable, averaged."""
    ahead_error = (after["hf"] - decision["H0"]) / decision["H0"]
    behind_error = (after["hb"] - decision["H0"]) / decision["H0"]
    return 0.5 * (ahead_error ** 2 + behind_error ** 2)


# =============================================================================
# PENALTY 2 OF 3 -- PASSENGER DELAY
# =============================================================================

def delay_at_stops(before, after, decision):
    """People waiting at the stop, times how long a gap they waited through."""
    return (after["queue"] * after["hf"]) / (Q_REF * decision["H0"])


def delay_on_board(before, after, decision):
    """People already on the bus, times how long they were held.

    This divides by capacity rather than by Q_REF, so a second of in-vehicle
    delay works out about three times cheaper than a second spent waiting at a
    stop. That accidental discount is why `delay_everyone` exists.
    """
    return (decision["hold"] / decision["H0"]) * (before["load"] / before["cap"])


def delay_everyone(before, after, decision):
    """Both kinds of delay, priced the same per rider-second.

    A minute of someone's time costs the same whether they spend it standing at
    a stop or sitting on a held bus. Runs A to C left the in-vehicle half
    unpriced and the agent duly over-held; see the design notes.
    """
    waiting_at_stops = after["queue"] * after["hf"]
    held_on_board = before["load"] * decision["hold"]
    return (waiting_at_stops + held_on_board) / (Q_REF * decision["H0"])


# =============================================================================
# PENALTY 3 OF 3 -- SKIPPING A STOP
# =============================================================================

def skip_cost_by_riders(before, after, decision):
    """Skipping is charged for only if people were actually left behind."""
    return decision["skip"] * (before["queue"] / Q_REF)


def skip_cost_flat(before, after, decision):
    """A fixed charge for skipping at all, however many people were there."""
    return float(decision["skip"])


# The names Config uses to choose between the alternatives above.
SPACING = {"dev": spacing_vs_timetable, "even": spacing_vs_neighbours, "both": spacing_both_gaps}
DELAY = {"queue": delay_at_stops, "hold": delay_on_board, "both": delay_everyone}
SKIP = {"stranded": skip_cost_by_riders, "flat": skip_cost_flat}

# The older names, kept so nothing that imports them breaks.
IRR, WAIT = SPACING, DELAY


def compose(before, after, action_id, config):
    """The score for one decision: add the three penalties, then make it negative.

    before     the bus's situation when it decided
    after      its situation at the next control stop, which is what it caused
    action_id  what it chose (0 to 9)
    config     which penalty forms to use, and the three weights
    """
    # config may be a Config object or a plain dictionary, so read it either way.
    def setting(name):
        if isinstance(config, dict):
            return config[name]
        return getattr(config, name)

    hold_seconds, skip = decode_action(action_id, setting("H0"), setting("dt"))
    decision = {"H0": setting("H0"), "hold": hold_seconds, "skip": skip}

    weight_spacing, weight_delay, weight_skip = setting("w")
    spacing_penalty = SPACING[setting("irr")](before, after, decision)
    delay_penalty = DELAY[setting("wait")](before, after, decision)
    skip_penalty = SKIP[setting("skip")](before, after, decision)

    total = (weight_spacing * spacing_penalty
             + weight_delay * delay_penalty
             + weight_skip * skip_penalty)
    return -total


if __name__ == "__main__":
    settings = dict(irr="dev", wait="queue", skip="stranded", w=(1.0, 0.5, 1.0), H0=600.0, dt=300.0)
    before = dict(hf=600, hb=600, load=20, queue=5, cap=60)
    on_time = dict(hf=600, hb=600, queue=3, cap=60)      # perfect headway -> almost no penalty
    bunched = dict(hf=240, hb=960, queue=12, cap=60)     # early, with a big gap behind

    print("action decode 0,4,5,9:", [decode_action(a) for a in (0, 4, 5, 9)])
    print(f"reward on-time (a=0 hold): {compose(before, on_time, 0, settings):.3f}")
    print(f"reward bunched (a=0 hold): {compose(before, bunched, 0, settings):.3f}")
    print(f"reward bunched (a=9 max hold+skip): {compose(before, bunched, 9, settings):.3f}")
