"""Check the two-state thermodynamics against published values.

Source: A. V. Kladova, doctoral thesis (Universidade Nova de Lisboa, 2009), Chapter 2 =
Int. J. Biol. Macromol. 45(5):524-531 (2009), Table 3 (AK from D. gigas, pH 10.0).
Columns: Tm (degC), dH(Tm) kcal/mol, dG(25 degC) kcal/mol, Ts (degC), dG(Ts) kcal/mol.
dCp = 2.0 kcal/K/mol for all forms. Published Tm +-0.2 K, dH +-5 %; derived values are
rounded to 1 decimal, so tolerances below allow for rounding only.
"""
import numpy as np
import pytest

from app import models

KELVIN = 273.15
DCP = 2.0

TABLE3 = {
    "Zn-AK": (45.3, 134.8, 7.3, -15.4, 13.3),
    "Co-AK": (43.7, 137.1, 7.0, -17.9, 13.8),
    "Fe-AK": (45.0, 127.8, 6.8, -12.9, 12.0),
}


@pytest.mark.parametrize("form", TABLE3)
def test_dg_at_25c_matches_published(form):
    tm, dh, dg25, _, _ = TABLE3[form]
    assert models.gibbs_energy(25 + KELVIN, tm + KELVIN, dh, DCP) == pytest.approx(dg25, abs=0.06)


@pytest.mark.parametrize("form", TABLE3)
def test_temperature_of_max_stability_matches_published(form):
    tm, dh, _, ts, _ = TABLE3[form]
    ts_calc = models.temperature_of_max_stability(tm + KELVIN, dh * 1.0, DCP) - KELVIN
    assert ts_calc == pytest.approx(ts, abs=0.1)


@pytest.mark.parametrize("form", TABLE3)
def test_dg_at_ts_matches_published(form):
    tm, dh, _, _, dg_ts = TABLE3[form]
    Tm = tm + KELVIN
    Ts = models.temperature_of_max_stability(Tm, dh, DCP)
    assert models.gibbs_energy(Ts, Tm, dh, DCP) == pytest.approx(dg_ts, abs=0.06)


def test_ts_is_the_maximum_of_dg():
    Tm = 45.3 + KELVIN
    Ts = models.temperature_of_max_stability(Tm, 134.8, DCP)
    T = np.linspace(Ts - 20, Ts + 20, 4001)
    assert T[np.argmax(models.gibbs_energy(T, Tm, 134.8, DCP))] == pytest.approx(Ts, abs=0.02)
