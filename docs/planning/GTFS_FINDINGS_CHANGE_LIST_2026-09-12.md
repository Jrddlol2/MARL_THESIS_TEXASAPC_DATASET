# GTFS findings — change list

**Date:** 2026-09-12 · **Status:** none of this is applied yet · **Blocking for:** MSA2 (Oct 5–10) · **Not blocking:** MSA1

---

## What happened

We obtained the current CapMetro GTFS feed (`capmetro.zip`, Aug 2026 – Jan 2027) and overlaid it on
our 2021 APC subset. It is the wrong year, so it cannot close the historical-GTFS gate on its own —
but it identified direction 6, and it sent us looking for a 2021 schedule record, which we found.

Two things came out of that:

1. **Direction code 6 is southbound**, Tech Ridge Park & Ride → Southpark Meadows.
2. **The scheduled headway is 600 s, not the 300 s hardcoded in our simulator.** Everything scaled
   by `H0` is therefore mis-parameterised by a factor of two.

The second one is the reason this document exists.

---

## What is now established

| Claim | Evidence | Strength |
|---|---|---|
| Direction 6 = southbound | 28 of our 29 stop IDs match the GTFS SB pattern in identical order, median offset **8.5 m**, max 102 m. The 3 GTFS-only stops (6528 Braker, 546 Stassney, 2763 Vic Mathias) were built after 2021 | Corroborated — from the **2026** feed, not a 2021 snapshot. Say so |
| Scheduled headway `H0` = **600 s** | Official Route 801 timetable, captured **2021-07-20** and **2021-11-18**, both inside our Jul–Dec 2021 window. Weekday 5–7a 15 min, **7a–6p 10 min**, 6–8p 15 min, 8p–12:30a 20 min. Identical across the Nov-2020 / Apr-2021 / Jul-2021 / Nov-2021 / Aug-2022 captures | Primary source, checksummed, in-window |
| Route shape correct | GTFS `shape_dist_traveled` 5280→5872 = 27,918 m vs our SUMO arclength 27,598.75 m — **1.2%** | Independent confirmation |
| Stop 6361 = Slaughter Station (SB) | Real stop between 5872 Pleasant Hill and the 5873 terminal. GTFS order and latitude agree | We dropped it as an "anomaly" — wrongly |
| Stop 6372 → renumbered 2763 | Vic Mathias/Auditorium Shores, ~130 m away | Fine for 2021; the ID is dead now |
| 2021 GTFS file | **Not publicly archived.** Six sources exhausted (below) | Document as unavailable, not pending |

**Sources checked for a 2021 GTFS, all negative:** Wayback on `data.texas.gov/download/r4v4-vz24`
(1 capture, Dec 2024, 302 only); Wayback on the `data.austintexas.gov` mirror (4 captures, 2024–25,
all 302); transitfeeds.com / OpenMobilityData (Cloudflare-walled; Wayback archived only its
2013-10..2014-12 CapMetro versions); transit.land v1 API (retired); Mobility Database full catalog
(CapMetro = `mdb-150`, archive URL is `mdb-latest` = current feed only); Socrata asset metadata
(public, confirms a single blob — revision history still needs auth).

**Archived locally:** `data/raw/capmetro/schedule_2021/` — five timetable PDFs with SHA-256s.
July 2021 = `8dfd88258b3b8f8288e5c23498b77bb69dabb6534c10facab1617c8f18307c5f`.

---

## Code changes

`H0 = 300` is hardcoded in **eight** places. Change them file by file — do **not** bulk-copy
`starter_kit/` over the repo's `starter/`, because the repo has newer figure scripts.

| File | Line | Change |
|---|---|---|
| `starter/envs/corridor_sim.py` | 34 | `H0 ... = 300.0` → `600.0` — the authoritative one |
| `starter/envs/marl_env.py` | `Config` | `H0: float = 300.0; dt: float = 300.0` → `600.0` both |
| `starter/envs/reward.py` | 17 | `decode_action(a, H0=300.0, dt=300.0)` defaults |
| `starter/envs/reward.py` | 61 | self-test cfg |
| `starter/envs/obs.py` | 35 | self-test obs dict |
| `starter/scripts/run_baseline.py` | 23 | |
| `starter/scripts/run_disturbances.py` | 31 | |
| `starter/scripts/verify_real_net.py` | 36 | |
| `starter/scripts/watch.py` | 49 | viewer only — cosmetic, but keep consistent |

**Also:** `corridor.txt` — restore stop **6361** between 5872 and 5873. Corridor goes 26 → 27 stops.
Re-check the control-stop indices afterwards; `CONTROL_STOPS = [0,1,5,17,20]` are positional.

### Three consequences that are easy to miss

**1. The observation vector rescales.** `obs.py:25-26` normalises `hf/H0` and `hb/H0`. Doubling `H0`
halves those inputs, so the network sees a different input distribution. **The gate1 policy cannot be
fine-tuned — retrain from scratch.** No loss: gate1 never wrote a checkpoint.

**2. Action semantics shift.** `{0, 30, 60, 90, 120}` s → `{0, 60, 120, 180, 240}` s. This is the
prime suspect for the gate1 plateau: the agent was scored on recovering from a 400 s breakdown while
its largest available action was a 120 s hold. Test this *before* touching reward coefficients.

**3. Disturbance severity halves relative to headway, without touching the disturbance code.**
`TBREAK = 400 s` goes from 1.33 × `H0` to 0.67 × `H0`.

### `NBUS` / run-time consistency

Three parameters are currently asserted independently and are now over-determined. Source two, derive
one, and say in the text which is derived.

- Observed dir-6 trip duration: **89.5 min** median (n = 9,352)
- Observed concurrent buses, weekday peak: **median 10, p90 12, max 13** (n = 132 days)
- Current sim: `NBUS = 12`, travel ≈ 84 min

`NBUS = 12` is defensible against observation — it sits at the p90. But at `H0 = 600` with an 84-min
run, only ~8.4 buses overlap; the first finishes before the twelfth departs. At `H0 = 300` all 12
overlapped.

---

## Results to regenerate

- `starter/results/mc_results.csv`, `mc_summary.md` — the N=30 baseline table
- `starter/experiments/gate1/` — retrain from scratch
- Every figure built from those

**Not** the calibration outputs — GEH/RMSPE/segment times are independent of `H0`. Safe.

---

## Manuscript changes

### Fixes

| Where | Change |
|---|---|
| `methods.tex:144` | `H0` row: `%TODO-DATA` → **600 s**, cited to the archived timetable. Needs a new bib entry (Wayback URL, capture date, SHA-256) |
| `methods.tex:188` | Historical-schedule gate: rewrite from *pending* to a **closed limitation** — "not publicly archived, six sources verified." A finished limitation reads better than an outstanding one |
| `problem.tex:66(e)` | Same — direction 6 is no longer unlabeled |
| `introduction.tex:66`, `problem.tex:9` | Direction 6 gets its compass label, attributed to the 2026-feed overlay, not a 2021 snapshot |
| `methods.tex:81` | Declares **RMSE** (absolute seconds); slide and code both use **RMSPE** (percentage). The implementation is the better choice — update the manuscript to declare RMSPE |
| `methods.tex:71-75` | GEH is defined on hourly bus **volume**; the code applies it to segment **travel times** (`calibrate_corridor.py:7-9` admits this). Either redefine, or state it as a closeness statistic with RMSPE as the binding criterion. Already grounding-audit must-fix #3 |
| `methods.tex:141` | `M = 29` is a **union over 12,504 trips**, not stops served per trip. Footnote it |
| §rationale | Add the missing **direction-6-vs-4 selection** paragraph (below) |
| `futurework.tex` | Still template residue from an unrelated neuroscience thesis. Rewrite |

### Additions we can now make

- **A headway-variability validation criterion for SO1.** SO1 currently validates travel time only
  (GEH/RMSPE). Nothing validates headway variability — the metric the whole thesis reports on.
  Observed weekday 07:00–18:00 headway CV is **0.620 mean / 0.607 median** (n = 131 days, 6,456
  headways). "The no-control baseline reproduces the observed headway CV" is a far stronger SO1
  claim. *Caveat:* 0.620 is measured at the trip origin across 11 h spanning two schedule
  transitions; our 0.331 is at control stops over a short horizon. Measure the sim the same way
  before tabling them together.
- **Empirical justification for the skip action.** APC stop events are demand-triggered — a record
  exists only when the doors opened. Coverage ranges from **37.8%** (2738 Capitol) to **93.4%**
  (5304 Tech Ridge). Real 801 buses already skip roughly half their stops. The skip action is
  currently motivated only by citation.
- **A stated limitation** that segment travel times are estimated from the subsample of trips that
  stopped at *both* endpoints — non-random by construction, since stopping implies demand.
- **Real stop names** in every corridor figure.

### Direction-6 rationale — text to insert

The route choice (801 over 803) is documented in `route_selection_audit.json`. The **direction**
choice is not documented anywhere. Suggested text:

> Within Route 801, direction code 6 was selected over code 4 under the same coverage criterion
> applied to the route comparison: it yields more clean stop events (229,421 vs 226,233), more
> boardings (420,201 vs 390,108, +7.7%), and marginally more trip-day pairs, across an identical
> 29-stop set. The two directions are otherwise closely matched, so the choice maximises sample size
> rather than selecting a structurally different corridor. Direction 4 remains available as a
> replication subset.

Do **not** argue direction 6 is the peak commute direction — it isn't. Weekday boardings are flat all
day (AM 06–10 = 27.0%, PM 15–19 = 24.8%).

---

## Config / data changes

- `config/texas_capmetro_801.json` — `primary_direction_label` is `null`; set it to `southbound` with
  a provenance note that it comes from the 2026 feed overlay. Update the `gtfs` block: status goes
  from `historical_archive_not_yet_verified` to *not publicly archived*, and add the timetable as the
  schedule source.
- `data/audit/texas_capmetro/GTFS_ACQUISITION_STATUS.md` — rewrite to close the headway item and
  record the six exhausted sources.
- `data/audit/texas_capmetro/APC_FIELD_USE_MAP.md` — the `direction_code_id` row now has a label.

---

## Slide fixes (MSA1 scope)

- The Canva funnel slide reads **9,917,694** raw. True figure is **9,197,694** — two digits
  transposed. `B3_MSA1_Deck_v2.pptx` already has this right; present v2, not the Canva file.
- The appendix equations slide shows **RMSPE with a `1/2`** where the code uses `np.mean`, i.e.
  `1/n` over 25 segments. Fix before presenting.

---

## What does NOT change

Research question · SO1/SO2/SO3 · scope (801 dir 6, Jul–Dec 2021) · the cleaning pipeline and every
number in the funnel · **calibration** (GEH, RMSPE 0.75%, segment times — all `H0`-independent) ·
corridor geometry · control-stop selection (`{5280, 5857, 5859, 5867, 4046}`, from the §3.2.2 demand
criteria) · the MARL method itself (parameter-shared DDQN under CTDE, 7-vector obs, 10 actions,
3-term reward) · **MSA1 deliverables** — the v2 deck has zero mentions of headway or `H0`.

---

## Open questions

1. **The 24% trip gap.** The published timetable implies ~95 SB trips/weekday; our clean subset has a
   median of 72. Cleaning drops or genuine 2021 cancellations? Resolve before quoting trip counts.
   Does not affect `H0`. *Partial evidence:* the observed peak headway histogram is unimodal at
   10–12 min with a long right tail and **no second bump at ~20 min**, which is what missing trips
   would produce — so the tail is real irregularity, not data gaps.
2. **Does the Stage B finding survive?** "Sparse fixed control fails under severe disturbance,
   therefore MARL" is the load-bearing claim for the whole MARL chapter — and it was measured with
   disturbances scaled to roughly twice their intended severity relative to headway. It may come back
   stronger, weaker, or gone. Unknown until it re-runs.
3. **Can observed CV 0.620 and simulated CV be reconciled** once measured the same way?

---

## Order of operations

1. Set `H0 = 600` across the eight sites; restore 6361; reconcile `NBUS` / run-time.
2. Re-run the N=30 baselines. Hours on 12 cores.
3. Re-run the gate from scratch and see whether the plateau survives.
4. *Then* tune reward coefficients — not before. Tuning against a mis-scaled action space would burn
   the MSA2 window.
5. Manuscript edits in parallel; they don't depend on the re-runs except for the results numbers.
