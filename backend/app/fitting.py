"""Least-squares fitting wrappers with parameter uncertainties and fit quality.

All fitted parameters are expressed in practical units (kcal/mol, degC) so the
optimiser sees well-scaled numbers; conversion to the model's cal/mol / K happens
inside the wrapper functions.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

from . import models

KELVIN = 273.15


class FitError(ValueError):
    """Raised for unusable input or a failed fit (message is user-facing)."""


@dataclass
class Param:
    name: str
    value: float
    stderr: float | None
    ci95: tuple[float, float] | None
    unit: str

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "stderr": self.stderr,
            "ci95": list(self.ci95) if self.ci95 else None,
            "unit": self.unit,
        }


@dataclass
class FitResult:
    model: str
    params: list[Param]
    x: list[float]
    y: list[float]
    x_fit: list[float]
    y_fit: list[float]
    residuals: list[float]
    r2: float
    rmse: float
    n_points: int
    extras: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "model": self.model,
            "params": [p.as_dict() for p in self.params],
            "x": self.x,
            "y": self.y,
            "x_fit": self.x_fit,
            "y_fit": self.y_fit,
            "residuals": self.residuals,
            "r2": self.r2,
            "rmse": self.rmse,
            "n_points": self.n_points,
            "extras": self.extras,
        }


# ------------------------------------------------------------------ helpers
def _clean(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise FitError("x and y must be one-dimensional arrays of equal length.")
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    order = np.argsort(x)
    x, y = x[order], y[order]
    if len(np.unique(x)) != len(x):
        raise FitError("x values must be unique (duplicate temperatures / concentrations found).")
    return x, y


def _uncertainties(popt, pcov, n, names, units):
    dof = n - len(popt)
    params = []
    if dof > 0 and np.all(np.isfinite(pcov)):
        se = np.sqrt(np.diag(pcov))
        tcrit = stats.t.ppf(0.975, dof)
    else:
        se = [None] * len(popt)
        tcrit = None
    for name, unit, val, s in zip(names, units, popt, se):
        if s is None or tcrit is None:
            params.append(Param(name, float(val), None, None, unit))
        else:
            params.append(
                Param(name, float(val), float(s), (float(val - tcrit * s), float(val + tcrit * s)), unit)
            )
    return params


def _quality(y, y_model):
    resid = y - y_model
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rmse = float(np.sqrt(ss_res / len(y)))
    return resid, r2, rmse


def _run_curve_fit(f, x, y, p0, lo, hi):
    try:
        return curve_fit(f, x, y, p0=p0, bounds=(lo, hi), maxfev=20000)
    except (RuntimeError, ValueError) as exc:
        raise FitError(f"Fit did not converge: {exc}") from exc


def _baseline_start(T, y):
    """Estimate a linear baseline from the first and last 10 % of the data."""
    n = max(3, len(T) // 10)
    tl, yl = T[:n].mean(), y[:n].mean()
    th, yh = T[-n:].mean(), y[-n:].mean()
    slope = (yh - yl) / (th - tl)
    return yl + slope * (T - tl), slope


# ------------------------------------------------------------------ DSC
def fit_dsc_two_state(T_c, cp, cp_unit="kcal", fit_dcp=False) -> FitResult:
    """Fit a reversible two-state model to a DSC thermogram.

    T_c : temperature in degC.   cp : heat capacity in `cp_unit` per mol per K
    ("kcal" -> kcal/mol/K, "cal" -> cal/mol/K).
    """
    T_c, cp = _clean(T_c, cp)
    if len(T_c) < 15:
        raise FitError("Need at least 15 data points for a DSC fit.")
    scale = 1.0 if cp_unit == "kcal" else 1e-3  # work internally in kcal/mol/K
    y = cp * scale
    T = T_c + KELVIN

    base, slope = _baseline_start(T, y)
    peak = y - base
    i_max = int(np.argmax(peak))
    Tm0 = T[i_max]
    area = np.trapezoid(np.clip(peak, 0, None), T)  # kcal/mol (heat of the transition)
    dH0 = max(area, 1.0)

    def f_free(T_, Tm, dH, dCp, b0, b1):
        return models.dsc_two_state(T_, Tm, dH * 1e3, dCp * 1e3, b0 * 1e3, b1 * 1e3) / 1e3

    def f_fixed(T_, Tm, dH, b0, b1):
        return f_free(T_, Tm, dH, 0.0, b0, b1)

    b0_0 = float(np.interp(Tm0, T, base))
    if fit_dcp:
        names = ["Tm", "ΔH", "ΔCp", "baseline offset", "baseline slope"]
        units = ["K", "kcal/mol", "kcal/mol/K", "kcal/mol/K", "kcal/mol/K²"]
        p0 = [Tm0, dH0, 0.0, b0_0, slope]
        lo = [T.min(), 1.0, -30.0, -np.inf, -np.inf]
        hi = [T.max(), 5000.0, 30.0, np.inf, np.inf]
        popt, pcov = _run_curve_fit(f_free, T, y, p0, lo, hi)
        y_model = f_free(T, *popt)
    else:
        names = ["Tm", "ΔH", "baseline offset", "baseline slope"]
        units = ["K", "kcal/mol", "kcal/mol/K", "kcal/mol/K²"]
        p0 = [Tm0, dH0, b0_0, slope]
        lo = [T.min(), 1.0, -np.inf, -np.inf]
        hi = [T.max(), 5000.0, np.inf, np.inf]
        popt, pcov = _run_curve_fit(f_fixed, T, y, p0, lo, hi)
        y_model = f_fixed(T, *popt)

    params = _uncertainties(popt, pcov, len(T), names, units)
    # report Tm in degC for convenience
    tm = params[0]
    params[0] = Param(
        "Tm", tm.value - KELVIN, tm.stderr,
        (tm.ci95[0] - KELVIN, tm.ci95[1] - KELVIN) if tm.ci95 else None, "°C",
    )
    resid, r2, rmse = _quality(y, y_model)

    # component curves for plotting
    pdict = {p.name: p.value for p in params}
    Tm_K = pdict["Tm"] + KELVIN
    dCp = pdict.get("ΔCp", 0.0)
    T_fine = np.linspace(T.min(), T.max(), 400)
    y_fine = f_free(T_fine, Tm_K, pdict["ΔH"], dCp, pdict["baseline offset"], pdict["baseline slope"])
    baseline_fine = pdict["baseline offset"] + pdict["baseline slope"] * (T_fine - Tm_K)
    # van't Hoff / calorimetric enthalpy ratio is a standard two-state check
    dH_cal = float(np.trapezoid(np.clip(y - (pdict["baseline offset"] + pdict["baseline slope"] * (T - Tm_K)), 0, None), T))

    return FitResult(
        model="two_state",
        params=params,
        x=(T - KELVIN).tolist(), y=(y / scale).tolist(),
        x_fit=(T_fine - KELVIN).tolist(), y_fit=(y_fine / scale).tolist(),
        residuals=(resid / scale).tolist(), r2=r2, rmse=rmse / scale, n_points=len(T),
        extras={
            "baseline": (baseline_fine / scale).tolist(),
            "dH_calorimetric_kcal": dH_cal,
            "cp_unit": "kcal/mol/K" if cp_unit == "kcal" else "cal/mol/K",
        },
    )


def fit_dsc_irreversible(T_c, cp, scan_rate_K_per_min, cp_unit="kcal") -> FitResult:
    """Fit the irreversible N -> D model (Sanchez-Ruiz) at a known scan rate."""
    if scan_rate_K_per_min is None or scan_rate_K_per_min <= 0:
        raise FitError("A positive scan rate (K/min) is required for the irreversible model.")
    T_c, cp = _clean(T_c, cp)
    if len(T_c) < 15:
        raise FitError("Need at least 15 data points for a DSC fit.")
    scale = 1.0 if cp_unit == "kcal" else 1e-3
    y = cp * scale
    T = T_c + KELVIN
    base, slope = _baseline_start(T, y)
    peak = y - base
    i_max = int(np.argmax(peak))
    Tmax0 = T[i_max]
    dH0 = max(np.trapezoid(np.clip(peak, 0, None), T), 1.0)
    v = float(scan_rate_K_per_min)

    def f(T_, dH, T_star, Ea, b0, b1):
        return models.dsc_irreversible(T_, dH * 1e3, T_star, Ea * 1e3, b0 * 1e3, b1 * 1e3, v) / 1e3

    # T* (k = 1/min) sits slightly below the peak; Ea guess ~ 100 kcal/mol
    p0 = [dH0, Tmax0 - 1.0, 100.0, float(np.interp(Tmax0, T, base)), slope]
    lo = [1.0, T.min(), 5.0, -np.inf, -np.inf]
    hi = [5000.0, T.max(), 1000.0, np.inf, np.inf]
    popt, pcov = _run_curve_fit(f, T, y, p0, lo, hi)
    y_model = f(T, *popt)
    names = ["ΔH", "T* (k = 1/min)", "Ea", "baseline offset", "baseline slope"]
    units = ["kcal/mol", "K", "kcal/mol", "kcal/mol/K", "kcal/mol/K²"]
    params = _uncertainties(popt, pcov, len(T), names, units)
    resid, r2, rmse = _quality(y, y_model)

    T_fine = np.linspace(T.min(), T.max(), 800)  # fine grid for the numerical integral
    y_fine = f(T_fine, *popt)
    return FitResult(
        model="irreversible",
        params=params,
        x=(T - KELVIN).tolist(), y=(y / scale).tolist(),
        x_fit=(T_fine - KELVIN).tolist(), y_fit=(y_fine / scale).tolist(),
        residuals=(resid / scale).tolist(), r2=r2, rmse=rmse / scale, n_points=len(T),
        extras={
            "scan_rate_K_per_min": v,
            "cp_unit": "kcal/mol/K" if cp_unit == "kcal" else "cal/mol/K",
        },
    )


def fit_dsc_irreversible_global(curves) -> FitResult:
    """Global fit of the irreversible N -> D model to several scan rates.

    curves: list of (T_degC, cp, scan_rate_K_per_min, ) with cp in kcal/mol/K.
    T* and Ea are SHARED between curves (they are properties of the process, not of the scan);
    dH and the linear baseline are fitted per curve. This is how the scan-rate dependence
    pins down Ea much better than a single curve can.
    """
    from scipy.optimize import least_squares

    if len(curves) < 2:
        raise FitError("A global fit needs at least two scan rates.")
    data = []
    for T_c, cp, v in curves:
        if v is None or v <= 0:
            raise FitError("Every curve needs a positive scan rate.")
        T_c, cp = _clean(T_c, cp)
        if len(T_c) < 15:
            raise FitError("Need at least 15 data points per curve.")
        data.append((T_c + KELVIN, cp, float(v)))
    k = len(data)

    # starting values from the single-curve fits
    singles = [fit_dsc_irreversible(T - KELVIN, cp, v) for T, cp, v in data]
    ts0 = float(np.mean([next(p for p in s.params if p.name.startswith("T*")).value for s in singles]))
    ea0 = float(np.mean([next(p for p in s.params if p.name == "Ea").value for s in singles]))
    p0 = [ts0, ea0]
    for s in singles:
        d = {p.name: p.value for p in s.params}
        p0 += [d["ΔH"], d["baseline offset"], d["baseline slope"]]

    def model_i(p, i):
        T, _, v = data[i]
        dH, b0, b1 = p[2 + 3 * i: 5 + 3 * i]
        return models.dsc_irreversible(T, dH * 1e3, p[0], p[1] * 1e3, b0 * 1e3, b1 * 1e3, v) / 1e3

    def resid(p):
        return np.concatenate([model_i(p, i) - data[i][1] for i in range(k)])

    try:
        sol = least_squares(resid, p0, x_scale=np.maximum(np.abs(p0), 1e-2))
    except (RuntimeError, ValueError) as exc:
        raise FitError(f"Global fit did not converge: {exc}") from exc

    n = sum(len(d[0]) for d in data)
    dof = max(n - len(p0), 1)
    s2 = float(np.sum(sol.fun**2)) / dof
    try:
        cov = np.linalg.inv(sol.jac.T @ sol.jac) * s2
        se = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError:
        se = [None] * len(p0)
    tcrit = stats.t.ppf(0.975, dof)

    def mk(name, idx, unit):
        s_ = None if se[idx] is None else float(se[idx])
        ci = None if s_ is None else (float(sol.x[idx] - tcrit * s_), float(sol.x[idx] + tcrit * s_))
        return Param(name, float(sol.x[idx]), s_, ci, unit)

    params = [mk("T* (k = 1/min)", 0, "K"), mk("Ea", 1, "kcal/mol")]
    for i, (_, _, v) in enumerate(data):
        params.append(mk(f"ΔH @ {v:g} K/min", 2 + 3 * i, "kcal/mol"))

    y_all = np.concatenate([d[1] for d in data])
    r2 = 1.0 - float(np.sum(sol.fun**2)) / float(np.sum((y_all - y_all.mean()) ** 2))
    return FitResult(
        model="irreversible_global",
        params=params,
        x=np.concatenate([d[0] - KELVIN for d in data]).tolist(),
        y=y_all.tolist(),
        x_fit=[], y_fit=[],
        residuals=(-sol.fun).tolist(), r2=r2, rmse=float(np.sqrt(np.mean(sol.fun**2))), n_points=n,
        extras={"scan_rates_K_per_min": [d[2] for d in data]},
    )
