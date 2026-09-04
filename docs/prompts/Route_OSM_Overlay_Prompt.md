# Prompt — Clean a BBBike OSM Extract into a Real Route-801 Overlay for the SUMO Viewer

Turn a raw OpenStreetMap extract (from BBBike) into a **clean, real-geometry rendering of CapMetro
Route 801, direction 6**, so the `sumo-gui` viewer shows buses running along the actual route shape
(and, optionally, a map image behind it) — **without changing the calibrated simulation or any
results.** This is a *presentation* layer: the numbers must not move. Paste everything below the line
into a session with file access to `THESIS Claude/starter_kit/` and the OSM extract.

---

## Role
You are building a visual overlay. The simulation's dynamics and calibration are fixed and validated;
your job is to make the corridor *look* like the real route while leaving every reported metric
unchanged. Verify by headless numbers, since the GUI cannot be previewed on this machine.

## Inputs
- **OSM extract** (BBBike): `.osm`, `.osm.xz`, `.osm.pbf`, or `.osm.bz2`. Path given by the user. It
  must cover the whole dir-6 corridor (lat ≈ 30.19–30.42, lon ≈ −97.78 to −97.69).
- `starter_kit/corridor.txt` — the 26 ordered stop IDs.
- `starter_kit/sim_inputs/stop_coordinates.csv` — `bs_id, mean_lat, mean_lon` for every stop.
- The projection used everywhere else (match it exactly): with `lat0,lon0` = the mean lat/lon of the
  26 corridor stops, `X = (lon − lon0)·cos(lat0)·111320`, `Y = (lat − lat0)·110540` (metres).

## Steps

**1. Read the extract.** Handle the compression (`.xz`/`.bz2`/`.pbf`). Prefer `pyosmium` (osmium) or
`pyrosm`; for a small `.osm`, `lxml` is fine. Install what's missing (`pip install osmium` etc.).

**2. Get the Route-801 dir-6 polyline.**
- *Preferred:* find the OSM **route relation** with `route=bus` and `ref=801` (there may be one
  relation per direction). Take the ordered member ways, concatenate their node geometry, and pick the
  direction whose endpoints match the corridor's first/last stops (5280 → 5872 region).
- *Fallback (no relation in the extract):* snap each of the 26 stops to the nearest highway way, then
  trace the shortest path along the road graph through the stops in sequence. Flag that this is
  reconstructed, not authoritative.

**3. Clean it.** Filter out everything that isn't the corridor; stitch disconnected ways at shared
nodes; drop spurs/roundabout detours that aren't on the through-route; simplify with
Douglas–Peucker (tolerance ~5–10 m) to remove redundant vertices; then **project to (X, Y)** with the
formula above. Output an ordered list of `(X, Y)` points.

**4. Align to the stops (validation).** Each of the 26 stop coordinates should lie within a small
tolerance of the polyline. Report the max and mean stop-to-polyline distance; if any stop is far off
(> ~60 m), the extraction is wrong — say so rather than proceeding. Confirm the polyline order matches
the stop sequence (monotonic along the route).

**5. Wire it into the viewer — the SAFE way.** The corridor's SUMO net must carry this real geometry so
buses render *on* the route (a background-only decal won't work, because buses draw at their positions
on the sim net). **Do it with edge `shape` geometry, NOT by only repositioning junction nodes** — an
earlier attempt that moved nodes to real coordinates created sharp junction angles that stalled buses.
Instead: place each stop's node at its real `(X, Y)`, **and** give each edge a `shape` following the
real polyline points between consecutive stops, so the road curves smoothly and the junction directions
match the real road (no sharp reversals). Rebuild the net (`netconvert`).

**6. Re-calibrate and prove the numbers didn't move.** Re-run `scripts/calibrate_corridor.py` on the
new-geometry net; edge lengths equal the along-route distances, so it must still meet **GEH < 5 and
RMSPE ≈ 0.75%**. Then run one headless check (`corridor_sim.simulate` for a Stage-A cell, or
`run_baseline.py`) and confirm CV/travel match the committed values within seed noise. If they don't,
stop — the geometry changed the dynamics and must be reconciled before shipping.

**7. (Optional, stretch) Map image behind the route.** If a basemap is wanted, add a SUMO background
`<decal>` in the viewer's gui-settings file, georeferenced to the projected extent (`X,Y` min/max).
Note that Google Maps tiles can't be used directly; use an OSM-rendered or open satellite image. Treat
this as optional — the real curved geometry alone already reads as the route.

## Constraints
- **Results are frozen.** The baseline / Monte-Carlo numbers, calibration RMSPE, and the disturbance
  behaviour must be unchanged (within seed noise). If the real-geometry net can't reproduce them,
  keep the schematic net for the headless results pipeline and use the real-geometry net for the
  **viewer only**.
- This is future-work-adjacent: do **not** rebuild the simulation from the OSM road network (that is the
  street-level microsimulation the manuscript defers). Use OSM only for the route *shape*.
- Everything runs from `starter_kit/`; write generated artifacts under `sumo/` and the cleaned polyline
  to `sim_inputs/route_shape.csv`. Do not touch unrelated files.

## Verification (the GUI can't be previewed — rely on these)
- Extraction: max stop-to-route distance reported and small; polyline monotonic along the sequence.
- Traversal: a headless run completes with all buses reaching the last stop (no stalls).
- Calibration: GEH < 5 on 100% of segments, RMSPE ≈ 0.75%.
- Parity: a Stage-A CV/travel check matches the committed baseline within noise.
Report all four numbers.

## Deliverables
1. `sim_inputs/route_shape.csv` — the cleaned, projected route polyline.
2. The viewer running on the real-geometry net (`watch.py` unchanged in behaviour; buses follow the
   real shape), with the control-stop colouring preserved.
3. A short note: which extraction path was used (relation vs reconstructed), the alignment error, and
   the four verification numbers.
4. (If done) the optional map decal.
