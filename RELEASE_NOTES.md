# v1.0.0 release notes

This is the first sanitized reproducibility release associated with the manuscript *Strict CT-Baseline Multimodal Learning for Future FVC Prediction in Pulmonary Fibrosis*.

## Included

- frozen final-v10 model source;
- strict CT-baseline eligibility and deterministic five-fold reconstruction code;
- anonymous cohort-structure manifest using one-time `PF###` release labels;
- aggregate fold and primary-performance summaries;
- reviewer-requested persistence/oracle and catastrophic-failure aggregate diagnostics;
- standardized bootstrap ablation summaries;
- scripts for authorized OSIC users to regenerate source-level cohort/fold assignments and local OOF analyses.

## Deliberately excluded

- original OSIC clinical CSVs and DICOM images;
- OSIC pseudonymous patient identifiers;
- any source-ID crosswalk;
- submitted row-level OOF predictions;
- per-patient source-derived clinical trajectories.

## Reference aggregate results

Strict cohort: 29 patients / 231 future targets.

Final ensemble: MAE 169.416 mL; RMSE 243.886 mL; modified LLL -6.954222.

This software release is for research reproducibility and is not a clinical decision-support system.
