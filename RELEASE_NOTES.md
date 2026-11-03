# v1.1.0 release notes

This release extends the sanitized reproducibility package for the manuscript *Strict CT-Baseline Multimodal Learning for Future FVC Prediction in Pulmonary Fibrosis* with reviewer-requested sensitivity analyses.

## New in v1.1.0

- Reviewer 2 Comment 2 baseline-only outer-fold sensitivity analysis.
- Exact unified patch against frozen v10 changing only the outer patient-fold construction.
- Paired local comparison script for submitted-v10 versus sensitivity OOF predictions.
- Aggregate sensitivity summary, fold-level results, fold profiles, and patient-cluster bootstrap confidence intervals.
- Expanded privacy audit blocking row-level OOF, patient-level change, local source-ID fold-assignment, and related source-derived files from public Git history.

## Reviewer 2 sensitivity design

Outer-fold assignment uses prediction-origin variables only: Age, Sex, SmokingStatus, baseline FVC, Percent, baseline week, CT-derived FSS, and patient-count balancing.

It does not use forward PatientSlope, rapid-decliner status, future-target count, future horizon, future FVC/Delta-FVC, or held-out prediction error.

Everything else in frozen v10 remains unchanged.

## Aggregate sensitivity result

Same strict cohort: 29 patients / 231 future targets.

- Submitted v10 MAE: 169.416 mL
- Baseline-only outer-fold MAE: 198.402 mL
- Paired Delta MAE: +28.986 mL, 95% CI 1.306 to 57.002 mL
- Submitted v10 RMSE: 243.886 mL
- Sensitivity RMSE: 267.997 mL
- Paired Delta RMSE: +24.111 mL, 95% CI -3.619 to 50.666 mL
- Submitted v10 LLL: -6.954222
- Sensitivity LLL: -7.053661
- Absolute errors >=500 mL: 14 versus 18

The sensitivity supports a more cautious interpretation: estimated MAE is materially affected by outer-fold composition in this small cohort, and both estimates remain exploratory pending external validation.

## Privacy boundary

This release does not contain original OSIC records, DICOM images, OSIC pseudonymous identifiers, source-ID crosswalks, row-level OOF predictions, patient-level change tables, or local source-ID fold assignments.

This software release is for research reproducibility and is not a clinical decision-support system.
