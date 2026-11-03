# Strict CT-Baseline Multimodal FVC Forecasting — Reproducibility Release

This repository is the **sanitized public reproducibility release** for the manuscript *Strict CT-Baseline Multimodal Learning for Future FVC Prediction in Pulmonary Fibrosis*.

## Data-use and privacy boundary

The release does **not** contain:

- original OSIC clinical CSV files or DICOM images;
- OSIC pseudonymous patient identifiers;
- any source-ID-to-release-ID crosswalk;
- row-level OOF target/prediction files containing source-derived patient trajectories;
- per-patient clinical measurements that could facilitate linkage back to the source dataset.

The `PF###` labels are one-time study-specific anonymous release labels. They are not hashes, are not derived from OSIC identifiers or clinical values, and are not intended to identify which source patient corresponds to a particular release label.

## What is released

- the frozen final-v10 model source;
- executable code implementing the strict CT-baseline eligibility rule;
- executable code implementing the deterministic patient-balanced five-fold construction used in the manuscript;
- an anonymous cohort-structure manifest containing release label, fold, and number of future targets only;
- aggregate fold summaries and aggregate manuscript/reviewer results;
- scripts that authorized OSIC users can run locally to reconstruct the exact source-ID strict cohort, exclusions, future targets, outer folds, OOF metrics, reviewer oracle analysis, catastrophic-error table, and clinical-temporal Ridge baseline.

## Reproducibility workflow

Researchers with authorized access to the OSIC Pulmonary Fibrosis Progression dataset should obtain the original `train.csv` and DICOM data from the authorized source. Then run:

```bash
python analysis/rebuild_strict_cohort_and_folds.py --train-csv /path/to/train.csv
```

For the manuscript dataset, the script should reproduce:

- 176 source patients;
- 29 strict eligible patients;
- 147 excluded patients;
- 231 strictly post-CT future targets;
- the deterministic five outer folds used in the manuscript.

The locally regenerated files retain the original source identifiers and are written under `local_outputs/`, which is excluded from Git.

The anonymous `PF###` manifest is therefore a public description of cohort/fold structure, not a crosswalk to the source data. Exact source-level verification is performed locally by rerunning the supplied eligibility and fold-construction code on an authorized OSIC copy.

## Manuscript reference results

- MAE: **169.416 mL**
- RMSE: **243.886 mL**
- modified Laplace log-likelihood: **-6.954222**
- mean predicted uncertainty: **196.857 mL**
- predictions with absolute error >=500 mL: **14**

Reviewer-requested diagnostics:

- persistence MAE/RMSE: **210.100 / 293.985 mL**
- retrospective oracle-best-expert MAE/RMSE: **99.029 / 182.002 mL**
- catastrophic targets outside the seven-expert prediction range: **14/14**
- catastrophic cases remaining >=500 mL under retrospective oracle selection: **10/14**

## Recomputing prediction metrics

After generating local OOF predictions with the frozen model:

```bash
python analysis/analyze_local_oof.py --oof local_outputs/your_oof.csv
python analysis/make_catastrophic_expert_range_table.py --oof local_outputs/your_oof.csv
```

## Availability boundary

The 231-row submitted OOF file is intentionally not distributed because exact row-level source-derived trajectories can remain linkable even after direct identifiers are removed. Aggregate reference values are provided so authorized users can verify their locally regenerated outputs.

## Clinical-use disclaimer

This repository supports research reproducibility. The model has not undergone external or prospective clinical validation and is not a clinical decision-support system.
