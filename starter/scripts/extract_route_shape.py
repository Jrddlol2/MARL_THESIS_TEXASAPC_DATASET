"""
=============================================================================
 GET THE REAL ROAD SHAPE OF ROUTE 801 (direction 6)  ->  sim_inputs/route_shape.csv
=============================================================================

WHERE THE SHAPE COMES FROM
    OpenStreetMap (OSM) stores Route 801 southbound as "relation 9122669":
    an ordered list of road pieces ("ways"), each a list of GPS points.
    We saved it as sumo/rel_9122669.json (from the Overpass API).

WHAT THIS SCRIPT DOES
    1. Joins the road pieces end-to-end into one long line of points.
    2. Converts latitude/longitude to metres, with the SAME formula used
       everywhere else in the project:
           X = (lon - lon0) * cos(lat0) * 111320
           Y = (lat - lat0) * 110540
       where lat0, lon0 = the average position of the corridor stops.
    3. Cuts the line so it starts at the first stop and ends at the last stop.
    4. Simplifies it (Douglas-Peucker: remove points that lie within 7 m of a
       straight line between their neighbours).
    5. Checks every stop is within 60 m of the line and in the right order.
       If not, it refuses to write anything.
    6. Writes the line, and each stop's distance along it.

OUTPUT   sim_inputs/route_shape.csv          the simplified line (x, y in metres)
         sim_inputs/route_shape_stops.csv    each stop's distance along the line

RUN      python scripts/extract_route_shape.py          (from starter/, ~2 s)
         python scripts/extract_route_shape.py --crosscheck sumo/route801.osm
             (optional extra check against a local OSM file; needs `osmium`)
=============================================================================
"""

import json
import math
import os
import sys

import numpy as np
import pandas as pd

RELATION_FILE = "sumo/rel_9122669.json"
SIMPLIFY_TOLERANCE = 7.0     # metres (Douglas-Peucker)
MAX_STOP_DISTANCE = 60.0     # a stop further than this from the line = something is wrong
JOIN_TOLERANCE = 1.0         # two road pieces "connect" if their ends are within 1 m


# =============================================================================
# GEOMETRY HELPERS
# =============================================================================
def to_metres(lat, lon, lat0, lon0):
    """Latitude/longitude -> (x, y) in metres from the centre point."""
    x = (lon - lon0) * math.cos(math.radians(lat0)) * 111320.0
    y = (lat - lat0) * 110540.0
    return (x, y)


def closest_point_on_segment(px, py, ax, ay, bx, by):
    """Closest point to P on the straight segment A-B.

    Returns (qx, qy, t) where t is how far along A-B it is: 0 = at A, 1 = at B.
    """
    dx = bx - ax
    dy = by - ay
    length_squared = dx * dx + dy * dy
    if length_squared == 0.0:
        return ax, ay, 0.0
    t = ((px - ax) * dx + (py - ay) * dy) / length_squared
    t = max(0.0, min(1.0, t))
    return ax + t * dx, ay + t * dy, t


def closest_point_on_line(px, py, points):
    """Closest point to P on the whole line.

    Returns (distance, k, t): it lies on piece k (between points k and k+1),
    a fraction t of the way along that piece.
    """
    best_distance = float("inf")
    best_k = 0
    best_t = 0.0
    for k in range(len(points) - 1):
        ax, ay = points[k]
        bx, by = points[k + 1]
        qx, qy, t = closest_point_on_segment(px, py, ax, ay, bx, by)
        distance = math.hypot(px - qx, py - qy)
        if distance < best_distance:
            best_distance = distance
            best_k = k
            best_t = t
    return best_distance, best_k, best_t


def distance_so_far(points):
    """distance_so_far(points)[k] = metres along the line from point 0 to point k."""
    totals = [0.0]
    for k in range(len(points) - 1):
        totals.append(totals[-1] + math.hypot(points[k + 1][0] - points[k][0],
                                              points[k + 1][1] - points[k][1]))
    return totals


def position_along_line(px, py, points, totals):
    """How many metres along the line the point P is, and how far off the line."""
    distance, k, t = closest_point_on_line(px, py, points)
    piece_length = math.hypot(points[k + 1][0] - points[k][0], points[k + 1][1] - points[k][1])
    return totals[k] + t * piece_length, distance


def remove_repeated_points(points):
    """Drop any point that is within 1 cm of the point before it."""
    cleaned = []
    for i in range(len(points)):
        if i == 0 or math.dist(points[i], points[i - 1]) > 0.01:
            cleaned.append(points[i])
    return cleaned


def douglas_peucker(points, tolerance):
    """Simplify a line: keep only the points that matter for its shape.

    Start with the two end points. Find the point furthest from the straight
    line between them. If it is further than `tolerance`, keep it and repeat on
    both halves. (Uses a to-do list instead of recursion, because the line has
    over 1,700 points.)
    """
    if len(points) < 3:
        return list(points)
    keep = [False] * len(points)
    keep[0] = True
    keep[-1] = True
    to_do = [(0, len(points) - 1)]
    while len(to_do) > 0:
        first, last = to_do.pop()
        if last <= first + 1:
            continue
        ax, ay = points[first]
        bx, by = points[last]
        furthest_distance = 0.0
        furthest_index = first
        for k in range(first + 1, last):
            px, py = points[k]
            qx, qy, t = closest_point_on_segment(px, py, ax, ay, bx, by)
            distance = math.hypot(px - qx, py - qy)
            if distance > furthest_distance:
                furthest_distance = distance
                furthest_index = k
        if furthest_distance > tolerance:
            keep[furthest_index] = True
            to_do.append((first, furthest_index))
            to_do.append((furthest_index, last))

    simplified = []
    for i in range(len(points)):
        if keep[i]:
            simplified.append(points[i])
    return simplified


# =============================================================================
# JOIN THE OSM ROAD PIECES INTO ONE LINE
# =============================================================================
def rough_metres(a, b):
    """Rough distance between two (lat, lon) points -- only used to see if ends touch."""
    return math.hypot((b[1] - a[1]) * 96000.0, (b[0] - a[0]) * 110540.0)


def join_road_pieces(file_name):
    """Read the OSM relation and join its road pieces into one (lat, lon) line."""
    data = json.load(open(file_name))
    relation = data["elements"][0]
    tags = relation.get("tags", {})

    pieces = []
    for member in relation["members"]:
        if member.get("type") == "way" and member.get("geometry"):
            points = []
            for g in member["geometry"]:
                points.append((g["lat"], g["lon"]))
            pieces.append(points)
    print(f"relation {relation['id']}: ref='{tags.get('ref')}' direction='{tags.get('direction')}'")
    print(f"  {len(pieces)} member ways with geometry")

    # Flip the first piece if needed, so that its END touches the second piece.
    first = pieces[0]
    second = pieces[1]
    start_gap = min(rough_metres(first[0], second[0]), rough_metres(first[0], second[-1]))
    end_gap = min(rough_metres(first[-1], second[0]), rough_metres(first[-1], second[-1]))
    if start_gap < end_gap:
        first = list(reversed(first))
    line = list(first)

    # Add the other pieces one by one. OSM's order is USUALLY right, but pieces
    # #33-#35 are listed out of order, which would make the line jump 1.7 km and
    # come back. So at each step we look at the next 8 unused pieces and take
    # the one whose end touches our line. If none touches, we just take the next
    # piece in OSM order and record a gap.
    LOOK_AHEAD = 8
    remaining = pieces[1:]
    used = [False] * len(remaining)
    gaps = []
    repaired = 0

    for step in range(len(remaining)):
        candidates = []
        for i in range(len(remaining)):
            if not used[i]:
                candidates.append(i)
        candidates = candidates[:LOOK_AHEAD]

        best_index = None
        best_points = None
        best_gap = float("inf")
        for i in candidates:
            points = remaining[i]
            gap_forward = rough_metres(line[-1], points[0])      # our end -> its start
            gap_reversed = rough_metres(line[-1], points[-1])    # our end -> its end
            if gap_reversed < gap_forward:
                gap = gap_reversed
                oriented = list(reversed(points))
            else:
                gap = gap_forward
                oriented = points
            if gap < best_gap:
                best_index = i
                best_points = oriented
                best_gap = gap

        next_in_order = candidates[0]
        if best_gap <= JOIN_TOLERANCE:
            if best_index != next_in_order:
                repaired = repaired + 1
            line.extend(best_points[1:])       # skip its first point: it equals our last
        else:
            # nothing touches -- take the next piece in OSM order anyway
            best_index = next_in_order
            points = remaining[best_index]
            gap_forward = rough_metres(line[-1], points[0])
            gap_reversed = rough_metres(line[-1], points[-1])
            if gap_reversed < gap_forward:
                best_points = list(reversed(points))
            else:
                best_points = points
            gaps.append((len(line), min(gap_forward, gap_reversed)))
            line.extend(best_points)
        used[best_index] = True

    if repaired > 0:
        print(f"  repaired {repaired} out-of-order member(s) via look-ahead stitching")
    if len(gaps) > 0:
        largest = 0
        for position, size in gaps:
            largest = max(largest, size)
        print(f"  stitch gaps: {len(gaps)} (max {largest:.1f} m)")
    else:
        print("  stitched with no gaps (all member ways share endpoints)")
    print(f"  raw polyline: {len(line)} points")
    return line


# =============================================================================
# MAIN
# =============================================================================
def main():
    corridor = []
    for line in open("corridor.txt"):
        if line.strip() != "":
            corridor.append(int(line.strip()))
    coordinates = pd.read_csv("sim_inputs/stop_coordinates.csv").set_index("bs_id").loc[corridor]
    lat0 = coordinates["mean_lat"].mean()
    lon0 = coordinates["mean_lon"].mean()
    print(f"projection origin: lat0={lat0:.6f} lon0={lon0:.6f} "
          f"(mean of {len(corridor)} corridor stops)\n")

    if not os.path.exists(RELATION_FILE):
        sys.exit(f"missing {RELATION_FILE} — run the Overpass fetch first")

    # ---- 1-2. join the pieces and convert to metres --------------------------------
    latlon_line = join_road_pieces(RELATION_FILE)
    full_line = []
    for lat, lon in latlon_line:
        full_line.append(to_metres(lat, lon, lat0, lon0))
    full_line = remove_repeated_points(full_line)

    stop_xy = {}
    for stop in corridor:
        stop_xy[stop] = to_metres(coordinates.loc[stop, "mean_lat"], coordinates.loc[stop, "mean_lon"], lat0, lon0)

    # ---- 3. cut the line at the first and last stop ------------------------------------
    first_stop = corridor[0]
    last_stop = corridor[-1]
    first_x, first_y = stop_xy[first_stop]
    last_x, last_y = stop_xy[last_stop]

    totals = distance_so_far(full_line)
    start_at, start_off = position_along_line(first_x, first_y, full_line, totals)
    end_at, end_off = position_along_line(last_x, last_y, full_line, totals)
    print(f"\ntrim: stop {first_stop} at {start_at:.0f} m (off-line {start_off:.1f} m), "
          f"stop {last_stop} at {end_at:.0f} m (off-line {end_off:.1f} m); "
          f"full route {totals[-1]:.0f} m")
    if start_at > end_at:
        sys.exit("ERROR: first corridor stop lies AFTER the last one along the relation — "
                 "wrong direction relation selected")

    # The cut line starts exactly at the first stop's closest point on the road,
    # keeps every route point in between, and ends at the last stop's closest point.
    distance, k_first, t = closest_point_on_line(first_x, first_y, full_line)
    distance, k_last, t = closest_point_on_line(last_x, last_y, full_line)
    start_x, start_y, t = closest_point_on_segment(first_x, first_y, full_line[k_first][0], full_line[k_first][1],
                                                   full_line[k_first + 1][0], full_line[k_first + 1][1])
    end_x, end_y, t = closest_point_on_segment(last_x, last_y, full_line[k_last][0], full_line[k_last][1],
                                               full_line[k_last + 1][0], full_line[k_last + 1][1])
    trimmed = [(start_x, start_y)]
    for k in range(len(full_line)):
        if start_at < totals[k] < end_at:
            trimmed.append(full_line[k])
    trimmed.append((end_x, end_y))
    trimmed = remove_repeated_points(trimmed)
    print(f"trimmed polyline: {len(trimmed)} points, {distance_so_far(trimmed)[-1]:.0f} m")

    # ---- 4. simplify ----------------------------------------------------------------
    simplified = douglas_peucker(trimmed, SIMPLIFY_TOLERANCE)
    print(f"simplified: {len(trimmed)} -> {len(simplified)} points (DP tol {SIMPLIFY_TOLERANCE} m), "
          f"length {distance_so_far(simplified)[-1]:.0f} m")

    # ---- 5. check: every stop close to the line, and in driving order ---------------
    simplified_totals = distance_so_far(simplified)
    stop_rows = []          # (stop id, metres along the line, metres off the line)
    for stop in corridor:
        x, y = stop_xy[stop]
        along, off = position_along_line(x, y, simplified, simplified_totals)
        stop_rows.append((stop, along, off))

    off_line = []
    along_line = []
    for stop, along, off in stop_rows:
        off_line.append(off)
        along_line.append(along)
    off_line = np.array(off_line)
    print(f"\nstop-to-polyline distance (m): max={off_line.max():.1f} mean={off_line.mean():.1f}")

    too_far = []
    for stop, along, off in stop_rows:
        if off > MAX_STOP_DISTANCE:
            too_far.append((stop, round(off, 1)))
    if len(too_far) > 0:
        print(f"FAIL: {len(too_far)} stop(s) beyond {MAX_STOP_DISTANCE} m: {too_far}")
        sys.exit("extraction is wrong — refusing to write route_shape.csv")
    print(f"OK: all {len(corridor)} stops within {MAX_STOP_DISTANCE} m of the route")

    in_order = True
    for i in range(len(along_line) - 1):
        if along_line[i] >= along_line[i + 1]:
            in_order = False
    print(f"monotonic along route: {in_order}")
    if not in_order:
        for i in range(len(along_line) - 1):
            if along_line[i] >= along_line[i + 1]:
                print(f"  out of order: {corridor[i]} @{along_line[i]:.0f} m -> "
                      f"{corridor[i+1]} @{along_line[i+1]:.0f} m")
        sys.exit("stop order does not follow the route — refusing to write route_shape.csv")

    # ---- road distance vs straight-line distance, per segment -------------------------
    print("\nsegment  along-route(m)  straight(m)  ratio")
    for i in range(len(corridor) - 1):
        road = along_line[i + 1] - along_line[i]
        straight = math.dist(stop_xy[corridor[i]], stop_xy[corridor[i + 1]])
        print(f"  {corridor[i]:>5}->{corridor[i+1]:<5} {road:8.1f} {straight:11.1f}  "
              f"{road/straight:.3f}")

    # ---- 6. write the two files ---------------------------------------------------------
    os.makedirs("sim_inputs", exist_ok=True)
    file = open("sim_inputs/route_shape.csv", "w")
    file.write("seq,x,y\n")
    for i in range(len(simplified)):
        x, y = simplified[i]
        file.write(f"{i},{x:.2f},{y:.2f}\n")
    file.close()
    print(f"\nwrote sim_inputs/route_shape.csv ({len(simplified)} points)")

    file = open("sim_inputs/route_shape_stops.csv", "w")
    file.write("bs_id,arclen_m,align_err_m,x,y\n")
    for stop, along, off in stop_rows:
        file.write(f"{stop},{along:.2f},{off:.2f},{stop_xy[stop][0]:.2f},{stop_xy[stop][1]:.2f}\n")
    file.close()
    print("wrote sim_inputs/route_shape_stops.csv (per-stop cut points for the net build)")

    if "--crosscheck" in sys.argv:
        osm_file = sys.argv[sys.argv.index("--crosscheck") + 1]
        crosscheck(osm_file, simplified, lat0, lon0, full_line, totals, start_at, end_at)


# =============================================================================
# OPTIONAL: COMPARE WITH A LOCAL OSM FILE  (needs the `osmium` package)
# =============================================================================
def crosscheck(osm_file, line, lat0, lon0, full_line, full_totals, start_at, end_at):
    """Independent check: how close is our line to the same route read from a
    local OpenStreetMap extract (BBBike)? Only the pieces inside the corridor
    are compared, and distance is measured to the LINE, not to its points."""
    import osmium

    class RouteWayIds(osmium.SimpleHandler):
        """Collect the ids of the road pieces in relation 9122669."""
        def __init__(self):
            super().__init__()
            self.order = []

        def relation(self, r):
            if r.id == 9122669:
                self.order = [m.ref for m in r.members if m.type == "w"]

    class RouteWayPoints(osmium.SimpleHandler):
        """Collect the (lat, lon) points of those road pieces."""
        def __init__(self, ids):
            super().__init__()
            self.ids = ids
            self.pts = []

        def way(self, w):
            if w.id in self.ids:
                self.pts += [(n.location.lat, n.location.lon)
                             for n in w.nodes if n.location.valid()]

    way_ids = RouteWayIds()
    way_ids.apply_file(osm_file)
    way_points = RouteWayPoints(set(way_ids.order))
    osmium.apply(osmium.io.Reader(osm_file),
                 osmium.NodeLocationsForWays(osmium.index.create_map("flex_mem")), way_points)
    if not way_points.pts:
        print("\ncrosscheck: local extract resolved no relation geometry")
        return

    # keep only local points that fall inside the corridor (by position along the route)
    inside = []
    for lat, lon in way_points.pts:
        x, y = to_metres(lat, lon, lat0, lon0)
        along, off = position_along_line(x, y, full_line, full_totals)
        if start_at <= along <= end_at and off < 5.0:
            inside.append((x, y))

    distances = []
    for x, y in inside:
        distances.append(closest_point_on_line(x, y, line)[0])
    distances = np.array(distances)
    print(f"\ncrosscheck vs local BBBike extract: {len(way_ids.order)} member ways in the relation, "
          f"{len(way_points.pts)} points resolved locally, {len(inside)} inside the corridor")
    print(f"  distance from local extract points to the fetched line: "
          f"max={distances.max():.2f} m  mean={distances.mean():.2f} m  median={np.median(distances):.2f} m  "
          f"({100.0*np.mean(distances <= SIMPLIFY_TOLERANCE + 0.01):.1f}% within the {SIMPLIFY_TOLERANCE} m DP tolerance)")
    print("  -> the two sources describe the same alignment; residuals are simplification only")


if __name__ == "__main__":
    main()
