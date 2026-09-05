# Prompt — Improve the MSA1 Presentation (storytelling, flow, correctness)

Revise the MSA1 defense deck into a **tighter, better-sequenced story** without changing its factual
claims or its MSA1 scope. Keep the existing visual template; fix the flow, remove redundancy, correct
errors, and give the data section a narrative spine that builds to the calibration result. Paste
everything below the line into a session with access to the deck and the repo.

---

## Role
You are the team's presentation editor. The panel are experienced researchers, so the deck must read as
a clear argument — problem → what we built → proof it is valid → what's next — not a catalogue of data
facts. Preserve the deck's template, fonts, and colours; change sequence, wording, and emphasis.

## Source
The current deck (`MSA1 - PRESENTATION.pptx` if the editable file is available; the 19-slide PDF export
is the reference for content and order). Match its style exactly. If only the PDF exists, deliver the
changes as a slide-by-slide revision plan plus any replacement slides.

## Hard scope guardrail (MSA 1 = data cleaning + calibration ONLY)
Do **not** show control stops, the MARL agent, disturbance results, holding/skip, or any later-stage
result. In particular, **remove "the five control stops are highlighted"** from the per-stop demand
slide — control-stop selection is a later deliverable and must not appear yet. The updated,
control-stop-free figures are in `starter/results/figures/datacleaning/`.

## The narrative spine (impose this order)
1. **Title**
2. **Outline**
3. **Problem & stakes** — high-frequency bunching; *why it matters* (service reliability, passenger
   waiting); frame it as a Vehicle Scheduling Problem. Sharpen the stakes in one line — what breaks when
   a bus bunches.
4. **Objectives** — Main + SO1–SO3, brief.
5. **The corridor** — Route 801: where it is (a map grounds the audience) and *why this route and
   direction* (highest-boarding CapMetro route; direction 6). **Merge the two duplicate route-selection
   beats into one.**
6. **The dataset & why it** — CapMetro APC; *why not EDSA* (no open, calibratable dataset within scope);
   what it provides (demand; dwell/segment time; the NOAA weather join; stop geometry); what is
   **synthetic** (vehicle breakdown; severe weather). Group into 2–3 points, not a five-item list.
6b. **What the dataset contains (field inventory)** — a compact **table of the 13 retained APC columns
   and what each gives us** (see "Content to add" below), so the panel sees exactly what is in the data
   and what is extracted from it. This is the "what can we pull from this dataset" slide.
6c. **The weather dataset (currently missing)** — a dedicated slide for the NOAA weather join, which the
   deck only mentions in passing. Source, join method, coverage, and — crucially — the honest
   data-vs-simulation boundary (see "Content to add" C). Place it in the dataset section, near the
   demand/geometry description, since weather is one of the data layers the study rests on.
7. **Cleaning** — in logical order: the **six rules → the funnel (9,197,694 → 229,421) → what was
   removed.** Keep these three together and in this order, and **show the actual cleaning code** — a
   short, styled snippet of the six-rule filter and the per-stop aggregation — so the process is concrete
   and defensible when the panel asks "how did you do it?"
8. **What the clean data looks like** — distributions (long tails → median) → per-stop demand (**no
   control stops**) → temporal coverage (184 days, Jul–Dec 2021).
9. **The corridor in SUMO** — network construction, built from the averaged stop GPS (a map/screenshot).
10. **Calibration — the climax.** GEH < 5 on **100%** of segments (85% was the target) and RMSPE
    **0.75%** vs empirical travel time. Build to this as the proof the environment is valid; give it
    room, not a footnote.
11. **Status & timeline** — MSA 1 done (cleaned dataset + calibrated corridor); MSA 2 / MSA 3 ahead.
12. **Close.**

## Specific fixes (from the current deck)
- **Delete the duplicate** "Route and Direction Selection" slide (it appears twice).
- **Fix the typo:** raw count `9,917,694` → **`9,197,694`** (match the funnel and the audit).
- **Reorder the data section:** currently the funnel precedes the cleaning rules and route selection —
  put selection → rules → funnel → removed → distributions → demand → temporal.
- **Remove the control-stop highlight** from the per-stop demand slide (swap in the updated figure).
- **Compress "What the Data Gives Us"** from a five-bullet list into grouped, story-advancing points.
- **Elevate the calibration slide** to the high point of the "what we accomplished" arc.

## Content to add (dataset depth)

### A. Field-inventory table (slide 6b)
A two-column table — **Field kept | Reason** — for the 13 retained columns. Use exactly this content
(it matches `scripts/extract_sim_inputs.py` and the walkthrough docx):

| Field kept | Reason |
|---|---|
| route_id | Selects Route 801. |
| current_route_id | Must equal route_id — excludes trips reassigned to another route mid-service. |
| import_error | Kept only where 0 (record imported without error). |
| import_trip_error | Kept only where 0 (trip imported without error). |
| bs_id | Bus-stop identifier; bs_id = 0 (unknown) is excluded. |
| direction_code_id | Restricts to direction code 6, the study direction. |
| actual_sequence | Orders the stops along the corridor. |
| ons | Boardings (APC count) — the demand signal. |
| offs | Alightings (APC count). |
| dwell_time | Time stopped; the dwell parameter, and removed from rev_seconds to get running time. |
| rev_seconds | Revenue open-to-open time; the source of segment running time. |
| rev_distance | Inter-stop distance (miles; units flagged as unresolved). |
| transit_date_time | Timestamp; scopes records to July–December 2021. |

Frame it as "13 of 47 columns retained" and note the grouping (route/quality gates, location, demand,
dwell/time/distance). Keep it legible — small font, one row per field; split across two slides only if
it does not fit.

### B. Code snippets (slide 7, styled code panel)
Quote **verbatim** from `scripts/extract_sim_inputs.py`, kept short and readable on a slide (monospace,
light panel, ~8–14 lines). Two excerpts:
- **The six-rule filter** — the streamed `pd.read_csv(..., usecols=need, chunksize=...)` loop and the
  boolean mask (`route_id=="801"` … `direction_code_id=="6"`), with the `9,197,694 -> 229,421` comment.
- **The derivation + aggregation** — `run_seconds = rev_seconds - dwell_time` and the
  `groupby("bs_id").agg(...)` block, annotated `mean` for demand and `median` (robust to tails) for
  dwell/time/distance → `stops.csv`.
Do not paraphrase code; if a line is too long for the slide, shorten variable display but keep it valid.
A fuller listing may go on a backup/appendix slide for the "show me everything" question. (Both excerpts
already exist as the styled "Data Cleaning — In Code" slide built earlier; reuse that treatment.)

### C. Weather dataset (slide 6c)
Facts, verified against `data/audit/texas_capmetro/weather_*` — use exactly these:
- **Source:** NOAA NCEI **Local Climatological Data v2 (LCDv2)**, 2021, two Austin stations — Camp Mabry
  (USW00013904, primary) and Bergstrom (USW00013958).
- **Join method:** each APC event matched to the **nearest NOAA observation within 90 minutes**, with
  timestamps normalised to America/Chicago.
- **Coverage:** **100%** of the 229,421 cleaned events matched a weather reading; **11,804** were
  rain-exposed.
- **The honest boundary (state this plainly — it is the whole point):** *ordinary rain is observed* at
  the data layer (this join), **but** the simulation's weather stressor is still the **synthetic
  lognormal factor**. An *empirical* rain multiplier requires stratified modelling (segment, time-of-day,
  day-type controls) and is **MSA2** work; **severe/out-of-support weather stays a labelled synthetic
  stress test.** Do not present the join as if the simulator already uses empirical rain.
Frame the slide as "weather exposure is measured and joined; using it to drive the simulator is the next
step" — a strength (the data is ready) told honestly.

**Figures (already generated) — `starter/results/figures/weather/` (PDF+PNG, captions in its CAPTIONS.md):**
`fig_weather_precip` (daily precipitation across Jul–Dec 2021 — episodic storms), `fig_weather_exposure`
(11,804 of 229,421 events rain-exposed), `fig_weather_traveltime` (descriptive dry 204 s vs rain 212 s —
caption must carry the "unadjusted, not causal, MSA2" caveat), `fig_weather_join` (100% joined within
90 min; stations agree 94%). Use one or two on the weather slide; the travel-time one is the strongest
motivator but must keep its caveat.

## Storytelling rules
- One idea per slide. Make each slide **title a claim, not a topic** ("Six rules cut 9.2 M events to
  229,421", not "Cleaning Rules").
- Every figure is named in the spoken line; captions say what to look at.
- Keep one through-line audible across the deck: *"a real, publicly-calibrated, validated environment —
  ready for the MARL study."*
- **Weather consistency:** the NOAA join to events is a *data* result (ordinary rain observed); the
  simulation's weather stressor is *synthetic*. State both, and do not blur them.

## Accuracy guardrails
- Numbers must match the committed data: **229,421**, **9,197,694**, **184** service days, GEH < 5 on
  **100%**, RMSPE **0.75%**. Do not invent or round away.
- Do not touch the manuscript `.tex`. Keep every existing correct claim.

## Deliverable
1. A one-page **revised storyline** (the final slide list with each change marked: moved / merged /
   deleted / reworded).
2. If the editable `.pptx` is available, the **rebuilt deck** in the same template; otherwise the exact
   per-slide edits to apply, plus any replacement slides.
3. A short note listing what was fixed (duplicate removed, typo corrected, order changed, control stops
   removed) and what was added (field-inventory table, code snippets, weather-dataset slide), and
   confirming MSA1 scope held and the weather data-vs-synthetic boundary stated correctly.
