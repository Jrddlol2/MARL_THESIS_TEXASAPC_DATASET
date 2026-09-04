# -*- coding: utf-8 -*-
"""Data-cleaning visualization figures (MSA1), publication style (_figstyle). Streams the raw APC CSV
ONCE to compute the cleaning funnel, by-route selection, and raw-vs-clean distributions, then builds
per-stop / geography / temporal figures from the cleaned dir-6 subset + committed inputs.

Run from starter/ :  python scripts/figures_datacleaning.py   (add --refresh to re-stream the raw CSV)
Saves PDF+PNG to results/figures/datacleaning/. The raw pass is cached to _cache.json / _clean_dir6.csv.
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S

RAW = r"C:\Users\jared\Desktop\THESIS\APC_Raw_July_2021_-_December_2021_20260824.csv"
OUT = "results/figures/datacleaning"; os.makedirs(OUT, exist_ok=True)
CACHE = f"{OUT}/_cache.json"
CONTROL = {"5280", "5857", "5859", "5867", "4046"}
NEED = ["route_id", "current_route_id", "import_error", "import_trip_error", "bs_id",
        "direction_code_id", "actual_sequence", "ons", "offs", "dwell_time", "rev_seconds",
        "rev_distance", "transit_date_time"]


def stream_raw():
    n_raw = 0
    funnel = dict(raw=0, r801=0, route_match=0, import_ok=0, trip_ok=0, bs_ok=0, dir6=0)
    by_route_cnt, by_route_ons = {}, {}
    d801 = {}
    raw801 = {"dwell": [], "rev": [], "ons": []}
    clean_parts = []
    ci = 0
    for ch in pd.read_csv(RAW, usecols=NEED, dtype=str, chunksize=1_000_000, na_filter=False):
        ci += 1; n_raw += len(ch)
        onsn = pd.to_numeric(ch["ons"], errors="coerce").fillna(0)
        for rid, g in ch.groupby("route_id"):
            by_route_cnt[rid] = by_route_cnt.get(rid, 0) + len(g)
        for rid, v in onsn.groupby(ch["route_id"]).sum().items():
            by_route_ons[rid] = by_route_ons.get(rid, 0.0) + float(v)
        m1 = ch["route_id"] == "801"
        m2 = m1 & (ch["route_id"] == ch["current_route_id"])
        m3 = m2 & (ch["import_error"] == "0")
        m4 = m3 & (ch["import_trip_error"] == "0")
        m5 = m4 & (ch["bs_id"] != "0")
        m6 = m5 & (ch["direction_code_id"] == "6")
        funnel["r801"] += int(m1.sum()); funnel["route_match"] += int(m2.sum())
        funnel["import_ok"] += int(m3.sum()); funnel["trip_ok"] += int(m4.sum())
        funnel["bs_ok"] += int(m5.sum()); funnel["dir6"] += int(m6.sum())
        b801 = ch[m1]
        if len(b801):
            ons801 = pd.to_numeric(b801["ons"], errors="coerce").fillna(0)
            for dirc, v in ons801.groupby(b801["direction_code_id"]).sum().items():
                d801[dirc] = d801.get(dirc, 0.0) + float(v)
            raw801["dwell"].append(pd.to_numeric(b801["dwell_time"], errors="coerce").values)
            raw801["rev"].append(pd.to_numeric(b801["rev_seconds"], errors="coerce").values)
            raw801["ons"].append(ons801.values)
        if int(m6.sum()):
            clean_parts.append(ch[m6].copy())
        print(f"  chunk {ci}: cumulative raw={n_raw:,}  dir6_clean={funnel['dir6']:,}", flush=True)
    funnel["raw"] = n_raw
    clean = pd.concat(clean_parts, ignore_index=True)
    raw801 = {k: np.concatenate(v) for k, v in raw801.items()}
    return funnel, by_route_cnt, by_route_ons, d801, raw801, clean


def main():
    S.apply()
    import matplotlib.pyplot as plt

    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        C = json.load(open(CACHE))
        funnel = C["funnel"]; by_route_ons = C["by_route_ons"]; d801 = C["d801"]
        raw801 = {k: np.array(v) for k, v in C["raw801_sample"].items()}
        clean = pd.read_csv(f"{OUT}/_clean_dir6.csv", dtype=str)
        print("loaded cache")
    else:
        funnel, by_route_cnt, by_route_ons, d801, raw801, clean = stream_raw()
        clean.to_csv(f"{OUT}/_clean_dir6.csv", index=False)
        json.dump({"funnel": funnel, "by_route_ons": by_route_ons,
                   "d801": d801,
                   "raw801_sample": {k: v[~np.isnan(v)][::40].tolist() for k, v in raw801.items()}},
                  open(CACHE, "w"), indent=1)
        print("wrote cache")

    assert funnel["dir6"] == 229421, f"funnel end {funnel['dir6']} != 229421 — filter drifted"

    for c in ["actual_sequence", "ons", "offs", "dwell_time", "rev_seconds", "rev_distance"]:
        clean[c] = pd.to_numeric(clean[c], errors="coerce")
    clean["run_seconds"] = (clean["rev_seconds"] - clean["dwell_time"]).clip(lower=0)

    # ---- FIG 1: cleaning funnel -----------------------------------------------------------------
    stages = [("Raw (all routes)", funnel["raw"]), ("Route 801", funnel["r801"]),
              ("No mid-trip reassignment", funnel["route_match"]), ("Import error-free", funnel["import_ok"]),
              ("Trip error-free", funnel["trip_ok"]), ("Valid stop ID", funnel["bs_ok"]),
              ("Direction 6", funnel["dir6"])]
    labels = [s[0] for s in stages]; vals = [s[1] for s in stages]
    fig, ax = plt.subplots(figsize=S.WIDE_TALL)
    y = np.arange(len(vals))[::-1]
    cols = [S.CONTEXT] + [S.PRIMARY]*(len(vals)-2) + [S.CTRL_ACCENT]
    ax.barh(y, vals, color=cols, edgecolor="white", linewidth=0.5)
    for i, v in enumerate(vals):
        drop = "" if i == 0 else f"  (\u2212{vals[i-1]-v:,})"
        ax.text(v + max(vals)*0.01, y[i], f"{v:,}{drop}", va="center", fontsize=7.5)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    ax.set_xlabel("records remaining")
    ax.set_xlim(0, max(vals)*1.20); ax.grid(axis="x")
    S.save(fig, "fig_funnel", OUT)

    # ---- FIG 2: route selection + 801 direction split -------------------------------------------
    top = sorted(by_route_ons.items(), key=lambda kv: kv[1], reverse=True)[:12]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=S.TWO, gridspec_kw={"width_ratios": [2, 1]})
    names = [k for k, _ in top]; bo = [v for _, v in top]
    a1.bar(range(len(names)), bo, color=[S.CTRL_ACCENT if n == "801" else S.PRIMARY for n in names],
           edgecolor="white", linewidth=0.4)
    a1.set_xticks(range(len(names))); a1.set_xticklabels(names, rotation=45, ha="right")
    a1.set_ylabel("total boardings"); a1.set_xlabel("route")
    dirs = sorted(d801.items(), key=lambda kv: kv[0])
    a2.bar(range(len(dirs)), [v for _, v in dirs],
           color=[S.CTRL_ACCENT if k == "6" else S.CONTEXT for k, _ in dirs], edgecolor="white", linewidth=0.4)
    a2.set_xticks(range(len(dirs))); a2.set_xticklabels([f"dir {k}" for k, _ in dirs])
    a2.set_ylabel("boardings"); a2.set_xlabel("direction (route 801)")
    S.save(fig, "fig_route_selection", OUT)

    # ---- FIG 3: raw vs clean distributions ------------------------------------------------------
    fields = [(raw801["dwell"], clean["dwell_time"].values, "Dwell time (s)", 120),
              (raw801["rev"], clean["rev_seconds"].values, "Segment revenue time (s)", 600),
              (raw801["ons"], clean["ons"].values, "Boardings per stop-event", 20)]
    fig, axs = plt.subplots(1, 3, figsize=(5.9, 2.4))
    for ax, (rawv, clnv, lab, xhi) in zip(axs, fields):
        rawv = rawv[np.isfinite(rawv)]; clnv = clnv[np.isfinite(clnv)]
        bins = np.linspace(0, xhi, 40)
        ax.hist(np.clip(rawv, 0, xhi), bins=bins, density=True, alpha=0.55, color=S.CONTEXT, label="raw 801")
        ax.hist(np.clip(clnv, 0, xhi), bins=bins, density=True, alpha=0.65, color=S.PRIMARY, label="cleaned dir-6")
        ax.axvline(np.median(clnv), color=S.LINE, ls="--", lw=1.1, label=f"median {np.median(clnv):.0f}")
        ax.set_xlabel(lab); ax.grid(alpha=0.2)
        ax.legend(fontsize=6.5, loc="upper right")
    axs[0].set_ylabel("density")
    S.save(fig, "fig_distributions", OUT)

    # ---- FIG 4: per-stop demand profile ---------------------------------------------------------
    st = pd.read_csv("sim_inputs/stops.csv", dtype={"bs_id": str})
    corr = [l.strip() for l in open("corridor.txt") if l.strip()]
    st = st.set_index("bs_id").loc[corr].reset_index()
    fig, ax = plt.subplots(figsize=S.WIDE)
    x = np.arange(len(st))
    ax.bar(x, st["mean_boardings"], color=[S.CTRL_ACCENT if b in CONTROL else S.PRIMARY for b in st["bs_id"]],
           edgecolor="white", linewidth=0.4, label="mean boardings")
    ax.plot(x, st["mean_alightings"], color=S.LINE, marker="o", ms=2.5, lw=1.0, label="mean alightings")
    ax.set_xticks(x); ax.set_xticklabels(st["bs_id"], rotation=90, fontsize=6)
    ax.set_ylabel("passengers / stop-event"); ax.set_xlabel("stop (corridor order; orange = control stop)")
    ax.legend(); ax.grid(axis="y")
    S.save(fig, "fig_demand_profile", OUT)

    # ---- FIG 5: corridor geography --------------------------------------------------------------
    co = pd.read_csv("sim_inputs/stop_coordinates.csv", dtype={"bs_id": str}).set_index("bs_id")
    co = co.loc[[b for b in corr if b in co.index]]
    sz = (st.set_index("bs_id").loc[co.index, "mean_boardings"].values + 0.5) * 45
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    ax.plot(co["mean_lon"], co["mean_lat"], color=S.CONTEXT, lw=1, zorder=1)
    ax.scatter(co["mean_lon"], co["mean_lat"], s=sz, zorder=2, edgecolor="white", linewidth=0.4,
               c=[S.CTRL_ACCENT if b in CONTROL else S.PRIMARY for b in co.index])
    ax.scatter([], [], c=S.CTRL_ACCENT, label="control stop"); ax.scatter([], [], c=S.PRIMARY, label="stop")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude"); ax.legend(); ax.grid(alpha=0.2)
    S.save(fig, "fig_corridor_map", OUT)

    # ---- FIG 6: exclusion composition -----------------------------------------------------------
    drops = [("Reassigned mid-trip", funnel["r801"] - funnel["route_match"]),
             ("Import error", funnel["route_match"] - funnel["import_ok"]),
             ("Trip import error", funnel["import_ok"] - funnel["trip_ok"]),
             ("Invalid stop ID", funnel["trip_ok"] - funnel["bs_ok"]),
             ("Wrong direction", funnel["bs_ok"] - funnel["dir6"])]
    dn = [d[0] for d in drops]; dv = [d[1] for d in drops]
    fig, ax = plt.subplots(figsize=S.WIDE)
    ax.bar(range(len(dn)), dv, color=S.GREY, edgecolor="white", linewidth=0.4)
    for i, v in enumerate(dv): ax.text(i, v + max(dv)*0.01, f"{v:,}", ha="center", fontsize=7)
    ax.set_xticks(range(len(dn))); ax.set_xticklabels(dn, rotation=15, ha="right")
    ax.set_ylabel("records removed"); ax.grid(axis="y")
    S.save(fig, "fig_exclusions", OUT)

    # ---- FIG 7: temporal coverage ---------------------------------------------------------------
    try:
        dt = pd.to_datetime(clean["transit_date_time"], errors="coerce")
        mc = dt.dt.to_period("M").astype(str).value_counts().sort_index()
        fig, ax = plt.subplots(figsize=S.WIDE)
        ax.bar(range(len(mc)), mc.values, color=S.PRIMARY, edgecolor="white", linewidth=0.4)
        ax.set_xticks(range(len(mc))); ax.set_xticklabels(mc.index, rotation=30, ha="right")
        ax.set_ylabel("clean stop-events"); ax.set_xlabel("month"); ax.grid(axis="y")
        S.save(fig, "fig_temporal", OUT)
    except Exception as e:
        print("temporal fig skipped:", e)

    print(f"\nfunnel: raw={funnel['raw']:,} -> 801={funnel['r801']:,} -> dir6={funnel['dir6']:,} (expect 229,421)")
    print("stops in demand profile:", len(st))


if __name__ == "__main__":
    main()
