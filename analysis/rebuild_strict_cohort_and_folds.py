#!/usr/bin/env python3
"""Regenerate the strict CT-baseline cohort and exact five outer folds.

This script requires an authorized local copy of OSIC train.csv. It writes
source pseudonymous identifiers only to a local output directory, which should
remain outside version control. The public repository never contains those IDs.

The eligibility and fold-balancing logic mirrors FVC_Pred_FinalStable_v10.py.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

SEED = 42
N_SPLITS = 5
CT_WEEK_ZERO = 0.0
MIN_TARGET_WEEK_FROM_CT = 0.0
RAPID_Q = 0.25
W_PATIENT = 1.5
W = np.array([1.8, 1.0, 1.0, 0.8, 1.6, 1.0, 1.0], dtype=float)
W_RAPID = 1.6

def _select_baseline(group):
    g = group.copy()
    g['Weeks'] = pd.to_numeric(g['Weeks'], errors='coerce')
    g = g[np.isfinite(g['Weeks'])].copy()
    e = g[g['Weeks'] <= CT_WEEK_ZERO].copy()
    if e.empty:
        return None
    best = float(e['Weeks'].max())
    return e[np.isclose(e['Weeks'], best)].reset_index(drop=True).iloc[0]

def _ols_slope(group):
    x = group['Weeks'].to_numpy(float)
    y = group['FVC'].to_numpy(float)
    if len(x) < 2 or np.allclose(x, x[0]):
        return 0.0
    xc = x - x.mean()
    return float(np.sum(xc * (y-y.mean())) / max(np.sum(xc**2), 1e-8))

def _forward_slope(group, baseline):
    bw = float(baseline['Weeks'])
    f = group[(group['Weeks'].astype(float) > MIN_TARGET_WEEK_FROM_CT) &
              (group['Weeks'].astype(float) > bw)].copy()
    s = (pd.concat([pd.DataFrame([baseline]), f], ignore_index=True)
           .sort_values('Weeks').drop_duplicates('Weeks', keep='first')
           .reset_index(drop=True))
    return _ols_slope(s)

def build_records(df):
    rows, excluded = [], []
    for pid, group in df.groupby('Patient'):
        group = group.sort_values('Weeks').reset_index(drop=True)
        b = _select_baseline(group)
        if b is None:
            excluded.append((pid, 'no_FVC_at_or_before_CT'))
            continue
        bw = float(b['Weeks'])
        target_mask = ((group['Weeks'].astype(float) > MIN_TARGET_WEEK_FROM_CT) &
                       (group['Weeks'].astype(float) > bw))
        if not bool(np.any(target_mask)):
            excluded.append((pid, 'no_post_CT_target'))
            continue
        bfvc = float(b['FVC'])
        pct = float(b['Percent'])
        slope = _forward_slope(group, b)
        for _, cur in group.iterrows():
            tw = float(cur['Weeks'])
            if tw <= MIN_TARGET_WEEK_FROM_CT or tw <= bw:
                continue
            rows.append({'Patient':str(pid),'TargetFVC':float(cur['FVC']),
                         'BaselineFVC':bfvc,'Percent':pct,'BaselineWeek':bw,
                         'PatientSlope':slope,'TargetWeekFromCT':tw})
    return pd.DataFrame(rows), pd.DataFrame(excluded, columns=['Patient','ExclusionReason'])

def patient_summary(records):
    p=(records.groupby('Patient').agg(
        NTargets=('TargetFVC','size'), BaselineFVC=('BaselineFVC','first'),
        Percent=('Percent','first'), BaselineWeek=('BaselineWeek','first'),
        PatientSlope=('PatientSlope','first'), MeanHorizon=('TargetWeekFromCT','mean'),
        MaxHorizon=('TargetWeekFromCT','max')).reset_index())
    q=float(np.quantile(p['PatientSlope'].to_numpy(float), RAPID_Q))
    p['RapidDecliner']=(p['PatientSlope'].to_numpy(float) <= q).astype(float)
    return p

def make_folds(records):
    p=patient_summary(records); n=len(p)
    cols=['NTargets','BaselineFVC','Percent','BaselineWeek','PatientSlope','MeanHorizon','MaxHorizon']
    X=p[cols].to_numpy(float); mu=X.mean(0); sd=X.std(0,ddof=0); sd=np.where(sd<1e-8,1.0,sd)
    Z=(X-mu)/sd; rapid=p['RapidDecliner'].to_numpy(float); rapid_centered=rapid-rapid.mean()
    V=np.column_stack([np.ones(n)*W_PATIENT, Z*W.reshape(1,-1), rapid_centered*W_RAPID])
    desired=V.sum(0)/float(N_SPLITS); sums=np.zeros((N_SPLITS,V.shape[1])); members=[[] for _ in range(N_SPLITS)]
    rng=np.random.default_rng(SEED); extremeness=np.linalg.norm(V[:,1:],axis=1); jitter=rng.uniform(0,1e-6,size=n)
    order=np.argsort(-(extremeness+jitter))
    for f,idx in enumerate(order[:N_SPLITS]): members[f].append(int(idx)); sums[f]+=V[idx]
    for idx in order[N_SPLITS:]:
        costs=[]
        for f in range(N_SPLITS):
            trial=sums.copy(); trial[f]+=V[idx]
            imbalance=np.sum((trial-desired.reshape(1,-1))**2)
            counts=np.array([len(m)+(1 if k==f else 0) for k,m in enumerate(members)],float)
            costs.append(float(imbalance + 0.25*np.var(counts)))
        best_cost=min(costs)
        candidates=[f for f,c in enumerate(costs) if np.isclose(c,best_cost,rtol=1e-10,atol=1e-10)]
        best=min(candidates,key=lambda f:len(members[f])); members[best].append(int(idx)); sums[best]+=V[idx]
    assignment=[]
    for fold,idxs in enumerate(members,start=1):
        for pid in p.iloc[idxs]['Patient'].astype(str): assignment.append((pid,fold))
    return p, pd.DataFrame(assignment,columns=['Patient','OuterFold'])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--train-csv',required=True,type=Path)
    ap.add_argument('--out-dir',type=Path,default=Path('local_outputs'))
    args=ap.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(args.train_csv)
    records, excluded=build_records(df); p, folds=make_folds(records)
    manifest=p.merge(folds,on='Patient',how='left')
    manifest.to_csv(args.out_dir/'strict_cohort_LOCAL_DO_NOT_PUBLISH.csv',index=False)
    excluded.to_csv(args.out_dir/'strict_excluded_LOCAL_DO_NOT_PUBLISH.csv',index=False)
    print(f'Source patients: {df.Patient.nunique()}')
    print(f'Strict eligible patients: {records.Patient.nunique()}')
    print(f'Strict excluded patients: {excluded.Patient.nunique()}')
    print(f'Strict future targets: {len(records)}')
    print('Fold patient counts:', folds.groupby('OuterFold').size().to_dict())
    if df.Patient.nunique()==176:
        assert records.Patient.nunique()==29, 'Expected 29 strict patients for the manuscript dataset.'
        assert len(records)==231, 'Expected 231 strict future targets.'
        assert excluded.Patient.nunique()==147, 'Expected 147 excluded patients.'
        print('PASS: cohort counts match the manuscript.')
    print(f'Local outputs written to {args.out_dir} (do not publish these source-ID files).')

if __name__=='__main__': main()