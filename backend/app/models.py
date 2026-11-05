"""Physical models for protein thermal stability (DSC): reversible two-state and irreversible.

Units
-----
Temperature  : K inside the models (API accepts degC and converts)
Energy       : cal/mol  (DSC literature convention; kcal/mol in the API output)
Heat capacity: cal/(mol K)
R            : 1.987204 cal/(mol K)
"""
from __future__ import annotations

import numpy as np

R_CAL = 1.987204  # cal / (mol K)


# --------------------------------------------------------------------------- #
# 1) Reversible two-state unfolding  N <-> D
# --------------------------------------------------------------------------- #
def two_state_fraction_unfolded(T, Tm, dH, dCp):
    """Fraction unfolded alpha(T) for a reversible two-state transition.

    dH is the enthalpy at Tm. The temperature dependence of the enthalpy uses
    a constant heat-capacity change dCp (Gibbs-Helmholtz):
        dH(T) = dH + dCp (T - Tm)
        dG(T) = dH (1 - T/Tm) + dCp (T - Tm - T ln(T/Tm))
        K     = exp(-dG / RT),   alpha = K / (1 + K)
    """
    T = np.asarray(T, dtype=float)
    dG = dH * (1.0 - T / Tm) + dCp * (T - Tm - T * np.log(T / Tm))
    # clip the exponent to avoid overflow far from Tm
    x = np.clip(-dG / (R_CAL * T), -700, 700)
    K = np.exp(x)
    return K / (1.0 + K)


def two_state_excess_cp(T, Tm, dH, dCp):
    """Excess heat capacity of a two-state transition.

    Cp_ex = dH(T) * d(alpha)/dT + alpha * dCp
          = dH(T)^2 * K / (R T^2 (1+K)^2)  +  alpha * dCp
    """
    T = np.asarray(T, dtype=float)
    dH_T = dH + dCp * (T - Tm)
    alpha = two_state_fraction_unfolded(T, Tm, dH, dCp)
    van_t_hoff = dH_T**2 * alpha * (1.0 - alpha) / (R_CAL * T**2)
    return van_t_hoff + alpha * dCp


def dsc_two_state(T, Tm, dH, dCp, b0, b1):
    """Observed DSC signal: two-state excess Cp + linear baseline.

    Baseline: b0 + b1 * (T - Tm). Parameters in cal/mol/K (b0), cal/mol/K^2 (b1).
    """
    T = np.asarray(T, dtype=float)
    return two_state_excess_cp(T, Tm, dH, dCp) + b0 + b1 * (T - Tm)


# --------------------------------------------------------------------------- #
# 2) Irreversible one-step unfolding  N -> D  (Sanchez-Ruiz, 1988)
# --------------------------------------------------------------------------- #
def irreversible_excess_cp(T, dH, T_star, Ea, scan_rate_K_per_min):
    """Excess Cp for N -> D with first-order Arrhenius kinetics at a constant scan rate.

        k(T)  = exp( Ea/R (1/T* - 1/T) )          [1/min], k(T*) = 1/min
        x(T)  = exp( -(1/v) * integral_{T0}^{T} k dT' )   (fraction native)
        Cp_ex = dH * k(T) / v * x(T)

    T must be strictly increasing. The integral is evaluated numerically
    (cumulative trapezoid), so keep the temperature grid reasonably fine.
    """
    T = np.asarray(T, dtype=float)
    v = float(scan_rate_K_per_min)
    k = np.exp(Ea / R_CAL * (1.0 / T_star - 1.0 / T))
    seg = 0.5 * (k[1:] + k[:-1]) * np.diff(T)
    integral = np.concatenate([[0.0], np.cumsum(seg)])
    x_native = np.exp(-integral / v)
    return dH * k / v * x_native


def dsc_irreversible(T, dH, T_star, Ea, b0, b1, scan_rate_K_per_min):
    T = np.asarray(T, dtype=float)
    return irreversible_excess_cp(T, dH, T_star, Ea, scan_rate_K_per_min) + b0 + b1 * (T - T_star)


def irreversible_tm(T, dH, T_star, Ea, scan_rate_K_per_min):
    """Temperature at which the (baseline-free) excess Cp is maximal."""
    cp = irreversible_excess_cp(T, dH, T_star, Ea, scan_rate_K_per_min)
    return float(np.asarray(T)[int(np.argmax(cp))])


# --------------------------------------------------------------------------- #
# Derived thermodynamics of the two-state model
# --------------------------------------------------------------------------- #
def gibbs_energy(T, Tm, dH, dCp):
    """Unfolding free energy dG(T) in the same energy units as dH (Gibbs-Helmholtz)."""
    T = np.asarray(T, dtype=float)
    return dH * (1.0 - T / Tm) + dCp * (T - Tm - T * np.log(T / Tm))


def temperature_of_max_stability(Tm, dH, dCp):
    """Ts: the temperature where dG is maximal (d dG / dT = 0, i.e. dS = 0).

    Ts = Tm * exp(-dH / (Tm * dCp)). It can lie below 0 degC (cold denaturation regime).
    """
    return Tm * np.exp(-dH / (Tm * dCp))
