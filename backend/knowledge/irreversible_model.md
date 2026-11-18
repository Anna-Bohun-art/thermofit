# Irreversible model (N → D)

## What the model assumes
The protein unfolds in one step from the native state (N) to a final state (D), and the process cannot be reversed. Cooling the sample does not bring the protein back to the folded state, for example because it aggregates after unfolding. The unfolding is a first-order reaction whose rate depends on temperature according to the Arrhenius law (Sanchez-Ruiz model).

## Why the scan rate matters
The process is controlled by kinetics, not by an equilibrium. The faster the sample is heated, the higher the temperature at which the peak appears. The same protein therefore gives a different peak position at 0.5 K/min than at 1 K/min. The scan rate must be entered when fitting, and the peak temperature is not a true equilibrium melting temperature.

## T* (temperature of one unfolding per minute)
T* is the temperature at which the rate constant equals 1 per minute. It describes where the unfolding becomes fast for the given kinetics, and it does not depend on the scan rate.

## Ea (activation energy)
Ea is the energy barrier of the unfolding. It describes how strongly the unfolding rate increases with temperature. A larger Ea gives a sharper and narrower peak. In the app it is shown in kcal/mol.

## ΔH (unfolding enthalpy)
ΔH is the heat absorbed by the unfolding of one mole of protein, which is the area under the peak. For an irreversible process it is not an equilibrium value, so no Gibbs energy (ΔG) or stability curve can be derived from it.

## Baseline and fitting
A straight baseline is fitted together with the model. The app fits one scan rate at a time. Fitting several scan rates together gives a more precise Ea, but this global fit exists only in the backend and is not available in the web interface yet.
