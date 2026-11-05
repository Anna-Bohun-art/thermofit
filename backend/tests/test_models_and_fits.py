import numpy as np
import pytest

from app import fitting, models, synthetic

KELVIN = 273.15


# ---------------------------------------------------------------- physics sanity
def test_fraction_unfolded_is_half_at_tm():
    a = models.two_state_fraction_unfolded(np.array([318.45]), 318.45, 134800, 2000)
    assert a[0] == pytest.approx(0.5, abs=1e-9)


def test_two_state_peak_area_equals_enthalpy():
    """Integral of the baseline-free excess Cp over T equals dH (without dCp)."""
    T = np.linspace(290, 350, 20001)
    cp = models.two_state_excess_cp(T, 318.45, 134800, 0.0)
    assert np.trapezoid(cp, T) == pytest.approx(134800, rel=1e-3)


def test_two_state_peak_maximum_at_tm_without_dcp():
    T = np.linspace(290, 350, 6001)
    cp = models.two_state_excess_cp(T, 318.45, 134800, 0.0)
    # The 1/T^2 factor shifts the maximum ~0.03 K below Tm (real physics, not a bug).
    assert T[np.argmax(cp)] == pytest.approx(318.45, abs=0.1)


def test_irreversible_peak_shifts_up_with_scan_rate():
    T = np.linspace(300, 360, 4000)
    peaks = [models.irreversible_tm(T, 120000, 325.0, 95000, v) for v in (0.5, 1.0, 2.0)]
    assert peaks[0] < peaks[1] < peaks[2]


def test_irreversible_area_equals_enthalpy():
    T = np.linspace(295, 370, 20001)
    cp = models.irreversible_excess_cp(T, 120000, 325.0, 95000, 1.0)
    assert np.trapezoid(cp, T) == pytest.approx(120000, rel=2e-3)


# ---------------------------------------------------------------- fits recover truth
def test_two_state_fit_recovers_parameters_no_dcp():
    T, cp = synthetic.dsc_two_state(dCp=0.0)
    res = fitting.fit_dsc_two_state(T, cp)
    p = {x.name: x for x in res.params}
    assert p["Tm"].value == pytest.approx(45.3, abs=0.1)
    assert p["ΔH"].value == pytest.approx(134.8, rel=0.02)
    assert res.r2 > 0.99


def test_two_state_fit_recovers_parameters_with_free_dcp():
    T, cp = synthetic.dsc_two_state(dCp=2.0, noise=0.01)
    res = fitting.fit_dsc_two_state(T, cp, fit_dcp=True)
    p = {x.name: x for x in res.params}
    assert p["Tm"].value == pytest.approx(45.3, abs=0.2)
    assert p["ΔH"].value == pytest.approx(134.8, rel=0.05)
    assert p["ΔCp"].value == pytest.approx(2.0, abs=0.8)


def test_true_value_lies_inside_confidence_interval():
    T, cp = synthetic.dsc_two_state(dCp=0.0, seed=7)
    res = fitting.fit_dsc_two_state(T, cp)
    tm = next(p for p in res.params if p.name == "Tm")
    assert tm.ci95[0] <= 45.3 <= tm.ci95[1]


def test_cal_units_give_same_result_as_kcal():
    T, cp = synthetic.dsc_two_state(dCp=0.0)
    a = fitting.fit_dsc_two_state(T, cp, cp_unit="kcal")
    b = fitting.fit_dsc_two_state(T, cp * 1000, cp_unit="cal")
    assert a.params[1].value == pytest.approx(b.params[1].value, rel=1e-4)


def test_irreversible_fit_recovers_parameters():
    T, cp, v = synthetic.dsc_irreversible()
    res = fitting.fit_dsc_irreversible(T, cp, v)
    p = {x.name: x.value for x in res.params}
    assert p["ΔH"] == pytest.approx(120.0, rel=0.05)
    assert p["Ea"] == pytest.approx(95.0, rel=0.08)
    assert p["T* (k = 1/min)"] - KELVIN == pytest.approx(52.0, abs=0.5)
    assert res.r2 > 0.99


# ---------------------------------------------------------------- input validation
def test_too_few_points_rejected():
    with pytest.raises(fitting.FitError):
        fitting.fit_dsc_two_state(np.arange(5.0), np.arange(5.0))


def test_duplicate_temperatures_rejected():
    T = np.linspace(30, 60, 30)
    T[5] = T[4]
    with pytest.raises(fitting.FitError):
        fitting.fit_dsc_two_state(T, np.ones(30))


def test_irreversible_needs_scan_rate():
    T, cp, _ = synthetic.dsc_irreversible()
    with pytest.raises(fitting.FitError):
        fitting.fit_dsc_irreversible(T, cp, 0)
