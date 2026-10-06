"""build_net.py -- write the road + bus stops + bus type, then run netconvert.

Guide: Section 4, Step 1 (manuscript Sec 3.2.1 Simulation Environment).
A straight corridor: 21 nodes, 20 one-lane edges e0..e19, 20 bus stops s0..s19.
Stop s_i sits on lane e_i_0 from 5 m to 25 m. The last edge e19 carries the
500 m tail so buses can drive off past s19.
"""
import os
import subprocess
from sumolib import checkBinary
import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
NET_DIR = os.path.join(HERE, "net")


def _write_nodes(path):
    # One node per stop at x = 0, 400, ... plus one 500 m after the last stop.
    lines = ['<nodes>']
    for i in range(P.N_STOPS):            # n0 .. n19  (the stops)
        lines.append(f'    <node id="n{i}" x="{i * P.STOP_SPACING:.1f}" y="0"/>')
    last_x = (P.N_STOPS - 1) * P.STOP_SPACING + P.TAIL   # n20, end of the tail
    lines.append(f'    <node id="n{P.N_STOPS}" x="{last_x:.1f}" y="0"/>')
    lines.append('</nodes>')
    open(path, "w").write("\n".join(lines))


def _write_edges(path):
    # e_i from n_i to n_{i+1}, one lane, speed = limit. e19 is the 500 m tail.
    lines = ['<edges>']
    for i in range(P.N_STOPS):            # e0 .. e19
        lines.append(
            f'    <edge id="e{i}" from="n{i}" to="n{i + 1}" '
            f'numLanes="1" speed="{P.SPEED_LIMIT}"/>'
        )
    lines.append('</edges>')
    open(path, "w").write("\n".join(lines))


def _write_busstops(path):
    # s_i on lane e_i_0 from 5 m to 25 m.
    lines = ['<additional>']
    for i in range(P.N_STOPS):
        lines.append(
            f'    <busStop id="s{i}" lane="e{i}_0" '
            f'startPos="{P.BUSSTOP_START}" endPos="{P.BUSSTOP_END}"/>'
        )
    lines.append('</additional>')
    open(path, "w").write("\n".join(lines))


def _write_vtype(path):
    # One bus type: no random speed variation (speedDev=0) so runs are repeatable.
    lines = [
        '<additional>',
        f'    <vType id="bus" vClass="bus" length="{P.BUS_LENGTH}" '
        f'personCapacity="{P.BUS_CAPACITY}" speedFactor="1.0" speedDev="0"/>',
        '</additional>',
    ]
    open(path, "w").write("\n".join(lines))


def build():
    os.makedirs(NET_DIR, exist_ok=True)
    nod = os.path.join(NET_DIR, "corridor.nod.xml")
    edg = os.path.join(NET_DIR, "corridor.edg.xml")
    net = os.path.join(NET_DIR, "corridor.net.xml")
    busstops = os.path.join(NET_DIR, "busstops.add.xml")
    vtype = os.path.join(NET_DIR, "vtype.add.xml")

    _write_nodes(nod)
    _write_edges(edg)
    _write_busstops(busstops)
    _write_vtype(vtype)

    # --no-turnarounds stops netconvert from building U-turns at the ends.
    cmd = [
        checkBinary("netconvert"),
        "--node-files", nod,
        "--edge-files", edg,
        "--output-file", net,
        "--no-turnarounds", "true",
        "--no-warnings", "true",
    ]
    subprocess.run(cmd, check=True)
    print("built network:", net)
    return {"net": net, "busstops": busstops, "vtype": vtype}


if __name__ == "__main__":
    paths = build()
    length_km = ((P.N_STOPS - 1) * P.STOP_SPACING + P.TAIL) / 1000.0
    print(f"corridor length {length_km:.1f} km, {P.N_STOPS} stops")
