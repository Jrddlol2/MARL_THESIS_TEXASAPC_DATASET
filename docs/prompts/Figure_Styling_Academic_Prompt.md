# Prompt — Restyle the Generated Figures to Publication (Academic-Paper) Standard

Take the project's generated figures and bring them to **publication quality for an academic manuscript**:
a single consistent house style, vector output for LaTeX, print-sized typography, a restrained
colourblind- and grayscale-safe palette, and captions moved out of the image into LaTeX. **Change only
the presentation — never the data or the numbers.** Paste everything below the line into a session with
file access to the thesis repo.

---

## Role
You are preparing figures for a thesis manuscript, not slides. Apply one coherent style across every
generated figure so the paper reads as a unified document, and follow the conventions a reviewer expects
(vector graphics, no chartjunk, captions in the text, legible at final print size). The underlying data
and computed values must be identical to what the current scripts produce.

## Scope — all generated result figures (make them consistent)
Restyle the figures produced by these scripts, together, to the same standard:
- `scripts/figures_datacleaning.py` — the 7 data-cleaning figures (funnel, route selection,
  distributions, demand profile, corridor map, exclusions, temporal).
- `scripts/figures.py` — calibration validation, MC headway-CV, MC wait.
- `scripts/marey.py` — Marey time–space diagram.
- `scripts/degradation.py` — degradation curve.
- `scripts/convergence.py`, `scripts/plot_curve.py` — MARL gate figures.

## The house style (implement as a shared module, applied everywhere)
Create `scripts/_figstyle.py` defining one style all figure scripts import and call (e.g. `apply()` set
of `matplotlib.rcParams`, plus helpers for column-width figure sizes, the palette, and a `save(fig, name)`
that writes both formats). Then have each script import and use it. The style:

1. **Vector-first output.** Save every figure as **PDF** (vector, for `\includegraphics` in LaTeX) **and**
   a 300-dpi PNG (for slides). Same basename, both extensions. Embed fonts in the PDF (`pdf.fonttype = 42`).
2. **Typography.** A serif family that harmonises with the LaTeX body (e.g. a Times/Computer-Modern-like
   serif via matplotlib's `mathtext`/`STIX`, or the manuscript's font if declared). Base size ~9 pt so
   that at final print width the smallest text is ≥ 7 pt. Consistent sizes: axis labels 9, ticks 8,
   legend 8.
3. **No baked-in titles.** Remove the bold in-figure titles — the figure's title belongs in the LaTeX
   `\caption`. Keep concise axis labels **with units**. (Panels in a multi-part figure may keep small
   `(a)`, `(b)` subplot tags.)
4. **Sizing to the column.** Set figure widths to the manuscript's text/column width — read it from the
   `.tex` (`\textwidth`) or assume a single-column ≈ 3.4 in and full-width ≈ 6.9 in; pick per figure and
   keep aspect ratios consistent. Use `constrained_layout`.
5. **Restrained, safe palette.** One limited palette, **colourblind-safe and legible in grayscale**
   (e.g. a muted blue / orange / grey set, or Okabe–Ito). Map roles consistently across figures — the
   same colour for NC / FH / EH everywhere, one fixed accent for the control stops, greys for context.
   Prefer patterns/linestyles over colour where a print may be B&W.
6. **De-clutter.** Despine top/right, thin light gridlines only where they aid reading, unobtrusive
   legends (no frame or a light one), thousands separators on large tick values, no drop shadows or 3-D.

## Grounding / consistency
Look at the manuscript's existing figures in `Figures/` (the pipeline/architecture diagrams) and match
their visual register — line weights, font feel, colour temperature — so the generated figures sit
naturally beside them. Keep the corridor/control-stop colour identical to whatever those diagrams use if
they encode it.

## Hard constraints
- **Data unchanged.** Do not alter any computation, filter, count, or value — restyling only. The funnel
  must still end at 229,421; calibration RMSPE still 0.75 %; the MC numbers unchanged.
- Do **not** edit the manuscript `.tex`. Read it only to pull `\textwidth` / font.
- Keep filenames stable (add the `.pdf` sibling next to each existing `.png`); don't break references in
  the docx/runbook.
- Import matplotlib in the parent only (worker-crash pitfall); regenerate the data-cleaning figures from
  the cache so the 3.7 GB raw stream isn't repeated.

## Deliverables
1. `scripts/_figstyle.py` — the shared style module.
2. Each figure regenerated as **`.pdf` + `.png`** in its existing folder(s), in the new consistent style.
3. `docs/progress/FIGURES_CAPTIONS.md` — a LaTeX-ready `\caption{…}` (2–3 sentences, self-contained,
   defines any symbol) for every figure, since the titles now live in captions.
4. A one-paragraph note listing what changed stylistically and confirming no data/number changed
   (spot-check: funnel 229,421; calibration RMSPE 0.75 %; MC Stage-A FH −28 %).

## Verification
Open two or three regenerated PDFs, confirm text is legible at column width, the palette is distinct in
grayscale (desaturate-check), and the values match the pre-restyle figures. Report the list of
regenerated files and the spot-checked numbers.
