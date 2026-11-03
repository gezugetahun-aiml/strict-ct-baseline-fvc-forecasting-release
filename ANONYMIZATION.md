# Anonymization and release policy

Under the applicable OSIC data-use restrictions, the source pseudonymous patient identifiers are not redistributed. This release therefore uses one-time study-specific anonymous labels (`PF001`–`PF029`) only to describe cohort size, fold membership, and target counts.

The release labels are **not hashes** and are not computed from OSIC identifiers, clinical measurements, row order, or any other source variable. No source-ID crosswalk is distributed in this repository, its Git history, releases, or archives.

The anonymous labels are not intended to allow a reader to identify which OSIC source patient corresponds to a given `PF###` label. Exact source-level reproducibility is instead achieved by running the supplied deterministic eligibility and fold-construction code on an authorized local copy of the OSIC data.

To further reduce linkage risk, the public release omits row-level source-derived trajectories and per-patient clinical measurements. Those outputs can be regenerated locally by authorized investigators.
