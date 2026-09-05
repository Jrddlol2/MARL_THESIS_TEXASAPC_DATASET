# -*- coding: utf-8 -*-
"""Weather-dataset figures (MSA1) — NOAA LCDv2 join, publication style (_figstyle).

Builds from the processed NOAA weather (data/processed/texas_capmetro/) and the verified join audit
(data/audit/texas_capmetro/weather_join_audit.json). Honest boundary: ordinary rain is OBSERVED here;
the simulator's weather stressor is still synthetic; an empirical multiplier needs stratified modelling
(MSA2). Saves PDF+PNG to results/figures/weather/.  Run from starter/ :  python scripts/figures_weather.py
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _figstyle as S

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # repo root
WCSV = os.path.join(ROOT, "data/processed/texas_capmetro/weather_camp_mabry_2021_jul_dec.csv")
AUD  = os.path.join(ROOT, "data/audit/texas_capmetro/weather_join_audit.json")
OUT  = "results/figures/weather"; os.makedirs(OUT, exist_ok=True)


def main():
    S.apply()
    import matplotlib.pyplot as plt
    A = json.load(open(AUD))
    c = A["counts"]; m = A["descriptive_unadjusted_segment_medians"]
    APC = c["apc_rows"]; RAIN = c["primary_rain_exposed_rows"]; DRY = APC - RAIN
    AGREE = c["station_rain_flag_agreement"]; DIS = c["station_rain_flag_disagreement"]
    GAPMED = A["median_absolute_join_delta_minutes"]; GAPP95 = A["p95_absolute_join_delta_minutes"]

    # ---- FIG 1: precipitation over the study window --------------------------------------------
    w = pd.read_csv(WCSV)
    w["t"] = pd.to_datetime(w["timestamp_austin"], utc=True, errors="coerce")
    w["p"] = pd.to_numeric(w["precipitation"], errors="coerce").fillna(0.0)
    daily = w.set_index("t")["p"].resample("D").sum()
    fig, ax = plt.subplots(figsize=S.WIDE)
    ax.bar(daily.index, daily.values, width=1.0, color=S.PRIMARY, edgecolor="none")
    ax.set_ylabel("daily precipitation (LCDv2)"); ax.set_xlabel("2021 (July–December)")
    ax.grid(axis="y")
    S.save(fig, "fig_weather_precip", OUT)

    # ---- FIG 2: rain exposure of the cleaned events -------------------------------------------
    fig, ax = plt.subplots(figsize=(4.2, 4.0))
    ax.pie([DRY, RAIN], colors=[S.CONTEXT, S.ORANGE], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.42, edgecolor="white"))
    ax.text(0, 0.12, f"{RAIN:,}", ha="center", va="center", fontsize=15, color=S.ORANGE, fontweight="bold")
    ax.text(0, -0.14, f"rain-exposed\nof {APC:,} events", ha="center", va="center", fontsize=8, color="#444")
    ax.legend([f"dry ({DRY:,})", f"rain-exposed ({RAIN:,})"], loc="lower center",
              bbox_to_anchor=(0.5, -0.12), ncol=1); ax.set_aspect("equal")
    S.save(fig, "fig_weather_exposure", OUT)

    # ---- FIG 3: descriptive dry vs rain segment time -----------------------------------------
    dry_med, rain_med = m["dry_median_rev_seconds"], m["rain_median_rev_seconds"]
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    ax.bar([0, 1], [dry_med, rain_med], color=[S.CONTEXT, S.ORANGE], width=0.6, edgecolor="white")
    for x, v in [(0, dry_med), (1, rain_med)]:
        ax.text(x, v + 0.4, f"{v:.0f} s", ha="center", fontsize=9)
    ax.set_xticks([0, 1]); ax.set_xticklabels([f"dry\n({m['dry_positive_time_distance_segments']:,} seg)",
                                               f"rain\n({m['rain_positive_time_distance_segments']:,} seg)"])
    ax.set_ylabel("median segment revenue time (s)"); ax.set_ylim(190, rain_med + 6); ax.grid(axis="y")
    S.save(fig, "fig_weather_traveltime", OUT)

    # ---- FIG 4: join validity (coverage + station agreement) ---------------------------------
    fig, ax = plt.subplots(figsize=S.WIDE)
    labels = ["APC events\njoined to NOAA", "Two stations\nagree on rain"]
    vals = [100.0, 100.0 * AGREE / APC]
    ax.barh([1, 0], vals, color=[S.PRIMARY, S.GREEN], edgecolor="white", height=0.55)
    for y, v in [(1, vals[0]), (0, vals[1])]:
        ax.text(v - 3, y, f"{v:.1f}%", va="center", ha="right", color="white", fontsize=10, fontweight="bold")
    ax.set_yticks([1, 0]); ax.set_yticklabels(labels); ax.set_xlim(0, 100); ax.set_xlabel("percent of 229,421 events")
    ax.grid(axis="x")
    ax.text(0.99, -0.28, f"nearest reading within 90 min · median gap {GAPMED:.1f} min · 95% within {GAPP95:.1f} min",
            transform=ax.transAxes, ha="right", fontsize=7.5, style="italic", color="#555")
    S.save(fig, "fig_weather_join", OUT)

    # ---- captions -----------------------------------------------------------------------------
    caps = [
      ("fig_weather_precip.png", "Daily precipitation at Camp Mabry (NOAA LCDv2) across the July–December 2021 study window; rain is episodic, concentrated in a few storm days."),
      ("fig_weather_exposure.png", f"Weather exposure of the cleaned events: {RAIN:,} of {APC:,} stop-events ({100*RAIN/APC:.1f}%) occurred under observed rain."),
      ("fig_weather_traveltime.png", f"Descriptive median segment time, dry ({dry_med:.0f} s) vs rain ({rain_med:.0f} s). UNADJUSTED and NOT a causal weather effect — a multiplier requires segment, time-of-day, and day-type controls (MSA2). The simulator's weather stressor remains synthetic."),
      ("fig_weather_join.png", f"Join validity: 100% of {APC:,} events matched a NOAA reading within 90 minutes (median gap {GAPMED:.1f} min); the two stations agree on the rain flag for {100*AGREE/APC:.0f}% of events."),
    ]
    with open(f"{OUT}/CAPTIONS.md", "w", encoding="utf-8") as fh:
        fh.write("# Weather-dataset figures — captions\n\n")
        for f, cp in caps: fh.write(f"- **{f}** — {cp}\n")
    print("wrote weather figures to", OUT)
    for f, _ in caps: print("  ", f)
    print(f"exposure: {RAIN:,}/{APC:,} rain  |  dry {dry_med}s vs rain {rain_med}s  |  agree {100*AGREE/APC:.1f}%")


if __name__ == "__main__":
    main()
