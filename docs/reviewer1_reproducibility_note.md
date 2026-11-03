# Reviewer 1 — reproducibility and identifier restriction

The reviewer requested release of the 29-patient inclusion list and outer-fold definitions. The applicable OSIC data-use conditions do not permit redistribution of the original pseudonymous patient identifiers, so the source-ID inclusion list cannot be published directly.

To address the reproducibility concern while complying with those restrictions, the public repository provides:

1. the exact strict CT-baseline eligibility logic;
2. the deterministic patient-balanced five-fold construction used in the manuscript;
3. a study-specific anonymous cohort-structure manifest (`PF###`) reporting fold membership and target counts only;
4. aggregate expected counts and performance values for reproduction checks; and
5. local analysis scripts that authorized OSIC users can run on their own source copy.

The `PF###` labels are intentionally not cross-linked to OSIC source identifiers. An authorized investigator can instead regenerate the exact source-ID cohort, exclusions, 231 future targets, and five outer folds locally and compare the resulting aggregate outputs with the reference values in this repository.

No OSIC source-ID mapping is distributed.
