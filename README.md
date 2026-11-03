# Strict CT-Baseline Multimodal FVC Forecasting — Public Reproducibility Release

This is the **sanitized public-release package** for the manuscript *Strict CT-Baseline Multimodal Learning for Future FVC Prediction in Pulmonary Fibrosis*.

## Privacy and OSIC data-use compliance

The public release does **not** contain:

- original OSIC clinical CSV files or DICOM images;
- OSIC pseudonymous patient identifiers;
- any mapping between OSIC identifiers and the study-specific `PF###` release labels;
- row-level OOF target/prediction files containing source-derived patient trajectories;
- per-patient clinical measurements that could facilitate linkage back to the source dataset.

The `PF###` labels are one-time random release labels with no algorithmic relationship to OSIC identifiers. The mapping is not distributed.

## What is released

- the frozen final-v10 model source;
- the exact strict CT-baseline eligibility and patient-balanced fold construction code;
- an anonymous 29-patient release manifest with fold and target-count information only;
- aggregate fold summaries;
- aggregate primary, oracle/persistence, catastrophic-failure, and audited ablation results;
- scripts that authorized OSIC users can run locally to reconstruct the strict cohort, folds, OOF metrics, reviewer oracle analysis, catastrophic-error table, and clinical-temporal Ridge baseline.

## Manuscript reference results

- source cohort: 176 patients;
- strict cohort: 29 patients;
- strict future targets: 231;
- MAE: 169.416 mL;
- RMSE: 243.886 mL;
- modified Laplace log-likelihood: -6.954222;
- mean predicted uncertainty: 196.857 mL;
- 14 predictions had absolute error >=500 mL.

Reviewer-requested diagnostics:

- persistence MAE/RMSE: 210.100 / 293.985 mL;
- retrospective oracle-best-expert MAE/RMSE: 99.029 / 182.002 mL;
- all 14 catastrophic targets lay outside the seven-expert prediction range;
- 10/14 remained >=500 mL even under retrospective oracle selection.

## Reconstructing the strict cohort and folds

Obtain an authorized local copy of the OSIC `train.csv`, then run:

```bash
python analysis/rebuild_strict_cohort_and_folds.py --train-csv /path/to/train.csv
```

For the manuscript dataset this should report 176 source patients, 29 strict eligible patients, 147 excluded patients, and 231 future targets. The locally generated files retain source identifiers and are written under `local_outputs/`, which is excluded from Git.

## Recomputing prediction metrics

Run the frozen model on your authorized OSIC copy to generate an OOF file, then:

```bash
python analysis/analyze_local_oof.py --oof local_outputs/your_oof.csv
python analysis/make_catastrophic_expert_range_table.py --oof local_outputs/your_oof.csv
```

## Important reproducibility note

The public repository intentionally does not ship the submitted 231-row OOF file because exact row-level source-derived trajectories can remain linkable even after replacing direct identifiers. Aggregate reference values are provided so an authorized user can check the locally regenerated output.

## Clinical-use disclaimer

This repository supports research reproducibility. The model has not undergone external or prospective clinical validation and is not a clinical decision-support system.
