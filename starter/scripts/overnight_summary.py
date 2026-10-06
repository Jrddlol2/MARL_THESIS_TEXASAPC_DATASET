"""Collect the overnight runs into results/OVERNIGHT_SUMMARY.md: Stage A and Stage B headline numbers and
the acceptance verdicts of every v2_* evaluation (development seeds 0-29). Run from starter/."""
import glob, os, re
import pandas as pd

rows, verdicts = [], []
for path in sorted(glob.glob("results/marl_eval_v2_*.csv")):
    run = os.path.basename(path)[len("marl_eval_"):-4]
    if run.endswith(("_s100",)):
        continue
    d = pd.read_csv(path)
    for cell in ["A", "B_obs", "B_heavy", "B_extreme"]:
        c = d[d.cell == cell]
        if c.empty:
            continue
        m, e = c[c.controller == "MARL"], c[c.controller == "EH"]
        rows.append(dict(run=run, cell=cell,
                         marl_cv=m.headway_cv.mean(), eh_cv=e.headway_cv.mean(),
                         marl_wait=m.wait_direct.mean(), eh_wait=e.wait_direct.mean(),
                         wait_gap_pct=100 * (m.wait_direct.mean() / e.wait_direct.mean() - 1),
                         marl_trip=m.travel_s.mean(), eh_trip=e.travel_s.mean()))
    md = open(path[:-4] + ".md", encoding="utf-8").read()
    verdicts.append(f"### {run}\n" + md[md.find("**Acceptance criteria**"):].strip())

lines = ["# Overnight results (development seeds 0-29; test seeds 100-129 untouched)", "",
         "Recorded per-passenger wait is primary. Gap = MARL wait vs Even Headway.", ""]
if rows:
    t = pd.DataFrame(rows)
    lines += ["| Run | Cell | MARL CV | EH CV | MARL wait (s) | EH wait (s) | Gap % | MARL trip (s) | EH trip (s) |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples():
        lines.append(f"| {r.run} | {r.cell} | {r.marl_cv:.3f} | {r.eh_cv:.3f} | {r.marl_wait:.0f} | {r.eh_wait:.0f} | "
                     f"{r.wait_gap_pct:+.2f} | {r.marl_trip:.0f} | {r.eh_trip:.0f} |")
    lines += ["", "## Mean over training seeds", "",
              "| Config | Cell | Seeds | MARL CV (min-max) | Wait gap % (min-max) |", "|---|---|---|---|---|"]
    t["config"] = t.run.str.replace(r"_s\d+$", "", regex=True)
    for (cfg, cell), g in t.groupby(["config", "cell"]):
        lines.append(f"| {cfg} | {cell} | {len(g)} | {g.marl_cv.mean():.3f} ({g.marl_cv.min():.3f}-{g.marl_cv.max():.3f}) | "
                     f"{g.wait_gap_pct.mean():+.2f} ({g.wait_gap_pct.min():+.2f} to {g.wait_gap_pct.max():+.2f}) |")
else:
    lines.append("No evaluations finished yet.")
lines += ["", "## Acceptance verdicts", ""] + verdicts
open("results/OVERNIGHT_SUMMARY.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"summary: {len(rows)} rows from {len(verdicts)} runs -> results/OVERNIGHT_SUMMARY.md")
