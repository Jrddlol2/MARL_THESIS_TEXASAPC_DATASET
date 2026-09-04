# Demo fallbacks

Pre-captured visuals to show if a live step fails during the panel demo.

## Already available (committed) — use directly
The non-GUI steps fall back to their committed figures in `starter/results/figures/`:
- `calibration_validation.png` — if calibration won't run (B2)
- `mc_headway_cv.png`, `marey_diagram.png`, `degradation_curve.png` — the results story (B5/B6)
- `gate1_convergence.png` — the MARL learning curve (B7)

## You must capture this one yourself (needs a display)
The **live SUMO GUI** (step B3) can't be screenshotted headlessly. Capture it once before the panel:

```powershell
# from starter/  (MARL/starter or "THESIS Claude/starter_kit")
python scripts\watch.py EH "Weather+Breakdown"
```
When the window is open:
1. Let a few buses depart; raise the **Delay (ms)** box (~200) so it's slow enough to catch.
2. Wait for a bus to reach a **red control stop** and **flash amber** (that's a hold being applied).
3. Screenshot the window then (Win+Shift+S), and again once buses have **bunched** under weather.
4. Save the images here as `watch_hold.png` and `watch_bunching.png`.

Then in the demo, if the GUI won't open, show these two plus `marey_diagram.png` and say the same
narration from DEMO_RUNBOOK.md step B3.
