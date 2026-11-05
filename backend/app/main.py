"""FastAPI application: upload a CSV, get a fit back as JSON."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import fitting, synthetic

MAX_UPLOAD_BYTES = 2_000_000
DATA_DIR = Path(__file__).parent / "data"
THESIS_SOURCE = (
    "Digitized from Fig. 6 of A. V. Kladova, Int. J. Biol. Macromol. 45:524 (2009) / PhD thesis, "
    "Univ. Nova de Lisboa (2009). Marker positions read from the vector graphic; "
    "not the raw instrument file."
)

FE_RATES = {"thesis_fe_0p5": 0.5, "thesis_fe_1p0": 1.0, "thesis_fe_1p46": 1.46}

app = FastAPI(title="ThermoFit API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _read_two_columns(raw: bytes) -> tuple[list[float], list[float]]:
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large (max 2 MB).")
    try:
        text = raw.decode("utf-8-sig")
        df = pd.read_csv(io.StringIO(text), sep=None, engine="python", decimal=".")
    except Exception as exc:  # pandas raises many types
        raise HTTPException(400, f"Could not parse CSV: {exc}") from exc
    df = df.apply(pd.to_numeric, errors="coerce").dropna(how="all")
    if df.shape[1] < 2:
        raise HTTPException(400, "CSV needs at least two numeric columns (x, y).")
    df = df.iloc[:, :2].dropna()
    return df.iloc[:, 0].tolist(), df.iloc[:, 1].tolist()


def _run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs).as_dict()
    except fitting.FitError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/fit/dsc")
async def fit_dsc(
    file: UploadFile = File(...),
    model: str = Form("two_state"),
    cp_unit: str = Form("kcal"),
    scan_rate: float | None = Form(None),
    fit_dcp: bool = Form(False),
):
    """CSV columns: temperature in degC, heat capacity (kcal/mol/K or cal/mol/K)."""
    if cp_unit not in ("kcal", "cal"):
        raise HTTPException(422, "cp_unit must be 'kcal' or 'cal'.")
    T, cp = _read_two_columns(await file.read())
    if model == "two_state":
        return _run(fitting.fit_dsc_two_state, T, cp, cp_unit=cp_unit, fit_dcp=fit_dcp)
    if model == "irreversible":
        return _run(fitting.fit_dsc_irreversible, T, cp, scan_rate, cp_unit=cp_unit)
    raise HTTPException(422, "model must be 'two_state' or 'irreversible'.")


@app.get("/api/demo/{kind}")
def demo(kind: str):
    """Demo data as CSV text. Simulated sets are flagged synthetic; thesis sets carry their source."""
    source = None
    scan_rate = None
    if kind == "dsc_two_state":
        T, cp = synthetic.dsc_two_state(dCp=0.0)
        body = "T_degC,Cp_kcal_per_mol_K\n" + "\n".join(f"{a:.4f},{b:.5f}" for a, b in zip(T, cp))
    elif kind == "dsc_irreversible":
        T, cp, _ = synthetic.dsc_irreversible()
        body = "T_degC,Cp_kcal_per_mol_K\n" + "\n".join(f"{a:.4f},{b:.5f}" for a, b in zip(T, cp))
    elif kind in ("thesis_zn", "thesis_co"):
        name = "Zn" if kind == "thesis_zn" else "Co"
        body = (DATA_DIR / f"fig6_{name}_AK_digitized.csv").read_text()
        source = f"{name}2+-adenylate kinase. " + THESIS_SOURCE
    elif kind in FE_RATES:
        scan_rate = FE_RATES[kind]
        body = (DATA_DIR / f"fig7_Fe_AK_{kind.removeprefix('thesis_fe_')}Kmin_digitized.csv").read_text()
        source = f"Fe2+-adenylate kinase, scan rate {scan_rate:g} K/min. " + THESIS_SOURCE.replace("Fig. 6", "Fig. 7")
    else:
        raise HTTPException(404, "Unknown demo dataset.")
    return {"csv": body, "synthetic": source is None, "source": source, "scan_rate": scan_rate}
