#!/usr/bin/env python3
from pathlib import Path
import re, sys, pandas as pd

root=Path(__file__).resolve().parents[1]
id_pattern=re.compile(r'ID\d{20,}')
forbidden_name_patterns=[
    re.compile(r'(^|/)submitted_oof_predictions\.csv$', re.I),
    re.compile(r'(^|/).*_oof_predictions\.csv$', re.I),
    re.compile(r'(^|/).*_patient_changes\.csv$', re.I),
    re.compile(r'(^|/).*_outer_fold_assignments_LOCAL_DO_NOT_PUBLISH\.csv$', re.I),
    re.compile(r'(^|/).*_per_patient_oof_metrics\.csv$', re.I),
    re.compile(r'(^|/).*_strict_excluded_patients\.csv$', re.I),
    re.compile(r'(^|/).*_dynamic_followup_manifest\.csv$', re.I),
    re.compile(r'(^|/)PRIVATE_osic.*', re.I),
    re.compile(r'.*\.dcm$', re.I),
]

violations=[]
for p in root.rglob('*'):
    if not p.is_file() or '.git' in p.parts:
        continue
    rel=str(p.relative_to(root))
    if any(rx.search(rel) for rx in forbidden_name_patterns):
        violations.append(f"forbidden file: {rel}")
        continue
    if p.suffix.lower() in {'.zip','.png','.jpg','.jpeg','.pdf','.pkl'}:
        continue
    try:
        txt=p.read_text(errors='ignore')
    except Exception:
        continue
    if id_pattern.search(txt):
        violations.append(f"protected ID in: {rel}")

if violations:
    print('FAIL: public-release audit violations:')
    for v in violations:
        print(' -',v)
    sys.exit(1)

x=pd.read_csv(root/'cohort/release_patient_manifest.csv')
assert len(x)==29 and x.ReleasePatientID.nunique()==29 and x.NFutureTargets.sum()==231
assert x.ReleasePatientID.str.fullmatch(r'PF\d{3}').all()

print('PASS: no OSIC-style pseudonymous IDs detected in text files.')
print('PASS: no prohibited row-level/source-linked files detected.')
print('PASS: anonymous manifest has 29 patients and 231 targets.')
