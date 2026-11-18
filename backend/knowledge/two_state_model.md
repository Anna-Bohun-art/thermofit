# Two-state model (reversible)

## What the model assumes
The protein exists in only two states: folded (N) and unfolded (D). The two states convert into each other reversibly, so the unfolded protein can fold back when the sample is cooled. The unfolding is treated as one cooperative transition: the whole protein unfolds in a single step, with no stable intermediate states.

## What the plot shows
The x axis is the temperature in °C. The y axis is the excess heat capacity Cp, meaning the extra heat the sample absorbs per degree of heating. Unfolding absorbs heat, so the curve shows a peak. The fitted line is the model curve plus a straight baseline.

## Tm (melting temperature)
Tm is the temperature at which half of the protein is unfolded. It is also the position of the peak maximum. A higher Tm means the protein is more thermally stable.

## ΔH (unfolding enthalpy)
ΔH is the total heat absorbed when one mole of protein unfolds. It is the area under the peak, not the peak height. A larger ΔH means more heat is needed to unfold the protein. In the app it is shown in kcal/mol.

## ΔCp (heat-capacity change)
ΔCp is the difference in heat capacity between the unfolded and the folded state. It makes the heat capacity step up across the transition and determines how the stability changes with temperature. Fitting ΔCp together with a free baseline slope is poorly determined, so ΔCp is only fitted when the user switches "fit ΔCp" on.

## Baseline
The instrument background is described by a straight line (offset and slope) that is fitted together with the model. A sigmoidal (progress) baseline is not implemented.

## Uncertainties
The uncertainty (±) and the 95 % range of each parameter come from the least-squares covariance matrix. This is a linear approximation, not a bootstrap.
