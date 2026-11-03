# Anonymization and release policy

The OSIC data-use conditions permit anonymous identifiers but do not permit redistribution of the source pseudonymous patient identifiers. This release therefore uses one-time random labels (`PF001`–`PF029`) solely to describe the anonymous study cohort and fold membership.

The release labels are **not hashes** and are not computed from OSIC identifiers, clinical measurements, row order, or any other source variable. The private mapping is not included in this repository, its Git history, releases, or archives.

To reduce linkage risk, this public package also omits row-level source-derived trajectories and patient-level clinical measurements. Authorized investigators can regenerate those outputs locally from the original OSIC data using the included scripts.
