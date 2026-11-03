# Data availability and OSIC terms

The original OSIC Pulmonary Fibrosis Progression data must be obtained from the original authorized distribution and remain subject to the applicable OSIC/Kaggle data-use conditions.

This repository does not redistribute source clinical records, DICOM images, OSIC pseudonymous patient identifiers, or a source-ID crosswalk. It also omits row-level source-derived prediction trajectories that could facilitate linkage back to the source dataset.

The public package provides model/analysis code, an anonymous cohort-structure manifest, aggregate derived results, and executable scripts for local reconstruction. Researchers with authorized OSIC access can regenerate the exact strict source-ID cohort, exclusions, future targets, and five outer folds from their own copy of the data using `analysis/rebuild_strict_cohort_and_folds.py`.

The `PF###` labels are random study-specific release labels and cannot be mapped to source identifiers using information distributed in this repository.
