"""Fit the digitized thermograms of Fig. 6 and compare with the published Table 3.

Data: Fig. 6 of Kladova et al., Int. J. Biol. Macromol. 45:524 (2009) = Chapter 2 of the PhD thesis
(Univ. Nova de Lisboa, 2009). Points were read from the vector graphic (exact marker centres) and
converted with a tick-mark calibration (scripts/digitize_fig6.py).

Published (Table 3): Zn-AK Tm 45.3 degC, dH 134.8 kcal/mol; Co-AK Tm 43.7 degC, dH 137.1 kcal/mol;
Tm +-0.2 K, dH +-5 %.
Observed: Tm reproduced to < 0.1 degC; dH about 2 % higher than published (cause not established,
e.g. baseline treatment / normalisation in the original software) - inside the published +-5 %.
"""
from pathlib import Path

import numpy as np
import pytest

from app import fitting

DATA = Path(__file__).resolve().parents[1] / "app" / "data"
PUBLISHED = {"Zn": (45.3, 134.8), "Co": (43.7, 137.1)}


def _fit(form):
    a = np.loadtxt(DATA / f"fig6_{form}_AK_digitized.csv", delimiter=",", skiprows=1)
    res = fitting.fit_dsc_two_state(a[:, 0], a[:, 1])
    return {p.name: p for p in res.params}, res


@pytest.mark.parametrize("form", PUBLISHED)
def test_tm_reproduces_published_value(form):
    p, _ = _fit(form)
    assert p["Tm"].value == pytest.approx(PUBLISHED[form][0], abs=0.1)


@pytest.mark.parametrize("form", PUBLISHED)
def test_enthalpy_within_published_uncertainty(form):
    p, _ = _fit(form)
    assert p["ΔH"].value == pytest.approx(PUBLISHED[form][1], rel=0.05)


@pytest.mark.parametrize("form", PUBLISHED)
def test_two_state_model_describes_the_curve(form):
    _, res = _fit(form)
    assert res.r2 > 0.995


def test_free_dcp_is_consistent_with_baseline_subtracted_curve():
    """The published curves are baseline-subtracted, so a free dCp should be ~0 with a large error."""
    a = np.loadtxt(DATA / "fig6_Zn_AK_digitized.csv", delimiter=",", skiprows=1)
    res = fitting.fit_dsc_two_state(a[:, 0], a[:, 1], fit_dcp=True)
    dcp = next(p for p in res.params if p.name == "ΔCp")
    assert abs(dcp.value) < 3 * dcp.stderr + 0.5


def test_digitized_files_have_expected_point_counts():
    assert len(np.loadtxt(DATA / "fig6_Zn_AK_digitized.csv", delimiter=",", skiprows=1)) == 124
    assert len(np.loadtxt(DATA / "fig6_Co_AK_digitized.csv", delimiter=",", skiprows=1)) == 120
