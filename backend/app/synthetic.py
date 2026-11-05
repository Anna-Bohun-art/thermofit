"""Synthetic (clearly artificial) data generators used for tests and the demo button.

The default two-state parameters mirror values reported for a Zn-adenylate-kinase
DSC experiment (Tm 45.3 degC, dH 134.8 kcal/mol, dCp 2.0 kcal/mol/K). The data
are SIMULATED, never measured.
"""
from __future__ import annotations

import numpy as np

from . import models

KELVIN = 273.15


def dsc_two_state(Tm_c=45.3, dH=134.8, dCp=2.0, b0=1.0, b1=0.004, noise=0.02, seed=1, n=250):
    """Return (T_degC, cp_kcal_per_mol_per_K). dH, dCp in kcal/mol(/K)."""
    rng = np.random.default_rng(seed)
    T_c = np.linspace(Tm_c - 15, Tm_c + 15, n)
    Tm = Tm_c + KELVIN
    cp = models.dsc_two_state(T_c + KELVIN, Tm, dH * 1e3, dCp * 1e3, b0 * 1e3, b1 * 1e3) / 1e3
    return T_c, cp + rng.normal(0, noise, n)


def dsc_irreversible(dH=120.0, T_star_c=52.0, Ea=95.0, b0=0.8, b1=0.003, v=1.0, noise=0.02, seed=2, n=300):
    rng = np.random.default_rng(seed)
    T_c = np.linspace(T_star_c - 15, T_star_c + 20, n)
    T_star = T_star_c + KELVIN
    cp = models.dsc_irreversible(T_c + KELVIN, dH * 1e3, T_star, Ea * 1e3, b0 * 1e3, b1 * 1e3, v) / 1e3
    return T_c, cp + rng.normal(0, noise, n), v
