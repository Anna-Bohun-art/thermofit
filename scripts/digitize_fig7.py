"""Extract the data points of Fig. 7 (DSC of Fe2+-AK, irreversible, three scan rates) from the thesis PDF.

Vector graphic: marker centres are exact. Squares = 0.5 K/min, triangles = 1 K/min, circles = 1.46 K/min
(legend in the figure caption). Axis calibration from the vector tick marks.

Usage:  python digitize_fig7.py thesis.pdf [page_index_0based=47] [outdir=../backend/app/data]
Source: A. V. Kladova, PhD thesis, Univ. Nova de Lisboa (2009), Chapter 2 = Int. J. Biol. Macromol. 45:524 (2009), Fig. 7.
"""
import sys
import numpy as np
import pymupdf as fitz

pdf = sys.argv[1]
page_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 47
out = sys.argv[3] if len(sys.argv) > 3 else "../backend/app/data"
page = fitz.open(pdf)[page_idx]
AREA = fitz.Rect(262, 400, 420, 522)  # plot region on the page (points)

# --- calibration from major ticks (long ticks: 2.7 pt) ---------------------------------
x_ticks, y_ticks = [], []
for d in page.get_drawings():
    if d["type"] == "s" and len(d["items"]) == 1:
        a, b = d["items"][0][1], d["items"][0][2]
        if abs(a.x - b.x) < 1e-6 and abs(abs(a.y - b.y) - 2.69) < 0.05 and AREA.contains(fitz.Point(a.x, a.y)):
            x_ticks.append(a.x)  # vertical major tick below the x axis
        if abs(a.y - b.y) < 1e-6 and abs(abs(a.x - b.x) - 2.67) < 0.05 and AREA.contains(fitz.Point(a.x, a.y)):
            y_ticks.append(a.y)  # horizontal major tick left of the y axis
x_ticks, y_ticks = sorted(x_ticks), sorted(y_ticks, reverse=True)
assert len(x_ticks) == 5 and len(y_ticks) == 6, (x_ticks, y_ticks)
ax, bx = np.polyfit(x_ticks, [30, 35, 40, 45, 50], 1)
ay, by = np.polyfit(y_ticks, [0, 5, 10, 15, 20, 25], 1)
print(f"calibration: {1/ax:.4f} pt/degC, {-1/ay:.4f} pt/(kcal/K/mol)")

# --- markers: shape identifies the scan rate -------------------------------------------
series = {0.5: [], 1.0: [], 1.46: []}
for d in page.get_drawings():
    if d["type"] != "fs" or not AREA.intersects(d["rect"]) or d["rect"].width > 3.2:
        continue
    kinds = tuple(sorted({it[0] for it in d["items"]}))
    n = len(d["items"])
    if kinds == ("re",):
        rate = 0.5                     # square
    elif kinds == ("c",):
        rate = 1.46                    # circle
    elif kinds == ("l",) and n == 3:
        rate = 1.0                     # triangle
    elif kinds == ("l",) and n == 4:
        rate = 0.5                     # square drawn as 4 lines
    else:
        continue
    r = d["rect"]
    series[rate].append((ax * (r.x0 + r.x1) / 2 + bx, ay * (r.y0 + r.y1) / 2 + by))
for rate, pts in series.items():
    arr = np.array(sorted(pts))
    fn = f"{out}/fig7_Fe_AK_{str(rate).replace('.', 'p')}Kmin_digitized.csv"
    np.savetxt(fn, arr, delimiter=",", header="T_degC,Cp_ex_kcal_per_mol_K", comments="", fmt="%.4f")
    print(f"{rate} K/min: {len(arr)} points -> {fn}")
