"""Extract the data points of Fig. 6 (DSC of Co-/Zn-AK) from the thesis PDF.

The figure is VECTOR graphics: every data point is a small closed path whose centre
can be read exactly. Open circles (white fill) = Zn2+-AK, solid circles (black fill) = Co2+-AK.
Axis calibration comes from the tick marks found in a high-resolution render of the figure.

Usage:  python digitize_fig6.py thesis.pdf [page_index_0based=46] [outdir=../backend/app/data]
Source: A. V. Kladova, PhD thesis, Univ. Nova de Lisboa (2009), Chapter 2 = Int. J. Biol. Macromol. 45:524 (2009), Fig. 6.
"""
import sys
import numpy as np
import pymupdf as fitz

pdf = sys.argv[1]
page_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 46
out = sys.argv[3] if len(sys.argv) > 3 else "../backend/app/data"
page = fitz.open(pdf)[page_idx]
AREA = fitz.Rect(255, 495, 420, 640)  # region of Fig. 6 on the page (points)

# --- axis calibration from tick marks (found via a 10x render) -----------------------
S = 10
clip = fitz.Rect(262, 495, 415, 625)
pix = page.get_pixmap(matrix=fitz.Matrix(S, S), clip=clip, alpha=False)
img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 0] < 110
H, W = img.shape


def runs(idx):
    groups, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            groups.append(cur)
            cur = []
        cur.append(i)
    if cur:
        groups.append(cur)
    return [float(np.mean(g)) for g in groups]


x_axis_row = max(range(H), key=lambda i: img[i].sum())
y_axis_col = max(range(W), key=lambda j: img[:, j].sum())
xt = runs([j for j in range(W) if img[x_axis_row + 6:x_axis_row + 20, j].sum() >= 10])
yt = runs([i for i in range(H) if img[i, y_axis_col - 20:y_axis_col - 7].sum() >= 10])
x_ticks_pt = [clip.x0 + g / S for g in xt][:8]            # 25,30,...,60 degC
y_ticks_pt = [clip.y0 + g / S for g in yt][:6]            # 25,20,...,0
assert len(x_ticks_pt) == 8 and len(y_ticks_pt) == 6, (x_ticks_pt, y_ticks_pt)
t_vals = np.arange(25, 61, 5)
cp_vals = np.array([25, 20, 15, 10, 5, 0])
ax, bx = np.polyfit(x_ticks_pt, t_vals, 1)
ay, by = np.polyfit(y_ticks_pt, cp_vals, 1)
print(f"calibration: {1/ax:.4f} pt/degC, {-1/ay:.4f} pt/(kcal/K/mol)")

# --- markers -------------------------------------------------------------------------
zn, co = [], []
for d in page.get_drawings():
    if d["type"] == "fs" and len(d["items"]) == 4 and AREA.intersects(d["rect"]):
        r = d["rect"]
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        (zn if d["fill"] == (1.0, 1.0, 1.0) else co).append((ax * cx + bx, ay * cy + by))
for name, pts in (("Zn-AK", zn), ("Co-AK", co)):
    pts.sort()
    arr = np.array(pts)
    fn = f"{out}/fig6_{name.split('-')[0]}_AK_digitized.csv"
    np.savetxt(fn, arr, delimiter=",", header="T_degC,Cp_ex_kcal_per_mol_K", comments="", fmt="%.4f")
    print(name, len(arr), "points ->", fn)
