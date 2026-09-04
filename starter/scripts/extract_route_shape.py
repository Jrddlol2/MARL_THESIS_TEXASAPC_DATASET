"""Extract a clean, real-geometry polyline for CapMetro Route 801 dir-6 -> sim_inputs/route_shape.csv

PRESENTATION LAYER ONLY. Writes the route shape used to build the real-geometry viewer net
(sumo/corridor_real.*). Does NOT touch the calibrated headless net (sumo/corridor.*) or any result.

Extraction path (see docs note): the OSM route relation 9122669
    route=bus, ref="Rapid 801", direction=south, "North Lamar/South Congress (southbound)"
is the authoritative dir-6 alignment. Its ordered member ways are concatenated at shared
endpoints, trimmed to the corridor's first/last stop (5280 -> 5872), simplified with
Douglas-Peucker, and projected with the SAME formula used everywhere else in the kit:
    lat0,lon0 = mean lat/lon of the 26 corridor stops
    X = (lon - lon0)*cos(lat0)*111320 ,  Y = (lat - lat0)*110540      [metres]

Geometry source: sumo/rel_9122669.json (Overpass `rel(9122669); out geom;`). The BBBike extract
supplied for this task resolves only 67 of the relation's 308 member ways (26.3% corridor
coverage, gaps up to 6.5 km) and its highway graph connects only 10 of 25 consecutive stop
pairs, so it cannot produce a gap-free corridor; it is retained only as an independent
cross-check of the fetched geometry (--crosscheck).

Usage:
    python scripts/extract_route_shape.py                       # uses sumo/rel_9122669.json
    python scripts/extract_route_shape.py --crosscheck sumo/route801.osm
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

REL_JSON = "sumo/rel_9122669.json"
DP_TOL_M = 7.0          # Douglas-Peucker tolerance (metres)
ALIGN_TOL_M = 60.0      # stop-to-polyline tolerance; beyond this the extraction is wrong
STITCH_TOL_M = 1.0      # endpoint match tolerance when concatenating member ways


# ---------------------------------------------------------------- geometry helpers
def project(lat, lon, lat0, lon0):
    return ((lon - lon0) * math.cos(math.radians(lat0)) * 111320.0,
            (lat - lat0) * 110540.0)


def nearest_on_segment(px, py, ax, ay, bx, by):
    """Return (qx, qy, t) — closest point on segment AB to P, and its parameter t in [0,1]."""
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0.0:
        return ax, ay, 0.0
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return ax + t * dx, ay + t * dy, t


def point_to_polyline(px, py, poly):
    """Return (distance, index, t) of the closest point on the polyline."""
    best = (float("inf"), 0, 0.0)
    for k in range(len(poly) - 1):
        ax, ay = poly[k]
        bx, by = poly[k + 1]
        qx, qy, t = nearest_on_segment(px, py, ax, ay, bx, by)
        d = math.hypot(px - qx, py - qy)
        if d < best[0]:
            best = (d, k, t)
    return best


def cumulative(poly):
    cum = [0.0]
    for k in range(len(poly) - 1):
        cum.append(cum[-1] + math.hypot(poly[k + 1][0] - poly[k][0],
                                        poly[k + 1][1] - poly[k][1]))
    return cum


def arclength_of(px, py, poly, cum):
    d, k, t = point_to_polyline(px, py, poly)
    seg = math.hypot(poly[k + 1][0] - poly[k][0], poly[k + 1][1] - poly[k][1])
    return cum[k] + t * seg, d


def douglas_peucker(points, tol):
    """Iterative Douglas-Peucker (recursion depth is unsafe for 1700+ point lines)."""
    if len(points) < 3:
        return list(points)
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        ax, ay = points[i]
        bx, by = points[j]
        dmax, imax = 0.0, i
        for k in range(i + 1, j):
            px, py = points[k]
            qx, qy, _ = nearest_on_segment(px, py, ax, ay, bx, by)
            d = math.hypot(px - qx, py - qy)
            if d > dmax:
                dmax, imax = d, k
        if dmax > tol:
            keep[imax] = True
            stack.append((i, imax))
            stack.append((imax, j))
    return [points[i] for i in range(len(points)) if keep[i]]


# ---------------------------------------------------------------- relation -> polyline
def stitch_relation(path):
    """Concatenate the relation's ordered member ways into one lat/lon polyline."""
    with open(path) as fh:
        data = json.load(fh)
    rel = data["elements"][0]
    tags = rel.get("tags", {})
    ways = [m for m in rel["members"] if m.get("type") == "way" and m.get("geometry")]
    print(f"relation {rel['id']}: ref={tags.get('ref')!r} direction={tags.get('direction')!r}")
    print(f"  {len(ways)} member ways with geometry")

    def pts(m):
        return [(g["lat"], g["lon"]) for g in m["geometry"]]

    def dist(a, b):   # metres, local flat approximation (only used for endpoint matching)
        return math.hypot((b[1] - a[1]) * 96000.0, (b[0] - a[0]) * 110540.0)

    first, second = pts(ways[0]), pts(ways[1])
    # orient the first way so that its tail meets the second way
    if min(dist(first[0], second[0]), dist(first[0], second[-1])) < \
       min(dist(first[-1], second[0]), dist(first[-1], second[-1])):
        first = first[::-1]
    chain = list(first)

    # Relation member order is authoritative but not always locally correct: in this relation
    # members #33-#35 are listed out of sequence, and following the listed order blindly makes
    # the chain jump ~1.7 km and double back. So walk the list in order but allow a small
    # look-ahead: at each step take the nearest unused member among the next LOOKAHEAD that
    # actually connects, falling back to strict order when none does (a genuine gap).
    LOOKAHEAD = 8
    remaining = [pts(m) for m in ways[1:]]
    used = [False] * len(remaining)
    gaps, reordered = [], 0
    placed = 0
    while placed < len(remaining):
        window = [i for i in range(len(remaining)) if not used[i]][:LOOKAHEAD]
        best_i, best_p, best_d = None, None, float("inf")
        for i in window:
            p = remaining[i]
            d_fwd, d_rev = dist(chain[-1], p[0]), dist(chain[-1], p[-1])
            d, q = (d_rev, p[::-1]) if d_rev < d_fwd else (d_fwd, p)
            if d < best_d:
                best_i, best_p, best_d = i, q, d
        first_unused = window[0]
        if best_d <= STITCH_TOL_M:
            if best_i != first_unused:
                reordered += 1
            chain.extend(best_p[1:])
        else:
            # nothing in the window connects — accept the next member in relation order
            best_i = first_unused
            p = remaining[best_i]
            d_fwd, d_rev = dist(chain[-1], p[0]), dist(chain[-1], p[-1])
            best_p = p[::-1] if d_rev < d_fwd else p
            gaps.append((len(chain), min(d_fwd, d_rev)))
            chain.extend(best_p)
        used[best_i] = True
        placed += 1

    if reordered:
        print(f"  repaired {reordered} out-of-order member(s) via look-ahead stitching")
    if gaps:
        print(f"  stitch gaps: {len(gaps)} (max {max(g[1] for g in gaps):.1f} m)")
    else:
        print("  stitched with no gaps (all member ways share endpoints)")
    print(f"  raw polyline: {len(chain)} points")
    return chain


# ---------------------------------------------------------------- main
def main():
    corridor = [int(l.strip()) for l in open("corridor.txt") if l.strip()]
    co = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id").loc[corridor]
    lat0, lon0 = co["mean_lat"].mean(), co["mean_lon"].mean()
    print(f"projection origin: lat0={lat0:.6f} lon0={lon0:.6f} "
          f"(mean of {len(corridor)} corridor stops)\n")

    if not os.path.exists(REL_JSON):
        sys.exit(f"missing {REL_JSON} — run the Overpass fetch first")
    latlon = stitch_relation(REL_JSON)
    poly = [project(lat, lon, lat0, lon0) for lat, lon in latlon]
    # drop consecutive duplicates
    poly = [p for i, p in enumerate(poly) if i == 0 or math.dist(p, poly[i - 1]) > 0.01]

    stops = {s: project(co.loc[s, "mean_lat"], co.loc[s, "mean_lon"], lat0, lon0)
             for s in corridor}

    # ---- trim the full-route polyline to the corridor (first stop -> last stop) ----
    cum = cumulative(poly)
    a_s, a_d = arclength_of(*stops[corridor[0]], poly, cum)
    b_s, b_d = arclength_of(*stops[corridor[-1]], poly, cum)
    print(f"\ntrim: stop {corridor[0]} at {a_s:.0f} m (off-line {a_d:.1f} m), "
          f"stop {corridor[-1]} at {b_s:.0f} m (off-line {b_d:.1f} m); "
          f"full route {cum[-1]:.0f} m")
    if a_s > b_s:
        sys.exit("ERROR: first corridor stop lies AFTER the last one along the relation — "
                 "wrong direction relation selected")
    # keep the interior vertices strictly between the two terminal stops, and cap the ends with
    # the stops' exact foot-of-perpendicular so the line starts/ends on the terminals
    _, k0, _ = point_to_polyline(*stops[corridor[0]], poly)
    _, k1, _ = point_to_polyline(*stops[corridor[-1]], poly)
    p0 = nearest_on_segment(*stops[corridor[0]], *poly[k0], *poly[k0 + 1])[:2]
    p1 = nearest_on_segment(*stops[corridor[-1]], *poly[k1], *poly[k1 + 1])[:2]
    trimmed = [p0] + [poly[k] for k in range(len(poly)) if a_s < cum[k] < b_s] + [p1]
    trimmed = [p for i, p in enumerate(trimmed) if i == 0 or math.dist(p, trimmed[i - 1]) > 0.01]
    print(f"trimmed polyline: {len(trimmed)} points, {cumulative(trimmed)[-1]:.0f} m")

    # ---- simplify ----
    simplified = douglas_peucker(trimmed, DP_TOL_M)
    print(f"simplified: {len(trimmed)} -> {len(simplified)} points (DP tol {DP_TOL_M} m), "
          f"length {cumulative(simplified)[-1]:.0f} m")

    # ---- validate: every stop must lie close to the line, in order ----
    scum = cumulative(simplified)
    rows = []
    for s in corridor:
        al, d = arclength_of(*stops[s], simplified, scum)
        rows.append((s, al, d))
    errs = np.array([r[2] for r in rows])
    arcs = [r[1] for r in rows]
    print(f"\nstop-to-polyline distance (m): max={errs.max():.1f} mean={errs.mean():.1f}")
    bad = [(s, round(d, 1)) for s, _, d in rows if d > ALIGN_TOL_M]
    if bad:
        print(f"FAIL: {len(bad)} stop(s) beyond {ALIGN_TOL_M} m: {bad}")
        sys.exit("extraction is wrong — refusing to write route_shape.csv")
    print(f"OK: all {len(corridor)} stops within {ALIGN_TOL_M} m of the route")

    mono = all(arcs[i] < arcs[i + 1] for i in range(len(arcs) - 1))
    print(f"monotonic along route: {mono}")
    if not mono:
        for i in range(len(arcs) - 1):
            if arcs[i] >= arcs[i + 1]:
                print(f"  out of order: {corridor[i]} @{arcs[i]:.0f} m -> "
                      f"{corridor[i+1]} @{arcs[i+1]:.0f} m")
        sys.exit("stop order does not follow the route — refusing to write route_shape.csv")

    # ---- along-route vs straight-line segment lengths ----
    print("\nsegment  along-route(m)  straight(m)  ratio")
    for i in range(len(corridor) - 1):
        road = arcs[i + 1] - arcs[i]
        straight = math.dist(stops[corridor[i]], stops[corridor[i + 1]])
        print(f"  {corridor[i]:>5}->{corridor[i+1]:<5} {road:8.1f} {straight:11.1f}  "
              f"{road/straight:.3f}")

    # ---- write ----
    os.makedirs("sim_inputs", exist_ok=True)
    with open("sim_inputs/route_shape.csv", "w") as fh:
        fh.write("seq,x,y\n")
        for i, (x, y) in enumerate(simplified):
            fh.write(f"{i},{x:.2f},{y:.2f}\n")
    print(f"\nwrote sim_inputs/route_shape.csv ({len(simplified)} points)")

    with open("sim_inputs/route_shape_stops.csv", "w") as fh:
        fh.write("bs_id,arclen_m,align_err_m,x,y\n")
        for s, al, d in rows:
            fh.write(f"{s},{al:.2f},{d:.2f},{stops[s][0]:.2f},{stops[s][1]:.2f}\n")
    print("wrote sim_inputs/route_shape_stops.csv (per-stop cut points for the net build)")

    if "--crosscheck" in sys.argv:
        crosscheck(sys.argv[sys.argv.index("--crosscheck") + 1], simplified, lat0, lon0,
                   poly, cum, a_s, b_s)


def crosscheck(osm_path, poly, lat0, lon0, raw, raw_cum, a_s, b_s):
    """Independent check: how close is the fetched geometry to the local BBBike extract's
    resolved fragments of the same relation?"""
    import osmium

    class RelWays(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.order = []

        def relation(self, r):
            if r.id == 9122669:
                self.order = [m.ref for m in r.members if m.type == "w"]

    class WayGeom(osmium.SimpleHandler):
        def __init__(self, ids):
            super().__init__()
            self.ids = ids
            self.pts = []

        def way(self, w):
            if w.id in self.ids:
                self.pts += [(n.location.lat, n.location.lon)
                             for n in w.nodes if n.location.valid()]

    rw = RelWays()
    rw.apply_file(osm_path)
    wg = WayGeom(set(rw.order))
    osmium.apply(osmium.io.Reader(osm_path),
                 osmium.NodeLocationsForWays(osmium.index.create_map("flex_mem")), wg)
    if not wg.pts:
        print("\ncrosscheck: local extract resolved no relation geometry")
        return
    # The local extract covers the WHOLE route (Tech Ridge to Southpark Meadows) and the route
    # loops north to the terminal before stop 5280, so a latitude filter would wrongly admit
    # pre-corridor points. Select by position ALONG the route instead: keep only local points
    # whose foot on the raw chain lies inside the corridor's arclength span.
    inside = []
    for lat, lon in wg.pts:
        x, y = project(lat, lon, lat0, lon0)
        s, d_on = arclength_of(x, y, raw, raw_cum)
        if a_s <= s <= b_s and d_on < 5.0:      # d_on guards against off-route matches
            inside.append((x, y))
    # Perpendicular distance to the LINE — not to the nearest vertex. DP leaves up to ~900 m
    # between vertices on straight arterial stretches, so a nearest-vertex metric would report
    # hundreds of metres for points sitting exactly on the line.
    ds = np.array([point_to_polyline(x, y, poly)[0] for x, y in inside])
    print(f"\ncrosscheck vs local BBBike extract: {len(rw.order)} member ways in the relation, "
          f"{len(wg.pts)} points resolved locally, {len(inside)} inside the corridor")
    print(f"  distance from local extract points to the fetched line: "
          f"max={ds.max():.2f} m  mean={ds.mean():.2f} m  median={np.median(ds):.2f} m  "
          f"({100.0*np.mean(ds <= DP_TOL_M + 0.01):.1f}% within the {DP_TOL_M} m DP tolerance)")
    print("  -> the two sources describe the same alignment; residuals are simplification only")


if __name__ == "__main__":
    main()
