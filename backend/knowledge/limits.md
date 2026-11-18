# Limits of ThermoFit

## What the app can do
ThermoFit fits differential scanning calorimetry (DSC) curves with two models: a reversible two-state model and an irreversible N → D model. It reports the fitted parameters with uncertainties and the quality of the fit (R² and the typical deviation).

## What the app cannot do
- It fits only DSC data. Other methods such as fluorescence or circular dichroism are not supported.
- The two-state model assumes one cooperative transition with a constant ΔCp. Multi-domain proteins, intermediate states and aggregation need more elaborate models that are not implemented.
- The irreversible model describes a single N → D step. More complex mechanisms are not covered.
- The baseline is a straight line. A sigmoidal baseline is not available.
- The web interface fits one scan rate at a time.
- The app does not give medical, regulatory or GxP-validated results. It is a research and learning tool.

## How reliable the results are
- Uncertainties come from a linear approximation, not from bootstrapping.
- On real curves, the residuals are structured near the peak, up to about 4 % of the peak height. The ideal model is a very good, but not a perfect description.
- On the digitized thesis curves, Tm agrees with the published values within about 0.1 °C. ΔH is about 2 % higher than published, and the reason is not established.

## About the demo data
The simulated demo curves are not measurements. The thesis demo curves are digitized from published figures (A. V. Kladova, Int. J. Biol. Macromol. 45:524, 2009), not raw instrument files.

## What the assistant does not know
The assistant explains the fit and the models using only this knowledge base. It cannot judge the quality of the sample, the experiment or the biological meaning of a result beyond what is described here.
