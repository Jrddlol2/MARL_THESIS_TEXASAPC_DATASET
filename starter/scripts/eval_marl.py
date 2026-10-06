"""Evaluate a trained MARL checkpoint as the 4th controller vs NC/FH/EH (SO3 / the Dec-5 comparison).

Runs the greedy policy on the manuscript's evaluation matrix (methods.tex, Stage A / Stage B
evaluation and computational cost: 9 cells x 4 controllers x 30 seeds = 1,080 runs), at the SAME
control stops and seeds 0..N-1 as the baselines, and checks the manuscript's acceptance criteria.

    python scripts/eval_marl.py --ckpt experiments/gate/checkpoint_best.pt
    python scripts/eval_marl.py --ckpt experiments/gate/checkpoint_best.pt --cells A     # Stage A only (the gate)

THE EVALUATION MATRIX
    Stage A                 D+T
    Ablation S              D+T+S
    Ablation W              D+T+W, observed ordinary rain only
    Ablation B              D+T+B
    Stage B, observed rain  D+T+S+W+B
    Stage B, light / moderate / heavy rain / extreme rainstorm
                            D+T+S+W+B with a corridor-wide slowdown of 5.3 / 6.3 / 7.4 / 25% speed
                            (TSSP 2018; Ji et al. 2024), the same for every bus
Baseline results are read from results/mc_results*.csv (same seeds, so pairing holds); a cell with no
saved baseline is simulated here.

ANALYSIS CONFIGURATION (fixed 2026-09-14, before any MARL evaluation)
    alpha 0.05. Paired Wilcoxon signed-rank test by seed, one-sided. Holm correction over MARL's three
    comparisons (vs NC, FH, EH) within each cell and metric. Bootstrap: 5,000 resamples, 95% intervals.

ACCEPTANCE CRITERIA (methods.tex; Stage A (i) margin locked 2026-09-18, before the re-runs)
    Stage A (i)   mean wait non-inferior to EH within a 1.5% margin: one-sided paired Wilcoxon test that
                  MARL wait < EH wait x 1.015 is significant (margin from Rodriguez et al. 2023, p. 13,
                  who call a 1.5% difference "marginal"). The original no-margin version is also reported.
    PRIMARY wait = SUMO's recorded per-passenger wait (wait_direct), the manuscript's definition
    (methods.tex, mean passenger waiting time). The headway formula (wait_s) is a cross-check only;
    its verdicts are printed but do not decide the criteria.
    Seeds: --seed-start picks the block (0 = development seeds 0-29; 100 = the fresh test seeds).
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
NI_MARGIN = 0.015        # Stage A (i) non-inferiority margin (locked 2026-09-18)
# Primary measure (decided 2026-09-18): SUMO's recorded per-passenger wait, the manuscript's definition
# (methods.tex, "average time elapsed from a passenger's arrival at a stop to their successful boarding").
# The headway formula (H/2)(1 + CV^2) is reported as a cross-check only.
WAITS = [("wait_direct", "recorded wait (PRIMARY)"), ("wait_s", "formula wait (cross-check)")]
STAGE_B = dict(T=True, S=True, W=True, B=True)
# short name, label, simulate settings, weather slowdown, baseline file tag, scenario name in that file
CELLS = [
    ("A",          "Stage A (D+T)",                dict(T=True),          0.0,   "",                 "Stage A (D+T)"),
    ("S",          "Ablation S (D+T+S)",           dict(T=True, S=True),  0.0,   "",                 "Ablation S (D+T+S)"),
    ("W",          "Ablation W (observed rain)",   dict(T=True, W=True),  0.0,   "",                 "Ablation W (D+T+W)"),
    ("B",          "Ablation B (D+T+B)",           dict(T=True, B=True),  0.0,   "",                 "Ablation B (D+T+B)"),
    ("B_obs",      "Stage B (observed rain)",      STAGE_B,               0.0,   "",                 "Stage B (D+T+S+W+B)"),
    ("B_light",    "Stage B (light rain)",         STAGE_B,               0.053, "stageB_light",     "Stage B (D+T+S+W+B)"),
    ("B_moderate", "Stage B (moderate rain)",      STAGE_B,               0.063, "stageB_moderate",  "Stage B (D+T+S+W+B)"),
    ("B_heavy",    "Stage B (heavy rain)",         STAGE_B,               0.074, "stageB_heavy",     "Stage B (D+T+S+W+B)"),
    ("B_extreme",  "Stage B (extreme rainstorm)",  STAGE_B,               0.25,  "stageB_extreme",   "Stage B (D+T+S+W+B)"),
]
BASELINE_NAMES = ["NC", "FH", "EH"]

_agent = None       # one agent per worker process
_cfg = None         # the Config the checkpoint was trained with


def run_config(ckpt):
    """The Config saved next to the checkpoint (config.json), so evaluation acts exactly like
    training did -- above all skip_enabled. Falls back to the default Config if there is none."""
    path = os.path.join(os.path.dirname(os.path.abspath(ckpt)), "config.json")
    cfg = Config()
    if os.path.exists(path):
        import json
        saved = json.load(open(path)).get("config", {})
        for field in ("skip_enabled", "H0", "dt", "net", "control_stops"):
            if field in saved:
                value = saved[field]
                setattr(cfg, field, tuple(value) if isinstance(value, list) else value)
    return cfg


def _load_agent(ckpt):
    global _agent, _cfg
    _cfg = run_config(ckpt)
    _agent = DDQNAgent(OBS_DIM, N_ACTIONS, hidden=_cfg.net, seed=_cfg.seed)
    _agent.load(ckpt)


def _run(task):
    """One run: (cell, controller, seed) -> (cell, controller, seed, headway_cv, wait_s, travel_s, wait_direct)."""
    short, controller, seed = task
    _, _, settings, slowdown, _, _ = next(c for c in CELLS if c[0] == short)
    cfg = _cfg if _cfg is not None else Config()
    if controller == "MARL":
        decide = MarlController(_agent, cfg, training=False)
    else:
        decide = BASELINES[controller]
    extra = {"weather_slowdown": slowdown}
    r = simulate(decide, seed=seed, control_stops=list(cfg.control_stops), skip_enabled=cfg.skip_enabled,
                 **settings, **extra)
    return (short, controller, seed, r["headway_cv"], r["wait_s"], r["travel_s"], r["wait_direct"])


def saved_baselines(short, N, start):
    """Baseline rows for a cell from results/mc_results[_tag][_s<start>].csv, or None if not saved for all seeds."""
    _, _, _, _, tag, scenario = next(c for c in CELLS if c[0] == short)
    name = "mc_results" + ("_" + tag if tag else "") + (f"_s{start}" if start else "") + ".csv"
    path = os.path.join("results", name)
    if not os.path.exists(path):
        return None
    table = pd.read_csv(path, float_precision="round_trip")
    table = table[(table.scenario == scenario) & (table.seed >= start) & (table.seed < start + N)]
    if len(table) != 3 * N:
        return None
    return [(short, row.controller, int(row.seed), row.headway_cv, row.wait_s, row.travel_s, row.wait_direct)
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


def non_inferior_p(x, reference, margin):
    """One-sided paired Wilcoxon p-value that x < reference x (1 + margin), i.e. x is non-inferior."""
    x, reference = np.asarray(x), np.asarray(reference)
    return float(wilcoxon(x - reference * (1 + margin), alternative="less").pvalue)


def analyse(rows, cells, N):
    frame = pd.DataFrame(rows, columns=["cell", "controller", "seed", "headway_cv", "wait_s", "travel_s",
                                        "wait_direct"])
    frame = frame.sort_values(["cell", "controller", "seed"])
    rng = np.random.default_rng(0)
    lines = [f"MARL evaluation, N = {N} paired seeds. Paired Wilcoxon signed-rank (one-sided), Holm over "
             f"MARL vs NC/FH/EH, alpha {ALPHA}.", "",
             "| Cell | Ctrl | Headway CV [95% CI] | Recorded wait (s) [95% CI] | Formula wait (s) | Travel (s) |",
             "|---|---|---|---|---|---|"]
    get = lambda cell, ctrl, col: frame[(frame.cell == cell) & (frame.controller == ctrl)][col].to_numpy()
    for short, label, *_ in cells:
        for ctrl in BASELINE_NAMES + ["MARL"]:
            cv, wt = boot_mean(get(short, ctrl, "headway_cv"), rng), boot_mean(get(short, ctrl, "wait_direct"), rng)
            lines.append(f"| {label} | {ctrl} | {cv[0]:.3f} [{cv[1]:.3f}, {cv[2]:.3f}] | "
                         f"{wt[0]:.0f} [{wt[1]:.0f}, {wt[2]:.0f}] | {get(short, ctrl, 'wait_s').mean():.0f} | "
                         f"{get(short, ctrl, 'travel_s').mean():.0f} |")

    verdicts = []
    names = [c[0] for c in cells]
    if "A" in names:
        marl_cv = get("A", "MARL", "headway_cv")
        lower_cv = holm([one_sided_p(marl_cv, get("A", b, "headway_cv"), "less") for b in BASELINE_NAMES])
        eh_cv = get("A", "EH", "headway_cv")
        for col, measure in WAITS:
            marl_wait, eh_wait = get("A", "MARL", col), get("A", "EH", col)
            p_ni = non_inferior_p(marl_wait, eh_wait, NI_MARGIN)
            worse_wait = holm([one_sided_p(marl_wait, get("A", b, col), "greater") for b in BASELINE_NAMES])
            gap = 100 * (marl_wait.mean() / eh_wait.mean() - 1)
            verdicts += [
                f"- **Stage A (i), {measure}** within {100 * NI_MARGIN:.1f}% of EH: MARL {marl_wait.mean():.1f} s vs "
                f"EH {eh_wait.mean():.1f} s ({gap:+.2f}%), p(non-inferior) = {p_ni:.3f} -> "
                f"{'PASS' if p_ni < ALPHA else 'FAIL'}   [original no-margin test: Holm p(MARL worse) = "
                f"{worse_wait[2]:.3f} -> {'pass' if worse_wait[2] >= ALPHA else 'fail'}]"]
        verdicts += [
            f"- **Stage A (ii)** headway CV lower than NC: MARL {marl_cv.mean():.3f} vs NC "
            f"{get('A', 'NC', 'headway_cv').mean():.3f}, Holm p = {lower_cv[0]:.3f} -> "
            f"{'PASS' if lower_cv[0] < ALPHA else 'FAIL'}",
            f"- **Training gate** headway CV below EH: MARL {marl_cv.mean():.3f} vs EH {eh_cv.mean():.3f}, "
            f"Holm p = {lower_cv[2]:.3f} -> {'PASS' if marl_cv.mean() < eh_cv.mean() else 'FAIL'}"
            f"{' (significant)' if lower_cv[2] < ALPHA else ''}",
        ]
    stage_b = [c for c in cells if c[0].startswith("B_")]
    if stage_b:
        for col, measure in WAITS:
            all_pass, block = True, []
            for short, label, *_ in stage_b:
                means = {b: get(short, b, col).mean() for b in BASELINE_NAMES}
                best = min(means, key=means.get)
                p = holm([one_sided_p(get(short, "MARL", col), get(short, b, col), "less")
                          for b in BASELINE_NAMES])[BASELINE_NAMES.index(best)]
                ok = p < ALPHA; all_pass = all_pass and ok
                block.append(f"  - {label}: MARL {get(short, 'MARL', col).mean():.0f} s vs best baseline "
                             f"{best} {means[best]:.0f} s, Holm p = {p:.3f} -> {'pass' if ok else 'fail'}")
            complete = len(stage_b) == 5
            verdicts.append(f"- **Stage B, {measure}** below the best baseline in every Stage B cell -> "
                            f"{('PASS' if all_pass else 'FAIL') if complete else 'INCOMPLETE (not all 5 Stage B cells run)'}")
            verdicts += block
    lines += ["", "**Acceptance criteria**", ""] + verdicts
    return frame, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--N", type=int, default=30)
    ap.add_argument("--seed-start", type=int, default=0, help="first seed (0 = development, 100 = test)")
    ap.add_argument("--jobs", type=int, default=10)
    ap.add_argument("--cells", default=",".join(c[0] for c in CELLS), help="e.g. A  or  A,S,W,B,B_obs")
    ap.add_argument("--tag", default=None, help="output name (default: the checkpoint's folder name)")
    a = ap.parse_args()
    tag = a.tag or os.path.basename(os.path.dirname(os.path.abspath(a.ckpt)))
    if a.seed_start:
        tag += f"_s{a.seed_start}"
    wanted = a.cells.split(",")
    cells = [c for c in CELLS if c[0] in wanted]

    rows, tasks = [], []
    for short, label, *_ in cells:
        seeds = range(a.seed_start, a.seed_start + a.N)
        saved = saved_baselines(short, a.N, a.seed_start)
        if saved is None:
            print(f"{label}: no saved baselines for seeds {seeds.start}-{seeds.stop - 1}, simulating them", flush=True)
            tasks += [(short, b, s) for b in BASELINE_NAMES for s in seeds]
        else:
            rows += saved
        tasks += [(short, "MARL", s) for s in seeds]
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
