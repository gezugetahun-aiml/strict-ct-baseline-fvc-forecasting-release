# Data availability and OSIC terms

The original OSIC Pulmonary Fibrosis Progression data must be obtained from the original authorized distribution and remain subject to the applicable OSIC/Kaggle terms. This repository does not redistribute source clinical records, DICOM images, or OSIC pseudonymous patient identifiers.

The public package provides code and aggregate derived results. Study-specific `PF###` labels are random anonymous release labels and cannot be mapped back to source identifiers using information in this repository.

Authorized users can regenerate the strict cohort and fold assignments from their own OSIC copy with `analysis/rebuild_strict_cohort_and_folds.py`.
