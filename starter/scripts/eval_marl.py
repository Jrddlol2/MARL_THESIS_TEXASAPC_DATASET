"""Evaluate a trained MARL checkpoint as the 4th controller vs NC/FH/EH (SO3 / the Dec-5 comparison).

Runs the greedy policy on the manuscript's evaluation matrix (methods.tex, Stage A / Stage B
evaluation and computational cost: 9 cells x 4 controllers x 30 seeds = 1,080 runs), at the SAME
control stops and seeds 0..N-1 as the baselines, and checks the manuscript's acceptance criteria.

    python scripts/eval_marl.py --ckpt experiments/gate/checkpoint_best.pt
    python scripts/eval_marl.py --ckpt experiments/gate/checkpoint_best.pt --cells A     # Stage A only (the gate)

THE EVALUATION MATRIX
    Stage A                 D+T
    Ablation S              D+T+S
    Ablation W              D+T+W, observed ordinary rain only (eta = 0)
    Ablation B              D+T+B
    Stage B, observed rain  D+T+S+W+B, eta = 0
    Stage B, eta 0.3/0.6/1.0/1.3   D+T+S+W+B with labelled synthetic weather stress
Baseline results are read from results/mc_results*.csv (same seeds, so pairing holds); a cell with no
saved baseline is simulated here.

ANALYSIS CONFIGURATION (fixed 2026-09-14, before any MARL evaluation)
    alpha 0.05. Paired Wilcoxon signed-rank test by seed, one-sided. Holm correction over MARL's three
    comparisons (vs NC, FH, EH) within each cell and metric. Bootstrap: 5,000 resamples, 95% intervals.

ACCEPTANCE CRITERIA (methods.tex)
    Stage A (i)   mean wait no worse than EH: the test "MARL wait > EH wait" is NOT significant
    Stage A (ii)  headway CV significantly lower than NC
    Stage B       in every Stage B cell, mean wait significantly lower than the best baseline in that cell
    Training gate (decided 2026-09-14): Stage A mean headway CV below EH (0.342 in results/mc_summary.md)

Writes results/marl_eval_<tag>.csv (every run) and results/marl_eval_<tag>.md (tables and verdicts).
"""
import os, sys, csv, argparse, numpy as np, pandas as pd
from concurrent.futures import ProcessPoolExecutor
from scipy.stats import wilcoxon
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "envs"))
sys.path.insert(0, os.path.join(_here, "..", "agents"))
from corridor_sim import simulate, BASELINES, CONTROL_STOPS
from marl_env import Config, MarlController, N_ACTIONS
from obs import OBS_DIM
from ddqn import DDQNAgent

ALPHA = 0.05
STAGE_B = dict(T=True, S=True, W=True, B=True)
# short name, label, simulate settings, weather eta, baseline file, scenario name in that file
CELLS = [
    ("A",       "Stage A (D+T)",                dict(T=True),          None, "mc_results.csv",               "Stage A (D+T)"),
    ("S",       "Ablation S (D+T+S)",           dict(T=True, S=True),  None, "mc_results.csv",               "Ablation S (D+T+S)"),
    ("W",       "Ablation W (observed rain)",   dict(T=True, W=True),  0.0,  "mc_results_observed_rain.csv", "Ablation W (D+T+W)"),
    ("B",       "Ablation B (D+T+B)",           dict(T=True, B=True),  None, "mc_results.csv",               "Ablation B (D+T+B)"),
    ("B_obs",   "Stage B (observed rain)",      STAGE_B,               0.0,  "mc_results_observed_rain.csv", "Stage B (D+T+S+W+B)"),
    ("B_0.3",   "Stage B (eta 0.3)",            STAGE_B,               0.3,  "mc_results_stageB_eta0.3.csv", "Stage B (D+T+S+W+B)"),
    ("B_0.6",   "Stage B (eta 0.6)",            STAGE_B,               0.6,  "mc_results_stageB_eta0.6.csv", "Stage B (D+T+S+W+B)"),
    ("B_1.0",   "Stage B (eta 1.0)",            STAGE_B,               1.0,  "mc_results_stageB_eta1.0.csv", "Stage B (D+T+S+W+B)"),
    ("B_1.3",   "Stage B (eta 1.3)",            STAGE_B,               1.3,  "mc_results_stageB_eta1.3.csv", "Stage B (D+T+S+W+B)"),
]
BASELINE_NAMES = ["NC", "FH", "EH"]

_agent = None       # one agent per worker process


def _load_agent(ckpt):
    global _agent
    cfg = Config()
    _agent = DDQNAgent(OBS_DIM, N_ACTIONS, hidden=cfg.net, seed=cfg.seed)
    _agent.load(ckpt)


def _run(task):
    """One run: (cell, controller, seed) -> (cell, controller, seed, headway_cv, wait_s, travel_s)."""
    short, controller, seed = task
    _, _, settings, eta, _, _ = next(c for c in CELLS if c[0] == short)
    cfg = Config()
    if controller == "MARL":
        decide = MarlController(_agent, cfg, training=False)
    else:
        decide = BASELINES[controller]
    extra = {} if eta is None else {"eta": eta}
    r = simulate(decide, seed=seed, control_stops=list(cfg.control_stops), skip_enabled=cfg.skip_enabled,
                 **settings, **extra)
    return (short, controller, seed, r["headway_cv"], r["wait_s"], r["travel_s"])


def saved_baselines(short, N):
    """Baseline rows for a cell from results/mc_results*.csv, or None if not saved for all seeds."""
    _, _, _, _, file, scenario = next(c for c in CELLS if c[0] == short)
    path = os.path.join("results", file)
    if not os.path.exists(path):
        return None
    table = pd.read_csv(path, float_precision="round_trip")
    table = table[(table.scenario == scenario) & (table.seed < N)]
    if len(table) != 3 * N:
        return None
    return [(short, row.controller, int(row.seed), row.headway_cv, row.wait_s, row.travel_s)
            for row in table.itertuples()]


def holm(p_values):
    """Holm-adjusted p-values (same order as given)."""
    order = np.argsort(p_values); adjusted = np.empty(len(p_values)); running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


def one_sided_p(x, y, alternative):
    """Paired Wilcoxon signed-rank p-value for x vs y ("less": x < y, "greater": x > y)."""
    difference = np.asarray(x) - np.asarray(y)
    if np.all(difference == 0):
        return 1.0
    return float(wilcoxon(x, y, alternative=alternative).pvalue)


def boot_mean(x, rng):
    x = np.asarray(x); samples = [rng.choice(x, len(x)).mean() for _ in range(5000)]
    return x.mean(), np.percentile(samples, 2.5), np.percentile(samples, 97.5)


def analyse(rows, cells, N):
    frame = pd.DataFrame(rows, columns=["cell", "controller", "seed", "headway_cv", "wait_s", "travel_s"])
    frame = frame.sort_values(["cell", "controller", "seed"])
    rng = np.random.default_rng(0)
    lines = [f"MARL evaluation, N = {N} paired seeds. Paired Wilcoxon signed-rank (one-sided), Holm over "
             f"MARL vs NC/FH/EH, alpha {ALPHA}.", "",
             "| Cell | Ctrl | Headway CV [95% CI] | Wait (s) [95% CI] | Travel (s) |", "|---|---|---|---|---|"]
    get = lambda cell, ctrl, col: frame[(frame.cell == cell) & (frame.controller == ctrl)][col].to_numpy()
    for short, label, *_ in cells:
        for ctrl in BASELINE_NAMES + ["MARL"]:
            cv, wt = boot_mean(get(short, ctrl, "headway_cv"), rng), boot_mean(get(short, ctrl, "wait_s"), rng)
            lines.append(f"| {label} | {ctrl} | {cv[0]:.3f} [{cv[1]:.3f}, {cv[2]:.3f}] | "
                         f"{wt[0]:.0f} [{wt[1]:.0f}, {wt[2]:.0f}] | {get(short, ctrl, 'travel_s').mean():.0f} |")

    verdicts = []
    names = [c[0] for c in cells]
    if "A" in names:
        marl_wait, marl_cv = get("A", "MARL", "wait_s"), get("A", "MARL", "headway_cv")
        worse_wait = holm([one_sided_p(marl_wait, get("A", b, "wait_s"), "greater") for b in BASELINE_NAMES])
        lower_cv = holm([one_sided_p(marl_cv, get("A", b, "headway_cv"), "less") for b in BASELINE_NAMES])
        eh_cv = get("A", "EH", "headway_cv")
        verdicts += [
            f"- **Stage A (i)** wait no worse than EH: MARL {marl_wait.mean():.0f} s vs EH "
            f"{get('A', 'EH', 'wait_s').mean():.0f} s, Holm p(MARL worse) = {worse_wait[2]:.3f} -> "
            f"{'PASS' if worse_wait[2] >= ALPHA else 'FAIL'}",
            f"- **Stage A (ii)** headway CV lower than NC: MARL {marl_cv.mean():.3f} vs NC "
            f"{get('A', 'NC', 'headway_cv').mean():.3f}, Holm p = {lower_cv[0]:.3f} -> "
            f"{'PASS' if lower_cv[0] < ALPHA else 'FAIL'}",
            f"- **Training gate** headway CV below EH: MARL {marl_cv.mean():.3f} vs EH {eh_cv.mean():.3f}, "
            f"Holm p = {lower_cv[2]:.3f} -> {'PASS' if marl_cv.mean() < eh_cv.mean() else 'FAIL'}"
            f"{' (significant)' if lower_cv[2] < ALPHA else ''}",
        ]
    stage_b = [c for c in cells if c[0].startswith("B_")]
    if stage_b:
        all_pass = True
        for short, label, *_ in stage_b:
            means = {b: get(short, b, "wait_s").mean() for b in BASELINE_NAMES}
            best = min(means, key=means.get)
            p = holm([one_sided_p(get(short, "MARL", "wait_s"), get(short, b, "wait_s"), "less")
                      for b in BASELINE_NAMES])[BASELINE_NAMES.index(best)]
            ok = p < ALPHA; all_pass = all_pass and ok
            verdicts.append(f"  - {label}: MARL wait {get(short, 'MARL', 'wait_s').mean():.0f} s vs best baseline "
                            f"{best} {means[best]:.0f} s, Holm p = {p:.3f} -> {'pass' if ok else 'fail'}")
        complete = len(stage_b) == 5
        verdicts.insert(len(verdicts) - len(stage_b),
                        f"- **Stage B** wait below the best baseline in every Stage B cell -> "
                        f"{('PASS' if all_pass else 'FAIL') if complete else 'INCOMPLETE (not all 5 Stage B cells run)'}")
    lines += ["", "**Acceptance criteria**", ""] + verdicts
    return frame, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--N", type=int, default=30)
    ap.add_argument("--jobs", type=int, default=10)
    ap.add_argument("--cells", default=",".join(c[0] for c in CELLS), help="e.g. A  or  A,S,W,B,B_obs")
    ap.add_argument("--tag", default=None, help="output name (default: the checkpoint's folder name)")
    a = ap.parse_args()
    tag = a.tag or os.path.basename(os.path.dirname(os.path.abspath(a.ckpt)))
    wanted = a.cells.split(",")
    cells = [c for c in CELLS if c[0] in wanted]

    rows, tasks = [], []
    for short, label, *_ in cells:
        saved = saved_baselines(short, a.N)
        if saved is None:
            print(f"{label}: no saved baselines for seeds 0-{a.N - 1}, simulating them", flush=True)
            tasks += [(short, b, s) for b in BASELINE_NAMES for s in range(a.N)]
        else:
            rows += saved
        tasks += [(short, "MARL", s) for s in range(a.N)]
    print(f"{len(tasks)} runs on {a.jobs} workers", flush=True)
    with ProcessPoolExecutor(max_workers=a.jobs, initializer=_load_agent, initargs=(a.ckpt,)) as pool:
        for k, row in enumerate(pool.map(_run, tasks), 1):
            rows.append(row)
            if k % 30 == 0 or k == len(tasks):
                print(f"  {k}/{len(tasks)} runs done", flush=True)

    frame, lines = analyse(rows, cells, a.N)
    frame.to_csv(f"results/marl_eval_{tag}.csv", index=False)
    open(f"results/marl_eval_{tag}.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines).encode("ascii", "replace").decode())
    print(f"\n-> results/marl_eval_{tag}.md, results/marl_eval_{tag}.csv")


if __name__ == "__main__":
    main()
