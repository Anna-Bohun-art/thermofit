"""Fit the digitized Fe2+-AK thermograms (Fig. 7, three scan rates) and compare with Table 4.

Source: Kladova et al., Int. J. Biol. Macromol. 45:524 (2009) = Chapter 2 of the PhD thesis
(Univ. Nova de Lisboa, 2009). Published (Table 4), two-state irreversible model:
  scan rate (K/min)   0.5     1.0     1.46    global
  dH (kcal/mol)       106.5   108.5   110.1   -
  T* (degC)           43.2    43.1    43.1    43.1
  Ea (kcal/mol)       114.9   118.3   116.7   117.0
Observed: T* within 0.1 degC, dH within ~1.5 %, Ea within ~2.5 % (single curves) and within 1 % (global).
"""
from pathlib import Path

import numpy as np
import pytest

from app import fitting

DATA = Path(__file__).resolve().parents[1] / "app" / "data"
KELVIN = 273.15
PUBLISHED = {"0p5": (0.5, 106.5, 43.2, 114.9), "1p0": (1.0, 108.5, 43.1, 118.3), "1p46": (1.46, 110.1, 43.1, 116.7)}


def _load(key):
    return np.loadtxt(DATA / f"fig7_Fe_AK_{key}Kmin_digitized.csv", delimiter=",", skiprows=1)


def _single(key):
    v = PUBLISHED[key][0]
    a = _load(key)
    res = fitting.fit_dsc_irreversible(a[:, 0], a[:, 1], v)
    return {p.name: p for p in res.params}, res


@pytest.mark.parametrize("key", PUBLISHED)
def test_tstar_reproduces_published_value(key):
    p, _ = _single(key)
    assert p["T* (k = 1/min)"].value - KELVIN == pytest.approx(PUBLISHED[key][2], abs=0.1)


@pytest.mark.parametrize("key", PUBLISHED)
def test_enthalpy_and_activation_energy_close_to_published(key):
    p, _ = _single(key)
    assert p["ΔH"].value == pytest.approx(PUBLISHED[key][1], rel=0.03)
    assert p["Ea"].value == pytest.approx(PUBLISHED[key][3], rel=0.04)


@pytest.mark.parametrize("key", PUBLISHED)
def test_model_describes_curve(key):
    _, res = _single(key)
    assert res.r2 > 0.998


def test_global_fit_matches_published_global_values():
    curves = [(_load(k)[:, 0], _load(k)[:, 1], PUBLISHED[k][0]) for k in PUBLISHED]
    res = fitting.fit_dsc_irreversible_global(curves)
    p = {x.name: x for x in res.params}
    assert p["T* (k = 1/min)"].value - KELVIN == pytest.approx(43.1, abs=0.1)
    assert p["Ea"].value == pytest.approx(117.0, rel=0.02)
    assert res.r2 > 0.998


def test_global_fit_needs_two_curves():
    a = _load("1p0")
    with pytest.raises(fitting.FitError):
        fitting.fit_dsc_irreversible_global([(a[:, 0], a[:, 1], 1.0)])


def test_peak_shifts_up_with_scan_rate_in_the_data():
    """The kinetic signature: the measured peak moves to higher T when scanning faster."""
    peaks = [_load(k)[np.argmax(_load(k)[:, 1]), 0] for k in ("0p5", "1p0", "1p46")]
    assert peaks[0] < peaks[1] < peaks[2]
