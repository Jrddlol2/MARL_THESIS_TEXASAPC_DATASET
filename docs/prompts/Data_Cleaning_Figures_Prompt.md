# Prompt — Data-Cleaning Visualization Figures (raw → clean, for the MSA1 talk)

Produce a set of **publication-quality figures that visually document how the CapMetro dataset was
cleaned** — the raw data, the filtering funnel, and the key distributions — so the panel can *see* the
pipeline from ~9.2 M raw events to the 229,421-event Route-801/direction-6 subset and the 26-stop
parameter table. Reproducible from a script, grounded in the actual data. Paste everything below the
line into a session with file access to the thesis repo.

---

## Role
You are preparing the data-processing figures for the Mid-Stage Assessment 1 presentation. Each figure
must be built from the real data (not mocked), be self-explanatory with a caption, and match the visual
style of the existing figures in `starter/results/figures/`. The story the figures tell: *why Route 801
direction 6, what was dropped and why, and what the cleaned per-stop inputs look like.*

## Sources (real data — use these, don't invent numbers)
- **Raw APC CSV** (~3.5 GB): `C:\Users\jared\Desktop\THESIS\APC_Raw_July_2021_-_December_2021_20260824.csv`.
  Stream it in chunks (as `scripts/extract_sim_inputs.py` does) — never load it whole.
- `scripts/extract_sim_inputs.py` — the six cleaning rules and the per-stop aggregation (the ground truth
  for the funnel and the column choices).
- `data/route_801_direction_6_clean.csv` — the cached cleaned subset (fast source for post-clean plots).
- `sim_inputs/stops.csv` — the 26-stop parameter table (dwell, run time, distance, boardings).
- `sim_inputs/stop_coordinates.csv` — per-stop lat/lon (for the corridor map).
- `docs/prompts/DATA_CLEANING.md` and the route-selection audit JSON under `data_audit/` (or `docs/`) —
  the documented funnel and the route-selection statistics (Route 801 ≈ 810,309 boardings over 184
  service days). The funnel **must end at exactly 229,421** and **26 stops**.

## Figures to produce (save each as a PNG)
1. **Cleaning funnel (the headline).** A waterfall / horizontal bar showing rows remaining after each of
   the six rules applied in order: raw total → route_id == 801 → operating route == scheduled route →
   import_error == 0 → import_trip_error == 0 → bs_id ≠ 0 → direction_code_id == 6 = **229,421**.
   Label each step with the count and the number/percent removed. State the rule order (the final count
   is order-independent; the intermediate bars are not).
2. **Route selection.** Why 801: a bar of total boardings (or record count) by route with Route 801
   highlighted; and/or the direction split within 801 (direction 6 vs the rest) justifying the study
   direction. Pull the numbers from the route-selection audit; annotate the ≈810,309 boardings / 184
   service days.
3. **Raw vs cleaned distributions.** For the fields that drive the model — `dwell_time`, `rev_seconds`
   (or the derived `run_seconds`), and `ons` — histograms or boxplots **before vs after** filtering,
   showing the long tails / outlier records that motivate (a) the filters and (b) using the **median**
   for dwell/run/distance and the **mean** for boardings. Make the "why median, not mean" visible.
4. **Per-stop demand profile.** Mean boardings (and alightings) by stop in corridor sequence — a bar or
   step plot along the 26 stops — showing where demand concentrates. This is the same profile the
   control-stop criteria act on, so it doubles as motivation for §3.2.2; optionally mark the 5 control
   stops (5280, 5857, 5859, 5867, 4046).
5. **Corridor geography.** A scatter of the 26 stops by lon/lat (the real route shape), optionally sized
   or coloured by mean boardings. Gives the panel a spatial sense of the corridor.
6. **Data-quality / exclusions.** A small bar of *why* records were excluded — counts removed by each
   reason (wrong route, route≠scheduled, import errors, bs_id = 0, wrong direction). Complements the
   funnel by showing the composition of what was dropped.
7. **(Optional) Temporal coverage.** Records (or service days) per month across Jul–Dec 2021, showing the
   184-day window and any gaps.

## Grounding (say why, not just what)
Tie each figure to a decision: the funnel to the six documented rules; the route-selection figure to the
ridership justification; the raw-vs-clean distributions to the median-vs-mean choice and the outlier
removal; the demand profile to the control-stop criteria. Keep measured vs derived vs synthetic distinct
— these are all *measured/derived* from the APC; no weather/synthetic content belongs here.

## How to build it
- Write one script, `scripts/figures_datacleaning.py`, that (a) streams the raw CSV once to compute the
  funnel counts + exclusion composition + raw distributions (cache these to a small CSV so re-runs are
  fast), and (b) uses the cached clean subset / `stops.csv` for the post-clean plots. Import matplotlib
  in the parent only (a known crash otherwise).
- Match the house style: clean matplotlib, readable fonts, tight layout, one idea per figure, captions.
- Save to `starter/results/figures/datacleaning/` (new subfolder) so they don't collide with the results
  figures.

## Verification
- The funnel's final bar equals **229,421** and the stop count is **26** (assert these; if they don't
  match, stop and report — the filter drifted).
- Cross-check the per-stop boardings against `sim_inputs/stops.csv`.
- Report each figure's path and the funnel numbers used.

## Deliverables
1. `scripts/figures_datacleaning.py` (reproducible; streams raw once, caches counts).
2. The PNGs in `starter/results/figures/datacleaning/`.
3. A short caption sheet (one line per figure) the author can paste under each slide.
