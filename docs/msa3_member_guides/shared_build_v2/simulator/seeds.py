"""seeds.py -- one random stream per source of randomness (shared build v2).

Every source gets its OWN stream, all made from the run's seed, so switching a
disturbance on never changes the riders or the travel-time noise of that seed
(manuscript Sec 3.2.6 "Random Seed Control"; Patterson et al. 2024, JMLR, p.50).

    rng = stream(seed, "surge")      # use this generator for the surge draws

The order of NAMES is fixed. Never reorder it, only add new names at the END.
"""
import numpy as np

NAMES = ["riders", "noise", "surge", "weather", "breakdown"]


def stream(seed, name):
    """The random generator for one source of randomness in run `seed`."""
    children = np.random.SeedSequence(seed).spawn(len(NAMES))
    return np.random.default_rng(children[NAMES.index(name)])
