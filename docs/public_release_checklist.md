# Public release checklist

Before publication or Zenodo archiving:

- [ ] Use a **new repository with clean history**; do not make the internal repository containing OSIC pseudonymous IDs public.
- [ ] Confirm `grep -R -E "ID[0-9]{20,}" .` returns no matches.
- [ ] Confirm no `local_outputs/`, source OSIC CSV, DICOM, feature cache, or private mapping file is present.
- [ ] Confirm only anonymous `PF###` identifiers appear in cohort files.
- [ ] Run the static release audit.
- [ ] Tag the verified release as `v1.0.0`.
- [ ] Archive that tag in Zenodo and use the resulting DOI in the revised manuscript.
