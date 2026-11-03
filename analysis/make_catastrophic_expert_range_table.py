#!/usr/bin/env python3
"""Generate the 14-case reviewer expert-range table from a local OOF file.

Output stays local by default because row-level source-derived values can be
linkable to the source dataset even when direct identifiers are removed.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--oof',required=True,type=Path)
    ap.add_argument('--output',type=Path,default=Path('local_outputs/reviewer_catastrophic_expert_ranges_LOCAL.csv'))
    args=ap.parse_args(); df=pd.read_csv(args.oof)
    y=df.TargetFVC.to_numpy(float); p=df.PredFVC.to_numpy(float); ae=np.abs(p-y); cat=ae>=500
    ex=[c for c in df.columns if c.startswith('Expert_')]; A=df[ex].to_numpy(float); Ac=A[cat]; yc=y[cat]
    idx=np.argmin(np.abs(Ac-yc[:,None]),axis=1); oracle=Ac[np.arange(len(yc)),idx]
    out=pd.DataFrame({
        'Case':[f'Case{i:02d}' for i in range(1,cat.sum()+1)],
        'Fold':df.loc[cat,'Fold'].to_numpy(),
        'EnsembleAbsError_mL':ae[cat],
        'ExpertMinFVC_mL':Ac.min(1),'ExpertMaxFVC_mL':Ac.max(1),
        'TargetOutsideExpertRange':(yc<Ac.min(1))|(yc>Ac.max(1)),
        'OracleBestExpert':[ex[i] for i in idx],
        'OracleBestAbsError_mL':np.abs(oracle-yc),
    })
    args.output.parent.mkdir(parents=True,exist_ok=True); out.to_csv(args.output,index=False)
    print(out.to_string(index=False)); print(f'Wrote {args.output}')

if __name__=='__main__': main()
