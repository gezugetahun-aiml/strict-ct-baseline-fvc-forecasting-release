#!/usr/bin/env python3
from pathlib import Path
import re, sys, pandas as pd
root=Path(__file__).resolve().parents[1]
pattern=re.compile(r'ID\d{20,}')
violations=[]
for p in root.rglob('*'):
    if not p.is_file() or '.git' in p.parts: continue
    if p.suffix.lower() in {'.zip','.png','.jpg','.jpeg','.pdf','.pkl'}: continue
    try: txt=p.read_text(errors='ignore')
    except Exception: continue
    if pattern.search(txt): violations.append(str(p.relative_to(root)))
if violations:
    print('FAIL: protected OSIC-style IDs found:', violations); sys.exit(1)
x=pd.read_csv(root/'cohort/release_patient_manifest.csv')
assert len(x)==29 and x.ReleasePatientID.nunique()==29 and x.NFutureTargets.sum()==231
assert x.ReleasePatientID.str.fullmatch(r'PF\d{3}').all()
print('PASS: no OSIC-style pseudonymous IDs detected in text files.')
print('PASS: anonymous manifest has 29 patients and 231 targets.')
