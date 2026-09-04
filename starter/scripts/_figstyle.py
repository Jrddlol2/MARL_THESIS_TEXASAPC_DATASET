# -*- coding: utf-8 -*-
"""Shared publication figure style for the thesis (academic manuscript).

Usage in a figure script:
    import _figstyle as S
    S.apply()
    ... build fig ...
    S.save(fig, "mc_headway_cv")          # writes results/figures/mc_headway_cv.{pdf,png}

Design: titles are NOT baked into the image (they go in the LaTeX \caption); axis labels carry units.
Palette is the Okabe-Ito colourblind-safe set, also legible in grayscale. Role colours are fixed so the
same entity is the same colour in every figure. Figure widths target the manuscript text width
(report, A4, 3 cm margins => ~15 cm ~= 5.9 in). Output is vector PDF (for \includegraphics) + 300-dpi PNG.
"""
import os

# --- Okabe-Ito colourblind- & grayscale-safe palette ---------------------------------------------
ORANGE = "#E69F00"; SKY = "#56B4E9"; GREEN = "#009E73"; YELLOW = "#F0E442"
BLUE = "#0072B2"; VERM = "#D55E00"; PURPLE = "#CC79A7"; GREY = "#7A7A7A"; LGREY = "#BEBEBE"

# --- fixed role -> colour mapping (consistent across ALL figures) --------------------------------
NC_C = GREY            # No-Control / baseline context
FH_C = ORANGE          # Forward-Headway
EH_C = BLUE            # Even-Headway
CTRL_ACCENT = VERM     # the designated control stops
PRIMARY = BLUE         # single-series primary
CONTEXT = LGREY        # raw / background series
LINE = "#333333"       # median / reference lines

# --- figure sizes to the manuscript text width ---------------------------------------------------
WIDE = (5.9, 3.3)      # full text-width, standard
WIDE_TALL = (5.9, 4.2) # full-width, taller (maps, stacked)
SQUARE = (3.7, 3.7)    # square (calibration scatter)
TWO = (5.9, 2.9)       # two side-by-side panels across the width


def apply():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["CMU Serif", "DejaVu Serif", "Times New Roman", "Times"],
        "mathtext.fontset": "cm",
        "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8, "axes.axisbelow": True,
        "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
        "legend.frameon": False, "legend.handlelength": 1.6,
        "lines.linewidth": 1.4, "lines.markersize": 4,
        "figure.constrained_layout.use": True, "figure.dpi": 150,
        "savefig.dpi": 300, "savefig.bbox": "tight",
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def save(fig, name, folder="results/figures"):
    """Write both a vector PDF (for LaTeX) and a 300-dpi PNG (for slides). `name` has no extension."""
    os.makedirs(folder, exist_ok=True)
    base = os.path.join(folder, name)
    fig.savefig(base + ".pdf")
    fig.savefig(base + ".png")
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(f"wrote {base}.{{pdf,png}}")
