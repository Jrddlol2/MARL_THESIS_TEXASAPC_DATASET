# Prompt — Data Processing & Cleaning Walkthrough (presentation-ready, figures + code snippets)

Build a **step-by-step walkthrough of the data-processing and cleaning pipeline** for the MSA1
presentation: each step shown with the real code that did it, the figure that evidences it, a plain
explanation, and the reason it was done that way — so when the panel asks "what was your process?", the
presenter can show and defend every step. Paste everything below the line into a session with file
access to the thesis repo.

---

## Role
You are preparing the data-processing section of a defense presentation. The audience are experienced
researchers who may drill into any step. Every claim is backed by the actual code (quoted verbatim from
the repo) and the actual figures (the committed ones — do not regenerate), with numbers that match the
pipeline exactly. Keep it presentation-legible: short snippets, one idea per slide.

## Deliverable
A slide deck **`docs/progress/B3_Data_Processing_Walkthrough.pptx`** — one pipeline step per slide, each
slide carrying: a short title, the relevant **figure**, 2–4 **bullet points** (what + why), and a **short
code excerpt** (2–8 lines) where it illustrates the step. Then a short **backup/appendix** section with
the full `extract_sim_inputs.py` listing and the anticipated Q&A. (If the team prefers a document, the
same content as `.docx` is acceptable — confirm the format first.) Use the `pptx` skill to build it.

## Sources (use the real artifacts; quote code verbatim)
- **Code:** `starter/scripts/extract_sim_inputs.py` — the six cleaning rules, the column list, the
  aggregation. Quote snippets directly from it.
- **Figures (already generated; reuse the committed PNG/PDF):** `starter/results/figures/datacleaning/` —
  `fig_funnel`, `fig_route_selection`, `fig_distributions`, `fig_demand_profile`, `fig_corridor_map`,
  `fig_exclusions`, `fig_temporal`. Captions in `docs/progress/FIGURES_CAPTIONS.md`.
- **Numbers:** the route-selection audit `data/audit/texas_capmetro/route_selection_audit.json`
  (9,197,694 raw; Route 801 = 547,616; dir-6 clean = 229,421; 810,309 boardings; 184 service days;
  dwell median 18 s) and `starter/sim_inputs/stops.csv` (26 stops).
- **Context:** the manuscript data section (do not edit it) and `docs/prompts/DATA_CLEANING.md`.

## The steps (one slide each) — content + which snippet + which figure
1. **Source & scope.** CapMetro Automatic Passenger Counter data, July–December 2021, Route 801,
   direction 6; a public agency dataset streamed in chunks (the 3.7 GB file is never loaded whole).
   *Snippet:* the `pd.read_csv(..., usecols=NEED, chunksize=1_000_000)` line. *Figure:* `fig_temporal`.
2. **Why Route 801, direction 6.** Highest-ridership Rapid corridor (≈810,309 boardings / 184 days);
   direction 6 is the study direction. *Figure:* `fig_route_selection`.
3. **Column selection.** Thirteen of the forty-seven fields retained, each for a stated purpose
   (route id / reassignment screen / two error gates / stop / direction / order / demand / dwell /
   segment time & distance / timestamp). *Snippet:* the `need = [...]` list. Present the reasons as a
   compact table.
4. **The six cleaning rules.** route = 801; operating route = scheduled route (no mid-trip reassignment);
   both import-error gates clear; valid stop id; direction 6. *Snippet:* the boolean-mask block.
   *Figures:* `fig_funnel` (9,197,694 → 229,421) and `fig_exclusions` (what was dropped and why).
5. **Derivation & aggregation.** Segment running time = `rev_seconds − dwell_time`; per-stop reduction
   using the **median** for dwell / run-time / distance (robust to tails) and the **mean** for boardings.
   *Snippet:* the `run_seconds` line and the `groupby(...).agg(...)` block. *Figures:* `fig_distributions`
   (long tails → median) and `fig_demand_profile`.
6. **Provenance & reproducibility.** The cleaned subset is cached and a SHA-256 checksum recorded so the
   result is auditable and re-runnable; output is `sim_inputs/stops.csv` (26 stops), which feeds the
   SUMO calibration. *Figure:* `fig_corridor_map` (the resulting corridor).

## Backup / appendix (for the "show me exactly" question)
- The full `extract_sim_inputs.py` listing (verbatim).
- A short **Q&A**: where the data came from; what a stop-event is; what "operating route = scheduled
  route" means (drops mid-trip reassignments); why median not mean; units (`rev_distance` in miles);
  why 229,421 and not the audit's 29 distinct stops (3 low-use/terminal stops outside the modeled
  corridor); what the data does *not* provide (arrival times, capacity, breakdowns, schedule).

## Grounding & guardrails
- Every number must match the sources (funnel ends at **229,421**; 26 stops; dwell median 18 s). Do not
  invent figures or values.
- Code excerpts are quoted **verbatim** from the working tree; do not paraphrase code.
- Reuse the committed figures — do not regenerate (no need to re-stream the raw CSV).
- Do not edit the manuscript `.tex`. Write only the new deck under `docs/progress/`.
- Keep measured/derived facts distinct from anything synthetic (no weather/disturbance content here —
  this section is data processing only).

## Verification
Confirm the funnel figure ends at 229,421 and the deck's stated numbers match the audit JSON and
`stops.csv`; list the slides produced and the figures/snippets used on each.
