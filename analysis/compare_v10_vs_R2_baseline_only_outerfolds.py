#!/usr/bin/env python3
"""Paired comparison of frozen-v10 OOF predictions vs Reviewer-2 sensitivity OOF.

Run AFTER the baseline-only-outer-fold sensitivity model has completed.
This script does not retrain anything. It aligns the same strict targets and
performs a paired patient-cluster bootstrap of performance differences.

By convention:
  DeltaMAE  = sensitivity MAE - frozen-v10 MAE   (positive = sensitivity worse)
  DeltaRMSE = sensitivity RMSE - frozen-v10 RMSE (positive = sensitivity worse)
  LLLLoss   = frozen-v10 LLL - sensitivity LLL   (positive = sensitivity worse)

Patient identifiers remain local. Do not publish row-level outputs or source IDs.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

DEFAULT_REFERENCE = Path('/kaggle/working/recovery_v10_final_stable_oof_predictions.csv')
DEFAULT_SENSITIVITY = Path('/kaggle/working/reviewer2_v10_baseline_only_outerfold_oof_predictions.csv')
DEFAULT_OUT = Path('/kaggle/working/R2_comment2_baseline_only_outerfold_comparison.csv')
DEFAULT_BOOT = Path('/kaggle/working/R2_comment2_baseline_only_outerfold_bootstrap.csv')


def metrics(y, pred, sigma):
    y=np.asarray(y,float); pred=np.asarray(pred,float); sigma=np.asarray(sigma,float)
    e=pred-y; ae=np.abs(e)
    ss=np.maximum(sigma,70.0); delta=np.minimum(ae,1000.0)
    lll=np.mean(-(np.sqrt(2.0)*delta/ss + np.log(np.sqrt(2.0)*ss)))
    return {
        'MAE': float(ae.mean()),
        'RMSE': float(np.sqrt(np.mean(e**2))),
        'LLL': float(lll),
        'N500': int(np.sum(ae>=500.0)),
        'MeanSigma': float(np.mean(sigma)),
    }


def align(reference, sensitivity):
    keys=['Patient','BaselineWeek','BaselineFVC','TargetWeek','TargetFVC']
    for k in keys:
        if k not in reference or k not in sensitivity:
            raise KeyError(f'Missing alignment key: {k}')
    a=reference[keys+['PredFVC','PredSigma','Fold']].copy()
    b=sensitivity[keys+['PredFVC','PredSigma','Fold']].copy()
    a=a.rename(columns={'PredFVC':'PredFVC_ref','PredSigma':'PredSigma_ref','Fold':'Fold_ref'})
    b=b.rename(columns={'PredFVC':'PredFVC_sens','PredSigma':'PredSigma_sens','Fold':'Fold_sens'})
    m=a.merge(b,on=keys,how='outer',indicator=True,validate='one_to_one')
    if not (m['_merge']=='both').all():
        print(m[m['_merge']!='both'][keys+['_merge']].head(20).to_string(index=False))
        raise RuntimeError('Reference and sensitivity OOF targets do not align exactly.')
    return m.drop(columns='_merge')


def bootstrap(m, B=5000, seed=20260818):
    patients=np.array(sorted(m.Patient.astype(str).unique()))
    rng=np.random.default_rng(seed)
    rows=[]
    patient_array=m.Patient.astype(str).to_numpy()
    for b in range(B):
        sampled=rng.choice(patients,size=len(patients),replace=True)
        idx=np.concatenate([np.flatnonzero(patient_array==pid) for pid in sampled])
        z=m.iloc[idx]
        r=metrics(z.TargetFVC,z.PredFVC_ref,z.PredSigma_ref)
        s=metrics(z.TargetFVC,z.PredFVC_sens,z.PredSigma_sens)
        rows.append({
            'Bootstrap':b+1,
            'DeltaMAE':s['MAE']-r['MAE'],
            'DeltaRMSE':s['RMSE']-r['RMSE'],
            'LLLLoss':r['LLL']-s['LLL'],
            'DeltaN500':s['N500']-r['N500'],
        })
    return pd.DataFrame(rows)


def ci_row(name, observed, vals):
    vals=np.asarray(vals,float)
    return {
        'Metric':name,
        'ObservedDifference':observed,
        'BootstrapMean':float(np.mean(vals)),
        'CI_Lower':float(np.quantile(vals,0.025)),
        'CI_Upper':float(np.quantile(vals,0.975)),
        'ProbabilitySensitivityWorse':float(np.mean(vals>0)),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference',type=Path,default=DEFAULT_REFERENCE)
    ap.add_argument('--sensitivity',type=Path,default=DEFAULT_SENSITIVITY)
    ap.add_argument('--repetitions',type=int,default=5000)
    ap.add_argument('--seed',type=int,default=20260818)
    ap.add_argument('--output',type=Path,default=DEFAULT_OUT)
    ap.add_argument('--bootstrap-output',type=Path,default=DEFAULT_BOOT)
    args=ap.parse_args()

    ref=pd.read_csv(args.reference); sens=pd.read_csv(args.sensitivity)
    m=align(ref,sens)
    if len(m)!=231 or m.Patient.nunique()!=29:
        raise RuntimeError(f'Expected 29 patients / 231 targets; got {m.Patient.nunique()} / {len(m)}')

    mr=metrics(m.TargetFVC,m.PredFVC_ref,m.PredSigma_ref)
    ms=metrics(m.TargetFVC,m.PredFVC_sens,m.PredSigma_sens)
    observed={
        'DeltaMAE':ms['MAE']-mr['MAE'],
        'DeltaRMSE':ms['RMSE']-mr['RMSE'],
        'LLLLoss':mr['LLL']-ms['LLL'],
        'DeltaN500':ms['N500']-mr['N500'],
    }
    boot=bootstrap(m,B=args.repetitions,seed=args.seed)
    summary=pd.DataFrame([
        ci_row('DeltaMAE',observed['DeltaMAE'],boot.DeltaMAE),
        ci_row('DeltaRMSE',observed['DeltaRMSE'],boot.DeltaRMSE),
        ci_row('LLLLoss',observed['LLLLoss'],boot.LLLLoss),
        ci_row('DeltaN500',observed['DeltaN500'],boot.DeltaN500),
    ])
    summary['Patients']=29; summary['Targets']=231
    summary['BootstrapSeed']=args.seed; summary['BootstrapRepetitions']=args.repetitions

    print('\nFROZEN v10')
    print(pd.Series(mr).to_string())
    print('\nBASELINE-ONLY OUTER-FOLD SENSITIVITY')
    print(pd.Series(ms).to_string())
    print('\nPAIRED SENSITIVITY - FROZEN v10')
    print(summary.round(6).to_string(index=False))

    args.output.parent.mkdir(parents=True,exist_ok=True)
    summary.to_csv(args.output,index=False)
    boot.to_csv(args.bootstrap_output,index=False)
    print(f'\nSaved: {args.output}')
    print(f'Saved: {args.bootstrap_output}')


if __name__=='__main__':
    main()
