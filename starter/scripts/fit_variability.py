"""
=============================================================================
 FIT THE SIMULATOR'S VARIABILITY FROM THE APC DATA   (Week 2, items 5-8)
=============================================================================

WHAT IT DOES
    Reads the 229,421 clean direction-6 stop events and measures, from data,
    everything the simulator used to ASSUME:

      1. Passenger demand per stop, by time of day and day type
      2. Dwell time: how many seconds each boarding / alighting adds, and how
         much dwell varies beyond that
      3. Running time between stops, and how much it varies (dry weather only)
      4. How late or early buses actually start their trips (dispatch spread)
      5. The ordinary-rain effect on running time, compared within the same
         segment, time of day and day type
      6. The headway CV of real buses, measured the same way as the simulator
      7. A split of weekday service days into CALIBRATION days (alternating)
         and TEST days (the rest), so the corridor can be tested on unseen days
      8. How often real buses serve each stop (a record exists only when the
         doors open), so demand can be counted PER TRIP, not per recorded stop

PER TRIP, NOT PER RECORDED STOP
    APC writes a record only when the doors open. "Mean boardings per record"
    therefore overstates what an average bus picks up at a stop that half the
    buses skip. The simulator uses boardings per scheduled TRIP passing the
    stop: total boardings / trips. A trip "passes" a stop in a time window if its
    scheduled start plus the median time to reach that stop falls in the window.

WHY SPREADS ARE FITTED FROM NEIGHBOURING BUSES
    Bunching comes from DIFFERENCES between one bus and the next. A late
    afternoon slows every bus together, which does not bunch them. So the
    simulator's random spreads (dispatch, running time, dwell noise) are fitted
    from pairs of buses scheduled one headway apart on the same day: the spread
    of the difference, divided by sqrt(2), is the independent per-bus spread
    that reproduces it.

HOW EVENTS ARE USED
    A "run" is the time from the bus closing its doors at stop i to opening
    them at stop i+1. It is only used when the bus's NEXT record really is
    stop i+1. (A bus that skipped a stop has no record there, and its time
    would span two segments -- this was risk R9.)

TIME PERIODS  (the 10-minute service applies on weekdays 07:00-18:00)
    ALL = 07-18,  AM = 07-10,  MID = 10-15,  PM = 15-18

INPUT    data/raw/capmetro/route_801_direction_6_clean.csv
         data/processed/texas_capmetro/weather_camp_mabry_2021_jul_dec.csv
         corridor.txt
OUTPUT   sim_inputs/fitted/stop_params.csv        per period x stop
         sim_inputs/fitted/model_params.json      dwell model, dispatch, rain, demand spread
         sim_inputs/fitted/dispatch_deviation.csv sample of start deviations (s)
         sim_inputs/fitted/service_days.csv       calibration / test split
         sim_inputs/fitted/day_type_summary.csv   demand by day type and period
         results/validation/rain_effect_strata.csv
         results/validation/observed_headway_cv.csv

RUN      python scripts/fit_variability.py          (from starter/, ~2 min)
         python scripts/fit_variability.py --split chronological   (robustness check:
             early days calibrate, later days test; the study uses alternating days)
=============================================================================
"""

import json
import os
import sys

import numpy as np
import pandas as pd

# How weekday service days are split into calibration and test days.
#   python scripts/fit_variability.py                          alternating days (the study's split)
#   python scripts/fit_variability.py --split chronological    early days calibrate, later days test
SPLIT = "chronological" if "--split" in sys.argv and "chronological" in sys.argv else "alternating"

APC_FILE = "../data/raw/capmetro/route_801_direction_6_clean.csv"
WEATHER_FILE = "../data/processed/texas_capmetro/weather_camp_mabry_2021_jul_dec.csv"
OUT_DIR = "sim_inputs/fitted"
VALIDATION_DIR = "results/validation"

H0 = 600                                  # weekday 07-18 scheduled headway (s)
PERIODS = {"ALL": (7, 18), "AM": (7, 10), "MID": (10, 15), "PM": (15, 18)}
DAY_TYPE_NAMES = {"1": "weekday", "2": "saturday", "3": "sunday_holiday"}
RAIN_HOUR_BANDS = [0, 7, 10, 15, 18, 24]  # strata for the rain comparison
RANDOM = np.random.default_rng(2026)


def robust_log_sd(values):
    """Spread of log(values) that ignores extreme outliers: IQR / 1.349."""
    logs = np.log(values)
    q75, q25 = np.percentile(logs, [75, 25])
    return float((q75 - q25) / 1.349)


def in_hours(hours, first, last):
    return (hours >= first) & (hours < last)


# =============================================================================
# 0. LOAD AND PREPARE
# =============================================================================
def load_events():
    columns = ["open_date_time", "apc_date_time", "transit_date_time", "day_type_vs", "bs_id",
               "ext_trip_id", "vehicle_id", "act_trip_start_time", "start_trip_time", "ons", "offs",
               "dwell_time"]
    events = pd.read_csv(APC_FILE, usecols=columns, dtype=str)
    events["stop"] = events["bs_id"].astype(int)
    events["open"] = pd.to_datetime(events["open_date_time"], format="%Y%m%d%H%M%S", errors="coerce")
    events["close"] = pd.to_datetime(events["apc_date_time"], format="%Y%m%d%H%M%S", errors="coerce")
    events["day"] = events["transit_date_time"].str[:8]
    events["day_type"] = events["day_type_vs"].map(DAY_TYPE_NAMES)
    for column in ["ons", "offs", "dwell_time"]:
        events[column] = pd.to_numeric(events[column], errors="coerce")
    events["hour"] = events["open"].dt.hour
    events["trip"] = events["day"] + "|" + events["ext_trip_id"].fillna("") + "|" + events["vehicle_id"]

    # Scheduled trip start: the date of the actual start + the scheduled clock time.
    actual_start = pd.to_datetime(events["act_trip_start_time"], format="%Y%m%d%H%M%S", errors="coerce")
    clock = events["start_trip_time"].str[8:14]
    scheduled = pd.to_datetime(actual_start.dt.strftime("%Y%m%d") + clock, format="%Y%m%d%H%M%S", errors="coerce")
    # a trip scheduled just before midnight but started just after (or the reverse)
    difference = (actual_start - scheduled).dt.total_seconds()
    scheduled = scheduled.where(difference < 43200, scheduled + pd.Timedelta(days=1))
    scheduled = scheduled.where(difference > -43200, scheduled - pd.Timedelta(days=1))
    events["scheduled_start"] = scheduled
    events = events.dropna(subset=["open", "close"])
    return events.sort_values(["trip", "close"]).reset_index(drop=True)


def add_runs(events, corridor):
    """Attach the run time to the next stop, only when the next record IS the next stop."""
    next_stop_of = {}
    for i in range(len(corridor) - 1):
        next_stop_of[corridor[i]] = corridor[i + 1]
    events["next_record_stop"] = events.groupby("trip")["stop"].shift(-1)
    events["next_record_open"] = events.groupby("trip")["open"].shift(-1)
    consecutive = events["stop"].map(next_stop_of) == events["next_record_stop"]
    run = (events["next_record_open"] - events["close"]).dt.total_seconds()
    events["run_s"] = run.where(consecutive & (run > 0))
    return events


def add_rain(events):
    """Nearest Camp Mabry observation within 90 minutes (same rule as the pipeline)."""
    weather = pd.read_csv(WEATHER_FILE, usecols=["timestamp_utc", "rain_flag"])
    weather["obs_time"] = pd.to_datetime(weather["timestamp_utc"], utc=True)
    weather = weather.sort_values("obs_time")[["obs_time", "rain_flag"]]
    local = events["open"].dt.tz_localize("America/Chicago", ambiguous=True, nonexistent="shift_forward")
    events["event_time"] = local.dt.tz_convert("UTC")
    order = events["event_time"].argsort()
    joined = pd.merge_asof(events.iloc[order][["event_time"]].reset_index(), weather,
                           left_on="event_time", right_on="obs_time", direction="nearest",
                           tolerance=pd.Timedelta(minutes=90))
    events.loc[joined["index"].values, "rain"] = joined["rain_flag"].values
    return events


def split_days(events, how=SPLIT):
    """Weekday service days into calibration and test days.

    "alternating" (what the study uses): 1st, 3rd, 5th ... = calibration; 2nd, 4th ... = test, so both
    sets hold the same months and weekdays. "chronological": the first half of the days calibrate and
    the later half test -- kept as a robustness check, since ridership drifts over the six months.
    """
    weekdays = sorted(events.loc[events["day_type"] == "weekday", "day"].unique())
    rows = []
    for k in range(len(weekdays)):
        if how == "chronological":
            calibration = k < len(weekdays) / 2
        else:
            calibration = k % 2 == 0
        rows.append((weekdays[k], "calibration" if calibration else "test"))
    return pd.DataFrame(rows, columns=["day", "split"])


# =============================================================================
# 1-3. PER-STOP PARAMETERS
# =============================================================================
def trips_passing(events, stop, day_set, first, last):
    """Number of scheduled trips that pass `stop` between `first` and `last` o'clock
    on the given weekdays: scheduled start + median time to reach the stop."""
    here = events[(events["stop"] == stop) & events["scheduled_start"].notna()]
    offset = (here["open"] - here["scheduled_start"]).dt.total_seconds().median()
    trips = events[(events["day_type"] == "weekday") & events["day"].isin(day_set)
                   & events["scheduled_start"].notna()].drop_duplicates("trip")
    at_stop = trips["scheduled_start"] + pd.Timedelta(seconds=float(offset))
    hours = at_stop.dt.hour
    return int((in_hours(hours, first, last)).sum())


def stop_parameters(events, corridor, days):
    calibration_days = set(days.loc[days["split"] == "calibration", "day"])
    test_days = set(days.loc[days["split"] == "test", "day"])
    rows = []
    for period, (first, last) in PERIODS.items():
        weekday = events[(events["day_type"] == "weekday") & in_hours(events["hour"], first, last)]
        train = weekday[weekday["day"].isin(calibration_days)]
        test = weekday[weekday["day"].isin(test_days)]
        for stop in corridor + [5304]:
            here = train[train["stop"] == stop]
            here_test = test[test["stop"] == stop]
            trips = trips_passing(events, stop, calibration_days, first, last)
            trips_test = trips_passing(events, stop, test_days, first, last)
            dry_runs = here.loc[(here["rain"] == 0) & here["run_s"].notna(), "run_s"]
            runs_train = here["run_s"].dropna()
            runs_test = here_test["run_s"].dropna()
            rows.append({
                "period": period,
                "bs_id": stop,
                "events": len(here),
                "mean_boardings": round(here["ons"].mean(), 3),          # per recorded stop
                "mean_alightings": round(here["offs"].mean(), 3),
                "trips": trips,
                "boardings_per_trip": round(here["ons"].sum() / trips, 3) if trips else np.nan,
                "alightings_per_trip": round(here["offs"].sum() / trips, 3) if trips else np.nan,
                "served_share": round(here["trip"].nunique() / trips, 3) if trips else np.nan,
                "served_share_test": round(here_test["trip"].nunique() / trips_test, 3) if trips_test else np.nan,
                "dwell_median_s": round(here["dwell_time"].median(), 1),
                "runs": len(runs_train),
                "run_median_s": round(runs_train.median(), 1) if len(runs_train) else np.nan,
                "run_median_test_s": round(runs_test.median(), 1) if len(runs_test) else np.nan,
                "run_log_sd_dry": round(robust_log_sd(dry_runs / dry_runs.median()), 3) if len(dry_runs) >= 30 else np.nan,
            })
    return pd.DataFrame(rows)


def dwell_model(events, corridor, calibration_days):
    """dwell = intercept + a x boardings + b x alightings, fitted to MEDIANS of
    each (boardings, alightings) cell so a few 10-minute dwells cannot drag it."""
    d = events[(events["day_type"] == "weekday") & in_hours(events["hour"], 7, 18)
               & events["stop"].isin(corridor) & events["day"].isin(calibration_days)]
    d = d.dropna(subset=["dwell_time", "ons", "offs"])
    cells = d.groupby(["ons", "offs"])["dwell_time"].agg(["median", "count"]).reset_index()
    cells = cells[cells["count"] >= 30]
    weights = np.sqrt(cells["count"].values)
    X = np.c_[np.ones(len(cells)), cells["ons"].values, cells["offs"].values]
    coef = np.linalg.lstsq(X * weights[:, None], cells["median"].values * weights, rcond=None)[0]
    predicted = coef[0] + coef[1] * d["ons"] + coef[2] * d["offs"]
    ratio = (d["dwell_time"] / predicted.clip(lower=1.0))
    ratio = ratio[ratio > 0]
    return {
        "intercept_s": round(float(coef[0]), 2),
        "seconds_per_boarding": round(float(coef[1]), 2),
        "seconds_per_alighting": round(float(coef[2]), 2),
        "noise_log_sd": round(robust_log_sd(ratio), 3),
        "dwell_p95_s": round(float(d["dwell_time"].quantile(0.95)), 1),
        "cells_used": int(len(cells)),
        "events_used": int(len(d)),
    }


def demand_spread(events, corridor, calibration_days):
    """Day-to-day spread of total boardings per stop (weekday 07-18), versus
    what pure Poisson randomness would give. > 1 means extra day-to-day variation."""
    d = events[(events["day_type"] == "weekday") & in_hours(events["hour"], 7, 18)
               & events["stop"].isin(corridor) & events["day"].isin(calibration_days)]
    daily = d.groupby(["day", "stop"])["ons"].sum().unstack(fill_value=0)
    ratios = []
    for stop in daily.columns:
        mean, var = daily[stop].mean(), daily[stop].var()
        if mean > 5:
            ratios.append(var / mean)
    return round(float(np.median(ratios)), 2)


# =============================================================================
# 4. PAIRS OF NEIGHBOURING BUSES, AND THE SPREADS FITTED FROM THEM
# =============================================================================
def neighbour_pairs(events, calibration_days):
    """Each weekday 07-18 stop event, joined to the event of the bus scheduled
    ONE HEADWAY LATER at the same stop on the same day (when that bus logged it)."""
    d = events[(events["day_type"] == "weekday") & events["day"].isin(calibration_days)
               & events["scheduled_start"].notna()]
    d = d[in_hours(d["scheduled_start"].dt.hour, 7, 18)]
    d = d.drop_duplicates(["trip", "stop"])
    later = d.copy()
    later["scheduled_start"] = later["scheduled_start"] - pd.Timedelta(seconds=H0)
    columns = ["day", "stop", "scheduled_start", "open", "run_s", "dwell_time", "ons", "offs"]
    pairs = d[columns].merge(later[columns], on=["day", "stop", "scheduled_start"], suffixes=("", "_next"))
    return pairs


def dispatch_deviation(pairs):
    """Gap between neighbouring buses at the first corridor stop, minus one
    headway, divided by sqrt(2): a sample of per-bus start deviations whose
    DIFFERENCES match the observed gaps."""
    first = pairs[pairs["stop"] == 5280]
    gap = (first["open_next"] - first["open"]).dt.total_seconds()
    deviation = (gap - H0) / np.sqrt(2)
    low, high = deviation.quantile([0.01, 0.99])
    deviation = deviation[(deviation >= low) & (deviation <= high)]
    deviation = deviation - deviation.median()
    return deviation.round(0).astype(int)


def scale_dispatch_to_first_stop(deviation, target_cv, buses=18, runs=4000):
    """Shrink or stretch the deviation sample so that the headway CV at the FIRST
    stop -- which depends only on when buses start -- matches the observed
    first-stop CV on the calibration days. Solved by trying scales (bisection)
    on simulated departure times; SUMO is not needed for this."""
    random = np.random.default_rng(7)
    draws = random.choice(deviation.values, size=(runs, buses))
    schedule = np.arange(buses) * H0

    def mean_cv(scale):
        departures = np.sort(schedule + scale * draws, axis=1)
        gaps = np.diff(departures, axis=1)
        return float(np.mean(gaps.std(axis=1) / gaps.mean(axis=1)))

    low, high = 0.0, 2.0
    for _ in range(40):
        middle = (low + high) / 2
        if mean_cv(middle) < target_cv:
            low = middle
        else:
            high = middle
    scale = (low + high) / 2
    return scale, mean_cv(scale)


def pairwise_run_log_sd(pairs, corridor):
    """Per segment: robust spread of log(run of next bus / run of this bus), / sqrt(2)."""
    ok = pairs[(pairs["run_s"] > 0) & (pairs["run_s_next"] > 0)]
    result = {}
    for stop in corridor[:-1]:
        here = ok[ok["stop"] == stop]
        if len(here) >= 30:
            result[stop] = robust_log_sd(here["run_s_next"] / here["run_s"]) / np.sqrt(2)
    return result


def pairwise_dwell_noise(pairs, dwell):
    """Robust spread of log(dwell / predicted dwell) differences between neighbours, / sqrt(2)."""
    ok = pairs.dropna(subset=["dwell_time", "dwell_time_next", "ons", "offs", "ons_next", "offs_next"])
    ok = ok[(ok["dwell_time"] > 0) & (ok["dwell_time_next"] > 0)]
    predicted = dwell["intercept_s"] + dwell["seconds_per_boarding"] * ok["ons"] + dwell["seconds_per_alighting"] * ok["offs"]
    predicted_next = dwell["intercept_s"] + dwell["seconds_per_boarding"] * ok["ons_next"] + dwell["seconds_per_alighting"] * ok["offs_next"]
    ratio = (ok["dwell_time_next"] / predicted_next) / (ok["dwell_time"] / predicted)
    return robust_log_sd(ratio) / np.sqrt(2)


# =============================================================================
# 5. ORDINARY RAIN EFFECT
# =============================================================================
def rain_effect(events):
    r = events[events["run_s"].notna() & events["rain"].notna()].copy()
    r["band"] = pd.cut(r["hour"], RAIN_HOUR_BANDS, right=False)
    strata = []
    for (stop, day_type, band), group in r.groupby(["stop", "day_type", "band"], observed=True):
        wet = group.loc[group["rain"] == 1, "run_s"]
        dry = group.loc[group["rain"] == 0, "run_s"]
        if len(wet) >= 10 and len(dry) >= 30:
            strata.append({"bs_id": stop, "day_type": day_type, "hours": str(band),
                           "rain_n": len(wet), "dry_n": len(dry),
                           "rain_median_s": wet.median(), "dry_median_s": dry.median(),
                           "ratio": wet.median() / dry.median()})
    strata = pd.DataFrame(strata)
    weights = strata["rain_n"].values
    pooled = float(np.exp(np.average(np.log(strata["ratio"]), weights=weights)))

    # 95% CI: resample whole service days (rain comes in days, not single events)
    days = r["day"].unique()
    key = ["stop", "day_type", "band"]
    boot = []
    for _ in range(200):
        chosen = pd.Series(RANDOM.choice(days, len(days), replace=True))
        sample = r.merge(chosen.rename("day").to_frame(), on="day")
        med = sample.groupby(key + ["rain"], observed=True)["run_s"].agg(["median", "count"]).unstack("rain")
        med = med.dropna()
        med = med[(med[("count", 1)] >= 10) & (med[("count", 0)] >= 30)]
        if len(med) == 0:
            continue
        ratio = med[("median", 1)] / med[("median", 0)]
        boot.append(float(np.exp(np.average(np.log(ratio), weights=med[("count", 1)]))))
    low, high = np.percentile(boot, [2.5, 97.5])

    wet_ratios = []                                   # spread of rain slow-downs, for the W layer
    for _, s in strata.iterrows():
        g = r[(r["stop"] == s["bs_id"]) & (r["day_type"] == s["day_type"]) & (r["band"].astype(str) == s["hours"]) & (r["rain"] == 1)]
        wet_ratios.extend((g["run_s"] / s["dry_median_s"]).tolist())
    return strata, {
        "rain_multiplier": round(pooled, 4),
        "rain_multiplier_ci95": [round(float(low), 4), round(float(high), 4)],
        "rain_log_sd": round(robust_log_sd(np.array(wet_ratios)), 3),
        "strata_used": int(len(strata)),
        "rain_runs_used": int(strata["rain_n"].sum()),
    }


# =============================================================================
# 6. OBSERVED HEADWAY CV, MEASURED LIKE THE SIMULATOR
# =============================================================================
def observed_headway_cv(events, corridor, test_days):
    """At each stop and test day (weekday 07-18): sort arrivals, keep gaps between
    buses whose SCHEDULED starts are exactly one headway apart (so a trip that was
    never recorded does not look like a 20-minute gap), then CV = sd / mean."""
    d = events[(events["day_type"] == "weekday") & events["day"].isin(test_days)
               & events["stop"].isin(corridor) & in_hours(events["hour"], 7, 18) & events["scheduled_start"].notna()]
    rows = []
    for (day, stop), group in d.groupby(["day", "stop"]):
        group = group.sort_values("open")
        arrivals = group["open"].values.astype("datetime64[s]").astype(float)
        starts = group["scheduled_start"].values.astype("datetime64[s]").astype(float)
        gaps = np.diff(arrivals)
        scheduled_gaps = np.abs(np.diff(starts))
        keep = scheduled_gaps == H0
        if keep.sum() >= 3:
            g = gaps[keep]
            rows.append({"day": day, "bs_id": stop, "stop_index": corridor.index(stop),
                         "headways": int(keep.sum()), "cv": g.std() / g.mean()})
    return pd.DataFrame(rows)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(VALIDATION_DIR, exist_ok=True)
    corridor = [int(x) for x in open("corridor.txt").read().split()]

    events = load_events()
    events = add_runs(events, corridor)
    events = add_rain(events)
    days = split_days(events)
    days.to_csv(f"{OUT_DIR}/service_days.csv", index=False)
    calibration_days = set(days.loc[days["split"] == "calibration", "day"])
    test_days = set(days.loc[days["split"] == "test", "day"])
    print(f"events {len(events):,}; weekday service days {len(days)} "
          f"({len(calibration_days)} calibration, {len(test_days)} test)")

    params = stop_parameters(events, corridor, days)
    params.to_csv(f"{OUT_DIR}/stop_params.csv", index=False)

    summary = []
    for day_type in DAY_TYPE_NAMES.values():
        for period, (first, last) in PERIODS.items():
            d = events[(events["day_type"] == day_type) & in_hours(events["hour"], first, last) & events["stop"].isin(corridor)]
            n_days = d["day"].nunique()
            summary.append({"day_type": day_type, "period": period, "service_days": n_days,
                            "boardings_per_day": round(d["ons"].sum() / max(n_days, 1), 1),
                            "boardings_per_hour": round(d["ons"].sum() / max(n_days, 1) / (last - first), 1)})
    pd.DataFrame(summary).to_csv(f"{OUT_DIR}/day_type_summary.csv", index=False)

    dwell = dwell_model(events, corridor, calibration_days)
    pairs = neighbour_pairs(events, calibration_days)
    dispatch = dispatch_deviation(pairs)
    observed_calibration = observed_headway_cv(events, corridor, calibration_days)
    first_stop_target = float(observed_calibration.loc[observed_calibration["stop_index"] == 0, "cv"].mean())
    dispatch_scale, dispatch_cv = scale_dispatch_to_first_stop(dispatch, first_stop_target)
    dispatch = (dispatch * dispatch_scale).round(0).astype(int)
    run_spread = pairwise_run_log_sd(pairs, corridor)
    params["run_log_sd_pairwise"] = params["bs_id"].map(run_spread).round(3)
    params.to_csv(f"{OUT_DIR}/stop_params.csv", index=False)
    dwell["noise_log_sd_all_events"] = dwell["noise_log_sd"]
    dwell["noise_log_sd"] = round(float(pairwise_dwell_noise(pairs, dwell)), 3)
    dispatch.rename("deviation_s").to_csv(f"{OUT_DIR}/dispatch_deviation.csv", index=False)
    strata, rain = rain_effect(events)
    strata.to_csv(f"{VALIDATION_DIR}/rain_effect_strata.csv", index=False)
    observed = observed_headway_cv(events, corridor, test_days)
    observed.to_csv(f"{VALIDATION_DIR}/observed_headway_cv.csv", index=False)

    all_rows = params[params["period"] == "ALL"]
    model = {
        "source": "route_801_direction_6_clean.csv, weekday 07-18, calibration days unless stated",
        "dwell_model": dwell,
        "demand_dispersion_var_over_mean": demand_spread(events, corridor, calibration_days),
        "dispatch": {"neighbour_pairs_at_first_stop": int(len(dispatch)), "per_bus_sd_s": round(float(dispatch.std()), 1),
                     "first_stop_cv_target_calibration_days": round(first_stop_target, 3),
                     "scale_applied_to_pair_sample": round(dispatch_scale, 3),
                     "first_stop_cv_reproduced": round(dispatch_cv, 3),
                     "per_bus_robust_sd_s": round(float((dispatch.quantile(0.75) - dispatch.quantile(0.25)) / 1.349), 1)},
        "run_time_log_sd_dry_median_over_segments": round(float(all_rows["run_log_sd_dry"].median()), 3),
        "run_time_log_sd_pairwise_median_over_segments": round(float(np.median(list(run_spread.values()))), 3),
        "neighbour_pairs": int(len(pairs)),
        "rain": rain,
        "observed_headway_cv_test_days": {
            "mean_over_stops_and_days": round(float(observed["cv"].mean()), 3),
            "median": round(float(observed["cv"].median()), 3),
            "by_stop_index": observed.groupby("stop_index")["cv"].mean().round(3).to_dict(),
            "day_stop_cells": int(len(observed)),
        },
    }
    with open(f"{OUT_DIR}/model_params.json", "w") as file:
        json.dump(model, file, indent=2, default=str)

    print(json.dumps({k: v for k, v in model.items() if k != "observed_headway_cv_test_days"}, indent=2, default=str))
    print("observed headway CV (test days):", model["observed_headway_cv_test_days"]["mean_over_stops_and_days"])


if __name__ == "__main__":
    main()
