# -*- coding: utf-8 -*-
"""Data-cleaning visualization figures (MSA1). Streams the raw APC CSV ONCE to compute the cleaning
funnel, by-route selection, and raw-vs-clean distributions, then builds per-stop / geography / temporal
figures from the cleaned dir-6 subset + committed inputs. Saves PNGs to results/figures/datacleaning/.

Run from starter/ :  python scripts/figures_datacleaning.py
The raw pass is cached to results/figures/datacleaning/_cache.json so re-runs are instant.
"""
import os, sys, json, math
import numpy as np, pandas as pd

RAW = r"C:\Users\jared\Desktop\THESIS\APC_Raw_July_2021_-_December_2021_20260824.csv"
OUT = "results/figures/datacleaning"; os.makedirs(OUT, exist_ok=True)
CACHE = f"{OUT}/_cache.json"
CONTROL = {"5280", "5857", "5859", "5867", "4046"}
NEED = ["route_id", "current_route_id", "import_error", "import_trip_error", "bs_id",
        "direction_code_id", "actual_sequence", "ons", "offs", "dwell_time", "rev_seconds",
        "rev_distance", "transit_date_time"]


def stream_raw():
    """One pass over the 3.7 GB raw CSV. Returns funnel counts, by-route boardings, 801 direction split,
    raw-vs-clean numeric samples, and the cleaned dir-6 subset (as a DataFrame)."""
    n_raw = 0
    funnel = dict(raw=0, r801=0, route_match=0, import_ok=0, trip_ok=0, bs_ok=0, dir6=0)
    by_route_cnt, by_route_ons = {}, {}
    d801 = {}                                   # direction -> boardings within route 801
    raw801 = {"dwell": [], "rev": [], "ons": []}
    clean_parts = []
    ci = 0
    for ch in pd.read_csv(RAW, usecols=NEED, dtype=str, chunksize=1_000_000, na_filter=False):
        ci += 1; n_raw += len(ch)
        # by-route (all rows): count + boardings
        onsn = pd.to_numeric(ch["ons"], errors="coerce").fillna(0)
        for rid, g in ch.groupby("route_id"):
            by_route_cnt[rid] = by_route_cnt.get(rid, 0) + len(g)
        rs = onsn.groupby(ch["route_id"]).sum()
        for rid, v in rs.items():
            by_route_ons[rid] = by_route_ons.get(rid, 0.0) + float(v)
        # cumulative funnel
        m1 = ch["route_id"] == "801"
        m2 = m1 & (ch["route_id"] == ch["current_route_id"])
        m3 = m2 & (ch["import_error"] == "0")
        m4 = m3 & (ch["import_trip_error"] == "0")
        m5 = m4 & (ch["bs_id"] != "0")
        m6 = m5 & (ch["direction_code_id"] == "6")
        funnel["r801"] += int(m1.sum()); funnel["route_match"] += int(m2.sum())
        funnel["import_ok"] += int(m3.sum()); funnel["trip_ok"] += int(m4.sum())
        funnel["bs_ok"] += int(m5.sum()); funnel["dir6"] += int(m6.sum())
        # 801 direction split (boardings)
        b801 = ch[m1]
        if len(b801):
            ons801 = pd.to_numeric(b801["ons"], errors="coerce").fillna(0)
            for dirc, v in ons801.groupby(b801["direction_code_id"]).sum().items():
                d801[dirc] = d801.get(dirc, 0.0) + float(v)
            # raw (pre-clean) 801 distributions
            raw801["dwell"].append(pd.to_numeric(b801["dwell_time"], errors="coerce").values)
            raw801["rev"].append(pd.to_numeric(b801["rev_seconds"], errors="coerce").values)
            raw801["ons"].append(ons801.values)
        # collect the cleaned dir-6 rows
        if int(m6.sum()):
            clean_parts.append(ch[m6].copy())
        print(f"  chunk {ci}: cumulative raw={n_raw:,}  dir6_clean={funnel['dir6']:,}", flush=True)
    funnel["raw"] = n_raw
    clean = pd.concat(clean_parts, ignore_index=True)
    raw801 = {k: np.concatenate(v) for k, v in raw801.items()}
    return funnel, by_route_cnt, by_route_ons, d801, raw801, clean


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "axes.titleweight": "bold",
                         "figure.dpi": 150, "savefig.bbox": "tight"})
    NAVY, GOLD, GREY, RED = "#1F3B63", "#E8A33D", "#9AA6B2", "#C0392B"

    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        C = json.load(open(CACHE))
        funnel = C["funnel"]; by_route_ons = C["by_route_ons"]; by_route_cnt = C["by_route_cnt"]
        d801 = C["d801"]; raw801 = {k: np.array(v) for k, v in C["raw801_sample"].items()}
        clean = pd.read_csv(f"{OUT}/_clean_dir6.csv", dtype=str)
        print("loaded cache")
    else:
        funnel, by_route_cnt, by_route_ons, d801, raw801, clean = stream_raw()
        clean.to_csv(f"{OUT}/_clean_dir6.csv", index=False)
        json.dump({"funnel": funnel, "by_route_ons": by_route_ons, "by_route_cnt": by_route_cnt,
                   "d801": d801,
                   "raw801_sample": {k: v[~np.isnan(v)][::40].tolist() for k, v in raw801.items()}},
                  open(CACHE, "w"), indent=1)
        print("wrote cache")

    assert funnel["dir6"] == 229421, f"funnel end {funnel['dir6']} != 229421 — filter drifted"

    # numeric views of the clean subset
    for c in ["actual_sequence", "ons", "offs", "dwell_time", "rev_seconds", "rev_distance"]:
        clean[c] = pd.to_numeric(clean[c], errors="coerce")
    clean["run_seconds"] = (clean["rev_seconds"] - clean["dwell_time"]).clip(lower=0)

    # ---- FIG 1: cleaning funnel -----------------------------------------------------------------
    stages = [("Raw (all routes)", funnel["raw"]), ("Route 801", funnel["r801"]),
              ("Route = scheduled", funnel["route_match"]), ("Import OK", funnel["import_ok"]),
              ("Trip import OK", funnel["trip_ok"]), ("bs_id valid", funnel["bs_ok"]),
              ("Direction 6", funnel["dir6"])]
    labels = [s[0] for s in stages]; vals = [s[1] for s in stages]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    y = np.arange(len(vals))[::-1]
    cols = [GREY] + [NAVY]*(len(vals)-2) + [GOLD]
    ax.barh(y, vals, color=cols, edgecolor="white")
    for i, v in enumerate(vals):
        drop = "" if i == 0 else f"  (−{vals[i-1]-v:,})"
        ax.text(v + max(vals)*0.01, y[i], f"{v:,}{drop}", va="center", fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    ax.set_xlabel("records remaining"); ax.set_title("Data cleaning funnel: raw APC → Route 801, direction 6")
    ax.set_xlim(0, max(vals)*1.18); ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, -0.02, f"Six rules applied in order; final subset = {funnel['dir6']:,} stop-events.",
             ha="center", fontsize=8, style="italic", color="#555")
    fig.savefig(f"{OUT}/fig_funnel.png"); plt.close(fig)

    # ---- FIG 2: route selection + 801 direction split -------------------------------------------
    top = sorted(by_route_ons.items(), key=lambda kv: kv[1], reverse=True)[:12]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [2, 1]})
    names = [k for k, _ in top]; bo = [v for _, v in top]
    cols = [GOLD if n == "801" else NAVY for n in names]
    a1.bar(range(len(names)), bo, color=cols, edgecolor="white")
    a1.set_xticks(range(len(names))); a1.set_xticklabels(names, rotation=45, ha="right")
    a1.set_ylabel("total boardings (ons)"); a1.set_title("Boardings by route (Route 801 selected)")
    a1.spines[["top", "right"]].set_visible(False)
    dirs = sorted(d801.items(), key=lambda kv: kv[0])
    dn = [f"dir {k}" for k, _ in dirs]; dv = [v for _, v in dirs]
    dcol = [GOLD if k == "6" else GREY for k, _ in dirs]
    a2.bar(range(len(dn)), dv, color=dcol, edgecolor="white")
    a2.set_xticks(range(len(dn))); a2.set_xticklabels(dn)
    a2.set_title("Route 801 boardings by direction"); a2.set_ylabel("boardings")
    a2.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Route & direction selection", fontweight="bold")
    fig.text(0.5, -0.02, "Route 801 ≈ 810,309 boardings over 184 service days; direction 6 = 229,421 clean stop-events.",
             ha="center", fontsize=8, style="italic", color="#555")
    fig.savefig(f"{OUT}/fig_route_selection.png"); plt.close(fig)

    # ---- FIG 3: raw vs clean distributions ------------------------------------------------------
    fields = [("dwell_time", raw801["dwell"], clean["dwell_time"].values, "Dwell time (s)", 120),
              ("rev_seconds", raw801["rev"], clean["rev_seconds"].values, "Segment revenue time (s)", 600),
              ("ons", raw801["ons"], clean["ons"].values, "Boardings per stop-event", 20)]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    for ax, (nm, rawv, clnv, lab, xhi) in zip(axs, fields):
        rawv = rawv[np.isfinite(rawv)]; clnv = clnv[np.isfinite(clnv)]
        bins = np.linspace(0, xhi, 40)
        ax.hist(np.clip(rawv, 0, xhi), bins=bins, density=True, alpha=0.5, color=GREY, label=f"raw 801 (n={len(rawv):,})")
        ax.hist(np.clip(clnv, 0, xhi), bins=bins, density=True, alpha=0.6, color=NAVY, label=f"cleaned dir-6 (n={len(clnv):,})")
        ax.axvline(np.median(clnv), color=RED, ls="--", lw=1.4, label=f"clean median {np.median(clnv):.0f}")
        ax.set_title(lab); ax.set_xlabel(lab); ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=7)
    axs[0].set_ylabel("density")
    fig.suptitle("Raw vs cleaned distributions — long tails motivate the filters and the median aggregation", fontweight="bold")
    fig.savefig(f"{OUT}/fig_distributions.png"); plt.close(fig)

    # ---- FIG 4: per-stop demand profile (from committed stops.csv, corridor order) --------------
    st = pd.read_csv("sim_inputs/stops.csv", dtype={"bs_id": str})
    corr = [l.strip() for l in open("corridor.txt") if l.strip()]
    st = st.set_index("bs_id").loc[corr].reset_index()
    fig, ax = plt.subplots(figsize=(11, 4.2))
    x = np.arange(len(st))
    cols = [GOLD if b in CONTROL else NAVY for b in st["bs_id"]]
    ax.bar(x, st["mean_boardings"], color=cols, edgecolor="white", label="mean boardings")
    ax.plot(x, st["mean_alightings"], color=RED, marker="o", ms=3, lw=1.2, label="mean alightings")
    ax.set_xticks(x); ax.set_xticklabels(st["bs_id"], rotation=90, fontsize=7)
    ax.set_ylabel("passengers / stop-event"); ax.set_xlabel("stop (corridor order)")
    ax.set_title("Per-stop demand profile (gold = the 5 control stops)")
    ax.legend(); ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(f"{OUT}/fig_demand_profile.png"); plt.close(fig)

    # ---- FIG 5: corridor geography --------------------------------------------------------------
    co = pd.read_csv("sim_inputs/stop_coordinates.csv", dtype={"bs_id": str}).set_index("bs_id")
    co = co.loc[[b for b in corr if b in co.index]]
    sz = (st.set_index("bs_id").loc[co.index, "mean_boardings"].values + 0.5) * 60
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.plot(co["mean_lon"], co["mean_lat"], color=GREY, lw=1, zorder=1)
    cc = [GOLD if b in CONTROL else NAVY for b in co.index]
    ax.scatter(co["mean_lon"], co["mean_lat"], s=sz, c=cc, edgecolor="white", zorder=2)
    ax.scatter([], [], c=GOLD, label="control stop"); ax.scatter([], [], c=NAVY, label="stop")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.set_title("Route 801 dir-6 corridor (26 stops; marker size = demand)")
    ax.legend(); ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(f"{OUT}/fig_corridor_map.png"); plt.close(fig)

    # ---- FIG 6: exclusion composition (within route 801) ----------------------------------------
    drops = [("Route ≠ scheduled", funnel["r801"] - funnel["route_match"]),
             ("Import error", funnel["route_match"] - funnel["import_ok"]),
             ("Trip import error", funnel["import_ok"] - funnel["trip_ok"]),
             ("bs_id = 0 (unknown)", funnel["trip_ok"] - funnel["bs_ok"]),
             ("Direction ≠ 6", funnel["bs_ok"] - funnel["dir6"])]
    dn = [d[0] for d in drops]; dv = [d[1] for d in drops]
    fig, ax = plt.subplots(figsize=(8.5, 4))
    ax.bar(range(len(dn)), dv, color=RED, edgecolor="white", alpha=0.8)
    for i, v in enumerate(dv): ax.text(i, v + max(dv)*0.01, f"{v:,}", ha="center", fontsize=8)
    ax.set_xticks(range(len(dn))); ax.set_xticklabels(dn, rotation=20, ha="right")
    ax.set_ylabel("records removed"); ax.set_title("Why records were dropped (within Route 801)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(f"{OUT}/fig_exclusions.png"); plt.close(fig)

    # ---- FIG 7: temporal coverage ---------------------------------------------------------------
    try:
        dt = pd.to_datetime(clean["transit_date_time"], errors="coerce")
        month = dt.dt.to_period("M").astype(str)
        mc = month.value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(8.5, 3.8))
        ax.bar(range(len(mc)), mc.values, color=NAVY, edgecolor="white")
        ax.set_xticks(range(len(mc))); ax.set_xticklabels(mc.index, rotation=30, ha="right")
        ax.set_ylabel("clean stop-events"); ax.set_title("Temporal coverage — cleaned dir-6 (Jul–Dec 2021)")
        ax.spines[["top", "right"]].set_visible(False)
        fig.savefig(f"{OUT}/fig_temporal.png"); plt.close(fig)
    except Exception as e:
        print("temporal fig skipped:", e)

    # ---- caption sheet --------------------------------------------------------------------------
    caps = [
        ("fig_funnel.png", f"Cleaning funnel: {funnel['raw']:,} raw records reduce to {funnel['dir6']:,} Route-801/dir-6 stop-events through six rules."),
        ("fig_route_selection.png", "Route 801 is the highest-boarding corridor; direction 6 (229,421 events) is the study direction."),
        ("fig_distributions.png", "Raw vs cleaned dwell / segment-time / boardings: long right tails motivate the filters and the median aggregation."),
        ("fig_demand_profile.png", "Per-stop mean boardings/alightings along the 26-stop corridor; the five control stops (gold) sit at demand onsets."),
        ("fig_corridor_map.png", "Geographic layout of the 26 dir-6 stops (marker size = demand); the real corridor shape."),
        ("fig_exclusions.png", "Composition of removed Route-801 records by reason (route mismatch, import errors, unknown stop, wrong direction)."),
        ("fig_temporal.png", "Cleaned dir-6 stop-events per month across the Jul–Dec 2021 window (184 service days)."),
    ]
    with open(f"{OUT}/CAPTIONS.md", "w", encoding="utf-8") as fh:
        fh.write("# Data-cleaning figures — captions\n\n")
        for f, c in caps: fh.write(f"- **{f}** — {c}\n")
    print("\nWROTE:")
    for f, _ in caps: print("  ", f"{OUT}/{f}")
    print(f"funnel: raw={funnel['raw']:,} -> 801={funnel['r801']:,} -> dir6={funnel['dir6']:,} (expect 229,421)")
    print("stops in demand profile:", len(st))


if __name__ == "__main__":
    main()
